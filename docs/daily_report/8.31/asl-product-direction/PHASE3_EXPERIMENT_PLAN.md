# Phase 3 experiment plan — product-usable ASL→English search

**Status: plan only. Neither experiment below has been executed.** No
API has been called, no money spent, no environment created, no download
performed. This plan is written so at most two bounded first experiments
can be reviewed and approved separately, not run as part of this
document.

**Execution status update (2026-08-31, after this plan was written):** one
attempt was made to begin Experiment A with a company-provided
`GEMINI_API_KEY`. The key **failed authentication on both attempted API
paths** — the standard Gemini Developer API (`400 INVALID_ARGUMENT: API
key not valid`) and Vertex AI Express Mode (`401 UNAUTHENTICATED: API
keys are not supported by this API`) — before any video was sent. **Zero
of the 3 planned clips were run, no Gemini prediction of any kind was
produced, and no paid API call completed** (both failures occurred before
billed generation). **Gemini's ASL translation quality remains completely
unvalidated** — nothing below should be read as implying otherwise. The
3-clip experiment is unchanged and ready to run as soon as a working
credential (a plain Google AI Studio key, or a corrected/unrestricted
company key) is available.

At most two experiments are proposed, per instructions: **Experiment A**
(strongest commercially usable native-video VLM) and **Experiment B**
(strongest ASL-specific commercial option).

---

## Experiment A — Google Gemini API (native-video VLM)

### Why worth testing

Gemini is the only general-purpose VLM found in this search with **all
three** of: confirmed native video ingestion, a confirmed commercial-use
permission read directly from its own terms of service (not inferred),
and zero setup cost (no download, no new environment — a plain API call).
It is also the cleanest possible test of the open question this phase
exists to answer: does a frontier general-purpose video model, with no
ASL-specific training at all, already carry enough latent capability from
broad video pretraining to be a viable starting point — or does it fail
at recognizing ASL as a structured language entirely (as opposed to
narrating generic hand movement)? Either answer is useful and cheap to
obtain here.

### Exact input

The raw `.mp4` video file, sent as native video input via the Gemini API,
accompanied by a plain-language prompt asking for an English translation
of the ASL signing in the video (exact prompt wording to be finalized at
execution time, not decided here — this plan does not authorize
prompt-engineering iteration against the benchmark, only a first
straightforward attempt).

### Exact fixed benchmark examples

Use the **same two clip categories already established as this
project's evaluation backbone**, so results are directly comparable to
everything already measured:

1. **Internal verified-gold clips `155` and `1252`** — the only clips in
   this project with fully human-verified reference translations, and
   the same two clips SignCaption, Curify baseline0, and Curify
   temperature0 were all scored against. This is the highest-value
   comparison point available.
2. **The first clip of the frozen 19-clip How2Sign benchmark**
   (`-g0iPSnQt6w_11-1-rgb_front`) — the same clip used for both OpenSLT's
   and Uni-Sign's one-clip smoke tests, for direct three-way comparability.

### Start size: 1, 3, or 5 clips?

**Start with the 2 internal verified-gold clips (155, 1252) plus the 1
How2Sign smoke-test clip = 3 clips total.** Reasoning: these 3 specific
clips already have every other system's numbers on file (Curify, OpenSLT,
Uni-Sign, and — for 155/1252 — SignCaption), so 3 clips is the smallest
set that still yields a complete, multi-system comparison table rather
than an isolated number. Do not start with 1 (loses the internal
verified-gold comparison entirely) or jump to 5+ before reviewing these 3
(unnecessary cost/time before the basic viability question is answered).

### Expected cost

Genuinely uncertain from public pricing alone (see
`PRODUCT_CANDIDATES.md` — video-specific per-second/per-token input
pricing was not fully explicit in Google's own pricing page). Order-of-
magnitude estimate based on published token rates (~$0.30/1M tokens for a
mid-tier model) and the one concrete video-token reference point found
(~5,792 tokens/sec of 720p video, from a different pricing note): **well
under $1 total for 3 short clips** (the longest of the three is ~30
seconds), but this should be confirmed against the live pricing
calculator immediately before running, not assumed from this estimate.

### Expected runtime

Minutes, not hours — a handful of synchronous API calls, each likely
single-digit seconds to low tens of seconds depending on video length and
model response length. No environment setup time (unlike Phase 1/2's
academic checkpoints, which each required real environment-building
work).

### Metrics

Same as every other system evaluated in this project, for direct
comparability: WER, CER, SacreBLEU, chrF (via `asl-eval/lib.py` +
`sacrebleu`, the exact tools already used throughout Phase 1/2). Plus the
same qualitative checklist used for Uni-Sign's evaluation: topic
preservation, repetition, omissions, numbers, fingerspelling/names.

### Success criterion

**Gemini recognizably attempts ASL translation** (not a generic
video-description refusal or an unrelated response) **and** shows
materially better topic preservation than Uni-Sign/OpenSLT's near-zero
rate on at least the 3-clip sample — even a rough, imperfect translation
that correctly identifies the general subject matter of 155/1252 (human
services / volunteering content, per the existing gold) would be a
meaningfully different and more promising signal than anything seen from
either academic checkpoint so far.

### Stop criterion

**Stop after this 3-clip test and do not scale to more clips or begin
prompt engineering if:** the model declines to translate ASL content at
all (e.g., states it cannot interpret sign language), or produces content
as topically unrelated as OpenSLT/Uni-Sign's academic-checkpoint failures
with no qualitative improvement. In that case, report the result plainly
rather than iterating — per the same discipline applied to Uni-Sign (no
tuning against the frozen benchmark).

### Production licensing implication

If results are promising: Gemini's **paid-tier** terms of service already
permit commercial product use in principle (confirmed, not assumed) —
this would be the first candidate in this entire project where a
positive accuracy result and a clear licensing path could coexist. Any
production consideration would still need a full legal/procurement
review (data handling for user-uploaded video specifically, volume
pricing, SLA) before real integration — this experiment's job is only to
establish whether the accuracy signal justifies that review at all.

---

## Experiment B — Sign-Speak / SignCaption (ASL-specific commercial API)

### Why worth testing

SignCaption already has the strongest accuracy evidence of any system
touched by this project — WER 0.48/0.52 against verified human gold on
155/1252, versus ≥0.94 for both academic checkpoints, and it is the only
system (besides, arguably, nothing else) confirmed to correctly recover
fingerspelled proper names. That evidence already exists from earlier
project work (SignCaption outputs obtained and scored previously); what
does **not** yet exist is (a) confirmed commercial API pricing/terms, and
(b) a test on video Sign-Speak has not already produced a reference for
— i.e., a genuine blind test rather than reusing an existing annotation.

### Exact input

**Step 0 (not a technical experiment — a business/access step):**
contact Sign-Speak directly to obtain API/SDK access, published or
negotiated pricing, and — most specifically — explicit written
clearance on one named clause: Sign-Speak's public Customer ToS
(`sign-speak.com/legal/customer`) prohibits using the Service "in
connection with a service bureau for the benefit of any third party" or
to "create a competitive product," and Curify's own ASL translator is
arguably exactly that. This is not a generic "confirm the terms are
okay" step — it is asking Sign-Speak directly whether this specific
clause blocks Curify's intended use, and if so, whether an enterprise
agreement supersedes it. **This step must complete before any technical
call is made** — unlike Experiment A, there is no public self-serve API
key to simply start testing with, and running the technical test first
would not change the answer to this legal question.

Once access exists: the raw `.mp4` video file, submitted via whatever
upload/API mechanism Sign-Speak's SDK specifies.

### Exact fixed benchmark examples

Same 3-clip set as Experiment A (155, 1252, and the How2Sign smoke-test
clip), for direct cross-comparison with Experiment A's results and with
every other system already measured on these exact clips — **with one
caveat**: 155 and 1252 already have existing SignCaption annotations on
file from earlier project work. Re-running them through a fresh API call
(rather than reusing the existing annotations) is worth doing specifically
to confirm the existing numbers reproduce via the actual commercial API
path (not just however the earlier annotations were originally obtained) —
this is a reproducibility check, not a new data point in itself. The
How2Sign clip is the one genuinely new test here.

### Start size: 1, 3, or 5 clips?

**Start with 1 clip — the How2Sign smoke-test clip only** — once API
access is confirmed. Reasoning: 155/1252 already have SignCaption
numbers on file; re-running them is a reproducibility nicety, not the
priority. The one clip that actually tells us something new is the public
How2Sign clip, so that's the minimum first test. If access/pricing makes
it easy, re-running 155/1252 alongside costs little extra and confirms
reproducibility — but the plan's floor is 1 clip, not 3, specifically
because most of the value here is already banked from prior work.

### Expected cost

Unknown — gated entirely on Step 0 (pricing is not public). Cannot be
estimated responsibly until Sign-Speak provides a rate; this plan
explicitly does not guess a number here.

### Expected runtime

Step 0 (access/pricing confirmation) is likely the dominant cost in
*time*, not compute — could be anywhere from same-day (self-serve
signup, if one exists behind the "Enterprise" framing) to a multi-day
sales-contact cycle. The actual technical test, once access exists, is
minutes (a single API call per clip).

### Metrics

Same as Experiment A: WER, CER, SacreBLEU, chrF via the project's
existing tooling, plus the same qualitative checklist.

### Success criterion

**Commercial terms permit product integration**, and the fresh How2Sign
clip result is consistent with (not dramatically worse than) the existing
155/1252 accuracy — i.e., confirms SignCaption's strong performance
generalizes beyond the two clips already on file, on video it has not
seen before in this project.

### Stop criterion

**Stop and do not pursue further if either:** (a) Sign-Speak confirms the
public ToS's "competitive product" / "service bureau" clause applies to
Curify's use case and no enterprise agreement is offered to supersede it
— in which case the accuracy question becomes moot and should not be
tested further regardless of price, or (b) commercial terms are
otherwise incompatible with product needs (no redistribution rights,
prohibitive minimum commitment, data-handling terms Curify can't accept
— including the public ToS's perpetual license-back of uploaded user
video for their own model training), or (c) pricing is confirmed but
clearly incompatible with product-scale volume economics before any
technical test is even worth running.

### Production licensing implication

**This is the one candidate where the licensing question must be
resolved *before* the accuracy question**, not after — the reverse order
from every other candidate evaluated in this project so far (where
accuracy was tested first and licensing turned out to be the blocker
after the fact, as with OpenSLT and Uni-Sign). If Step 0 confirms
workable commercial terms, this becomes the single most promising
candidate in the entire project to date, given its already-demonstrated
accuracy advantage. If Step 0 fails, this candidate is closed without
needing to spend anything on the technical test at all.

---

## Both experiments — shared ground rules

- **No tuning against the frozen benchmark** — a first plain-language
  prompt (Experiment A) or default API call (Experiment B), not iterated
  against these specific reference texts.
- **No private Curify user videos** — only the already-staged internal
  verified-gold clips and the public How2Sign benchmark clip, same
  boundary honored throughout Phase 1/2.
- **No production code changes, no commit/push, no new conda/Python
  environment** — both experiments are pure API calls from wherever this
  evaluation work already runs.
- **Report both results plainly, including a negative result** — per the
  discipline established in Phase 2, a "this doesn't work" finding is a
  complete and useful outcome, not something to iterate past quietly.
