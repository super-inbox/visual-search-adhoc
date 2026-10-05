# Boss Summary — 2026-10-05

Analysis only: no new training, inference, or generation. Full reports:

- `asl-research-followup/ASL_DATA_REPRESENTATION_UNISIGN_ANALYSIS.md`
- `visual-production-research/` (landscape report, CSVs, pipelines, sources)

# ASL

## a. Current training scale

| Run | Train | Val | Test |
|---|---|---|---|
| P0.1 (overfit test) | 32 clips | — | evaluated on the same 32 |
| P0.2 ("10%" multi-epoch) | 2,751 clips / 1,208 videos | 366 | 147 (128 How2Sign v2 + 19 pilot) |

- That is about 9% of How2Sign's ~31k training sentences. The "10%" label was never formally verified.
- By hours, it is roughly 1% of what the Uni-Sign checkpoint was trained on (~984 h YouTube-ASL pretraining, then How2Sign fine-tuning).

## b. Data vs. representation

**What our experiments show**

- Optimization works: the model memorizes 32/32 training clips (BLEU 100).
- Generalization fails: validation/test BLEU is about 1.0, and fixing the padding bug didn't change that.
- The encoder output is almost identical across different videos (cosine 0.998). Using the correct video instead of a shuffled one gives only a small loss advantage.
- So the learned representation carries very little video-specific signal.

**What external research suggests (YouTube-ASL, NeurIPS 2023)**

- **Supervised scaling:** a comparable landmark+T5 model trained on **100%** of How2Sign reached only 0.86–1.22 BLEU, about where we are at ~9%.
- **Sign-language pretraining:** first pretraining on ~984 h of YouTube-ASL raised BLEU to 6.3 (T5 from scratch) or 12.4 (pretrained T5).
- Uni-Sign's own ablation (on Chinese sign language) shows BLEU rising steadily with pretraining data.
- **This does not prove data is irrelevant.** Pretraining *is* more, broader data. It suggests that scaling our current downstream supervised setup is unlikely to deliver the gains that sign-specific pretraining delivers.

**Still unproven**

- Whether a pretrained encoder would rescue *our* model on the same 2,751 clips (experiment E1).
- Whether going from 10% to 30% How2Sign is flat for us (E2).
- Whether any of this holds on real Curify videos (E3).
- No ASL-fluent review has been done.

**Conclusion:** Current evidence points more strongly to representation / sign-specific pretraining than to simply adding more supervised How2Sign labels.

## c. Uni-Sign

| | Value |
|---|---|
| Published result | How2Sign test BLEU-4 **14.5** (pose-only; 14.9 with RGB) |
| Our result | **5.4** BLEU on our frozen 128-clip benchmark, under our current Uni-Sign evaluation setup |

**Why the numbers are not yet directly comparable:**

1. Our benchmark intentionally over-samples hard clips: long, questions, numbers, names, fast signing.
2. Our pose extraction (lightweight rtmlib model) differs from the paper's (RTMPose-x).
3. We have not reproduced the official evaluation/deployment path: official pose files plus the official eval script, and the exact reference labels.

**We do not attribute the gap to any single cause yet.**

**Main limitations:**

- 37.5% of outputs contain repetition loops.
- 65% of clips over 15 s are truncated (output capped at 100 new tokens, `max_new_tokens=100`).
- Output is fluent but often on the wrong topic.
- No timestamps.
- Weights are non-commercial (CC BY-NC).
- The ASL-pretrained (YouTube-ASL) stage weights are not released, which limits adaptation.
- Heavy: ~32 s/clip on CPU.
- Even the paper's 14.5 BLEU is far from product quality.

**Build on it?** Conditionally yes: pause from-scratch Conformer+T5 training and use Uni-Sign (or a Uni-Sign-style pretrained encoder) as the base. Two conditions:

- E0 must reproduce roughly the paper's number.
- The commercial license question must be resolved.

**Immediate next experiment (E0, no training, highest priority):**

- **Setup:** download the official How2Sign pose files (~8.5 GB) and run the official eval script on:
  1. the full test set
  2. our 128 clips with official poses
  3. our 128 clips with our own poses (already measured: 5.4)
  4. our 128 clips with a higher-accuracy rtmlib model
- **How to read it:**
  - If (1) ≈ 14.5 and (2) ≈ 5: the gap is benchmark difficulty.
  - If (2) ≫ (3): the gap is our pose extraction.
  - If (1) ≪ 14.5: the release does not reproduce the paper.
- **Cost (estimate):** about 1 GPU-hour, or about 1 CPU-day for the full test set (the 128 clips take ~70 min on CPU). Requires rebuilding the Uni-Sign environment.

# Visual Production

## Current problem

Customer delivery for ecommerce model dressing and professional retouching often fails on demanding tasks, and repeated GPT/Astra revisions do not converge on client approval.

**Why they fail is a hypothesis until real customer cases are reviewed.** No case data or pipeline description is in the repo, and "Astra" is not documented anywhere I could access.

## What SOTA suggests

All of the following were verified at paper level:

- **No verified try-on model reliably preserves small text/logos.**
  - Leffa (best open specialist): "struggles to preserve… small text" due to latent compression.
  - CatVTON: reports VAE detail and color loss.
- **General editors are not clearly worse than specialists.**
  - On the independent OpenVTON-Bench human ratings, Nano Banana (4.60) and Qwen-Editor (4.55) sit near the top commercial try-on product (4.61).
  - All models still "hallucinate fine garment details".
  - Switching models alone is not a reliable fix.
- **Multi-turn editing drifts even in the best editors.**
  - FLUX Kontext's own paper: "excessive multi-turn editing can introduce visual artifacts."
  - OpenAI's docs: GPT Image masks are "guidance" and "may not follow its exact shape."
- **Garment fidelity can be checked per attribute.**
  - DAT checks 7 attributes: silhouette, color, neckline/sleeve, decoration, texture, fine detail, logo.
  - A prompted Gemini judge is almost as accurate as their trained checker (75.9% vs. 76.6%).
  - OpenVTON-Bench's region-based metric matches human rankings far better than SSIM (Kendall τ 0.83 vs. 0.61).
- **Licenses matter.** CatVTON, InfiniteYou, and FLUX-dev weights are non-commercial. Leffa is MIT; its training-data terms are unchecked.

## What practitioner workflows suggest

The recurring pattern (ComfyUI Crop-and-Stitch, Redux+Fill try-on, the PS-AI apparel SOP, retouching plugins):

1. Mark protected zones first.
2. Let the AI generate **only inside a region**.
3. Paste the untouched pixels back deterministically (they never pass through the model).
4. Restore detail and color deterministically (e.g. frequency "detail transfer").
5. Finish in Photoshop.
6. Run a named checklist before delivery.

- **Retouching:** professionals keep work as reversible dodge & burn / frequency-separation layers, so "a bit less" is a slider change, not a regeneration.

**Blocked sources:** Xiaohongshu (login wall) and Zhihu (403). Nothing was used from them. ZCOOL was accessible but its posts show results, not process.

## Recommended Curify direction

Replace "regenerate the whole image and hope" with a **multi-stage controlled pipeline**:

1. **Acceptance contract:** a per-order checklist built from the 7 garment attributes plus identity/background, agreed with the client, with reference assets (garment flat-lay, color swatch, logo file).
2. **Locked-region revision:** each revision edits only a masked region; everything else is copied bit-exact from the last approved version.
3. **Deterministic repair:** color-match to the swatch, logo/text patch paste-back, face paste-back from the source photo.
4. **Automated pre-checks + human region review:** color difference vs. the swatch (ΔE), logo OCR, face similarity, and a pixel diff outside the edited region.
5. **Retouching as layers/parameters,** not flattened regenerations.
6. **Generator choice by A/B on our cases.** Candidates: current GPT/Astra vs. Kontext/Qwen try-on LoRA vs. FASHN vs. Leffa.

## Next validation

Use 10–15 real rejected customer cases (about half try-on, half retouching):

1. Tag each rejection by failure type. This answers "what actually fails" with no generation.
2. Replay the hardest revision requests with the same generator in two arms:
   - **A:** whole-image edit (today)
   - **B:** localized locked-region revision + delivery-oriented QA
3. **Measure:**
   - changes outside the requested region
   - per-attribute checklist pass rate
   - rounds to internal approval (blind review)
   - time per round
4. **Decide:**
   - If B wins, productize the locked loop.
   - If the remaining failures are mostly garment fidelity, run the generator A/B next.

**Needed from you:** the customer cases (internal use), plus a description of the current GPT/Astra pipeline.
