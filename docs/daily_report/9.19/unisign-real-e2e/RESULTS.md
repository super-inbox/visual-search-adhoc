# Uni-Sign FastAPI service — real-checkpoint local E2E (task "a")

Date: 2026-09-19 · Scope: **local R&D validation only** (no ACR, no Azure, no checkpoint committed). This report folder was committed on its own; the service code and checkpoint were not.
Service under test: `curify-studio/uni_sign_server` @ branch `baobao/asl-unisign-fastapi-service` (HEAD `5425912`, **no code changes made**).

## 1. Checkpoint provenance

| | |
|---|---|
| Source | `https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_only_slt.pth` (official repo, direct, no mirrors) |
| Method | `curl -L --retry 5 -C -` |
| License | CC BY-NC-4.0 (non-commercial) — used for local R&D only |
| Local path | `curify-studio/uni_sign_server/checkpoints/how2sign_pose_only_slt.pth` |
| Git status | ignored (`git check-ignore` → `uni_sign_server/.gitignore:6 checkpoints/`); never appears in `git status` |
| Not done | not committed, not baked into the image, not pushed to ACR. Mounted read-only into the container at run time |

## 2. SHA256 / size

- Size: **1,186,925,007 bytes** (expected 1,186,925,007) ✅
- SHA256: `1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d` (expected: identical) ✅

## 3. Docker image / runtime

- Image: `uni-sign-local:test` (`e0ad26933d3b`), **`linux/amd64`**, built 2026-09-16 22:38 CDT — *after* the last Dockerfile/requirements edit (22:33), so **not rebuilt**. Not tagged for, or pushed to, any registry.
- Container: `docker run --platform linux/amd64`, `UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1`, checkpoint mounted `:ro` at `/app/checkpoints/how2sign_pose_only_slt.pth`.
- mT5: host `~/.cache/huggingface` mounted read-only at `/tmp/hf` with `HF_HUB_OFFLINE=1` → reused existing cache, **no mT5 re-download**.
- Host is Apple Silicon (Docker engine is arm64), so the amd64 container runs **under emulation**. Runtimes below are not representative of a native x86 server or a GPU.
- Docker VM limit: 12 CPUs, 7.65 GiB RAM.

## 4. `/healthz`

`HTTP 200 {"status":"ok"}`

## 5. `/readyz` — the key new test

**`HTTP 200 {"status":"ok","model_loaded":true}`**, first call (lazy model load) took **19.1 s**.
The real checkpoint loaded with `load_state_dict(strict=True)` and no missing or unexpected keys, and no SHA-mismatch warning was logged. Resident memory after load: ~4.1 GiB.

## 6. Short clip

| | |
|---|---|
| Clip ID | `g0uGWjwdOIw_1-8-rgb_front` (public How2Sign v2 frozen benchmark, official test split) |
| Path | `visual-search-adhoc-asl-task-c/asl-translator/data/public_benchmarks/how2sign_v2/videos/g0uGWjwdOIw_1-8-rgb_front.mp4` |
| Duration | 5.91 s per manifest (5.875 s ffprobe), 141 frames, 1280×720 @ 24 fps |
| Selection | deterministic: 4–8 s, ffprobe-readable, clean leakage check, no number / fingerspelling / fast-signing flags, no encoding fix, no question mark, not in pilot_v1; closest to 6 s → 40 candidates, this was #1 |
| **Reference** | It got a lot to do with math and geometry, geometric designs. |
| **Uni-Sign output** | So, the main thing is that mathematics are involved in the design. |
| HTTP status | 200 |
| Runtime | **56.9 s cold** (includes a one-time ~132 MB rtmlib ONNX download, ~13 s) · **39.6 s warm** (identical output on re-run → deterministic below the 256-frame cap). Pose extraction of 141 frames ≈ 6 s; the rest is model forward + beam search |
| Segments | one segment, `start 0.0`, `end 5.875`, **`"source": "wrapper_derived"`** ✅ (whole-clip span from ffprobe, *not* Uni-Sign timing; the response's own `note` says so) |

Metrics (n=1): **WER 1.000 · CER 0.746 · BLEU 0.00 · chrF 21.80**
Reference words 12, prediction words 12.

Human read: semantically close (math/geometry ↔ "mathematics … involved in the design") but lexically different, so WER is harsh here. Raw files: `short_response.json`, `short_response_warm.json`, `short_curl_meta.txt`, `short_warm_curl_meta.txt`.

## 7. Long clip

| | |
|---|---|
| Clip ID | `FzmL8SL6Bow_1-8-rgb_front` (previously-known candidate; still present, valid, in the frozen benchmark) |
| Duration | 25.77 s per manifest (25.75 s ffprobe), **618 frames**, 1280×720 @ 24 fps |
| **Reference** | You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there. |
| **Uni-Sign output** | We're going to go ahead and put this on the bottom and we're going to go ahead and put this on the bottom and we're going to go ahead and take our rubber band and |
| HTTP status | 200 (one `translation` string; one `segments[0]`, `wrapper_derived`, `start 0.0`, `end 25.75`) |
| Runtime | **101.0 s** (repeat run: 99.8 s) |

Metrics (n=1): **WER 0.872 · CER 0.702 · BLEU 2.48 · chrF 20.51** (reference 78 words, prediction 38 words).

### Runtime / preprocessing observations (from container logs + upstream source)

| Question | Observation |
|---|---|
| Pose frames extracted | **618** (= all video frames, no stride) |
| `max_length=256` subsampling | **Yes — it fired.** `S2T_Dataset_online.load_pose()` does `sorted(random.sample(range(618), k=256))` (`unisign_repo/datasets.py:640-641`), so **256 of 618 frames (41.4 %) reach the model; 362 (58.6 %) are randomly dropped**. Random, not uniform stride → uneven temporal gaps. |
| Pose extraction time | ≈ 26 s (618 frames at 23.7 it/s) |
| Generation time | ≈ 75 s, by subtraction (101 − 26; includes upload, ffprobe, dataset build) |
| `max_new_tokens=100` reached? | **No.** Output is 50 mT5 tokens (35 whitespace words). The model emitted end-of-sequence on its own, on a dangling "and". |
| Errors / warnings | None besides upstream noise (onnxruntime initializer notices, NNPACK "Unsupported hardware", tokenizer "truncate to max_length" notice from the label tokenizer). No traceback. Container: `OOMKilled=false`, 0 restarts. |
| Memory | Peak **6.60 GiB of 7.65 GiB** during beam search (3.9 → 5.1 → 5.8 → 6.6 GiB as generation progressed). Only ~1 GiB headroom, so it worked but is tight for anything longer. |
| Reproducibility | **Not reproducible across identical requests.** The identical long clip re-sent to the same live process gave a *different* translation: "So I'm going to take this hole because it's going to be nice and clean and then I'm going to take this hole and I'm going to have the rubber band here and I'" (WER 0.859, BLEU 1.86, chrF 21.99). Cause: `random.sample` uses Python's global RNG, seeded once at model load (`set_seed(42)`) and never re-seeded per request, so every request that exceeds 256 frames draws a different subset. The short clip (< 256 frames, no sampling) was bit-identical across runs. |

### Answers to the five long-clip questions

1. **Did the API technically succeed?** Yes. HTTP 200, no errors, no OOM, ~101 s.
2. **One translation string?** Yes: a single `translation` string, and a single `wrapper_derived` segment spanning 0–25.75 s.
3. **Was the full video represented?** No. All 618 frames were pose-extracted, but only a random 256 (41 %) were passed to the model.
4. **Obviously truncated?** Not truncated by the token cap (50 of 100 tokens; the model stopped itself). But it is clearly *incomplete and off-target*: 38 words against a 78-word reference (≈ 49 %), it ends on a dangling "and", it repeats a clause ("…put this on the bottom and we're going to go ahead…"), and it shares almost no content with the reference. Alternative wording: the failure is early EOS + degenerate repetition, not hard truncation.
5. **Does this support testing long-video segmentation next?** Yes, as motivation, with the caveats in section 9. Direct long input produced (a) a 59 % frame drop, (b) output that varies between identical requests, and (c) roughly half the reference length with near-zero content overlap.

## Comparison (human-readable)

```
SHORT  g0uGWjwdOIw_1-8-rgb_front  (5.91 s)
REFERENCE: It got a lot to do with math and geometry, geometric designs.
UNISIGN:   So, the main thing is that mathematics are involved in the design.
           WER 1.000  CER 0.746  BLEU 0.00  chrF 21.80

LONG   FzmL8SL6Bow_1-8-rgb_front  (25.77 s)
REFERENCE: You want to go and clean up that hole you just made and now we are going to go
           and start winding our hole you just made and start spreading it out just like
           that and all the while I am pulling it out while my hands here are watching this
           wall here because this wall here is going to want to get out of control but I'm
           not going to let it, my hands are there.
UNISIGN:   We're going to go ahead and put this on the bottom and we're going to go ahead
           and put this on the bottom and we're going to go ahead and take our rubber band and
           WER 0.872  CER 0.702  BLEU 2.48  chrF 20.51
UNISIGN (identical request, 2nd run):
           So I'm going to take this hole because it's going to be nice and clean and then
           I'm going to take this hole and I'm going to have the rubber band here and I'
           WER 0.859  CER 0.702  BLEU 1.86  chrF 21.99
```

Scoring method (`score_e2e.py`, same folder): **WER/CER = the repo's existing `asl-translator/asl-eval/lib.py::text_metrics`, unmodified** (lowercase, punctuation → space). The repo has **no BLEU/chrF implementation**, so those use the installed `sacrebleu` 2.6.0 library (`sentence_bleu` with `effective_order`, `sentence_chrf`) on the same normalized strings, with no custom scorer written. Sentence-level BLEU on one segment is very noisy; treat it as a rough signal. **n=2 (plus one repeat): no ranking, no conclusion about model quality should be drawn from these numbers.** In particular the short clip's WER (1.0) is *worse* than the long clip's (0.87), even though the short output is the more sensible one, which shows WER alone is a poor signal at this n.

Difference from the earlier 128-clip benchmark run (native macOS/arm64, `docs/daily_report/9.2/asl-baselines/results/unisign_predictions.jsonl`): the short clip then gave "The point of this is that mathematics properly involved in the design." (WER 1.0, CER 0.712), and now gives a different sentence. The container run is deterministic on its own but not bit-identical to the native run. This was not investigated (possible causes: bf16 CPU kernels under emulation, onnxruntime / rtmlib version differences in pose extraction). The earlier long-clip output began "So I'm going to take this hole because it's going to be nice and clean…", close to today's repeat run. Both are consistent with the random-subsampling variability above.

## 8. Is true E2E COMPLETE?

**COMPLETE** for pipeline validation: the real, hash-verified official checkpoint loads strictly, `/readyz` returns 200, and `/translate` returns real translations with HTTP 200 for both a short and a long public benchmark clip, inside the amd64 container, with `segments` correctly labeled `wrapper_derived`. This does **not** mean the translation *quality* is acceptable (see below), and it says nothing about production readiness: the CC BY-NC-4.0 license block on ACR/Azure is unchanged.

## 9. Does long-video segmentation look worth testing?

**Yes, with caveats.** Evidence for it: 59 % of frames dropped at random for a 25.75 s clip, non-deterministic outputs for the same input, and about half-length, off-target output. Both are consistent with the README's existing statement that v1 is for pre-segmented clips (~1–30 s, one sentence) and with the earlier benchmark's observed truncation on 15–31 s clips.
Caveats: n=1 long clip (+1 repeat); the short clip also scored WER 1.0, so poor lexical match is not unique to long input; I did not test a mid-length clip below 256 frames (~10.7 s at 24 fps), so I cannot separate "frame subsampling" from "model just handles long multi-clause signing poorly". No segmentation was implemented or tested here.

## 10. Exact next step

**c — NOT b.** Do not implement long-video segmentation (b) in this task or as a follow-on to it; proceed to (c) per the manager's a → c → b order.

## Incidental findings (for the record; nothing changed)

1. **`curl -F video=@x.mp4` returns 415.** curl labeled the part `application/octet-stream` and the service's allowlist rejected it (`short_response_415_octet_stream_attempt.json`). Passing `;type=video/mp4` works. The service behaved as coded; the allowlist is stricter than the task's example curl assumes.
2. **rtmlib ONNX weights (~132 MB: `yolox_tiny` + `rtmw-dw-l-m`) are downloaded from `download.openmmlab.com` at the first `/translate`,** into `/root/.cache/rtmlib` inside the container. This adds ~13 s cold-start latency and a run-time outbound-network dependency, and was not visible in the README's checkpoint/mT5 discussion. It is lost on every container recreate.
3. **Memory:** 6.6 GiB peak on a 25.75 s clip against the 7.65 GiB Docker limit. Size any deployment accordingly.
4. **`uni_sign_server/README.md` still says "not yet inference-tested end-to-end"** — now stale. Not edited (out of scope for this task).
5. `HF_HUB_OFFLINE=1` + read-only mounted HF cache worked; the service needs no network for mT5 when the cache is mounted.

## Files

All in `visual-search-adhoc-asl-task-c/docs/daily_report/9.19/unisign-real-e2e/` (committed as a standalone report folder; the checkpoint is not part of it): `RESULTS.md`, `MANAGER_SUMMARY.md`, `score_e2e.py`, `scores.json`, `short_response.json`, `short_response_warm.json`, `short_response_415_octet_stream_attempt.json`, `long_response.json`, `long_response_repeat.json`, `*_curl_meta.txt`, `long_ffprobe.txt`, `long_container_log_filtered.txt`, `long_docker_stats.log`.
