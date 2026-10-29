# P0-2 Round 1: same-input OpenAI vs Gemini, pre-registration

**Status:** frozen before any API call. No OpenAI, Gemini or Uni-Sign call was made. No production change, no
deployment. No model output exists for this design yet.

**Archival note (2026-10-29):** this protocol was executed unchanged on 2026-10-29. The result is in
[`P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md`](../2026-10-29/P0_2_OPENAI_VS_GEMINI_ROUND1_RESULT.md): frozen verdict C,
pause. The text below is the pre-registration as frozen before execution, with the 2026-10-29 additions made before
the first model request (model freeze, harness choices, capability smoke test).

Script: [`p0_2_openai_preregister.py`](../../experiments/p0-2026-10-28/p0_2_openai_preregister.py).
Protocol and estimates: [`p0_2_openai_preregistration.json`](../../experiments/p0-2026-10-28/results/p0_2_openai_preregistration.json).
Inventory and pilot frame manifest: [`p0_2_subset_manifest.json`](../../experiments/p0-2026-10-28/results/p0_2_subset_manifest.json).

Source plan: NEXT_P0_PLAN (2026-10-28) P0-2, "第一轮：只换模型". Round 1 changes only the model.

## Bottom line

- **Pilot:** 24 How2Sign v2 clips from outside the 45-case dev set, chosen by a deterministic rule that uses input-side
  fields only. The other 23 eligible clips are held back as a reserve for confirmation.
- **This is not a clean holdout.** All 47 eligible clips have prior research exposure:
  - Gemini (Curify, 2026-09-04, all 128 clips);
  - Uni-Sign runs, P0-12, P0-13;
  - the P0-15 fusion dev split.

  It is an independent comparison subset for P0-2, not untouched data.
- **Input recipe:** the production Gemini recipe from curify-studio `4220e03c`, frozen down to per-frame JPEG hashes.
  The frames are byte-identical across two extraction passes.
- **OpenAI model: FROZEN as `gpt-6.1-sol`** (2026-10-29, §4).
  - `models.retrieve("gpt-6.1-sol")` succeeded and returned the same ID. No generation was involved.
  - The fallback `gpt-6-astra` was not checked and is not selected.
  - The docs list no dated snapshot, so whether `gpt-6.1-sol` is fixed or an alias is not stated.
- **Calls:**
  - 29 OpenAI calls and 29 Gemini calls for the primary run;
  - plus 29 Gemini calls if the optional noise-floor repeat is approved.
- **Needed before execution:**
  - spend approval;
  - renewed approval of the Gemini credential source.

  Done 2026-10-29: the harness review (choices frozen, §6) and the capability smoke test (PASS, `detail: "high"`
  frozen, §4).

## 1. Candidate benchmark pool

How2Sign v2: 128 clips from the official test split, one per source video (128 distinct source videos). The freeze
fingerprint is `16c41282…`.

| Group | Clips | Status |
|---|---|---|
| Dev set (R01–R45, heavily studied) | 45 | excluded |
| Outside the 45 | 83 | — |
| … of which in P0-15's **sealed final split** | 36 | excluded |
| H18/H19 (How2Sign val) | 0 | not applicable; the guard passes for all 128 clips |
| **Eligible** | **47** | all in the P0-15 fusion dev split |

**P0-15 sealed final split:** P0_15_RESULTS says it is "untouched and sealed for a future P0" and "can be reused
once" under a new frozen plan. P0-2 is not that plan, so I excluded it at source-video level. This includes the merged
unit `G3di9jJTqDs+f_zna_wG3zo`.

**Video availability:**
- In this worktree, only the 45 dev videos are on disk.
- All 128 videos are present in the sibling worktree `visual-search-adhoc-asl-task-c`. Each one matches
  `FREEZE_CHECKSUMS.sha256` (verified by sha256), and that worktree's checksum file is identical to this one.
- Production-style frame extraction is reproducible for every eligible clip.

**Prior exposure of the 47 eligible clips** (from committed artifacts that name each clip; per-clip study folders are
in the inventory):

| Exposure | Clips |
|---|---|
| Curify/Gemini run, 2026-09-04 (all 128; older production build; outputs are not committed in this repo) | 47 |
| Uni-Sign runs (9.2 baselines, P0-11, 10.13, 10.14 and others) | 47 |
| P0-12 | 47 |
| P0-13 | 47 |
| P0-15 fusion dev (fitted on) | 47 |
| Manual SignCaption or human review folders | 5 |

None of this was used for selection. No reference text, model output or text-derived heuristic tag was read by the
selection code.

## 2. Pilot subset

**Size: 24 pilot clips and 23 reserve clips, splitting the 47 eligible clips in half.**
- The pool is small, so a larger pilot would leave nothing to confirm on.
- The plan says the pilot is for screening and conclusions come from a separate confirmation set.
- 24 paired cases cost 29 calls per arm, which is cheap.
- 24 is too few to prove a small effect. The decision rule (§9) therefore asks for a large, consistent gain, not
  significance on a small one.

**Rule** (deterministic, one draw, no redraw):
1. Sort the 47 clips by:
   - signer proxy (the How2Sign `-N-` suffix, the same proxy P0-15 used);
   - then single-batch before multi-batch (production batch count);
   - then `sha256("P0-2-R1-2026-10-28|" + clip_id)`.
2. Positions 0, 2, 4, … are the pilot; positions 1, 3, 5, … are the reserve.

**One revision before the freeze:** the first rule stratified on batch count only and gave signer proxy 8 eleven pilot
clips against five in the reserve. I replaced it once, before any model call, using input-side fields only.

**Balance:**

| | Pilot | Reserve |
|---|---|---|
| Clips | 24 | 23 |
| Single / multi-batch | 19 / 5 | 18 / 5 |
| Signer proxy 1 / 2 / 3 / 8 / 10 | 2 / 4 / 6 / 8 / 4 | 2 / 4 / 6 / 8 / 3 |
| Probe duration, median (range) | 5.25 s (1.0–23.5) | 5.0 s (1.25–20.5) |
| Active-motion ratio, median | 0.648 | 0.643 |
| Calls per arm | 29 | 28 |

**Pilot clips** (each from a different source video):

| Clip | Source video | Signer proxy | Official s | Frames | Batches | Active ratio | Manual-review exposure |
|---|---|---|---|---|---|---|---|
| `-g0sqksgyc4_3-2-rgb_front` | -g0sqksgyc4 | 2 | 5.35 | 24 | 1 | 0.524 | yes |
| `FZCEymcpq7I_14-1-rgb_front` | FZCEymcpq7I | 1 | 9.81 | 24 | 1 | 0.658 | yes |
| `FZd8Iv9ACVw_12-8-rgb_front` | FZd8Iv9ACVw | 8 | 11.05 | 24 | 1 | 0.651 | no |
| `Fz-N1S0swh8_2-8-rgb_front` | Fz-N1S0swh8 | 8 | 2.27 | 24 | 1 | 0.625 | no |
| `FzAIlhumvMA_4-2-rgb_front` | FzAIlhumvMA | 2 | 4.62 | 24 | 1 | 0.235 | no |
| `FzQPg4aqNYc_13-1-rgb_front` | FzQPg4aqNYc | 1 | 6.35 | 24 | 1 | 0.640 | yes |
| `FzoUVr98JmQ_6-8-rgb_front` | FzoUVr98JmQ | 8 | 8.80 | 24 | 1 | 0.647 | no |
| `G05uFub3YFc_9-2-rgb_front` | G05uFub3YFc | 2 | 17.49 | 34 | 2 | 0.652 | yes |
| `G1hb5HugzVk_2-8-rgb_front` | G1hb5HugzVk | 8 | 21.80 | 43 | 2 | 0.651 | no |
| `G23G21G49dk_14-2-rgb_front` | G23G21G49dk | 2 | 15.49 | 29 | 2 | 0.639 | no |
| `G2T2WCuU39Y_5-10-rgb_front` | G2T2WCuU39Y | 10 | 23.73 | 47 | 2 | 0.649 | no |
| `G3FhmHz_7hs_20-10-rgb_front` | G3FhmHz_7hs | 10 | 5.29 | 24 | 1 | 0.650 | no |
| `fzOH00UZg84_30-8-rgb_front` | fzOH00UZg84 | 8 | 23.62 | 47 | 2 | 0.649 | no |
| `fzcsY2gm7t0_8-8-rgb_front` | fzcsY2gm7t0 | 8 | 4.00 | 24 | 1 | 0.667 | no |
| `fzrJBu2qsM8_5-10-rgb_front` | fzrJBu2qsM8 | 10 | 1.13 | 24 | 1 | 0.250 | no |
| `fzueHkUDyhE_1-8-rgb_front` | fzueHkUDyhE | 8 | 5.51 | 24 | 1 | 0.571 | no |
| `g0Abwige7MQ_2-8-rgb_front` | g0Abwige7MQ | 8 | 4.51 | 24 | 1 | 0.647 | no |
| `g1HvmBOR7Y4_15-3-rgb_front` | g1HvmBOR7Y4 | 3 | 5.60 | 24 | 1 | 0.619 | no |
| `g1vUH8Iy4vw_8-3-rgb_front` | g1vUH8Iy4vw | 3 | 4.77 | 24 | 1 | 0.667 | no |
| `g1z6HOJ0yRw_2-3-rgb_front` | g1z6HOJ0yRw | 3 | 4.71 | 24 | 1 | 0.667 | no |
| `g2ELiaFjKfs_3-10-rgb_front` | g2ELiaFjKfs | 10 | 4.87 | 24 | 1 | 0.667 | no |
| `g2QdwYqm8pg_13-3-rgb_front` | g2QdwYqm8pg | 3 | 4.70 | 24 | 1 | 0.333 | no |
| `g3jQ5ecjGz8_6-3-rgb_front` | g3jQ5ecjGz8 | 3 | 5.47 | 24 | 1 | 0.619 | no |
| `g3ushtMfLiY_2-3-rgb_front` | g3ushtMfLiY | 3 | 4.67 | 24 | 1 | 0.667 | no |

**Reserve:** 23 clips, listed in the JSON. Round 1 must not touch them.

## 3. Frozen input recipe

**Source of truth:** curify-studio `4220e03c`, `curify_background/app/utils/asl_utils.py` (sha256 `90df9563…`).
- This is still `origin/main` as of 2026-10-28.
- It is the same file the production_45 run used.
- Prompt sha256: `ea8c5cb1…`.

| Item | Frozen value |
|---|---|
| Window | the whole How2Sign v2 clip (official sentence window, original timing, full 1280×720 frame) |
| Motion probe | 4 fps, 160 px grayscale, mean absolute frame difference |
| Runs | 5-tap smoothing; idle threshold = max(35th percentile, 2.0) |
| Budget | round(duration × 2.0), clamped to 24–240 frames |
| Allocation | across active runs by motion-energy share; ≥ 2 frames per run; sampled at (i + 0.5)/n inside each run; even trim to the budget |
| Extraction | one ffmpeg call per frame, `-ss t.3f` before `-i`, `scale=512:-2`, `-q:v 3` JPEG; frames are 512×288 |
| Labels | text part `[t=X.XXs]` before each image, from production's file-name regex |
| Batching | consecutive groups of 24 frames, in time order, each an independent call |
| Task wording | production `_PROMPT`, verbatim |
| Output fields | `segments[{start, end, text}]`, `confidence`, `notes` |
| Post-processing | drop empty segments, sort by start, merge adjacent duplicates (≤ 1.0 s gap), degenerate flag at 3 repeats; text = segments joined |

**Pilot manifest** (per clip):
- source video ID and sha256;
- source window;
- budget;
- exact timestamps and seek strings;
- 656 frames, with file name, label, size and sha256 for each;
- 29 batches, with frame range and an input hash for each.

The batch input hash is sha256 over the prompt hash plus every label and frame hash.

**Extraction check:** both passes gave byte-identical JPEGs for all 656 frames, and no frame was dropped. ffmpeg
8.1.1 is recorded. The frames themselves stay in scratch and are not committed. The run harness must verify each
frame's hash before every call.

## 4. OpenAI model selection: FROZEN, `gpt-6.1-sol` (verified 2026-10-29)

- **Frozen model ID:** `gpt-6.1-sol`.
- **Fallback:** `gpt-6-astra`, untested and not selected. It was to be checked only if the preferred model was
  unavailable.
- **Not used as primary:** `gpt-4o`.

**Credential source (user-approved 2026-10-29):** `OPENAI_API_KEY` from the user-approved local env file, outside the
repo (its path is not committed). Only that variable is loaded, into the harness process. The value is never printed, logged or written.

**SDK:**
- An isolated research venv outside the repo, Python 3.11.7, with `openai==3.41.0` pinned. It has both
  `client.responses.create` and `client.models.retrieve`.
- Production dependencies are untouched. Production still pins `openai==1.63.2`, which predates the Responses API.

**Account access check:** one `client.models.retrieve("gpt-6.1-sol")` call at 2026-10-29T07:19:51Z, with no retries.

| Requested | Returned ID | Result | `owned_by` | `created` |
|---|---|---|---|---|
| `gpt-6.1-sol` | `gpt-6.1-sol` | success | `system` | 1790552874 |

This was a metadata call only: no generation, no Responses API call, no images, no benchmark data.

**Snapshot caveat:** the docs list no dated snapshot. The returned ID equals the request, but the docs do not say
whether it is a fixed version or an alias. The per-call model-ID check below is the guard.

**What a no-generation check can and cannot show:** `models.retrieve` returns only `id`, `created` and `owned_by`. It
can confirm access and the exact ID. It cannot confirm image input, detail behaviour, temperature or usage fields:
those rest on the docs until the first real call.

**Documented capabilities** (models pages, vision, reasoning and structured-outputs guides, read 2026-10-29):

| | `gpt-6.1-sol` | `gpt-6-astra` |
|---|---|---|
| Snapshot | only `gpt-6.1-sol`; no dated ID; alias vs fixed not stated | only `gpt-6-astra`; same |
| Image input | yes (text and image in, text out) | yes |
| Multiple images per request | yes (guide: up to 1,500 images, 512 MB) | yes |
| Responses API | supported | supported |
| Structured outputs | listed (JSON mode not mentioned on the page) | listed (same) |
| Image `detail` values | **not documented for this model** | `low` (fits 512×512), `high` (≤ 2,500 patches), `original`, `auto` = `original`; 32 px patches, ×1.2 |
| Temperature | not documented | not documented |
| Reasoning effort | low / medium / high / xhigh / max; default medium; no `none` | low … max; `none` → HTTP 400; default not stated |
| Price per 1M tokens (input / cached / output) | $2 / $0.10 / $10 | $10 / $1 / $50 |

**Usage fields** (Responses API):
- `input_tokens`;
- `input_tokens_details.cached_tokens`;
- `output_tokens`;
- `output_tokens_details.reasoning_tokens`;
- `total_tokens`.

Reasoning tokens are billed as output tokens.

**Capability smoke test (2026-10-29): PASS.** Exactly one Responses API call, with no retry. The image was a locally
generated synthetic 512×288 JPEG (white canvas, one rectangle, one ellipse). It contains no photo, no ASL and no pilot,
reserve or benchmark content.

- **Request:** the benchmark structure.
  - Model `gpt-6.1-sol`, one user message: an `input_text` instruction, an `input_text` label `[t=0.00s]`, and an
    `input_image` data URL with `detail: "high"`.
  - `text.format: json_object`, `store: false`, temperature and reasoning omitted.
  - `openai==3.41.0`, `max_retries=0`, 60 s timeout.
- **Verified:**
  - request accepted, and the returned model was exactly `gpt-6.1-sol`;
  - image input and `detail: "high"` were accepted;
  - status `completed`, no refusal;
  - the reply parsed as a JSON object;
  - the reported reasoning effort was `medium`.
- **Usage fields returned:** 205 input tokens (0 cached), 13 output tokens (0 reasoning), 218 total.
  - The 205 input tokens are consistent with about 173 image tokens (144 patches × 1.2) plus about 30 text tokens. The
    API does not report image tokens separately.
- **Latency and cost:** 3.76 s. Cost is about $0.0005 (ESTIMATE ONLY, docs prices).
- **The answer text was not stored.** Only its JSON-object validity was checked.

**Frozen as a result:** `detail: "high"`, the Responses request structure above, the JSON-object output path, and the
usage fields listed above.

**Still open:** temperature support is not documented, and the request omits it (§5).

**Requirements kept from the original pre-registration:**
- the returned model ID equals the requested ID on every call, or the run is invalid;
- the ID and call date are logged on every request.

**Image tokens per frame** (documented, not verified by a call):
- 144 patches × 1.2 ≈ 173.
- Gemini for comparison: about 258 per frame (observed in production_45 usage).

## 5. Prompt adaptation

**Prompt:** the production `_PROMPT` is used verbatim in both arms.

**Request structure for OpenAI** (Responses API, `POST /v1/responses`, as you directed on 2026-10-29):
- `input` holds one user message;
- the prompt as an `input_text` part;
- then, for each frame, an `input_text` part with its label, followed by an `input_image` part (a
  `data:image/jpeg;base64,…` URL of the frozen bytes, `detail: "high"`).

This keeps the same order as Gemini's parts.

**Unavoidable API adaptations:**
- **Endpoint:** the Responses API instead of the Chat Completions endpoint used by production's dormant
  `_call_vlm_openai`.
- **Message format:** `input_text` / `input_image` parts instead of Gemini's `Part.from_text` / `Part.from_bytes`.
- **JSON mode:**
  - OpenAI: `text.format: {"type": "json_object"}`;
  - Gemini: `response_mime_type: application/json`;
  - neither applies a schema;
  - the prompt already says "STRICT JSON".
- **Image detail:** `detail: "high"` instead of production's dormant `"low"`. This keeps the 512 px frame. It is frozen
  and was verified for `gpt-6.1-sol` by the 2026-10-29 capability smoke test (§4).
- **Temperature:** omitted. Neither candidate documents support for it, and both are reasoning-only. This is a recorded
  difference from Gemini's temperature 0.
- **Reasoning effort:** not set, so the model default applies (documented as medium for `gpt-6.1-sol`). Production
  sets no Gemini thinking config either. The effective value is recorded from the response.
- **Storage:** `store: false`.
- **Timeout:** 60 s, mirroring Gemini's.
- **Incomplete responses:** `status: "incomplete"` is recorded with its reason. Any returned text is parsed as usual;
  no text counts as a parse failure.

**Not set:** `instructions` / system message, `max_output_tokens`, seed, tools, top_p, previous response ID.

**Parser:** both arms use production `_call_vlm` parsing:
1. `json.loads`;
2. otherwise the first `{…}` span;
3. otherwise a parse failure.

The dormant OpenAI path parses with `json.loads` only; I recorded this difference. A refusal or null content counts as
a parse failure.

**Harness:** the harness loads production `asl_utils` read-only and replaces only:
- `_extract_frames`, which returns the frozen frames;
- `_call_vlm_openai`, in arm O.

The batch loop, segment parsing, dedup and flags run unchanged for both arms.

**No added information:** the model gets no reference text, answer, Uni-Sign prediction, clip or video name, scoring
hint, audio or system message.

## 6. Failure and retry policy

**Batch outcomes:**

| Outcome | Meaning |
|---|---|
| `ok` | at least one valid non-empty segment |
| `valid_empty` | parsed, but no valid non-empty segment |
| `parse_failure` | response received but not parseable (includes refusal/null content) |
| `transport_failure` | the call raised (timeout, connection error, 5xx, 429 rate limit) |
| run-blocking | auth error, model not found, insufficient quota or spend cap, or HTTP 400/422 request configuration error → halt the whole run |

**Case status (R03-aware):**

| Status | Rule |
|---|---|
| `success` | every batch is `ok` or `valid_empty`, and at least one segment |
| `no_signing_detected` | every batch is `valid_empty` |
| `partial` | at least one failed batch and at least one segment; never counted as success |
| `parse_failure` | no segment, and at least one batch `parse_failure` |
| `transport_failure` | no segment, and every failed batch is a `transport_failure` |

**Denominator:** all 24 cases in every arm. A case without text is scored as the empty string. Production's result is
not altered; a pass-through wrapper records the per-batch outcomes.

**Retries:**
- **Primary:** none. Each batch gets one attempt, as in production.
- **Secondary view:** after the full pass, each `transport_failure` batch may be retried once, at least 60 s later.
  - This is reported only as a separate "transport-retried" view.
  - Retry calls, tokens and latency count toward cost and latency.
- **Never retried:** `parse_failure`, `valid_empty`, `no_signing_detected`.
- **Run-blocking errors:** halt the run and score nothing from an incomplete arm. Resuming requires your approval, and
  resumed cases are flagged.

**Call order:** both arms run back to back for each case. Which arm goes first is set by hash parity
(`P0-2-R1-2026-10-28|order|clip_id`).

**Harness choices, frozen before execution (approved 2026-10-29).** These must not change after any output is seen.

1. **Call order:** even parity of `sha256("P0-2-R1-2026-10-28|order|" + clip_id)` → Gemini first; odd → OpenAI
   first. This gives 12 cases Gemini-first and 12 OpenAI-first.
2. **HTTP 400 / 422:** a run-blocking configuration error. The run halts immediately. It is never counted as a
   transport failure, and no further calls are spent.
3. **Reply that is not a JSON object:** recorded as `parse_failure`. The case stays in the denominator and the run
   continues. The batch also records `production_would_crash = true`, because production `transcribe_asl` calls
   `data.get` on the parsed value and would crash on it.

## 7. Metrics (frozen)

**Automatic:**
- corpus chrF (primary);
- BLEU-4;
- WER;
- mean length ratio;
- `loop_out` count;
- degenerate-repetition count;
- counts of success / partial / no_signing_detected / parse_failure / transport_failure / empty.

All use the P0-A frozen functions.

**Paired analysis (O − G):**
- per-case sentence chrF and WER: mean, median, wins/losses/ties (tie if |Δ| < 1);
- 95 % paired bootstrap CI of mean Δ sentence chrF:
  - 10,000 resamples, seed 20261028;
  - resampled at case level, since each case is a different source video;
  - sensitivity check: bootstrap clustered by signer proxy.

**Regression / gain:** a regression is O ≤ G − 10 sentence chrF; a gain is O ≥ G + 10.

**Content / reliability review (blind):**
- **Labels:**
  - omission of key content;
  - key-content error (entity, number, action);
  - generic or hallucinated filler;
  - fingerspelling, name or number rendered correctly (yes / partial / no / NA).
- **Procedure:** the reviewer sees the reference and the two outputs as X/Y in seeded random order. Arm names stay
  hidden until the labels are locked.
- **Reviewer:** a human. Any AI pre-annotation is labelled as AI and cannot support verdict A.
- **Automatic proxy (descriptive only):** an output repeated verbatim on 2+ different clips within one arm.

**Uni-Sign:** the committed Uni-Sign predictions for these clips go in a separate reference column, labelled "not
input-matched". They are never paired as "only the model changed".

**Not claimed:** no semantic superiority from automatic metrics. Round 1 can name a candidate. It cannot establish
semantic correctness: the 2×2 correctness table needs reliable labels or blind review.

## 8. Cost and latency

**Per-request log fields:**
- arm, requested and returned model ID, call time (UTC);
- clip, batch index, number of images, batch input hash;
- input, cached-input, output, reasoning/thinking and total tokens;
- latency, finish reason, response ID;
- attempt number, batch outcome, error class and message;
- raw response text.

**Estimates:**

| | Calls | Input volume |
|---|---|---|
| OpenAI, primary | 29 | 656 images; about 113k image tokens at the documented ×1.2 patch rate, plus about 15k text tokens |
| Gemini, primary | 29 | about 182k prompt tokens (production_45 median: 6,653 per 24-frame call) |
| Gemini, optional noise-floor repeat | 29 | same as the primary Gemini run |
| Transport retries, worst case | ≤ 29 per arm | — |

**Gemini output** (production_45 medians per call): 102 output tokens and 1,506 thinking tokens.

**OpenAI dollar cost: ESTIMATE ONLY.** It uses docs prices read 2026-10-29. Account pricing and the tokenizer are
unverified, and no inference call was made. The frozen model is `gpt-6.1-sol`; the `gpt-6-astra` rows are kept for
reference only.

**Inputs to the estimate:**
- **Input tokens:** 656 frames × 173 + 29 calls × 500 assumed text tokens ≈ 128k.
- **Output plus reasoning tokens per call:**
  - low: 1,608 (the Gemini production_45 median);
  - high: 8,040 (5×, allowing for heavier default reasoning).

| Model | Primary run, low | Primary run, high | Worst case with one retry per batch |
|---|---|---|---|
| `gpt-6.1-sol` ($2 / $10 per 1M tokens) | $0.72 | $2.59 | $5.18 |
| `gpt-6-astra` ($10 / $50 per 1M tokens) | $3.61 | $12.94 | $25.88 |

## 9. Decision rule (fixed before any output)

**Gates:**

| Gate | Pass condition |
|---|---|
| R: reliability | non-answers (empty + no_signing + parse + transport) O ≤ G + 1, **and** partial O ≤ G + 1 |
| Q: quality (automatic) | corpus chrF O − G ≥ +2.0, **and** bootstrap 95 % CI lower bound of mean Δ sentence chrF > 0, **and** corpus WER O ≤ G; if the Gemini repeat ran, the gain must also exceed \|G_repeat − G\| |
| S: safety | regressions ≤ gains, **and** generic/hallucinated outputs O ≤ G (blind review; the automatic proxy alone makes the verdict provisional) |
| C: cost/latency | median call latency O ≤ 2× G, **and** total cost O ≤ 3× G (prices verified at run time; otherwise C is unresolved) |

**Verdicts:**
- **A, replacement candidate:** R, Q, S and C all pass, and blind-review key-content errors O ≤ G. Without human
  review, the verdict is "A provisional".
- **B, local specialist candidate:** not A, R passes, and in at least one pre-specified stratum with ≥ 5 cases, O
  beats that stratum's comparator by mean Δ sentence chrF ≥ +5 and wins ≥ 2/3 of its cases. The pre-specified strata
  are:
  - multi-batch clips;
  - one signer proxy;
  - cases where Gemini gave a non-answer, a loop or a degenerate output;
  - cases where Uni-Sign gave a `loop_out` or empty output.
- **C, pause:** everything else, including any R failure whatever the quality numbers.

**"Promising enough" for Round 2:** A or B only.
- A → confirm on the 23 reserve clips with the same frozen recipe, plus blind review.
- B → Round 2 input work limited to that stratum.

No production change happens in any case. The thresholds must not change after any output is seen.

## 10. Approvals needed before execution

1. **OpenAI credential source:** approved 2026-10-29 (§4). Done.
2. **Model freeze:** done 2026-10-29: `gpt-6.1-sol`, SDK `openai==3.41.0` (§4).
3. **Gemini credential source:** renewed approval. The earlier approval covered the production_45 run only.
4. **Spend approval:**
   - 29 + 29 primary calls;
   - optionally 29 more Gemini calls for the noise-floor repeat;
   - at most one transport retry per failed batch.
5. **Run harness:** `p0_2_same_input_comparison.py`, reviewed and approved 2026-10-29. The three harness choices are
   frozen (§6).
6. **Capability smoke test:** PASS 2026-10-29 (§4). `detail: "high"` is frozen.

## Limitations

- The pool is small (47 eligible clips), and every eligible clip has prior exposure. The pilot and reserve are
  independent of P0-2, not of the research program.
- 24 cases is a screening size. The gates require large, consistent effects, not a precise estimate.
- Signer proxy is the How2Sign file-name suffix, not a verified signer ID.
- Production `_call_vlm_openai` has never been validated. The harness adapter will differ from it in endpoint
  (Responses API), model ID, `detail`, temperature, timeout and parser fallback, as listed in §5.
