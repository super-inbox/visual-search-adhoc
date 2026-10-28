# R03 partial transcription: offline regression

**Status:** offline design and regression analysis for [PROGRESS_REVIEW.md](PROGRESS_REVIEW.md) item 2.
- No Gemini or other model call. No network.
- No production code changed. Nothing deployed.
- Everything below replays the responses saved by the 2026-10-27 production evaluation.

Script: [`r03_partial_regression.py`](../../experiments/p0-2026-10-28/r03_partial_regression.py).
Results: [`r03_partial_regression.json`](../../experiments/p0-2026-10-28/results/r03_partial_regression.json) (a rerun is
byte-identical).

## Evidence used

| Input | Identity |
|---|---|
| Saved R03 run | `asl-eval/production_45/raw/R03.json`, sha256 `e94dbe1b…`: 2 calls, raw text, usage, latency |
| R03 video | `G06Irzcwxiw_5-1-rgb_front.mp4` (10.18 inspection-sheet copy), sha256 `76b1f143…` |
| Production code | curify-studio `4220e03c`, `asl_utils.py` sha256 `90df9563…`: the same read-only export as 10/27, loaded by path, not modified |
| Pipeline caller | `pipelines/asl_pipeline.py` from the same export, sha256 `b21b0331…`. **Read only; its branch logic is mirrored, not executed** |
| Quota classifier | the 10/27 wrapper's mirror of `imagen_service.is_quota_exhausted`: substring match on `RESOURCE_EXHAUSTED`, `429`, `spend cap`, `quota`, `QUOTA`. The real `imagen_service.py` is not in the export |

**How the replay was checked.**
- The fake client returns the two saved `raw_text` values in call order.
- Production `transcribe_asl` ran on the real R03 video, and its motion probe chose **the same 30 frame timestamps** as
  the recorded run.
- Batch sizes were 24 + 6 as recorded, and the output was exactly `"I know now."` with `error=None`.
- So the analysis below runs on production's real code path, not on a re-implementation.

## 1. The malformed condition

Batch 0 (24 frames, `finish_reason=STOP`, 10,546 tokens, 17.3 s) returned:

```
    {
      "start": 3.21,
      "end": 4.04,
      "text": "Support each other."
    ,                       <- line 7: the '}' closing segment 1 is missing
    {                       <- line 8 col 5: parser is still inside segment 1 and expects a property name
      "start": 5.44,
```

`json.loads` raises `JSONDecodeError: Expecting property name enclosed in double quotes: line 8 column 5 (char 110)`.

Production then tries its fallback, `re.search(r"\{.*\}", raw, re.S)`. That greedy span is the **whole text**, so the
fallback fails the same way.

Apart from the missing brace, the reply is complete:
- 4 segments with 4 texts;
- `confidence` and `notes` fields;
- normal `STOP`.

It is not truncated.

## 2. Current production behaviour (policy A)

In `transcribe_asl`, the parse exception is caught by the same `except Exception` that handles network errors:
- The batch is skipped.
- A note `batch 0: JSONDecodeError: …` is appended.
- `transport_error = True` is set.

Then at the end:
- `had_transport_error = transport_error and not segs` is **False**, because batch 1 produced a segment.
- `error = None if segs else …` is **None**, so the parse note is discarded.

**Result for R03:**
- The output is `segments=[13.11–14.60 "I know now."]`, with `error=None`, `had_transport_error=False` and
  `quota_exhausted=False`.
- `asl_pipeline` treats it as a **normal completed transcript**.
- No field anywhere says that 1 of 2 batches (24 of 30 frames, 3.2–12.8 s of the clip) was lost.
- The only flags the pipeline writes are `asl_unverified` and `review_required`, which are always set, and
  `asl_low_confidence`, which comes only from density or repetition.

**So policy A must not count as full success, and today it cannot be told apart from one.**

I replayed the same code on scenario fixtures (synthetic placeholder texts, same video):

| Scenario | Production result | Pipeline (mirrored) | Problem |
|---|---|---|---|
| S1 all batches parse | text, `error=None` | completed | — |
| **S2 R03 as recorded** | `"I know now."`, `error=None` | **completed** | silent loss of 1/2 batches |
| S3 all batches malformed | no segments, `had_transport_error=True` | generic Exception → **queue re-runs the whole video** | parse failure mislabelled as transport |
| S4 valid empty, with notes | `error=notes` | NoSigningDetectedError | correct |
| S4b valid empty, no notes | `error=None` | NoSigningDetectedError | correct |
| S5 all transport errors | `had_transport_error=True` | queue retry | correct |
| S5b one transport error, one valid | text, `error=None` | **completed** | silent partial, as in R03 |
| **S6 top-level `[]` reply** | **`AttributeError: 'list' object has no attribute 'get'`** escapes `transcribe_asl` | unhandled | `data.get` is outside the `try` |
| S7 parse error at char 429, all batches | `quota_exhausted=True` **with the copied quota check** | "service hit its capacity limit" | **potential only**: the copied check substring-matches `429` in a JSON error message. See below |
| S8 a segment missing `end` | that segment silently dropped, text from the rest | completed | silent partial at segment level |

**Confidence of these findings:**

- **Confirmed in offline replay** of the real production `asl_utils.py`:
  - the saved R03 malformed response reproduces the silent partial loss (S2);
  - all-malformed batches are classified as a transport-style failure (S3);
  - a bare `[]` reply raises `AttributeError` (S6);
  - segment-level and one-transport-one-valid losses are equally silent (S8, S5b).
- **Potential, needs current production-code verification:**
  - a parse error whose message contains `429` may be mistaken for quota exhaustion (S7).
  - This was shown only with the 10/27 wrapper's **copy** of the quota check. The real `imagen_service.py` was not in
    the export and was not read, so this is **not confirmed** for the current production code.

## 3. Proposed status taxonomy (policies B and C)

**Per-batch outcome**, recorded for every attempt:

| Outcome | Meaning |
|---|---|
| `ok` | Strict JSON, schema-valid, ≥ 1 non-empty segment |
| `valid_empty` | Schema-valid reply with `segments: []`. The model answered "nothing readable here" |
| `parse_failure` | A response arrived but is not usable: malformed JSON (after the existing code-fence fallback), top level not an object, `segments` missing or not a list, or `finish_reason` other than STOP (`MAX_TOKENS` = truncated) |
| `transport_failure` | No response: exception from the client call (timeout, connection, 5xx, 429 rate limit, quota / spend cap, auth). **Only these** go through `is_quota_exhausted`, and it is applied to the provider exception, never to a parse error message |

**Video status**, decided after the retry policy:

| Status | When it applies |
|---|---|
| `success` | **Every** batch ends `ok` or `valid_empty`, ≥ 1 segment overall, and no segment was rejected by validation |
| `no_signing_detected` | Every batch ends `valid_empty`. This is the model's settled answer; it is not retried |
| `partial` | ≥ 1 batch valid **and** ≥ 1 batch failed (parse or transport) after retries, **or** all batches valid but ≥ 1 segment rejected (e.g. missing `end`). The text may even be empty, e.g. when the valid batches were empty; it is still not `no_signing_detected` |
| `parse_failure` | No batch valid, and all failures are parse failures |
| `transport_failure` | No batch valid and ≥ 1 transport failure, so the provider path itself is unhealthy. `quota_exhausted=true` only when every batch's final failure is a quota error |

**Invariant:** `success` requires every batch to have parsed strictly. A parse error, or a repaired batch (§4), can never
produce `success`. The reference implementation asserts this.

**Pre-model errors** (video missing, no frames) keep the existing `error` path. They are outside this batch-level
taxonomy; an `input_failure` status could be added later.

**Machine-readable result (policy B).** This is R03 under the proposed policy with no retry, as produced offline:

```json
{
 "status": "partial",
 "quota_exhausted": false,
 "batches_total": 2, "batches_succeeded": 1, "batches_failed": 1,
 "retry_calls": 0, "rejected_segments": 0,
 "failures": [{"batch": 0, "final": "parse_failure",
   "attempts": [{"attempt": 0, "outcome": "parse_failure",
     "detail": {"kind": "malformed_json", "retryable": true,
       "message": "Expecting property name enclosed in double quotes: line 8 column 5 (char 110)",
       "pos": 110, "raw_len": 445},
     "usage": {"tokens": 10546, "latency_s": 17.285}}]}],
 "segments": [{"start": 13.11, "end": 14.6, "text": "I know now.", "batch": 1, "recovered_by_repair": false}],
 "text": "I know now."
}
```

**What the pipeline should do with `partial`:**
- Persist `status`, the batch counts and the failed time ranges into `runtime_config` (e.g. `asl_partial`,
  `asl_failed_batches`).
- Show a stronger UI warning than `asl_low_confidence`.
- Do **not** trigger a whole-video queue retry; the batch retry in §5 has already happened.

## 4. Deterministic syntactic recovery (policy D)

**Search.**
- I tried every single-character edit of the malformed reply: insertion, deletion or substitution of any printable
  ASCII character at any position, **87,318 variants** in total.
- Each was parsed with Python's JSON parser.
- Each was then checked against the production prompt's own schema:
  - top-level keys a subset of `{segments, confidence, notes}`;
  - every segment exactly `{start, end, text}`;
  - numeric `0 ≤ start ≤ end`;
  - string text;
  - no duplicate keys.

**Results:**

| Criterion | Distinct parse results | Which |
|---|---|---|
| JSON grammar only | **2** | (a) insert `}` after `"Support each other."` → 4 segments; (b) **delete the second segment's `{`** → 3 segments, the first with duplicate `start`/`end`/`text` keys (Python keeps the last, so "Support each other." would silently vanish) |
| Grammar + schema | **1** | (a) only. 11 equivalent edits (insert or substitute `}` at any of the whitespace positions between `"Support each other."` and `,`) all give the same structure |

**The recovered structure:**

| start | end | text |
|---|---|---|
| 3.21 | 4.04 | Support each other. |
| 5.44 | 7.56 | The community helps people. |
| 8.65 | 10.43 | You are welcome to join. |
| 10.73 | 12.82 | I want to include you, you know. |

Plus `confidence: "high"` and `notes: ""`.

**Why this is deterministic and adds no content:**
- The only change is one structural character, `}`.
- Every string and number is the model's own token, checked verbatim against the raw text.
- No reference, no model and no guess is involved.
- The result is the **unique** schema-valid structure within one edit.

The production-safe form of the rule, also implemented as `unique_repair`, gives exactly 1 result for R03:
- Search only insertions or deletions of the structural characters `{}[],:`.
- Accept only when there is exactly one schema-valid result.
- Otherwise do not repair.

**Is it safe?** For this instance, yes in the strict syntactic sense. As a production policy, only as a **guarded
fallback**:
- **Grammar alone is ambiguous here.** It also allows the duplicate-key reading, which loses a segment. Safety depends on
  the schema check and the uniqueness check.
- **It rests on one example.** The 10/27 run had one malformed reply in 57 calls. Other malformations (truncation, two
  errors, unescaped quotes) may have zero or several candidate repairs. They must fall through to `parse_failure`.
- **It does not raise the status.** A repaired batch has `final="recovered_by_repair"`, each of its segments carries
  `recovered_by_repair: true`, and the video stays **`partial`**. The offline run gives exactly that for R03.

**Recommendation:** PARTIAL + controlled retry is the primary policy. The unique structural repair is optional and runs
only after the retry also fails, and it is surfaced as `partial`. Do not enable it until more malformed replies have
been collected and checked against the rule.

## 5. Controlled retry design (policy E, no call made)

- **Scope:** retry **only the failed batch**, with the same frames, prompt, model and config. Never the whole video.
  Batches already accepted are kept.
- **Limits:**
  - `MAX_BATCH_RETRIES = 1` (one retry per failed batch).
  - `MAX_VIDEO_RETRIES = 2` (at most two retry calls per video).
  - More than two failing batches suggests a systemic problem, so stop and report.
- **Failures that qualify for a retry:**
  - `parse_failure`: malformed JSON, non-object or schema-invalid top level, `finish_reason=MAX_TOKENS`;
  - transient `transport_failure`: timeout, connection, 5xx, 429 rate limit **that is not** quota or spend cap. Use a
    short jittered backoff for these, and none for parse failures.
- **Failures that do not qualify:**
  - `ok` and `valid_empty`;
  - quota or spend-cap errors (a retry cannot help and adds billing);
  - auth or invalid-request 4xx;
  - safety blocks and other non-STOP finish reasons.
- **Cost recording:** every attempt is logged with:
  - `attempt` index, `outcome`, error kind and message;
  - `prompt` / `output` / `thoughts` / `total` tokens and model version.

  The video totals carry `retry_calls`, `retry_tokens` and `total_tokens`, so retry spend is never hidden inside the
  first-attempt numbers.
- **Latency recording:** per-attempt `latency_s`, plus `retry_latency_s` and wall-clock `total_latency_s` for the video.
  Backoff sleep is recorded separately.
- **If the retry also fails:** the batch stays `parse_failure` or `transport_failure`. The video becomes `partial` if any
  batch is valid; otherwise `parse_failure` or `transport_failure` (§3). `success` is unreachable while any batch has
  failed (the invariant).
- **Determinism caveat:** at temperature 0 a retry may return the same malformed reply. That is why there is a single
  retry, and why the outcome is recorded rather than assumed. The success rate of a retry cannot be measured offline.

## 6. Expected cost and latency

From the saved 10/27 records (45 cases, 57 calls, 457,707 tokens):
- **Malformed-reply rate:** 1 of 57 calls (1.75 %). n = 1, so this is not a reliable rate.
- **R03 batch retry**, assuming it costs like the original batch 0: **+1 call, about +10.5k tokens** (6,663 prompt +
  3,694 thinking + 189 output). That is **+2.3 %** of the whole 45-case run's tokens.
- **R03 latency:** the batches run sequentially, so wall-clock time grows by about the batch latency: 27.7 s → about
  45 s (+17.3 s).
- **Worst case per video:** +2 calls. Bounded by `MAX_VIDEO_RETRIES` and the existing 240-frame (10-batch) cap.
- **Compared with today:**
  - The current path never retries a partial.
  - When **all** batches fail to parse, the current path misclassifies the job as transport and the queue re-runs the
    **whole** video. For R03 that would be about 13.9k tokens per re-run. The pipeline's own comment describes repeated
    whole-job recognitions.
  - Per-batch retry is cheaper than a whole-video re-run in every failing case.
- Dollar cost is not computed here. Multiply the recorded tokens by the price in effect, and note that thinking tokens
  dominate output tokens on these calls.

## 7. Regression tests production should add

The reference policy passes all 14 offline (`policy_tests` in the JSON):

| # | Fixture | Expected |
|---|---|---|
| T1 | all batches parse | `success` |
| T2 | one of two batches malformed (R03 golden fixture), no retry left | `partial`, 1/1 succeeded/failed, error metadata kept |
| T3 | all batches malformed, retry also malformed | `parse_failure` (not transport, not quota) |
| T4 | all batches valid with `segments: []` | `no_signing_detected` |
| T5 | all batches 5xx/timeout, retry fails too | `transport_failure` |
| T6 | R03 batch 0 malformed, retry valid | `success`, `retry_calls=1`, retry usage recorded |
| T7 | R03 batch 0 malformed, retry malformed again | `partial` |
| T8 | quota / spend-cap exception | `transport_failure` + `quota_exhausted`, **no retry** |
| T9 | malformed JSON whose error message contains `429` | `parse_failure`, `quota_exhausted=false` |
| T10 | top-level `[]` reply | no crash. Batch `parse_failure` → `partial` |
| T11 | a segment missing `end` | `partial`, `rejected_segments=1` |
| T12 | one batch malformed, the other timing out | `transport_failure` |
| T13 | truncated reply (`MAX_TOKENS`) then a valid retry | `success` |
| T14 | three failing batches | at most 2 retry calls, then `parse_failure` |

Two tests should also be added on the current code, so the fix is visible:
- **Golden replay of `R03.json`:** the current code returns a full-looking result. This test should fail until partial
  status exists.
- **S6:** a top-level `[]` reply currently raises `AttributeError`.

Tests T6, T7, T10 and T13 use synthetic placeholder texts. No transcript text was invented for R03.

## 8. Effect on the 45-case production score

**No change.** The 45-case score measures what production actually returned, and R03 is already marked PARTIAL in
[PRODUCTION_45_CASE_EVAL.md](../2026-10-27/PRODUCTION_45_CASE_EVAL.md). The saved corpus numbers reproduce exactly (chrF
9.2733, WER 98.25).

For sizing only: had R03 kept the recovered batch 0, its text would be the 4 recovered segments followed by
"I know now." (22 words). Then:
- R03 sentence chrF would be 3.30 → 15.43.
- 45-case corpus chrF would be **9.27 → 9.70**.
- Length ratio would be 0.376 → 0.387.

This is a hypothetical alternative policy, scored with automatic metrics only. It says nothing about whether the
recovered text is a correct translation, and it does not change the gap to Uni-Sign (18.22 on the same windows).

## 9. Limitations

- **One malformed example.** The repair rule and the error rate rest on n = 1.
- **Pipeline not executed.** The pipeline decision and quota classifier are mirrors. Production's real
  `imagen_service.is_quota_exhausted` must be checked before the S7 / T9 finding is treated as confirmed.
- **Retry not measured.** Whether a retry fixes the batch is unknown offline.
- **No product decision taken.** The taxonomy and retry policy are proposals. No production code, prompt or config was
  changed. Asking Gemini for structured output (`response_schema`) could reduce malformed replies, but that is a config
  change and was not evaluated.
