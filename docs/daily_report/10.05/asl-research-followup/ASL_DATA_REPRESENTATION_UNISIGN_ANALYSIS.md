# ASL follow-up: data vs. representation, and the Uni-Sign gap

Date: 2026-10-05 · Scope: analysis only. **No new training or inference was run for this report.**

Every claim is tagged:

- **[CURIFY]** = prior Curify evidence already in this repo (path given)
- **[EXT]** = new external research done for this report (source given)
- **[INF]** = new inference / recommendation (my reasoning, not measured)

## TL;DR（一句话结论）

- **a.** 当前小规模训练：P0.1 用 **32 条**训练片段；P0.2 用 **2,751 条训练片段**（1,208 个视频），外加 366 条 val、147 条 frozen test。约占 How2Sign 官方训练集（约 31k 句）的 9%。
- **b.** 现有证据**更强地指向"表示 / 手语专用的大规模预训练"**，而不是"单纯增加 How2Sign 监督标注"。这里区分三件事：
  - **监督数据扩展**：同一套下游监督训练加更多 How2Sign 标注。外部文献里，同类 landmark+T5 用**全量** How2Sign 训练也只有 0.86–1.22 BLEU，和我们约 9% 数据的约 1.0 相当。
  - **大规模手语预训练**：先在约 984 小时 YouTube-ASL 视频-字幕对上训练，再在 How2Sign 上微调。BLEU 升到 6.3（T5 从零）或 12.4（T5 预训练）。
  - **学到的表示**：我们 encoder 的输出在不同视频之间几乎相同（cosine 0.998）。
  
  这**不说明数据无关**：预训练本身就是更大规模、更广覆盖的数据。它说明的是，**把同一套下游监督设置单纯扩大，不太可能获得预训练那样的收益**。我们自己还没有在同一数据上直接对比"换表示"（见 E1）。
- **c.** **复现缺口是首要发现**：论文 How2Sign BLEU-4 为 14.5，我们测到 5.4。**这两个数字目前不能直接比较**，原因有三：
  1. 我们的 128 条 benchmark 刻意多采难样本；
  2. 我们的 pose 提取（rtmlib lightweight）与论文（RTMPose-x）不同；
  3. 官方评测/部署流程的复现还没有验证。
  
  没有证据把缺口归因于其中任何一项。**E0（官方 pose 文件 + 官方评测脚本，不需要训练）是 ASL 优先级最高的实验。** 有条件地建议在 Uni-Sign 上继续、暂停 Conformer+T5 从零训练：前提是 E0 复现论文量级，并且商用许可问题得到解决。

---

## 1. Question a — how many training samples are we using?

| Run | Train | Val | Test | Source |
|---|---|---|---|---|
| P0.1 tiny overfit | **32 clips** (≤30 tokens, sampled from 2,060 eligible) | — (evaluated on the same 32) | — | [CURIFY] branch `baobao/asl-p0-report-2026-09-25`, `p0_work_report_2026-09-25.md` §2.1, §4 |
| P0.2 "10%" multi-epoch | **2,751 clips / 1,208 videos** (677 with unknown signer) | 366 clips / 366 videos | 147 frozen (128 How2Sign v2 + 19 pilot_v1) | [CURIFY] same report §2.2 |

Caveats, all from [CURIFY]:

- The "10%" label comes only from the directory name `local_run_10pct`. The P0 report says it was never checked against the full corpus.
- Train/val features are third-party Kaggle "How2Sign Holistic" MediaPipe extractions. The frozen test features were extracted locally, so there may be a distribution shift between them.
- Every P0 run used t5-small on CPU with one seed.

Context:

- **[EXT]** How2Sign's official train split has about 31k sentence clips (How2Sign paper: 31,128 train / 1,741 val / 2,322 test — from prior knowledge, not re-read in this pass), about 79 h in total (Uni-Sign paper, Table 1).
- **[INF]** That makes 2,751 clips about 9% of How2Sign train, roughly consistent with the "10%" label.
- **[EXT]** Uni-Sign's ASL model saw far more data: it was pretrained on **YouTube-ASL (984 h, about 60K vocabulary)** and then fine-tuned on How2Sign (Uni-Sign §4.1; Table 1).
- **[INF]** By hours, our P0.2 set is therefore roughly 1% of what the Uni-Sign checkpoint we benchmark was trained on.

## 2. FIRST-CLASS FINDING: the Uni-Sign reproduction gap (14.5 published vs. 5.4 measured)

**The gap is real and large, but the two numbers are not yet directly comparable**, for three reasons:

1. **Different test population.** Our 128-clip benchmark intentionally over-samples difficult strata: long clips, questions, numbers, proper nouns, fast signing. It is one clip per video, not the full ~2.3k-sentence test set (V2 below).
2. **Different pose extraction.** We used `rtmlib` lightweight (`rtmw-dw-l-m`, 256×192). The paper and its released pose files use RTMPose-x via MMPose (V1 below).
3. **The exact evaluation/deployment path has not been verified.** We ran the demo inference script on CPU, not upstream `eval_stage3.sh` on the official pose files. We have also not confirmed which reference TSV the paper scored against (H2 below).

**We do not attribute the gap to any single cause.** No experiment has yet isolated any of these factors. **E0 (§6) is the highest-priority ASL experiment** because it separates all three at once without training.

### 2.1 Numbers

| | Paper (Uni-Sign, ICLR 2025, Table 21) [EXT] | Ours (frozen How2Sign v2) [CURIFY] |
|---|---|---|
| Model | pose-only, mT5-Base, YouTube-ASL pretrain → How2Sign fine-tune | same released checkpoint `how2sign_pose_only_slt.pth` (sha256 verified; 627 keys, 0 missing) |
| Test set | full How2Sign test (~2.3k sentences) | 128 clips, one per source video, **stratified toward hard strata** |
| BLEU-4 (SacreBLEU) | **14.5** (RGB-pose: 14.9) | **5.39** (full 128); 5.40 (matched-126) |
| BLEU-1 / ROUGE / BLEURT | 40.4 / 34.3 / 48.6 | not computed |
| chrF / WER | not reported | 22.75 / 0.982 |

Sources: [EXT] arXiv 2501.15187 v3, Table 6/21. [CURIFY] `docs/daily_report/9.2/asl-baselines/HOW2SIGN_V2_OPENSLT_UNISIGN_FULL_RESULTS.md` §1, §3.

**For calibration, other How2Sign results [EXT]:**

| Paper | Setting | How2Sign BLEU-4 |
|---|---|---|
| YouTube-ASL (Uthus et al., NeurIPS 2023), Table 3 | MediaPipe landmarks + T5.1.1-Base, **How2Sign only** | 0.86 (from scratch) / 1.22 (pretrained T5) |
| same | YouTube-ASL only, zero-shot on How2Sign | 1.41 (from scratch) / 3.95 (pretrained T5) |
| same | YouTube-ASL → How2Sign fine-tune | 6.26 (from scratch) / **12.39** (pretrained T5) |
| Prior How2Sign-only systems (GloFE-VN, Álvarez et al.) | — | 2.2 |
| SSVP-SLT (RGB, self-supervised pretraining) | — | 15.5 |

**[EXT]** The YouTube-ASL authors also note that How2Sign's test set shares most signers, and some narratives, with train. That inflates fine-tuned scores compared with real-world zero-shot use. Their zero-shot number (3.95) is the better proxy for unseen users.

**[INF]** Even a perfect reproduction (14.5 BLEU) is still poor translation by product standards. The paper's own How2Sign examples (Table 16) are loose paraphrases. Our 5.4 is a number that is *lower than expected*, but the expected ceiling is itself low.

## 3. Possible contributors to the gap, separated by evidence level (none isolated yet)

### 3a. Verified differences between our run and the paper's protocol

| # | Difference | Evidence | Expected direction |
|---|---|---|---|
| V1 | **Pose extractor mismatch.** We used `rtmlib` `Wholebody(mode="lightweight")` (YOLOX-tiny detector + `rtmw-dw-l-m` 256×192). The paper used **RTMPose-x via MMPose**, and the released How2Sign `pose_format` files were made with MMPose RTMPose. | [CURIFY] `8.31/asl-next-baseline/results/raw_output.txt` lines 8–9; `9.15/unisign-inference-parameter-audit/README.md` (pose-extractor row). [EXT] Uni-Sign Appendix A.1; repo `docs/DATASET.md` | The checkpoint was trained on x-size poses. Lighter-model keypoints, especially for hands and face, are a train/test feature shift. **Size unknown.** |
| V2 | **Different test population.** 128 clips, one per video, stratified by fixed priority: 15–31 s clips (20), questions (12), number tokens (32), proper-noun proxy (28), fast signing (13). Clips are scored against the original-alignment TSV. | [CURIFY] `asl-translator/data/public_benchmarks/how2sign_v2/SELECTION_METHODOLOGY.md` §3–5; full results §4 | Harder than a random sample, so lower BLEU. A 128-sentence corpus BLEU is also noisy. **Size unknown.** |
| V3 | **Decoding truncation.** `max_new_tokens=100` truncates 13/20 (65%) of 15–31 s clips mid-sentence, and 12/12 clips ≥15.8 s in the 19-clip pilot. | [CURIFY] full results §6; `8.31/.../UNISIGN_19CLIP_RESULTS.md` | Lowers BLEU through the brevity penalty and missing n-grams. This is the upstream default, so the paper probably had it too. Its effect may be larger on our long-clip-heavy subset. |
| V4 | **Repetition loops.** 48/128 (37.5%) of predictions repeat a 3–6-gram; the worst repeats "iced" 10 times on a 4-word reference. `no_repeat_ngram_size=0` and `repetition_penalty=1.0` are the library defaults, and the upstream wrapper does not expose them. | [CURIFY] full results §6; `9.15/unisign-inference-parameter-audit/README.md` | Lowers BLEU. Probably also present in the paper's setup. |
| V5 | **Frame cap.** Clips longer than 256 pose frames are randomly subsampled to 256 (`seed=42`). | [CURIFY] inference-parameter audit (`datasets.py:606-641`) | Same code path as upstream, so not a protocol deviation. It does affect long clips, which our subset over-represents. |
| V6 | **CPU patch.** We removed 4 `.cuda()` calls to run on CPU; nothing else changed. | [CURIFY] `UNISIGN_ONE_CLIP_RESULT.md` | Not expected to matter beyond numerical noise. Not verified bit-for-bit against GPU. |
| V7 | **Decoding parameters.** We used beam 4 and max 100 tokens, the upstream defaults; never tuned. | [CURIFY] 9.15 audit | Same as upstream. Not a cause, but also not optimized. |

### 3b. Hypotheses (plausible, not verified)

- **H1. Some unknown share of the gap comes from V1 (poses) and/or V2 (harder subset), as opposed to the model itself.** There is currently no evidence for how the gap splits between them. E0 tests this without training.
- **H2. The paper's reference TSV may differ from ours** (manually re-aligned vs. original translations). The Uni-Sign `DATASET.md` does not say which labels it uses. [CURIFY] Our selection methodology found 33/149 alignment mismatches in the original-alignment archive.
- **H3. Hidden signer/narrative overlap inflates the paper's How2Sign test score** [EXT, YouTube-ASL §5]. Our clips come from the same test split, so this should affect us equally. It cannot explain the gap, but it does mean real Curify users will score lower than either number.
- **H4. Short-reference artifacts.** Clips under 2 s have WER 1.36; questions have 1.25 [CURIFY]. BLEU is less sensitive to this than WER, but it still lowers our subset's score.

**What we can rule out:**

- **Wrong checkpoint / corrupted weights.** Verified: sha256 matches, strict load, 0 missing/unexpected keys [CURIFY].
- **Tracking failure on clean clips.** On the 5-clip probe, tracking had 0% missing frames [CURIFY 9.10 D1]. That check used rtmlib too, so it says nothing about V1's quality gap against RTMPose-x.

## 4. Where is the bottleneck? (question b in full)

Below, our path is the Conformer+T5 model trained from scratch; Uni-Sign is the released checkpoint.

| Candidate bottleneck | Our Conformer+T5 path | Uni-Sign path | Evidence |
|---|---|---|---|
| **Optimization / implementation bugs** | **Largely ruled out.** P0.1 memorizes 32/32 (BLEU 100); the padding bug was fixed and retraining did not change val/test BLEU (0.99 / 1.02). | Not applicable (we only run inference). | [CURIFY] P0 report §2.1, §2.4, §3 |
| **Learned representation** | **Primary suspect (internal evidence).** Encoder outputs across different videos have cosine similarity 0.998–0.999; about 99.9% of their energy is a shared, video-independent component. Correct vs. shuffled video changes val loss by only about 0.1. The model uses the video, but only weakly. | Its pretrained pose representation produces partially on-topic output on some clips (e.g. salt/foam cooking; "body sweat", WER 0.17). Gemini frame, video, and trajectory-prompt approaches never did this. | [CURIFY] P0 report §2.3; 9.2 full results §6; 9.6/9.10 summaries |
| **Supervised dataset scaling** (more How2Sign labels, same downstream setup) | **Weakly supported as the main fix.** [EXT] A comparable landmark+T5 setup trained on 100% How2Sign reached only 0.86–1.22 BLEU, similar to our run at about 9%. This is a cross-paper comparison (different code and model size), not a scaling curve we ran. | Not applicable (no training). | YouTube-ASL Table 3 |
| **Large-scale sign-language pretraining** (about 1,000 h of broader video–text, then How2Sign fine-tune) | **Supported by external evidence.** [EXT] Adding 984 h of YouTube-ASL raises BLEU from 1.22 to 12.39 (T5 pretrained) and from 0.86 to 6.26 (from scratch). Uni-Sign Table 8 (CSL, not ASL): BLEU-4 rises monotonically with pretraining data (0% → 3.51, 25% → 21.13, 100% → 25.61 test). | Already built in. | YouTube-ASL Table 3; Uni-Sign Table 8 |
| **Domain / preprocessing mismatch** | Train features (Kaggle MediaPipe) differ from frozen-test features (local extraction). Unmeasured. | **Verified mismatch V1, size unknown.** Real Curify videos (self-recorded, home lighting) are a further domain shift; never tested. | [CURIFY] P0 §4; 9.15 audit |
| **Inference configuration** | Greedy decoding, max_length=30 truncation (P0 §4); small effect. | Truncation and repetition loops verified (V3/V4); improvable without retraining, but cannot move a topic-wrong prediction to correct. | [CURIFY] |

**[INF] Verdict on b:**

- **Current evidence points more strongly to representation / sign-specific pretraining than to simply adding more supervised How2Sign labels.** This is a weighting of evidence, not a proof.
- Three different things are being distinguished:
  - **Supervised dataset scaling:** more How2Sign labels in the same downstream setup. Externally, it did not lift a comparable landmark+T5 system above about 1 BLEU at 100% How2Sign. We have not run our own scaling curve.
  - **Large-scale sign-language pretraining:** about 1,000 h of broader, noisier video–text data before fine-tuning. Externally, this is what moves How2Sign BLEU from about 1 to 6–12 (YouTube-ASL) and 14.5 (Uni-Sign).
  - **Learned representation:** what the encoder actually encodes. Ours is near-constant across videos (cosine 0.998–0.999), and the shuffled-video Δloss is only about 0.1. This is direct internal evidence of a weak representation, but it doesn't say *how* to fix it.
- **The YouTube-ASL evidence does not show data is irrelevant.** Pretraining *is* more data: about 12× the hours, broader content, more signers. What it suggests is narrower: **scaling the same downstream supervised setup is unlikely to produce the gains that sign-specific pretraining produces.**
- **Still unproven for our own system:**
  - whether a pretrained encoder (Uni-Sign's) would rescue our same 2,751-clip training (E1)
  - whether our 10% → 30% curve is flat (E2)
  - whether the conclusion holds on real Curify videos (E3)
- **We should not claim more data will fix things.** External evidence supports large gains only from pretraining-scale data (about 1,000 h), and only up to about 12–15 BLEU on How2Sign test.

## 5. Question c — Uni-Sign's problems and whether to build on it

### Problems, ranked by what we can act on

1. **Reproduction not established (blocking; see §2).** We do not know whether 5.4 vs. 14.5 comes from our pipeline, our pose extraction, the harder subset, or a combination (§2–3). Until E0 runs, any "improvement" is measured against an unvalidated baseline. [CURIFY + INF]
2. **Decoding degeneration.** 37.5% repetition loops; 65% truncation on clips longer than 15 s. These are fixable by forwarding `no_repeat_ngram_size`/`repetition_penalty` (requires a source edit) and raising `max_new_tokens`. [CURIFY 9.15 audit] **[INF]** This improves fluency and BLEU, not topic correctness.
3. **Topic fabrication.** Output is fluent but often on the wrong topic ("mascara brush", "fish"). This is the representation/semantic ceiling, and the paper's own examples show it too. [CURIFY 8.31, 9.2; EXT Table 16]
4. **No timestamps or segmentation.** The model returns one string per clip; long videos need external sentence segmentation. [CURIFY 9.17]
5. **Can't fine-tune from the ASL pretrained stage.** Only the *CSL* stage-1/2 pretrained weights and the How2Sign/OpenASL *fine-tuned* pose-only checkpoints are released. **No YouTube-ASL stage-1/2 and no ASL RGB-pose checkpoint.** [EXT HF `ZechengLi19/Uni-Sign` file list] Practical options are: (a) continue fine-tuning `how2sign_pose_only_slt.pth`, or (b) re-run the YouTube-ASL pretraining ourselves (984 h, multi-GPU).
6. **License.** The weights (and CSL-News) are CC BY-NC-4.0, so not usable commercially without permission. [CURIFY 9.17; EXT HF]
7. **Cost.** About 32 s/clip on CPU and 3.5 GB RSS (mT5-Base, 582M params). [CURIFY 9.2; EXT Table 12]
8. **RGB fusion gives little.** The RGB-pose variant adds only +0.4 BLEU on How2Sign (14.5 → 14.9). Low priority. [EXT Table 21]

### Build on Uni-Sign vs. continue Conformer+T5? [INF]

**Recommendation: pause from-scratch Conformer+T5 training. Make Uni-Sign (or a Uni-Sign-style pretrained pose encoder + mT5) the base. Make it conditional on E0.**

- **For Uni-Sign:**
  - It has the best lexical metrics of every system we measured, and in single-reviewer qualitative reads, some outputs are partially on topic. No ASL-fluent review has been done.
  - Its paper's ablation (on CSL) attributes the gain to the factor our path lacks: large-scale generative pretraining.
  - Its code is public and already containerized [CURIFY 9.17].
- **Against continuing Conformer+T5 as-is:**
  - A comparable external landmark+T5 setup reached only about 1 BLEU at 100% How2Sign.
  - The encoder-collapse diagnosis suggests it would need a pretraining corpus to change.
- **What survives from the P0 work:**
  - The padding-invariance tests.
  - The input-dependence (shuffled-video Δloss) diagnostic. It is a good, cheap representation metric to reuse on any encoder.
- **Conditions:**
  - If E0 fails to reproduce about 14 BLEU with official poses and the official script, something about our understanding of the release is wrong. Resolve that before investing.
  - If commercial use is required, the non-commercial license means a Uni-Sign-*style* re-pretraining on YouTube-ASL (its license terms also need checking) is the long-term path, not the released weights.

## 6. Smallest discriminative experiments

Ordered by cost. Each one is designed so that its two possible outcomes point to different bottlenecks.

### E0 — Reproduce the paper: implementation/deployment mismatch vs. model ceiling (no training) ★ HIGHEST-PRIORITY ASL EXPERIMENT

- **Setup:**
  - Download the official `how2sign_pose_format.zip.*` (about 8.5 GB, RTMPose/MMPose) and the official checkpoint.
  - Run upstream `script/eval_stage3.sh` unchanged (GPU preferred; CPU about 32 s/clip, so the full test set ≈ 20 CPU-hours, while the 128 clips ≈ 70 min).
- **Arms (2×2 + 1):**
  1. Official poses × full test (target: about 14.5)
  2. Official poses × our 128 clips
  3. Our rtmlib-lightweight poses × our 128 clips (= existing 5.39, reuse)
  4. rtmlib `mode="performance"` (x-size) × 128 clips
  5. Optionally, also score arm 1 against the original vs. re-aligned TSV (H2)
- **How to read the results:**
  - (1) ≈ 14.5 and (2) ≈ 5 → **the gap is our subset's difficulty**; our pipeline is fine.
  - (2) ≫ (3) → **the pose extractor (V1) is the cause**. Switch the deployed container to the official extractor settings.
  - (1) ≪ 14.5 → the release itself does not reproduce the paper. Stop and report upstream.
- **Cost:** about 8.5 GB download + about 1 GPU-hour (or about 1 CPU-day). No training.

### E0b — Decoding fix, inference only (no training)

- **Setup:** On whichever pose setting wins E0, run on the diagnostic-12 subset, then on 128 clips:
  - `num_beams` ∈ {1, 4, 8}
  - `max_new_tokens` ∈ {100, 200}
  - `no_repeat_ngram_size` ∈ {0, 3} (requires forwarding the argument in `models.py`)
- **Metrics:**
  - BLEU, chrF, WER
  - repetition rate and truncation rate
  - **topic-match rate**, using the existing 40-clip semantic-review rubric
- **How to read the results:** If repetition/truncation falls but topic-match does not move, the remaining gap more likely lies in the representation than in decoding. This is the 9.15 proposal, extended.

### E1 — Data vs. representation on our own path (small training, the key discriminator for question b)

- **Setup:**
  - **Hold the data fixed:** the same 2,751-clip P0.2 split and the same t5-small decoder/recipe.
  - **Vary only the input representation:**
    - (A) our Conformer on MediaPipe landmarks (existing P0.2 result, reuse)
    - (B) **frozen Uni-Sign pose+temporal encoder features** (from `how2sign_pose_only_slt.pth`), on RTMPose poses of the same clips
    - (C) optional: the same frozen encoder with **randomly initialized** weights, to control for architecture vs. pretraining
- **Metrics:**
  - val/frozen BLEU and chrF
  - **shuffled-video Δloss** (the P0 input-dependence diagnostic)
  - cross-video cosine similarity of encoder outputs
- **How to read the results:**
  - **B ≫ A at the same data → representation bottleneck.**
  - B ≈ A ≈ 1 BLEU → the small decoder or the data size limits even a good representation (data/decoder bottleneck).
  - B ≫ C → the gain is from pretraining, not architecture.
- **Caveat:** The Uni-Sign encoder was fine-tuned on How2Sign *train*, so evaluate only on val/frozen-test, never on train.
- **Cost:** about the cost of one P0.2 run (about 2.4 h CPU) per arm, plus feature extraction.

### E2 — Data-scaling slope (only if E1 is ambiguous)

- **Setup:** Arm B (or A) at 10% → 30% of How2Sign train, 2 seeds each.
- **How to read the results:** A flat slope from 10% to 30% confirms the literature (more How2Sign alone does not help). A clear rise would be the first evidence *for* labeled-data scaling.
- **Why not first:** Literature already brackets the answer for arm A; E1 is cheaper and more informative.

### E3 — Domain gap on real Curify video (no training, after E0)

- **Setup:** Run the reproduced Uni-Sign configuration on the private Curify corpus clips that have independent ground truth. [CURIFY] `asl-translator/data/asl_corpus/` has 13 videos, of which only 4 have any reference; check `inventory.json`. Private data only, never pushed.
- **How to read the results:** Compare with the How2Sign subset. A collapse would mean domain shift (lighting, framing, signer variety) dominates for the product. This is the number that actually matters for Curify.

**Not recommended now [INF]:**

- Scaling Conformer+T5 to 100% How2Sign
- Swapping to flan-t5-base
- More Gemini prompt, frame, or trajectory variants (three axes already flat [CURIFY 9.6/9.10])
- RGB-pose fusion (+0.4 BLEU)

## 7. Open blockers

- **Compute and environment.** The Uni-Sign conda env was deleted on this machine [CURIFY 9.15] and needs a rebuild. A GPU would turn E0 from a day into an hour.
- **License.** The CC BY-NC-4.0 weights are fine for research; a commercial path needs a decision.
- **Missing ASL pretrained weights.** No ASL stage-1/2 weights are released, which limits how deeply we can adapt Uni-Sign without re-pretraining.
- **No ASL-fluent review.** Still none anywhere; topic-match judgments are text-only.
- **Unpushed P0 code.** The P0 code commit `7da5734` is not pushed (403); E1 builds on it.

## Sources

**[EXT] external:**

- Li et al., *Uni-Sign: Toward Unified Sign Language Understanding at Scale*, ICLR 2025, arXiv:2501.15187v3. Tables 1, 2, 8, 12, 16, 21; §3.2, §4.1; Appendix A.1, C.
- Uthus et al., *YouTube-ASL*, NeurIPS 2023 D&B, arXiv:2306.15162. Table 3, §4–5.
- Uni-Sign repo `github.com/ZechengLi19/Uni-Sign`: README and `docs/DATASET.md` (official pose_format is RTMPose/MMPose).
- HF `huggingface.co/ZechengLi19/Uni-Sign` file listing (checkpoints released; no ASL stage-1/2).
- How2Sign split sizes: Duarte et al., CVPR 2021.

**[CURIFY] prior:**

- `docs/daily_report/9.2/asl-baselines/HOW2SIGN_V2_OPENSLT_UNISIGN_FULL_RESULTS.md`
- `docs/daily_report/8.31/asl-next-baseline/results/`
- `docs/daily_report/9.15/{ASL_MANAGER_SUMMARY.md, unisign-inference-parameter-audit/README.md}`
- `docs/daily_report/9.17/unisign-deployment-work-report/`
- `asl-translator/evaluation/diagnostics/phase1_temporal_ablation/`
- `docs/daily_report/9.10/trajectory-tracking-feasibility/`
- branch `baobao/asl-p0-report-2026-09-25` → `docs/daily_report/9.25/asl-p0-diagnostics/p0_work_report_2026-09-25.md`
- `asl-translator/data/public_benchmarks/how2sign_v2/SELECTION_METHODOLOGY.md`
