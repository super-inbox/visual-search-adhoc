# P0-19: Safe representation fusion for Uni-Sign (confidence-gated candidate reranking)

**Date:** 2026-10-20 · **Branch:** `baobao/visual-production-research-2026-10-05` · **Status: Stage 0 frozen
(`STAGE0_FREEZE.json`), not yet run.** Stage 1 and the H19 one-shot are outlined in §7 only; they are **not** frozen
and must not start without a separate approval and their own freeze.

## 1. Question

Can complementary representation evidence (P0-14: the mT5 encoder-state probe) improve Uni-Sign's final sentence
output **without** increasing hallucination, WER or repetition, by **selecting among Uni-Sign's own beam
hypotheses**, with abstention?

- No lexical content is generated or appended from the auxiliary detector (P0-15 showed naive union is unsafe:
  331 additions, 50 correct, net −231 on dev).
- The probe can only change which **Uni-Sign-generated** candidate is output, and only past a frozen margin;
  otherwise the system abstains and keeps Uni-Sign's top-1.

**Stage 0 asks the prerequisite question:** do Uni-Sign's top-k candidates differ enough, in the concepts the probe
can see and in quality, for any reranker to matter? If not, P0-19 stops here at almost no cost.

## 2. Data roles and holdouts (P0-16)

| Data | Role in P0-19 | Status |
|---|---|---|
| How2Sign train | lemma families of the frozen P0-14 matcher (train references only); later probe fitting | training-only |
| How2Sign test_clean (2,209 clips / 149 videos) | **Stage 0 data**; later Stage 1 development | exploratory / validation-used (P0-16 §3) |
| **H18** | **not used by P0-19.** `HOLDOUT_PLAN.md` §6 allows P0-19 to develop on H18 only after P0-18's one-shot run on it; P0-18 stopped at development and H18 was never opened | sealed, reserved for a stronger P0-18 candidate |
| **H19** | P0-19's one-shot evaluation, only after a full Stage 1/2 freeze | **sealed**; not touched in Stage 0 |

Holdout protection in every Stage 0 process (gate G3):
- every clip id passes `holdout_guard.assert_not_holdout` (P0-16);
- an `open()` tripwire is then installed that refuses any path naming How2Sign val material or the holdout lists
  (`scripts/p019_common.py`, `DENY`);
- official-archive members are read only under `test-pose-rtmpose-192/` (the archive has no val directory);
- the How2Sign **val** CSV is never opened: the P0-14 matcher's lemma families depend on train only, so its val slot
  is given the test CSV;
- the `val_pos` / `val_pos_videos` columns of `concept_list_v1.csv` (P0-14 aggregate val counts) are never read.

## 3. Stage 0 definitions (frozen in `config/stage0_config.json`)

**Input domain:** official poses (P0-14 Stage 4), so the stored baseline can be reproduced exactly. Stage 0 is
exploratory and only measures headroom; Stage 1 must move to the H19 input domain (official crops + our extractor).

**Decoding** (`scripts/decode_topk.py`): one frozen Uni-Sign forward per clip, exactly as P0-14
`decode_baseline.py` (same checkpoint `1bfd5f33…`, Uni-Sign `eed438bc`, ≤ 256 frames sampled with
`random.seed(int(sha256(clip_id)[:8], 16))`, fp32, batch 1, seed 42, cuDNN deterministic), then for each
k ∈ {4, 8}:
`mt5_model.generate(inputs_embeds, attention_mask, max_new_tokens=100, num_beams=k, num_return_sequences=k,
output_scores=True, return_dict_in_generate=True)`. Stored per candidate: rank, text, token ids, length,
HF `sequences_scores`.

**Candidate pools:**
- **k = 4:** the 4 returned beams; rank 0 is the baseline top-1 (gate G1).
- **k = 8:** the stored baseline top-1 first, then the 8 returned beams. (A `num_beams=8` search does not in general
  return the 4-beam top-1 first: in the 5-clip CPU smoke test it differed on 4 of 5 clips.)
- Exact-text duplicates removed, first occurrence kept.

**Concepts:** P0-14 Tier L, 24 concepts, frozen matcher (`build_concepts.py` lemmas + `concept_list_v1.csv`
match/forms), applied to candidate text exactly as P0-14 applied it to Uni-Sign's translation.

**Metrics** (all over the 2,209 test_clean clips, references = How2Sign test `SENTENCE`):

| ID | Metric |
|---|---|
| C1 concept-set diversity | fraction of clips whose pool contains ≥ 1 candidate whose Tier L concept set differs from the top-1's |
| C2 missed-concept recovery | of the **498 missed cells** (reference has Tier L concept c, stored top-1 does not), the number for which some pool candidate mentions c |
| C3 oracle-best-in-k | corpus chrF of the per-clip oracle candidate − corpus chrF of the stored top-1. Oracle = argmax sentence chrF vs the single reference, ties → earliest pool position. sacrebleu `corpus_chrf` / `sentence_chrf` defaults (chrF2, char order 6, word order 0); version and signature recorded |

Descriptive only (no decision weight): mean unique candidates per clip, corpus BLEU-4 of top-1 and oracle, clips
whose oracle sentence chrF ≥ top-1 + 5, decode seconds per k.

## 4. Gates, criteria and decision (truth table)

**Sanity gates** (any FAIL → **VOID**: nothing interpreted, no re-run, no redefinition; P0-16 §5):

| Gate | Requirement |
|---|---|
| G1 reproduction | with `num_beams=4`, rank-0 text == stored P0-14 prediction **and** trimmed token count == stored `n_tokens`, on 2,209 / 2,209 clips |
| G2 determinism | an independent second process on the first 40 test_clean clips (manifest order) gives identical candidate count, order, token ids and texts for k = 4 and k = 8; max \|seq_score Δ\| ≤ 1e-5 |
| G3 no holdout access | guard passes on every id; tripwire installed in both decode runs and the analysis with no refusal; archive members only under `test-pose-rtmpose-192/` |
| G4 input integrity | per-clip pose sha256 == P0-14 stored value on 2,209 / 2,209; stored predictions sha256 prefix `0116a41a`; candidates cover exactly the test_clean ids in manifest order |
| G5 label reproduction | matcher reproduces the manifest's 30 concept labels on all 2,209 references; 888 Tier L mentions in the stored predictions; exactly **498** missed cells |

**Criteria** (per k; unrounded values; boundaries inclusive):

| Criterion | GO threshold |
|---|---|
| C1_k | diversity fraction **≥ 0.10** |
| C2_k | recovered missed cells **≥ 50** (of 498) |
| C3_k | oracle chrF − top-1 chrF **≥ +3.0** |

**Decision** (`scripts/stage0_verdict.py`, a lookup on P0-16 `verdict_policy.verdict`; the plan-code test
`scripts/test_stage0_verdict.py` enumerates all 2⁵ × 2⁶ = 2,048 combinations):

| Gates | Criteria | Stage 0 decision |
|---|---|---|
| any gate FAIL | any | **VOID** |
| all PASS | C1_k4 ∧ C2_k4 ∧ C3_k4 | **GO**, Stage 1 uses k = 4 |
| all PASS | not the above, and C1_k8 ∧ C2_k8 ∧ C3_k8 | **GO**, Stage 1 uses k = 8 |
| all PASS | neither k passes all three | **NO-GO** |

`verdict_policy` words map as SUPPORTED → GO, NOT SUPPORTED → NO-GO, VOID → VOID. GO is **not** a P0-19 verdict; it
only permits planning and freezing Stage 1. No PARTIAL is defined.

## 5. Consequences

- **NO-GO:** P0-19 stops at Stage 0. **Development verdict: NOT SUPPORTED.** H19 stays sealed. The reason is
  recorded (which criterion failed, by how much).
- **VOID:** P0-19 Stage 0 is void; the failing gate is reported with diagnostics in a separate section. A repaired
  pipeline is a new, separately frozen experiment.
- **GO:** Stage 1 is planned in the H19 input domain (§7) and needs its own approval and freeze. H19 stays sealed.

## 6. Execution

Compute: the T4 VM `baobao-training-t4` (Spot, `asia-east1-a`), the P0-14 `unisign` conda env, the official pose
archive `~/p014/archive/how2sign_pose_format.zip.0{0..3}` (sha256 in `10.15/.../full_run/archive/sha256.txt`).

1. `python -I scripts/freeze_stage0.py` (Mac; runs the verdict test, writes `STAGE0_FREEZE.json`).
2. Upload (a repo-relative subset): `10.15/asl-unisign-representation-probe/{scripts/extract_representations.py,
   splits/manifest.csv}`, `10.16/asl-p0-16-experimental-credibility/{scripts/holdout_guard.py, holdout/}` (needed by
   the guard; ID lists only, no val data), and this folder. Copy `~/p014/env.sh` to `~/p019/env.sh`.
3. `bash scripts/run_stage0_vm.sh` (main run on 2,209 clips, then the 40-clip repeat; resumable after preemption).
4. Copy `~/p019/stage0/` back, verify `SHA256SUMS`, stop the VM.
5. `python -I scripts/stage0_analyze.py --main … --repeat … --out …` (Mac; checks the freeze first).

Outputs (local, not in git): `~/Desktop/curify/p019-work/stage0/{main,repeat,result}/`.

## 7. Outline of later stages (NOT frozen; for orientation only)

- **Stage 1 (development, H19 input domain):** official test crops + our extractor (P0-18 frozen); arms A baseline,
  B decoder-only rerank, C decoder + mT5 support, D = C + repetition filter + margin gate/abstain; controls N1
  (20 shuffled-probe seeds), N2 (length-only); out-of-fold by source video; GO criteria D1–D7 as proposed on
  2026-10-20 (ΔchrF D−A ≥ +0.3 with CI > 0; D−B CI > 0; WER, length, repetition and unsupported-concept
  do-no-harm; win:loss ≥ 1.5; probe-transfer AUROC ≥ 0.80; H19 power ≥ 0.6).
- **Stage 2:** full freeze, then one-shot on H19. NOT SUPPORTED or VOID on H19 closes the fusion line.

## 8. Files

| File | Purpose |
|---|---|
| `config/stage0_config.json` | frozen Stage 0 definitions and thresholds |
| `scripts/p019_common.py` | guard + tripwire, frozen P0-14 matcher (no val), token-id trimming |
| `scripts/decode_topk.py` | top-k candidates (k = 4, 8) |
| `scripts/stage0_analyze.py` | gates, criteria, decision |
| `scripts/stage0_verdict.py`, `scripts/test_stage0_verdict.py` | decision lookup and plan-code test |
| `scripts/freeze_stage0.py` | writes `STAGE0_FREEZE.json` |
| `scripts/run_stage0_vm.sh` | VM driver |
