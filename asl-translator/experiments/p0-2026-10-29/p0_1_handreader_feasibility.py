#!/usr/bin/env python3
"""P0-1 Stage A: HandReader_RGB technical feasibility only (no accuracy, no benchmark input, no Stage A clip).

Builds the exact RGB variant from the upstream config (configs/rgb_chicago.yaml), loads the released ChicagoFSWild+
RGB checkpoint strictly, runs the upstream eval preprocessing on a SYNTHETIC clip (geometric shapes only), runs a CPU
forward pass twice (determinism) and decodes with both upstream decoders. The decoded string is meaningless by design
and is recorded only to show that the decoding path runs.

Portability patch (runtime only, upstream files are not edited):
  P1 torchvision.models.resnet{18,34,50,101}(pretrained=True) inside make_resnet would download ImageNet weights at
     construction. They are overwritten by the strict checkpoint load, so construction uses pretrained=False instead.
     No model logic or weight changes.
  P2 torch.Tensor.cuda() is a no-op without CUDA: tsm_resnet.py:452 hard-codes .cuda() on a zero padding buffer.
Device is CPU (upstream configs say cuda).

usage: python -I p0_1_handreader_feasibility.py --repo DIR --ckpt-zip FILE --rgb-ckpt FILE --out FILE
"""
import argparse, hashlib, json, platform, subprocess, sys, time
from pathlib import Path


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def synthetic_clip(n=24, size=224):
    """Shapes-only RGB frames: a white canvas with a moving dark rectangle and a coloured disc. No real-world content."""
    import numpy as np
    frames = []
    yy, xx = np.mgrid[0:size, 0:size]
    for t in range(n):
        img = np.full((size, size, 3), 235, np.uint8)
        x0 = 20 + 4 * t
        img[60:140, x0:x0 + 50] = (40, 40, 40)
        disc = (xx - (160 - 2 * t)) ** 2 + (yy - 150) ** 2 < 30 ** 2
        img[disc] = (200, 60, 60)
        frames.append(img)
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True); ap.add_argument("--ckpt-zip", type=Path, required=True)
    ap.add_argument("--rgb-ckpt", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    rec = {"stage": "P0-1 Stage A HandReader_RGB feasibility (technical only; no accuracy; synthetic input)",
           "date": "2026-10-29"}
    rec["upstream"] = {
        "repo_url": "https://github.com/ai-forever/HandReader",
        "commit": subprocess.check_output(["git", "-C", str(a.repo), "rev-parse", "HEAD"], text=True).strip(),
        "commit_date": subprocess.check_output(["git", "-C", str(a.repo), "log", "-1", "--format=%cI"], text=True).strip(),
        "n_commits": int(subprocess.check_output(["git", "-C", str(a.repo), "rev-list", "--count", "HEAD"], text=True)),
        "code_license": "Apache-2.0", "license_file_sha256": sha256(a.repo / "LICENSE"),
        "checkpoint_terms": "the checkpoint is trained on ChicagoFSWild+; its use remains subject to the relevant "
                            "dataset/checkpoint terms and is not necessarily covered by the code's Apache-2.0 licence",
        "paper": "arXiv 2505.10267, HandReader: Advanced Techniques for Efficient Fingerspelling Recognition",
        "config": "configs/rgb_chicago.yaml", "config_sha256": sha256(a.repo / "configs/rgb_chicago.yaml")}
    rec["checkpoint"] = {
        "archive": "HandReader_ChicagoFSWild+.zip (README link, Sber Cloud OBS)", "archive_sha256": sha256(a.ckpt_zip),
        "archive_bytes": a.ckpt_zip.stat().st_size, "file": "chicago+/rgb/best.pt", "sha256": sha256(a.rgb_ckpt),
        "bytes": a.rgb_ckpt.stat().st_size, "variant": "HandReader_RGB (TSM ResNet-34 + 2-layer BiGRU head, CTC)",
        "training_data": "ChicagoFSWild+ (dataset terms apply)", "binary_committed": False}

    import numpy as np, torch, torchvision, albumentations as A, hydra
    from albumentations.pytorch.transforms import ToTensorV2
    from omegaconf import OmegaConf
    rec["environment"] = {"python": sys.version.split()[0], "machine": platform.machine(),
                          "platform": platform.platform(), "torch": torch.__version__,
                          "torchvision": torchvision.__version__, "numpy": np.__version__,
                          "albumentations": A.__version__, "hydra": hydra.__version__,
                          "env": "isolated venv in the session scratch directory (not in the repo)",
                          "cuda_available": torch.cuda.is_available(), "threads": torch.get_num_threads(),
                          "python_interpreter": "anaconda Python 3.11.7 x86_64 under Rosetta on Apple Silicon (same "
                                                "platform as the OpenFS baseline runs)",
                          "install_deviations": [
                              "repo pins opencv-python(-headless) 4.10.0.82: no x86_64 macOS wheel for this Python; "
                              "opencv-python-headless 4.9.0.80 used (albumentations Resize uses cv2)",
                              "repo installs torch 2.0.1 from the cu118 index; the CPU macOS wheels of torch 2.0.1 / "
                              "torchvision 0.15.2 from PyPI used",
                              "only packages needed by the RGB inference path installed (no turbojpeg, decord, "
                              "face_recognition, mediapipe, h5py)",
                              "antlr4-python3-runtime 4.9.3 (hydra/omegaconf dependency) installed from its pure-Python "
                              "sdist", "pip check: no broken requirements"]}
    sys.path.insert(0, str(a.repo))

    patches = []
    orig = {n: getattr(torchvision.models, n) for n in ("resnet18", "resnet34", "resnet50", "resnet101")}
    for n, f in orig.items():
        setattr(torchvision.models, n, (lambda f: lambda pretrained=False, **kw: f(weights=None, **kw))(f))
    patches.append({"id": "P1", "what": "make_resnet(pretrained=True) -> constructed without the ImageNet download",
                    "why": "avoid a network fetch; those weights are overwritten by the strict checkpoint load",
                    "changes_model_logic": False, "upstream_file_edited": False})

    if not torch.cuda.is_available():
        torch.Tensor.cuda = lambda self, *a, **k: self
        patches.append({"id": "P2", "what": "torch.Tensor.cuda() returns the tensor unchanged (stays on CPU)",
                        "why": "src/models/modules/tsm_resnet.py:452 allocates the zero padding buffer with a "
                               "hard-coded .cuda(); the only CUDA call on the RGB inference path",
                        "changes_model_logic": False, "upstream_file_edited": False})

    OmegaConf.register_new_resolver("len", lambda x: len(x), replace=True)
    cfg = OmegaConf.load(a.repo / "configs/rgb_chicago.yaml")
    model = hydra.utils.instantiate(cfg.model)
    sd = torch.load(a.rgb_ckpt, map_location="cpu")
    keys_kind = type(sd).__name__
    if isinstance(sd, dict) and "state_dict" in sd:
        sd = sd["state_dict"]
    res = model.load_state_dict(sd, strict=True)                      # raises on any mismatch
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    chars = cfg.base.chars_ctc
    rec["model"] = {"target": cfg.model._target_, "encoder": cfg.model.encoder, "unidirection": cfg.model.unidirection,
                    "head": {k: cfg.model.decoder_net[k] for k in ("input_dim", "hidden_dim", "num_layers",
                                                                     "bidirectional")},
                    "num_classes": int(len(chars)), "checkpoint_object": keys_kind, "tensors": len(sd),
                    "load_state_dict_strict": f"PASS ({len(res.missing_keys)} missing, "
                                              f"{len(res.unexpected_keys)} unexpected)", "parameters": n_params}
    rec["vocabulary"] = {"chars_ctc": chars, "blank_index": 0, "blank_symbol": chars[0],
                         "letters": "a-z plus space, & ' . @", "size_including_blank": len(chars)}
    rec["preprocessing"] = {
        "upstream_input": "a directory of pre-cropped hand JPEG frames per clip (ChicagoFSWild+ crops from the "
                          "Shi et al. 2019 hand localizer, per the paper); the repo contains NO crop-generation code",
        "eval_transform": "BGR->RGB, albumentations Normalize(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225)) "
                          "THEN Resize(224,224), ToTensorV2 (exactly transfomrs_val in src/data/RGB/datasets.py)",
        "batching": "frames of all clips concatenated along dim 0 (sum T, 3, 224, 224) with input_lengths; TSAM shifts "
                    "per clip using those lengths",
        "frame_rate": "no resampling in eval (temporal_resample_prob 0)",
        "stage_a_consequence": "Stage A must supply its own hand crops (frozen MediaPipe pipeline); this is a "
                               "crop-source shift vs training and must be reported as such"}

    frames = synthetic_clip()
    tf = A.Compose([A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), A.Resize(224, 224),
                    ToTensorV2()])
    x = torch.stack([tf(image=f)["image"] for f in frames]).float()
    lengths = torch.tensor([len(frames)]).long()
    outs, times = [], []
    with torch.inference_mode():
        for _ in range(2):
            t0 = time.perf_counter(); y = model(x, lengths); times.append(time.perf_counter() - t0); outs.append(y)
    probs = torch.softmax(outs[0], dim=-1)
    p = probs[0].numpy() if probs.dim() == 3 else probs.numpy()
    greedy = "".join(model.decoder.greedy_decode(p))
    beam = "".join(model.decoder.beam_decode(p, 5, 0.4, 1.2))
    rec["synthetic_forward"] = {
        "input": "24 synthetic 224x224 RGB frames (white canvas, moving dark rectangle, red disc); no benchmark, "
                 "reviewer or real-world content", "input_shape": list(x.shape), "input_lengths": lengths.tolist(),
        "output_shape": list(outs[0].shape), "device": "cpu",
        "forward_s": [round(t, 3) for t in times], "deterministic_two_runs": bool(torch.equal(outs[0], outs[1])),
        "finite": bool(torch.isfinite(outs[0]).all()),
        "decoding": {"greedy_decode": {"ran": True, "length": len(greedy)},
                     "beam_decode_beam5_no_lm": {"ran": True, "length": len(beam)},
                     "decoded_strings": "not recorded as results: synthetic input, semantically meaningless"}}
    rec["decoding_notes"] = {
        "tester_default": "RGBTester computes both greedy and beam (beam 5, lm_beta 0.4, ins_gamma 1.2); with "
                          "scorer=None, lm_beta and ins_gamma have no effect, so beam is plain CTC prefix merging",
        "greedy_quirk": "upstream greedy_decode skips a letter equal to the previous emitted letter whenever 2+ letters "
                        "are already emitted, even across a blank, so legitimate double letters (e.g. 'll') can be "
                        "suppressed; beam_decode has no such rule",
        "frozen_for_stage_a": {"primary": "CTC beam search, beam 5, no language model (beam_decode, scorer None)",
                               "secondary": "greedy_decode, diagnostic only",
                               "not_claimed": "beam is not claimed to be more accurate on our data",
                               "statement": "This decoder choice was frozen before any Stage A evaluation output was "
                                            "produced and therefore was not selected based on benchmark accuracy."}}
    rec["portability_patches"] = patches
    rec["verdict"] = {"weights_load": True, "cpu_forward": True, "decoding": True,
                      "technically_viable_for_stage_a": True,
                      "caveats": ["no crop-generation code upstream: our MediaPipe crops differ from the training "
                                  "crops", "only 2 public commits; training/eval csv layout undocumented",
                                  "CPU under Rosetta x86_64 (torch 2.0.1)", "ChicagoFSWild+ domain vs How2Sign"]}
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("model", "synthetic_forward", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
