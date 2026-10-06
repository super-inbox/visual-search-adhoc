# Boss Summary — 2026-10-05

Analysis only: no new training, inference, or generation. Full reports:

- `asl-research-followup/ASL_DATA_REPRESENTATION_UNISIGN_ANALYSIS.md`
- `asl-research-followup/e0-unisign-reproduction/` (E0: Uni-Sign reproduction check, `E0_RESULTS.md`)
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

**E0 update (reproduction check, no training, no new inference):**

- **Scoring reproduction: succeeded.** Re-scoring the authors' released How2Sign predictions with the official scorer gives BLEU-4 **14.50**, exactly the paper's number.
- **Full official inference reproduction: not done.** The official Uni-Sign evaluation path requires CUDA + deepspeed, and this machine has no CUDA GPU. So we have not yet confirmed that the released checkpoint, run through the official pipeline, produces 14.5.

**The gap, decomposed** (same references, same official scorer):

| Predictions | Clips | BLEU-4 |
|---|---|---|
| Authors' released predictions | full How2Sign test (2,349) | **14.50** |
| Authors' released predictions | our 128 hard clips | **9.59** |
| Our current pipeline | same 128 clips | **5.39** |

- About **4.9 BLEU** of the 14.5 → 5.4 gap is explained by **benchmark difficulty**: our 128 clips intentionally over-sample long clips, questions, numbers, names, and fast signing.
- About **4.2 BLEU** remains attributable to **our current inference / preprocessing pipeline**, on identical clips.

**The cause of the remaining 4.2 BLEU is not known yet.**

- **Leading suspect (unverified): pose extraction.** Our pipeline uses rtmlib RTMW-dw-l-m (lightweight); the paper uses RTMPose-x, and the checkpoint was fine-tuned on RTMPose-x poses.
- **Smaller unverified candidates:** bf16 on CPU vs. CUDA kernels, and batch size 1 (ours) vs. 8 (official).
- Ruled out as main causes: scorer/reference differences, and frame subsampling (the gap is the same on clips that are never subsampled).

**Main limitations:**

- 37.5% of outputs contain repetition loops.
- 65% of clips over 15 s are truncated (output capped at 100 new tokens, `max_new_tokens=100`).
- Output is fluent but often on the wrong topic.
- No timestamps.
- Weights are non-commercial (CC BY-NC).
- The ASL-pretrained (YouTube-ASL) stage weights are not released, which limits adaptation.
- Heavy: ~32 s/clip on CPU.
- Even the paper's 14.5 BLEU is far from product quality.

**Build on it? (revised after E0)** Still promising, but **conditional**. Pausing from-scratch Conformer+T5 training in favor of Uni-Sign (or a Uni-Sign-style pretrained encoder) remains the leading direction, but it should not be committed to until:

- **Official GPU inference is reproduced:** the released checkpoint, run through the official path, gives ≈14.5 on the full test set (and ≈9.6 on our 128 clips).
- **Model/license constraints are resolved:** weights are non-commercial (CC BY-NC), and the ASL-pretraining-stage weights are not released.

**Next experiment (E0-b, needs a CUDA GPU, ~1 GPU-hour + ~8.5 GB download):**

1. Run the official eval on the full How2Sign test set with the official pose files. Expect ≈14.5.
2. Score our 128 clips from that output. Expect ≈9.6.
3. **Pose-extractor isolation:** run our 128 clips through the same official loader with (a) official RTMPose-x poses and (b) our rtmlib RTMW-dw-l-m poses. If (a) ≈ 9.6 and (b) ≈ 5.4, pose extraction explains the remaining gap.

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
