"""Regression tests: a sequence's outputs must not depend on how much padding its batch adds.

Covers the three padding leaks fixed in src/models/manual_encoder.py (projected padding
frames entering the strided conv, the max-pool mask marking an extra position valid for even
lengths, and GLU bias re-filling padded positions before the depthwise conv).
"""

import math

import pytest
import torch

from src.models.manual_encoder import ConformerEncoder
from src.models.translation_model import ASLTranslationModel

ATOL = 1e-5
INPUT_DIM = 501


def _batch(seqs: list[torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
    """Zero-pad like CollateLandmarks: (B, T_max, D) features and a 0/1 float mask."""
    t_max = max(len(s) for s in seqs)
    x = torch.zeros(len(seqs), t_max, seqs[0].shape[1])
    mask = torch.zeros(len(seqs), t_max)
    for i, s in enumerate(seqs):
        x[i, : len(s)] = s
        mask[i, : len(s)] = 1.0
    return x, mask


def _contexts(target: torch.Tensor, gen: torch.Generator) -> dict[str, tuple[list, int]]:
    """Batches containing `target` with different amounts of padding and positions."""
    n = len(target)

    def rand(length):
        return torch.randn(length, INPUT_DIM, generator=gen)

    long_a, long_b = rand(n + 45), rand(n + 30)
    return {
        "alone": ([target], 0),
        "one_frame_pad": ([target, rand(n + 1)], 0),
        "long_pad_first": ([target, long_a, long_b], 0),
        "long_pad_middle": ([long_a, target, long_b], 1),
        "long_pad_last": ([long_a, long_b, target], 2),
    }


@pytest.fixture(scope="module")
def encoder():
    torch.manual_seed(0)
    enc = ConformerEncoder(input_dim=INPUT_DIM, d_model=64, num_layers=2, num_heads=4, kernel_size=15)
    return enc.eval()


@pytest.mark.parametrize("length", range(1, 42))
def test_mask_length_matches_conv_output(encoder, length):
    x, mask = _batch([torch.randn(length, INPUT_DIM), torch.randn(length + 7, INPUT_DIM)])
    with torch.no_grad():
        out, kpm = encoder(x, mask)
    assert kpm.shape == out.shape[:2]
    # an unpadded sequence of L frames gives ceil(L/2) conv positions; padding must not add any
    assert int((~kpm[0]).sum()) == math.ceil(length / 2)
    assert int((~kpm[1]).sum()) == math.ceil((length + 7) / 2)
    assert bool(kpm[0, math.ceil(length / 2):].all())


@pytest.mark.parametrize("length", [37, 40])  # odd and even
def test_encoder_output_independent_of_padding(encoder, length):
    gen = torch.Generator().manual_seed(length)
    target = torch.randn(length, INPUT_DIM, generator=gen)
    n_valid = math.ceil(length / 2)
    ref = None
    with torch.no_grad():
        for name, (seqs, row) in _contexts(target, gen).items():
            out, kpm = encoder(*_batch(seqs))
            assert int((~kpm[row]).sum()) == n_valid, name
            assert torch.equal(kpm[row, :n_valid], torch.zeros(n_valid, dtype=torch.bool)), name
            valid = out[row, :n_valid]
            if ref is None:
                ref = valid
            else:
                torch.testing.assert_close(valid, ref, atol=ATOL, rtol=0, msg=name)


@pytest.fixture(scope="module")
def small_model():
    torch.manual_seed(0)
    m = ASLTranslationModel(input_dim=INPUT_DIM, d_model=64, t5_model_name="t5-small",
                            num_layers=2, num_heads=4, kernel_size=15)
    return m.eval()


@pytest.mark.slow
@pytest.mark.parametrize("length", [37, 40])
def test_model_forward_and_generate_independent_of_padding(small_model, length):
    """Covers both paths that reach T5: forward (training/eval loss) and generate."""
    gen = torch.Generator().manual_seed(1000 + length)
    target = torch.randn(length, INPUT_DIM, generator=gen)
    n_valid = math.ceil(length / 2)
    labels = torch.randint(2, 500, (1, 12), generator=gen)
    captured = {}
    hook = small_model.modality_bridge.register_forward_hook(
        lambda _m, _i, o: captured.__setitem__("bridge", o.detach()))
    ref = None
    try:
        with torch.no_grad():
            for name, (seqs, row) in _contexts(target, gen).items():
                x, mask = _batch(seqs)
                lab = labels.expand(len(seqs), -1).clone()
                logits = small_model(x, mask, labels=lab).logits[row]
                bridge = captured["bridge"][row, :n_valid]
                tokens = small_model.generate(x, mask, max_length=12, num_beams=1, do_sample=False)[row]
                tokens = tokens[tokens != 0].tolist()
                if ref is None:
                    ref = (logits, bridge, tokens)
                    continue
                torch.testing.assert_close(bridge, ref[1], atol=ATOL, rtol=0, msg=f"bridge {name}")
                # logits reach |~50|; different matmul shapes change float32 summation order, so
                # bound the difference relative to the logit scale (~3e-6 observed)
                tol = 1e-5 * float(ref[0].abs().max())
                torch.testing.assert_close(logits, ref[0], atol=tol, rtol=0, msg=f"logits {name}")
                assert torch.equal(logits.argmax(-1), ref[0].argmax(-1)), name
                assert tokens == ref[2], name
    finally:
        hook.remove()
