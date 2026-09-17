# Phase 3A — Controlled Sampling-Strategy Ablation: Adaptive vs. Uniform, 2 fps

**Research question:** Does the current motion-weighted/adaptive sampling strategy
itself hurt Gemini ASL translation compared with uniform temporal sampling, holding
the target density and all other inference conditions fixed?

**Scope:** the 12 fixed diagnostic clips (`diagnostic_12_clips.json`) only. Not the
40-clip taxonomy, not the 128-clip frozen benchmark.

## Design

| | Arm A — existing baseline | Arm B — new controlled arm |
|---|---|---|
| config | `evaluation_2026_09_04_gemini_3_6` | `evaluation_2026_09_07_gemini_3_6_uniform_2fps` |
| sampling strategy | adaptive / motion-weighted (`allocate_timestamps`) | **uniform**, evenly spaced (`allocate_timestamps_uniform`) — new, additive |
| target_frames_per_sec | 2.0 | 2.0 (unset -> same module default; **held fixed**) |
| model | gemini-3.6-flash | gemini-3.6-flash |
| thinking_level | medium | medium |
| batch_size | 24 | 24 |
| dedup | true | true |
| predictions | **REUSED**, not rerun (`curify_gemini_3_6_2026_09_04/predictions/`) | **NEW** real Gemini calls, this experiment |

The single controlled variable is the timestamp-allocation formula. Every other
knob (model, prompt, batch size, dedup, thinking_level, target density, frame
budget per clip) is identical between arms — see `config_or_metadata.json` and
`design_check.json` in this directory for the full config diff and per-clip proof.

The uniform sampler (`run_current_model.allocate_timestamps_uniform`) and its
config were added **additively** to `asl-eval/run_current_model.py`: the
production/baseline `allocate_timestamps()` function and every pre-existing
CONFIGS entry are byte-for-byte unchanged (`pytest test_run_current_model.py`:
56 passed, 6 skipped, both before and after this change).

## Design check (before any Gemini call — see `design_check.json`)

- **Frame counts matched exactly for all 12 clips** — 0 mismatches between the
  adaptive arm's actual sampled-frame count and the uniform arm's (which is
  always exactly `frame_budget` by construction).
- **Both samplers are chronologically ordered** for all 12 clips (asserted in
  `design_check.py`, not just checked by inspection).
- **MIN_FRAME_BUDGET=24 is binding on 8 of the 12 clips** (`-g0iPSnQt6w`,
  `-g0sqksgyc4`, `92V3oH63zbQ`, `Fz-N1S0swh8`, `g0TkUiO7t4I`, `g2ELiaFjKfs`,
  `g2NA_eBUcH8`, `G19uBylwQww` — all under 5.25s). For these, `duration_s * 2.0`
  is below 24, so the actual sampling density is well above a literal 2 fps for
  **both arms equally** (e.g. `92V3oH63zbQ` at 1.5s duration samples 24 frames =
  16 fps, not 2 fps). This is not a confound between arms — the same
  `resolve_frame_budget()` call produces the same budget for both configs on
  every clip — but it does mean "2fps" is not literally true for 8/12 clips, and
  is documented here so it isn't silently misread later.
- **No confound was found** that would prevent a fair comparison. Inference
  proceeded automatically per the experiment plan.
- Pre-flight estimate: 18 new Gemini calls, ~364 frames (uniform arm only,
  baseline reused). **Actual: 18 calls** (1 smoke-test call + 11 more), matching
  the estimate exactly — see run logs and `predictions/*.json` `run_metadata`.

## Scoring

Both arms scored with the existing, unmodified `asl-eval/evaluate.py` + `lib.py`
(same WER/CER normalization used everywhere else in this repo).

| metric | Arm A (adaptive) | Arm B (uniform) | delta (B - A) |
|---|---|---|---|
| corpus WER (pooled) | 1.0524 | 1.0594 | **+0.0070** |
| mean per-clip WER | 1.0825 | 1.0590 | **-0.0235** |
| median per-clip delta | — | — | **0.0000** |

Per-clip outcome: **2 improved, 5 worsened, 5 unchanged** (out of 12).

### Side-by-side

| clip_id | reference | adaptive_prediction | uniform_prediction | adaptive_WER | uniform_WER | delta | hint bucket |
|---|---|---|---|---|---|---|---|
| `FzmL8SL6Bow_1-8-rgb_front` | You want to go and clean up that hole you just made and now we are goi... | I looked and saw a dog approaching. It just stood there, completely fr... | Is it light or heavy? A large bear lumbered along, wandering through t... | 0.9615 | 0.9872 | +0.0257 | fingerspelling_candidate |
| `fzNnTgHa1lM_2-5-rgb_front` | So you can tune the G with the lower G and the D with the lower D. So ... | Whenever you go with someone... chronic friend | Dog Video game I have three | 0.9412 | 0.9706 | +0.0294 | fingerspelling_candidate |
| `fZM3IcM2Xs4_14_15_16-10-rgb_front` | Look at that. Morris sings(Ready to rock and roll today) Kind of feels... | People have many different perspectives and situations, and sharing va... | After crawling around for two hours, my body feels so sore and I am co... | 1.9130 | 1.0000 | -0.9130 | fingerspelling_candidate |
| `-g0iPSnQt6w_0-1-rgb_front` | Buenos Dias, I'm Bobby Larew, you didn't know I spoke Spanish, did you... | Back in Barcelona | Brenda | 1.0000 | 1.0000 | +0.0000 | fingerspelling_candidate |
| `G05uFub3YFc_9-2-rgb_front` | Again, do maybe twenty breaths, little flow, inhaling and exhaling the... | She smooths out the cloth and places it flat on the table. She sets th... | He sat down and looked around. He tried to calm himself down. He felt ... | 1.0294 | 1.5882 | +0.5588 | number_token |
| `-g0sqksgyc4_3-2-rgb_front` | So whenever you're moving forward, try to move the front foot first wh... | A spider was crawling on me! | Wait, there was one... ...creeping right toward me! I gripped the whee... | 1.0000 | 1.0000 | +0.0000 | number_token |
| `92V3oH63zbQ_5-1-rgb_front` | What is keeping your hands inside the baseball? | *(empty)* | Finished. | 1.0000 | 1.0000 | +0.0000 | question |
| `Fz-N1S0swh8_2-8-rgb_front` | I'm not going to use a lot, I'm going to use very very little. | Angry | What is the girl's name? | 1.0000 | 1.0000 | +0.0000 | fingerspelling_candidate |
| `g0TkUiO7t4I_6-8-rgb_front` | Cause wrinkle is the problem with the dry skin. | A cat and a friend a sweet girl comes to a full stop. | One day, a beautiful friend told the girl to calm down and stop crying... | 1.4444 | 1.4444 | +0.0000 | plain_no_flag |
| `g2ELiaFjKfs_3-10-rgb_front` | Now we're going to teach them to stay before walking in the road. | After that, then, and lastly, it crawls forward and sits on the edge, ... | Go over, then go under, and finally... | 1.1429 | 1.0000 | -0.1429 | plain_no_flag |
| `g2NA_eBUcH8_0-3-rgb_front` | Hi, have you ever wanted to learn a new game of poker? | If you want to learn | Do you know how to study to learn? | 0.7500 | 0.8333 | +0.0833 | question |
| `G19uBylwQww_1-2-rgb_front` | Hi, my name is Robert Segundo and today I'm going to teach you how to ... | My name is Robert. I was born in California. | My name is Rebecca Guido. | 0.8077 | 0.8846 | +0.0769 | fingerspelling_candidate |

Full text and all fields: `paired_results.csv` / `paired_results.json`. For
descriptive context only, `paired_results.csv` also carries the LLM-assisted
text-semantic review fields for the **baseline (Arm A)** predictions
(`semantic_adequacy`, `reference_topic_mismatch`, `requires_asl_expert_review`
from `taxonomy_40_text_semantic_review.json`). **No equivalent semantic review
was performed for Arm B's predictions** — those fields are reported for Arm A
only, and no human or ASL-expert semantic label exists for either arm's
predictions.

## Interpretation

### 1. Did uniform 2fps materially outperform adaptive 2fps?

**No.** Corpus WER moved by +0.0070 (uniform slightly *worse* pooled), mean
per-clip WER moved by -0.0235 (uniform slightly *better* on average), and the
median per-clip delta is exactly 0.0000 — half the clips (5/12) produced
*identical* WER under both samplers. The mean's small apparent improvement is
driven almost entirely by one clip (`fZM3IcM2Xs4`, WER 1.9130 -> 1.0000): WER
1.0 there still means the prediction shares essentially no words with the
reference (uniform's actual text is about "crawling around for two hours" and
"celebration," the reference is about a festive musical performance) — the
clip went from one severe failure mode (WER > 1, extra fabricated content) to
another (WER = 1, still wrong topic), not from failure to any success. With
that single non-meaningful outlier's influence discounted, this is a flat,
mixed result: **2 clips improved, 5 worsened, 5 unchanged.** A ±0.02–0.06 WER
movement on individual short clips (several under 5 seconds, 1-2 sentence
references) is well within what normal Gemini output variance could produce on
its own, even holding sampling fixed — this experiment did not run repeat
trials to separate that from a real sampling effect, so no claim beyond "no
material aggregate difference" is warranted.

### 2. Were improvements concentrated in any hint category?

**No consistent pattern, and sample sizes are too small (n=2–6 per bucket) to
draw a category-level conclusion.** These hint buckets are reference-derived
manifest heuristics, not confirmed ASL categories (see below).

| manifest hint bucket (reference-derived, NOT confirmed visual) | n | mean WER delta |
|---|---|---|
| fingerspelling_candidate | 6 | -0.1302 (driven entirely by the one outlier above; median of this bucket alone is 0.0) |
| number_token | 2 | +0.2794 (worse for uniform; n=2) |
| question | 2 | +0.0416 (worse for uniform; n=2) |
| plain_no_flag | 2 | -0.0714 (slightly better for uniform; n=2) |

Removing the `fZM3IcM2Xs4` outlier, the fingerspelling-candidate bucket's mean
delta flips to +0.0264 (slightly *worse* for uniform), matching the direction
of every other bucket except plain_no_flag. There is no bucket where uniform
sampling shows a clear, sample-size-credible win. **These `manifest_hint_bucket`
labels describe what the English reference text contains (a heuristic over the
reference), not a confirmed visual ASL category** — a "number_token" clip is
one whose reference text happens to contain a number, not a clip an ASL-fluent
reviewer confirmed shows number-handshape content.

### 3. Do the frame inspectors show obvious differences in temporal coverage?

**Yes, by construction, and the difference is visually largest exactly where
you'd expect.** Per `design_check.json`, clips with several active/idle motion
alternations show the starkest divergence: `FzmL8SL6Bow` (5 active runs, 25.5s)
and `fZM3IcM2Xs4` (7 active runs, 18.5s) — the adaptive sampler visibly
clusters extra timestamps inside each active-motion run and thins out over
idle stretches, while the uniform sampler's tick marks are perfectly evenly
spaced across the whole span regardless of the motion-run shading underneath.
See `inspectors/FzmL8SL6Bow_1-8-rgb_front.html` and
`inspectors/fZM3IcM2Xs4_14_15_16-10-rgb_front.html` for the clearest visual
contrast.

For the 8 short, MIN_FRAME_BUDGET-bound clips (1.5–5.25s, 1–3 active runs),
both samplers already place frames densely enough (16 fps or more in the most
extreme case) that the practical coverage difference is much smaller — there
simply isn't much of the clip either sampler could skip at that density. This
matches those 8 clips' near-total absence of WER movement (7 of 8 exactly
0.0000, one at +0.0833).

**This inspection is temporal-coverage only.** Neither this report nor the
inspector claims to know whether the *frames themselves* (as opposed to their
timestamps) capture the specific handshape/motion/sign an ASL-fluent viewer
would need — that determination requires watching the video with ASL fluency,
which this pass does not have (consistent with the Phase-1 human-review-schema
work: `HUMAN_REVIEW_GUIDE.md`, ASL/VISUAL review bucket).

### 4. Is the effect large enough to justify scaling this arm to more clips?

**No, not on this evidence.** A conservative reading of a flat corpus WER, a
zero median delta, and a mean improvement fully attributable to a single
outlier clip whose "improvement" is itself just a different flavor of total
failure, does not support scaling this specific ablation arm further. Both
arms' actual predictions remain dominated by severe topic-level hallucination
regardless of sampling strategy (see the side-by-side table — most predictions
under both arms describe unrelated content, not near-misses), which is the
same near-total-failure pattern documented in the Phase-1 40-clip
LLM-assisted text-semantic review (`TEXT_SEMANTIC_REVIEW_SUMMARY.md`) and in
the earlier temporal-density (2fps-vs-8fps) ablation
(`PAIRED_76_PRELIMINARY_ANALYSIS.md`), which also found no aggregate
improvement. Three independent probes now point the same way: neither raising
frame density nor changing the sampling-allocation strategy (holding density
fixed) has moved this benchmark's dominant failure mode. **No causal claim
beyond the single controlled variable is made** — this result says "changing
the allocation formula alone, at 2fps, on these 12 clips, did not help," not
"sampling strategy never matters" or "the model cannot read ASL under any
sampling scheme."

## Files in this directory

- `config_or_metadata.json` — experiment design, both arms' full config.
- `design_check.json` — LOCAL-ONLY (no model calls) per-clip timestamp
  comparison, frame-count/ordering validation, and the pre-flight call/frame
  estimate, produced by `design_check.py` before any inference.
- `predictions/` — the 12 new Arm-B (uniform) prediction JSONs. Arm A's
  predictions are read directly from `curify_gemini_3_6_2026_09_04/predictions/`
  and are not copied here.
- `paired_results.csv` / `.json` — per-clip WER for both arms, deltas, and
  descriptive-only baseline text-semantic-review fields, produced by
  `score_and_report.py`.
- `inspectors/` — one HTML page per clip (adaptive timeline+thumbnails vs.
  uniform timeline+thumbnails, side by side) plus `index.html`, produced by
  `build_comparison_inspector.py`. No model call; reuses (imports) the
  existing Phase-1 inspector's own thumbnail/timeline-rendering helpers.
- `design_check.py`, `run_uniform_arm.py`, `score_and_report.py`,
  `build_comparison_inspector.py` — the four scripts that produced everything
  above, run in that order.
