# Gemini Phase 3A — implementation verification + credential check, 2026-09-02

**Status: STOPPED at step 2, per instructions.** Step 1 (implementation
verification) completed fully. Step 2 (credential check) found no working
credential through any of the three explicitly permitted channels. Steps
3–7 (cost estimate, smoke tests, scoring) were **not attempted** — they
require a working credential this session does not have. No secret value
was printed, logged, committed, or echoed at any point. No production
infrastructure was searched; no production credentials were touched or
extracted.

---

## 1. Current Curify Gemini ASL implementation — verified

**Source:** `curify-studio` repo, `origin/main` (fetched read-only this
session; the local working-tree checkout is not touched — see note at the
end of this section), file
`curify_background/app/utils/asl_utils.py`.

| Field | Value |
|---|---|
| Model | `gemini-2.5-flash` |
| Temperature | `0.0` (pinned; unset previously caused repeat-run WER 0.97 between two identical-file submissions 11s apart — the module's own comment documents this) |
| Frame sampling | Motion-probe based (4fps, 160px grayscale probe, never shown to the model) → active/idle run segmentation → timestamps allocated within active runs |
| Frame budget | Duration-scaled: `TARGET_FRAMES_PER_SEC=2.0`, clamped to `[MIN_FRAME_BUDGET=24, MAX_FRAME_BUDGET=240]` |
| Frames actually sent | 512px-wide JPEGs, each labelled with its timestamp as a text part before the image |
| Batching | `BATCH_SIZE=24` frames per `generate_content` call; a video needing more than 24 frames is split into multiple sequential batches, each an independent call |
| Decoding config | `GenerateContentConfig(response_mime_type="application/json", temperature=0.0)` — no other parameters (no top_p/top_k/max_output_tokens override) |
| Output schema | `{"segments":[{"start":<sec>,"end":<sec>,"text":"..."}], "confidence":"high\|medium\|low", "notes":"..."}` |
| Prompt | Fixed, reproduced verbatim below |
| Fallback provider | `gpt-4o` (OpenAI) — exists only because the Gemini project hit its monthly spend cap mid-evaluation once; same prompt, same temperature, `detail:"low"` images |
| Cost | `JOB_CREDIT_COST["ASL_TRANSLATION"] = 0` since 2026-08-29 — **free** in production |

**Exact production prompt** (`_PROMPT` in `asl_utils.py`):
```
You are reading American Sign Language (ASL) from ordered video frames.

Each image is labelled with its timestamp in seconds. The frames are NOT evenly
spaced — they were sampled densely where the signer was actively signing and
sparsely where the signer was still.

Produce an English translation of what is being signed.

Rules:
- Translate meaning into natural English. Do NOT output ASL gloss.
- Group into short caption-length segments with start/end seconds taken from the
  frame timestamps you used.
- Frames are sparse: you are seeing key moments, not every sign. Where a sign is
  ambiguous, prefer the reading that fits the surrounding context.
- If a stretch shows no actual signing (signer resting, adjusting, or absent),
  omit it rather than inventing content.
- If you cannot read the signing with reasonable confidence, say so honestly in
  the `notes` field instead of guessing.

Return STRICT JSON only:
{"segments":[{"start":<sec>,"end":<sec>,"text":"..."}],
 "confidence":"high|medium|low",
 "notes":"what limited the reading, if anything"}
```

**A live, disclosed product issue (not something this check introduced):**
the prompt does not tell the model to ignore on-screen text. Confirmed
directly from the module's current docstring — a user uploading an
already-captioned video gets those captions read back as a "translation."
Not relevant to our public How2Sign clips (no burned-in captions, already
leakage-checked in Phase 1), but noted since it's exactly the class of
contamination this project already got burned by once (`CONTAMINATION.md`).

### Does `asl-eval/run_current_model.py` still match production?

**Yes — confirmed line-for-line for every constant and the prompt text
today**, not assumed from the script's own claim:

| | Production (`asl_utils.py`, `origin/main`) | Offline runner (`run_current_model.py`) |
|---|---|---|
| `ASL_MODEL` | `gemini-2.5-flash` | `gemini-2.5-flash` ✓ |
| `ASL_TEMPERATURE` | `0.0` | `0.0` ✓ |
| `TARGET_FRAMES_PER_SEC` | `2.0` | `2.0` ✓ |
| `MIN_FRAME_BUDGET` / `MAX_FRAME_BUDGET` | `24` / `240` | `24` / `240` ✓ |
| `BATCH_SIZE` | `24` | `24` ✓ |
| `KEYFRAME_WIDTH` | `512` | `512` ✓ |
| `DENSITY_FLOOR_FPS` | `1.0` | `1.0` ✓ |
| Prompt text | (above) | byte-identical (diffed directly) ✓ |

The offline runner's docstring pins its inspection to commit `f42a3a44`
(2026-08-29) and separately notes "last commit that touched that file at
inspection time: `08d12fb`" — both now slightly stale bookkeeping, because
one further commit touched the file since: `6972b8c2` (2026-08-30,
*"docs(asl): retract the demo-clip results"*). **Diffed this commit
directly** (`git show 6972b8c2 -- .../asl_utils.py`): 24 insertions / 4
deletions, **entirely inside the module docstring** (correcting a stale
"DO NOT SHIP" header and retracting a contaminated-input result) — zero
lines of executable code changed. **Parity holds; nothing in the offline
runner needs updating.**

**One thing that could not be re-verified today:** the automated
`TestProductionParity` suite (`test_run_current_model.py`) exists
specifically to do this comparison programmatically, but it **skips**
here — its `setUpClass` looks for
`~/curify-studio/curify_background/app/utils/asl_utils.py` or
`<this-repo>/../curify-studio/...` on local disk, and the second path
exists as a directory but its working-tree checkout is pinned to a stale
commit (`7b3fa5b`, 2026-07-16) that **predates asl_utils.py's own
existence in the repo** — the file is genuinely absent from that local
checkout's HEAD, confirmed via `git cat-file -e`. Per this session's
instructions not to check out, pull, or modify `curify-studio`, this was
left as-is; the manual `git show origin/main:...` comparison above serves
as this session's parity check instead, and reached the same "no drift"
conclusion the automated test would have.

---

## 2. Credential check — no valid credential found

All three explicitly permitted channels were checked, in order, cheapest
first. No secret value was ever printed, logged, or written anywhere
below — only existence, length, and a 4-character prefix (Gemini API keys
are not secret at the `AIza`-prefix level; this is the SDK's own
convention for key identification, e.g. in `gcloud` credential name
displays).

| Channel | Check performed | Result |
|---|---|---|
| Shell environment | `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`, `VERTEX_API_KEY`, `GOOGLE_GENAI_USE_VERTEXAI` — existence only | **None set** |
| `curify-frontend/.env.local` (the file you named) | Loaded the `GEMINI_API_KEY` value directly into the `google-genai` SDK in-process (never written to a new file, never printed) and called the **cheapest possible** endpoint: `client.models.list()` — a metadata call, no generation, no video, no tokens billed | **FAILURE**: `400 INVALID_ARGUMENT` / `API_KEY_INVALID` — *"API key not valid. Please pass a valid API key."* Identical failure mode to what you already documented. |
| Google ADC / gcloud auth state | `gcloud auth list` → an active interactive user login exists (`baobao2@illinois.edu`). `gcloud auth print-access-token` → succeeds (a personal OAuth token can be minted). **But** `gcloud auth application-default print-access-token` → explicit error: *"Your default credentials were not found."* ADC is not configured. `gcloud config get-value project` → unset — no GCP project is configured locally to call Vertex AI against even if ADC existed. | **No usable credential.** A personal user OAuth token exists in principle, but (a) ADC — the mechanism the `google-genai` SDK's Vertex path actually reads — is not set up, matching your prior documented "401, OAuth2 required" finding exactly, and (b) using that personal token against Curify's actual production GCP project (the only project ID found anywhere in local config, in `curify-studio/curify_background/app/config.py`) would mean attempting production access with an unauthorized personal credential — explicitly out of scope, not attempted. |

### Exact blocker

**No valid Gemini/Vertex credential is available in this environment
today.** The Developer API key in `.env.local` is invalid (server-side
rejection, not a local misconfiguration — same result as your prior
finding). Vertex AI requires real OAuth2 (ADC or a service account), and
no ADC is configured; the only alternative (a personal gcloud user token)
would require attempting access to Curify's production GCP project
without authorization, which this session was explicitly told not to do.

**Not attempted, and why:** guessing or deriving a different key,
searching for other `.env` files across the many `curify-frontend-*`
clone directories on this Desktop (out of scope — you named one specific
file), or running `gcloud auth application-default login` (would create a
*new* credential grant, not check an *existing* one — outside "already-
authorized... currently available").

---

## 3–7. Not performed

Cost estimation, the still-frame smoke test, the native-video smoke test,
and scoring all require a working API credential. None were attempted.
No API call that could incur cost or upload video was made at any point.

---

## Verification

1. **`FREEZE.sha256` unchanged:** confirmed —
   `16c41282b21928e36e4c5481d8c3de48d56794accbb091fde67698dd2963411a`
   (re-read directly from the tracked file; not recomputed since nothing
   in the benchmark was touched).
2. **`git status`:** only this new report file is untracked in
   `visual-search-adhoc-asl-task-c`; `curify-studio`'s own working tree
   was not modified (its pre-existing `_local_research/` untracked
   directory, unrelated to this session, is the only thing `git status`
   shows there).
3. **No secrets written to disk:** the credential-check script
   (`check_gemini_auth.py`, scratchpad-only, not in either repo) reads the
   key in-process and never writes it anywhere; its own output (captured
   in this conversation) contains only length/prefix, never the full key.
4. **Files created outside the benchmark:**
   - `docs/daily_report/9.2/asl-baselines/GEMINI_PHASE3A_CREDENTIAL_BLOCKER.md` (this file)
   - Nothing else — no predictions, no scratch video/frame extraction occurred (the frame-sampling/prompt verification above was read-only source inspection, not an execution of `run_current_model.py --extract-frames`).

## What would unblock this

Per your instructions, not guessed or worked around — flagging only:
- A **valid** Gemini Developer API key (the current one 400s server-side), or
- `gcloud auth application-default login` against a GCP project that both
  (a) has Vertex AI enabled/billing and (b) this account is authorized to
  use for this evaluation — neither confirmed to exist for a non-production
  project, and using the production project without explicit authorization
  was correctly out of scope for this check.
