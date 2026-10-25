# P0-16: Confirmatory holdout plan for P0-18 and P0-19

**Status: approved 2026-10-16. H18 and H19 are the confirmatory holdouts** (membership frozen in
`holdout/HOLDOUT.sha256`). No val video byte has been downloaded, no val pose extracted, and no model run on val. No
val reference was read beyond the automated duplicate screen, which outputs only IDs and counts.

## 1. Is How2Sign test still usable for confirmation? No.

| Test subset | Why it is not confirmatory |
|---|---|
| frozen 147 (pilot 19 + benchmark 128) | references and predictions inspected per clip, across the experiments in `DATA_USE_LEDGER.csv` |
| other clips from those 128 videos | same source videos as per-clip-inspected clips (128 of 149 test videos, 2,045 of 2,357 clips) |
| the remaining 21 videos (290 clean clips) | decoded and analysed in P0-14 aggregates, which shaped P0-15; too small anyway |
| P0-15 final half (1,157 clips) | unopened *for P0-15*, but all in P0-14 aggregates, and 66 are benchmark clips (`EXPERIMENT_PROTOCOL.md` H2) |

All of How2Sign test is now **development data** (exploratory or validation-used).

## 2. Alternatives considered

| Option | Verdict | Reason |
|---|---|---|
| **How2Sign val, with our own pose extraction** | **Recommended** | Same domain and protocol as test. **Never used by Uni-Sign's authors** (the How2Sign dev label path is empty upstream). **Never decoded by us.** Only aggregate reference counts were computed (P0-14 audit). Official signer-crop, re-aligned **val crop videos exist** in Uni-Sign's HF archive (§3). |
| Unseen remainder of How2Sign test | rejected | 290 clips, already in P0-14 aggregates |
| P0-15 final half | rejected and retired | previously observed (§1) |
| YouTube-ASL | rejected | part of Uni-Sign's pretraining data (about 984 h, per the P0-13 audit) |
| OpenASL or other public ASL translation sets | secondary only, later | out of domain for a How2Sign-fine-tuned checkpoint. Possible source overlap with YouTube-ASL (both YouTube-sourced; **not audited**). Would need its own overlap audit |
| A newly recorded / newly frozen set | best independence, not now | needs collection and references. The right choice once val is used up (§7) |

## 3. The holdout: How2Sign val (`scripts/build_holdout.py`, `holdout/SPLIT_LOG.json`)

**Source:**
- 1,741 val clips from 115 source videos (`how2sign_realigned_val.csv`, sha256 in `SPLIT_LOG.json`).
- Signer proxies 1, 2, 3, 5 and 8, all of which also occur in train. **Unseen signers are not tested.**

**Exclusions** (P0-14 duplicate rule: exact normalized match, or ≥ 50 % of a sentence's word 4-grams in a single
other sentence, for sentences of ≥ 6 words): **98 clips**, in `holdout/EXCLUDED.csv`.

| Reason | Clips |
|---|---|
| exact duplicate of a train reference | 53 |
| near duplicate of a train reference | 39 |
| exact duplicate of a test reference | 30 |
| near duplicate of a test reference | 6 |
| no official crop video | 3 |

Some clips have more than one reason, and no video is lost entirely.
- The train counts (53 and 39) reproduce P0-14's audit exactly.
- Test duplicates are excluded because all of How2Sign test is now development data.

**Units:** the source videos. Videos sharing a normalized sentence would have been merged; none do. This gives
**1,643 clips in 115 units**.

**Split into two sealed halves:**
- Units are stratified by majority signer proxy, randomly permuted, sorted by clip count, and assigned serpentine.
- Balance check: H18 clip share in [0.45, 0.55], and every stratum on both sides.
- Seeds were tried from 16; **seed 16 passed first**.
- **The split uses no labels and no model output.**

| Holdout | Units (videos) | Clips | Reserved for |
|---|---|---|---|
| **H18** | 57 | 814 | P0-18, one shot |
| **H19** | 58 | 829 | P0-19, one shot |

**Why two halves:** P0-19's design will be informed by P0-18's result. If both used one set, P0-19 would repeat the
P0-14 → P0-15 contamination.

**Video inputs available for val:**
- **Official crop videos** (`crop_val/`, signer crop, re-aligned timing): 1,738 files, 0.989 GB. They sit
  contiguously inside `how2sign_rgb_format.zip.ae` of Uni-Sign's HF repo, so they can be range-fetched. The index
  is in `holdout/crop_val_index.tsv`.
- **Raw val clips** (original timestamps, full frame; needed as P0-18's input) come from How2Sign's official
  `val_rgb_front_clips` archive. **Size not verified.** Scaling the test archive (2.41 GB for 2,357 clips) gives
  about 1.8 GB.
- **No official val poses exist.** Every val pose comes from our extractor (rtmlib Wholebody lightweight, as in
  P0-12). On test, our extractor on official crops (P0-12 condition C) was within 0.52 BLEU-4 of official poses.
  Val numbers are therefore **not directly comparable** to official-pose test numbers.

## 4. Seal rules (until the one-shot run of each half)

**Allowed before opening:**
- downloading val video bytes and verifying sizes, CRC-32 and sha256 **without decoding them**;
- recording file hashes.

Pose extraction and any other frame decoding of H18 / H19 run **only inside that P0's one-shot run**, after
`RUN_LOCK`.

**Forbidden before opening:**
- decoding, viewing or extracting from val frames or videos, by any development script or person;
- running Uni-Sign or any probe or verifier on val;
- reading val references or deriving labels from them (beyond the automated duplicate screen already done, which
  output only IDs and counts);
- computing any statistic that combines val references or val model output;
- changing `holdout/` (the guard checks `HOLDOUT.sha256`).

**One-shot procedure** (`SANITY_GATE_POLICY.md`, `EXPERIMENT_PROTOCOL.md` §4.3):
1. The P0's plan, code and `FREEZE.json` are committed first. They include the verdict truth table and the
   plan-code consistency test.
2. The one-shot script verifies the `FREEZE` and `HOLDOUT` hashes.
3. It writes `RUN_LOCK` before loading any val reference or producing any val output.
4. It runs once.
5. The half becomes **validation-used**.

## 5. Guard

`scripts/holdout_guard.py`: `assert_not_holdout(clip_ids)` raises if any ID is a val clip or belongs to a val source
video. It covers all 1,741 val clips, including the excluded ones, and all 115 val videos. Every P0-18 and P0-19
development script calls it.
- Tested: blocks 1,741/1,741 val clips and an unseen clip ID from a val video; passes all 33,522 train and test
  clips.

## 6. What P0-18 and P0-19 may tune on, and what is evaluated once

| | P0-18 (automatic preprocessing) | P0-19 (final fusion experiment) |
|---|---|---|
| **May tune / develop on** | **How2Sign train**, using **alignment-level targets only** (re-aligned timestamps, official crop boxes vs automatic ones). Translation scores on train are not evidence, because Uni-Sign trained on it. **How2Sign test, all 2,357 clips** (exploratory / validation-used), including translation metrics. The 147 locally available raw test clips. Official test crops (`crop_test/`) and poses as references. | **How2Sign train** (probe training, as in P0-14). **How2Sign test**: all test_clean, including the P0-15 dev and the retired P0-15 final half. **H18, but only after P0-18's one-shot run on it is complete** (it is then validation-used and gives development data in the val, our-extractor domain). |
| **May not touch before its one-shot run** | **H18 and H19**: any val clip, frame, reference or output | **H19**: any val clip, frame, reference or output. Also H18 before P0-18 has opened it. |
| **Evaluated once** | **H18** (814 clips, 57 videos) | **H19** (829 clips, 58 videos) |
| **Input pipeline on the holdout** | the automatic pipeline frozen in P0-18's FREEZE. Reference arms (naive original-timestamp full frame; official crop + our extractor) are pre-registered. Official val crops may be a **reference arm only**, never the automatic pipeline's input | exactly the pipeline frozen in P0-19's FREEZE. If P0-18 is SUPPORTED, its pipeline; otherwise official crops + our extractor. Development must use the same pose extractor as the holdout run. |
| **Must pre-register** | primary endpoint and arms, verdict truth table, sanity gates (≥ 20-seed nulls where relevant), bootstrap over H18 units | the same, **plus the explicit exit criteria** the manager asked for (e.g. NOT SUPPORTED or VOID on H19 closes the fusion line) |

## 7. After use

- When H18 is opened it becomes validation-used, and so does H19 when it is opened.
- After both, **no confirmatory How2Sign data remain.** A later confirmatory claim needs a new, independently frozen
  set (§2, last row).
