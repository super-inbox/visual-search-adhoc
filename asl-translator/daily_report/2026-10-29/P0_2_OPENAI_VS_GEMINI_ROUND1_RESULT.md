# P0-2 Round 1: OpenAI `gpt-6.1-sol` vs production Gemini, same input

**Status:** primary run complete, 2026-10-29. Frozen 24-case pilot, frozen frames, frozen gates.
- Automatic metrics only. There was no blind human review, so no semantic claim is made in either direction.
- No production change, no Gemini repeat, no retry view, no Round 2.

Pre-registration: [`P0_2_OPENAI_SAME_INPUT_PREREGISTRATION.md`](../2026-10-28/P0_2_OPENAI_SAME_INPUT_PREREGISTRATION.md).
Harness: [`p0_2_same_input_comparison.py`](../../experiments/p0-2026-10-28/p0_2_same_input_comparison.py).
Scoring: [`p0_2_round1_score.py`](../../experiments/p0-2026-10-28/p0_2_round1_score.py) (written before any output
was read).
Results: [`results/p0_2_same_input/`](../../experiments/p0-2026-10-28/results/p0_2_same_input/) (`comparison.json`,
per-case files and raw responses for each provider).

## Bottom line

**Frozen verdict: C, pause.** OpenAI fails gate R (reliability), gate Q (quality) and gate S (safety), and each of
these alone forces C. Gate C also fails, narrowly, on latency; it passes on cost. No local-specialist (B) stratum
passes. **Round 2 is therefore not justified under the frozen rule.**

- **The dominant effect is abstention.** On the identical frames and prompt, `gpt-6.1-sol` returned a valid JSON
  reply with `segments: []` on 20 of 29 batches. Each carried a "cannot read the signing with reasonable confidence"
  note and mostly `confidence: low`. That leaves 15 of 24 cases as `no_signing_detected`. Gemini answered every batch,
  mostly with `confidence: high`.
  - The production prompt explicitly asks for this behaviour when the model is unsure ("say so honestly in the `notes`
    field instead of guessing").
  - These are not transport or parse failures. All 29 OpenAI calls completed.
  - Under the frozen rule, they still count as non-answers.
- **Where OpenAI did answer (9 cases), its outputs were very short.** It won 1 case, tied 1 and lost 7 on sentence
  chrF.
- **Gemini's absolute level is also low on this pilot:** corpus chrF 13.2, WER 94.7, length ratio 0.42. A high-
  confidence Gemini output is not shown to be correct. Nothing here establishes that either model reads these clips.

The automatic results do not establish whether OpenAI's abstentions are semantically appropriate caution or a
capability limitation. They also do not establish that Gemini's confident outputs are correct.

Not claimed here:
- that Gemini is semantically accurate or production-ready;
- that OpenAI cannot understand ASL in general (one model, one prompt, one reasoning setting, 24 clips);
- that Uni-Sign is better in a same-input comparison. Uni-Sign is not input-matched and appears for orientation only.

## 1. Run integrity

| Check | Result |
|---|---|
| Cases attempted per arm | 24 / 24 (Gemini), 24 / 24 (OpenAI); no halt |
| Primary requests | 29 Gemini, 29 OpenAI (expected 29 each) |
| Retries | none (OpenAI SDK `max_retries=0`; genai default no retry; every batch attempt 1) |
| Frame hashes | all frozen. Each outgoing request was checked against the frozen labels, JPEG hashes, order and batch hash before it was sent |
| Prompt hash | frozen (`ea8c5cb1…`), checked per request |
| OpenAI returned model | `gpt-6.1-sol` on 29 / 29 calls |
| Gemini returned model | `gemini-2.5-flash` on 29 / 29 calls |
| Call order | followed the frozen hash-parity rule: 12 Gemini-first, 12 OpenAI-first |
| Denominator | all 24 cases in both arms; empty outputs scored as the empty string |
| Production timestamps | production's motion probe reproduced the frozen timestamps on all 48 case runs |

Configuration:
- `openai==3.41.0`, `google-genai==2.20.0`, Python 3.11.7.
- Image detail `high`; started 2026-10-29T08:30:32Z.

**Harness changes after the approved review, all made before the first model request:**
- **Resume-guard bug, disclosed.**
  - The first `--execute` launch stopped before any network or API request. The guard that refuses to overwrite
    existing case files used an always-true check (`any()` over generator objects, which are truthy even when
    empty), so it refused although no case file existed.
  - No request had been made: clients are created lazily, and the guard runs before the case loop. The `gemini/` and
    `openai/` folders held only empty `raw/` subfolders.
  - The check was fixed (`any(any(glob))`) and the run relaunched.
  - The fix changed only execution guarding. Request content, subset, frames, model, image detail, metrics, failure
    policy and decision rule were unchanged.
- **Two storage-only edits, made before the first launch.** The dry run was rerun afterwards: 29 + 29 requests
  matched the frozen input, with 0 connection attempts.
  - Stored Gemini raw responses exclude the SDK's `automatic_function_calling_history`, which can echo the input
    images.
  - A halt record keeps the in-flight batch metadata.

## 2. Reliability and status counts

| | Gemini | OpenAI |
|---|---|---|
| success | 24 | 9 |
| partial | 0 | 0 |
| no_signing_detected | 0 | **15** |
| parse_failure | 0 | 0 |
| transport_failure | 0 | 0 |
| empty output | 0 | 15 |
| non-answers (frozen definition) | 0 | **15** |
| `loop_out` | 0 | 0 |
| degenerate repetition | 0 | 0 |

**Batch level:**
- OpenAI: 9 `ok`, 20 `valid_empty`. All 29 responses had status `completed`, reasoning effort `medium`, no refusal and
  no incomplete response.
- Gemini: 29 `ok`.
- Two multi-batch OpenAI cases (`G1hb5HugzVk_2-8`, `G23G21G49dk_14-2`) had one `valid_empty` batch and one `ok` batch.
  That is a `success` under the frozen rule, because `valid_empty` is not a failure.

**Self-reported confidence (descriptive):**
- OpenAI: 26 `low`, 3 `medium`.
- Gemini: 24 `high`, 5 `medium`.

## 3. Automatic metrics (24 cases, P0-A frozen functions)

| | corpus chrF | BLEU-4 | WER | mean length ratio |
|---|---|---|---|---|
| Gemini (production) | **13.21** | **0.50** | **94.74** | 0.418 |
| OpenAI `gpt-6.1-sol` | 1.36 | 0.00 | 100.00 | 0.053 |
| Uni-Sign A_official (not input-matched / orientation only) | 29.32 | 10.73 | 88.79 | 0.901 |

Uni-Sign uses a different input pipeline. It is not input-matched and is shown for orientation only. It is never
paired as "only the model changed", and its numbers support no same-input comparison. Its `loop_out` count is 7 of 24.

## 4. Paired analysis (OpenAI − Gemini)

**Sentence chrF:**
- mean −9.72, median −10.06;
- wins / losses / ties: 1 / 22 / 1 (tie if |Δ| < 1);
- 95 % bootstrap CI of the mean, case level (10,000 resamples, seed 20261028): **[−12.30, −7.20]**;
- signer-proxy cluster bootstrap (sensitivity, 5 clusters): [−10.46, −8.82].

**Sentence WER:** mean +4.76, median +3.08. OpenAI is lower on 0 cases, higher on 14 and tied on 10.

**Regression / gain (|Δ sentence chrF| ≥ 10):** **12 regressions, 0 gains.**
- 15 OpenAI-empty cases: mean Δ chrF −11.36.
- 9 OpenAI-answered cases: mean Δ chrF −6.99, with 1 win and 7 losses.

## 5. Cost and latency

| | Calls | Input tokens | Output tokens | Reasoning / thinking | Total | Cost (list price) | Median call latency |
|---|---|---|---|---|---|---|---|
| Gemini | 29 | 182,370 | 3,879 | 61,531 thinking | 247,780 | **$0.22** | **11.2 s** |
| OpenAI | 29 | 125,011 | 20,115 (incl. reasoning) | 18,439 | 145,126 | **$0.45** | **22.9 s** |

- **Gemini cost:** official list price read 2026-10-29: $0.30 input, $2.50 output including thinking. Thinking tokens
  are billed as output.
- **OpenAI cost:** $2 input, $10 output; reasoning is included in output tokens.
- **Prices:** both are official list prices read on the run date. Account billing was not checked.
- **Cached input:** 0 tokens on both.
- **Latency:** OpenAI mean 23.0 s, max 41.2 s. Gemini mean 11.4 s, max 22.8 s.
- **Approved spend:** 58 calls. Actual: 58 calls, about $0.67 in total.

## 6. Frozen decision gates

| Gate | Condition | Result |
|---|---|---|
| **R: reliability** | non-answers O ≤ G + 1 **and** partial O ≤ G + 1 | **FAIL**: non-answers 15 vs 0; partial 0 vs 0 |
| **Q: quality** | corpus chrF O − G ≥ +2.0 **and** CI lower bound > 0 **and** WER O ≤ G | **FAIL**: Δ chrF −11.85; CI lower bound −12.30; WER 100.0 vs 94.7 |
| **S: safety** | regressions ≤ gains **and** generic outputs O ≤ G | **FAIL**: 12 regressions vs 0 gains. The generic proxy is 0 vs 0. This is the automatic proxy only (no blind review) |
| **C: cost/latency** | median latency O ≤ 2× G **and** cost O ≤ 3× G | **FAIL**, narrowly: latency 22.9 s vs a limit of 2 × 11.2 = 22.4 s; cost $0.45 vs a limit of 3 × $0.22 = $0.65 (passes) |

**B strata** (comparator: Gemini; each needs n ≥ 5, mean Δ ≥ +5 and wins ≥ 2/3):

| Stratum | n | Mean Δ chrF | W / L / T | Passes |
|---|---|---|---|---|
| multi-batch clips | 5 | −16.29 | 0 / 5 / 0 | no |
| signer proxy 3 | 6 | −9.24 | 0 / 5 / 1 | no |
| signer proxy 8 | 8 | −10.35 | 1 / 7 / 0 | no |
| Gemini non-answer / loop / degenerate | 0 | — | — | no (empty stratum) |
| Uni-Sign `loop_out` or empty | 7 | −12.06 | 0 / 7 / 0 | no |

Signer proxies 1, 2 and 10 have fewer than 5 cases and are not eligible.

**Verdict: C (pause).** Gate R fails, so C applies whatever the quality numbers say; Q and S fail independently. The
narrow latency failure does not drive the verdict. The decision rule allows Round 2 only after A or B, so Round 2 is
not justified.

**Main reliability failure:** OpenAI's 15/24 `no_signing_detected` cases (abstentions). All 5 multi-batch cases lose
for OpenAI.

**Interpretations fixed in the scoring script before any output was read:**
- non-answer = empty text, or status `no_signing_detected` / `parse_failure` / `transport_failure`;
- a win means Δ ≥ 1;
- the B comparator is Gemini for every stratum;
- "one signer proxy" is tested as each proxy with at least 5 cases.

## 7. Per-case results

Output texts are withheld here, as in the P0-A convention. They are in the per-case result files.

| Clip | Signer | Batches | Gemini | OpenAI | chrF G | chrF O | Δ chrF | WER G | WER O | Words G / O | Flag |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `-g0sqksgyc4_3-2` | 2 | 1 | success | no_signing | 9.83 | 0.00 | −9.83 | 100.0 | 100.0 | 6 / 0 | |
| `FZCEymcpq7I_14-1` | 1 | 1 | success | no_signing | 12.40 | 0.00 | −12.40 | 89.7 | 100.0 | 15 / 0 | regression |
| `FZd8Iv9ACVw_12-8` | 8 | 1 | success | no_signing | 11.80 | 0.00 | −11.80 | 97.0 | 100.0 | 10 / 0 | regression |
| `Fz-N1S0swh8_2-8` | 8 | 1 | success | success | 22.09 | 2.80 | −19.28 | 85.7 | 100.0 | 9 / 2 | regression |
| `FzAIlhumvMA_4-2` | 2 | 1 | success | success | 4.41 | 1.65 | −2.76 | 100.0 | 100.0 | 2 / 2 | |
| `FzQPg4aqNYc_13-1` | 1 | 1 | success | no_signing | 10.67 | 0.00 | −10.67 | 100.0 | 100.0 | 8 / 0 | regression |
| `FzoUVr98JmQ_6-8` | 8 | 1 | success | success | 11.33 | 3.11 | −8.22 | 88.0 | 100.0 | 10 / 3 | |
| `G05uFub3YFc_9-2` | 2 | 2 | success | no_signing | 13.43 | 0.00 | −13.43 | 94.1 | 100.0 | 21 / 0 | regression |
| `G1hb5HugzVk_2-8` | 8 | 2 | success | success | 18.24 | 2.72 | −15.52 | 93.3 | 100.0 | 27 / 4 | regression |
| `G23G21G49dk_14-2` | 2 | 2 | success | success | 14.10 | 0.68 | −13.42 | 96.9 | 100.0 | 21 / 1 | regression |
| `G2T2WCuU39Y_5-10` | 10 | 2 | success | no_signing | 19.79 | 0.00 | −19.79 | 97.0 | 100.0 | 39 / 0 | regression |
| `G3FhmHz_7hs_20-10` | 10 | 1 | success | no_signing | 6.03 | 0.00 | −6.03 | 95.5 | 100.0 | 7 / 0 | |
| `fzOH00UZg84_30-8` | 8 | 2 | success | no_signing | 19.28 | 0.00 | −19.28 | 94.6 | 100.0 | 26 / 0 | regression |
| `fzcsY2gm7t0_8-8` | 8 | 1 | success | no_signing | 5.85 | 0.00 | −5.85 | 100.0 | 100.0 | 4 / 0 | |
| `fzrJBu2qsM8_5-10` | 10 | 1 | success | no_signing | 3.91 | 0.00 | −3.91 | 100.0 | 100.0 | 1 / 0 | |
| `fzueHkUDyhE_1-8` | 8 | 1 | success | no_signing | 5.59 | 0.00 | −5.59 | 100.0 | 100.0 | 3 / 0 | |
| `g0Abwige7MQ_2-8` | 8 | 1 | success | success | 7.58 | 10.35 | **+2.77** | 85.7 | 100.0 | 7 / 6 | |
| `g1HvmBOR7Y4_15-3` | 3 | 1 | success | no_signing | 21.53 | 0.00 | −21.53 | 78.9 | 100.0 | 15 / 0 | regression |
| `g1vUH8Iy4vw_8-3` | 3 | 1 | success | no_signing | 14.74 | 0.00 | −14.74 | 94.4 | 100.0 | 10 / 0 | regression |
| `g1z6HOJ0yRw_2-3` | 3 | 1 | success | no_signing | 10.30 | 0.00 | −10.30 | 100.0 | 100.0 | 5 / 0 | regression |
| `g2ELiaFjKfs_3-10` | 10 | 1 | success | success | 5.82 | 3.04 | −2.78 | 100.0 | 100.0 | 4 / 2 | |
| `g2QdwYqm8pg_13-3` | 3 | 1 | success | success | 5.83 | 1.64 | −4.19 | 100.0 | 100.0 | 5 / 1 | |
| `g3jQ5ecjGz8_6-3` | 3 | 1 | success | no_signing | 5.23 | 0.00 | −5.23 | 95.0 | 100.0 | 5 / 0 | |
| `g3ushtMfLiY_2-3` | 3 | 1 | success | success | 9.42 | 9.95 | +0.53 | 100.0 | 100.0 | 7 / 5 | |

Clip IDs are shown without the `-rgb_front` suffix.

## 8. Important failure cases

- **All 5 multi-batch clips lose.**
  - Three are full abstentions: `G05uFub3YFc_9-2`, `G2T2WCuU39Y_5-10` (Δ −19.79) and `fzOH00UZg84_30-8` (Δ −19.28).
  - Two answered only one of their two batches: `G1hb5HugzVk_2-8` and `G23G21G49dk_14-2`.
- **Largest regressions:** `g1HvmBOR7Y4_15-3` (−21.53, OpenAI empty), `G2T2WCuU39Y_5-10` (−19.79, empty) and
  `Fz-N1S0swh8_2-8` (−19.28, OpenAI answered with 2 words).
- **The only win:** `g0Abwige7MQ_2-8` (+2.77). Both outputs score low in absolute terms (chrF 7.6 vs 10.4).
- **Not seen:** no OpenAI transport failure, parse failure, refusal, model-ID mismatch, HTTP 400/422 or incomplete
  response. The harness's halt paths were never triggered.

## Limitations

- **No blind human review.** Gate S used only the automatic generic proxy, and the key-content-error check required
  for A was not possible. That does not affect the verdict: R, Q and S fail on automatic counts alone.
- **24 cases is a screening size.** The effect is large and consistent: CI [−12.3, −7.2], 22 of 24 losses.
- **Only the default reasoning effort (`medium`) and one prompt were tested.** The prompt is production's; its
  "say so honestly instead of guessing" instruction drives the abstentions. Neither was tuned, by design.
- **Exposure:** every pilot clip has prior research exposure (pre-registration §1). This is not a clean holdout.
- **Gemini has run-to-run variance at temperature 0.** No repeat was approved, so the noise floor is unmeasured. It
  cannot explain a 15-case abstention gap.
- **Costs** (OpenAI about $0.45, Gemini about $0.22) are token counts multiplied by official list prices. They are
  estimates, not billed amounts.
