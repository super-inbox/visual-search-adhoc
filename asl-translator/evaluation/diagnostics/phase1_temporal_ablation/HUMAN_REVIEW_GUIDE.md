# Human Review Guide — Phase 1 qualitative taxonomy

Plain-language guide for filling in the annotation app
(`review_app/server.py`). Nothing here is pre-filled by the machine — every
field below is your judgment call after watching the clip.

## Reviewer-capability split — read this first

**If you are not fluent in ASL**, you cannot reliably tell from the source
video whether a prediction has "no visual basis," and you cannot reliably
diagnose handshape, motion, fingerspelling, numbers, facial/non-manual, or
segmentation failure types — those require visual sign-language expertise.
This guide (and the app) therefore separates every field into two buckets:

**TEXT-BASED REVIEW** — you can always fill these in by comparing the English
ground-truth reference to the English Gemini prediction, no ASL needed:
- `semantic_adequacy`
- `reference_topic_mismatch`
- `correct_meaning_different_english` (failure tag)
- `repetition` (failure tag) — only when it's obvious in the output *text*
  itself (the same word/phrase repeated), not a claim about the signing.

**ASL/VISUAL REVIEW** — leave these blank unless directly obvious; they exist
for an ASL-fluent reviewer, not a requirement for you:
- `handshape_sensitive` / `handshape` (content / failure)
- `motion` (content / failure)
- `fingerspelling` (content / failure)
- `numbers` (content / failure)
- `facial_non_manual` (content / failure)
- `segmentation` (failure)
- `hallucinated_topic` (failure) and `hallucination` = **yes** — both assert
  something has *no basis in the video*, which requires watching the signing
  itself with sign-language fluency, not just reading the English text.
- Whether a specific sign crosses a 24-frame batch boundary (the confident
  "yes" case for `batch_boundary_might_help`) — telling that a *sign*
  straddles the seam, rather than just that an error happens to sit near one,
  needs to see the sign itself.

If you are a non-ASL-fluent reviewer: fill in every TEXT-BASED field, leave
ASL/VISUAL fields blank unless something is directly obvious even without ASL
fluency (e.g. you can see two clearly different handshapes without knowing
what either means), and use `requires_asl_review` / `hallucination:
requires_asl_review` to flag clips that need a second, ASL-fluent pass.

## Before you start

Review the **12 PRIORITY DIAGNOSTIC clips first** (marked with a red badge
in the app and shown first). Those 12 were hand-picked to cover the main
suspected failure modes (long/multi-batch clips, fingerspelling, numbers,
fast signing/questions, worst-WER, and a couple of best-WER contrast cases)
and have a full frame-by-frame inspector page (button: "Open full frame
inspector") showing exactly which frames the model saw and where the
24-frame batch boundaries fall. Use that inspector for the 12; for the other
28 the video player plus the 6-frame thumbnail strip is usually enough.

Watch the actual video before reading the model's prediction, if you can —
it's easy to unconsciously rationalize a wrong prediction once you've read
it first.

## Content / clip tags — what is present in the SIGNING itself

Check every tag that applies to the clip's content, regardless of whether
the model got it right. These describe the video, not the model's output.
**Tags marked ASL/VISUAL below require ASL/visual review unless directly
obvious — leave them unchecked if you're not sure.**

- **handshape_sensitive** — *ASL/VISUAL.* Getting this clip right depends on
  seeing precise finger/hand configuration (not just where the hands move),
  e.g. distinct letters or number handshapes that look similar from a blurry
  or sparse frame.
- **motion** — *ASL/VISUAL.* The meaning depends on the *trajectory or path*
  of a movement (a repeated motion, a directional sign, a size/manner
  indicated by how a sign moves), not just a static handshape.
- **fingerspelling** — *ASL/VISUAL.* A name, acronym, or word is spelled
  letter-by-letter on the fingers.
- **numbers** — *ASL/VISUAL.* A number, count, or numeral is signed.
- **facial_non_manual** — *ASL/VISUAL.* Meaning depends on facial expression,
  eyebrow raise, mouth shape, or head tilt (e.g. marking a question,
  negation, or intensity) rather than the hands alone.
- **fast_signing** — the signer is moving through content quickly relative
  to the rest of the corpus. (Not ASL-fluency-gated — you can usually judge
  relative signing speed just by watching, without knowing what's signed.)
- **other** — anything notable that doesn't fit above (use the notes field
  to say what).

**Handshape vs. motion, concretely (ASL/VISUAL reviewers):** if you covered
the video and only looked at a single freeze-frame, would you have a chance
at the sign? If yes, it's more of a **handshape** clip. If a single
freeze-frame is meaningless and you need to see the hand move through a path
to understand it, it's more of a **motion** clip. A clip can be both.

## Failure tags — what actually went wrong in the MODEL'S OUTPUT

Check every tag that describes why the prediction is wrong (skip this
section, or leave everything unchecked, if the prediction is already
correct). **Tags marked ASL/VISUAL below require ASL/visual review unless
directly obvious — leave them unchecked if you're not sure.**

- **handshape** — *ASL/VISUAL.* The model's mistake looks like it misread a
  handshape (confused similar-looking signs/letters).
- **motion** — *ASL/VISUAL.* The model's mistake looks like it missed or
  misread how something moved.
- **fingerspelling** — *ASL/VISUAL.* A fingerspelled word came out garbled,
  wrong, or missing entirely.
- **numbers** — *ASL/VISUAL.* A number came out wrong, garbled, or missing.
- **facial_non_manual** — *ASL/VISUAL.* A facial/non-manual marker
  (question, negation, emphasis) was missed, e.g. a question was translated
  as a statement.
- **segmentation** — *ASL/VISUAL.* The model split or merged
  sentences/ideas incorrectly (a translation stops too early, starts too
  late, or two separate thoughts got mashed into one). Confirming this is
  really a segmentation error (rather than, say, an unrelated topic that
  happens to be a different length) requires watching where the signing
  itself starts/stops.
- **hallucinated_topic** — *ASL/VISUAL.* The prediction is fluent English
  but is about a **different topic altogether**, with **invented content
  that has no basis in the video** — not just a wrong word here or there.
  Example: reference is about cooking, prediction is about wrestling. This
  tag makes a visual-grounding claim ("no basis in the video"), which a
  non-ASL-fluent reviewer cannot verify. **If all you can tell is that the
  English topics don't match, use `reference_topic_mismatch` = yes instead**
  (see below) — don't check this box unless you (or an ASL-fluent
  co-reviewer) can confirm from the signing itself that nothing in the video
  supports the prediction.
- **repetition** — *TEXT-BASED.* The model repeats the same word/phrase over
  and over in its output text (a known Gemini-on-ASL failure mode). This is
  judged from reading the prediction, not from watching the signing.
- **correct_meaning_different_english** — *TEXT-BASED.* The model got the
  actual meaning right, just phrased differently in English (a paraphrase).
  This is important to flag because raw WER penalizes this as if it were
  wrong, even though the translation succeeded. Judged by comparing the two
  English texts.
- **other** — anything else (use notes).

## Semantic adequacy — TEXT-BASED, the single most important field

Score the prediction's actual meaning against the reference, independent of
exact wording. This is judged entirely by comparing the English reference to
the English prediction — no ASL fluency needed:

- **2 — core meaning correct.** A person who only read the prediction would
  understand the same essential point as the reference, even if phrasing,
  minor details, or some words differ.
- **1 — partially correct / important omission or error.** Some of the
  meaning came through, but something important is missing, wrong, or
  would mislead a reader about a meaningful part of the message.
- **0 — wrong meaning or essentially hallucinated.** A reader would come
  away believing something substantially different from, or unrelated to,
  what was actually signed.

This is why WER alone isn't enough: a clip can have WER near 1.0 (almost no
matching words) yet still deserve a semantic_adequacy of 2 if it's a fluent
paraphrase, and a clip with a "reasonable-looking" low-WER sentence can
still deserve a 0 if it's confidently describing the wrong thing.

## reference_topic_mismatch (yes/no) — TEXT-BASED

**yes** means the prediction's meaning/topic is clearly inconsistent with
the English ground-truth reference. This is a **text-based** judgment made
purely by comparing the two English strings — it does **not** claim anything
about direct visual grounding (i.e. it is not a claim that the video has "no
basis" for the prediction, only that the two texts disagree).

**no** means the prediction's topic is broadly consistent with the
reference, even if specific words or details differ.

Use this field whenever you notice a topic mismatch but cannot (or don't
want to) claim the stronger, visually-grounded `hallucination: yes` /
`hallucinated_topic` judgment.

## Hallucination — ASL/VISUAL

Options: **yes / no / uncertain / requires_asl_review**.

**`hallucination: yes` requires confidence that the predicted content has no
basis in the signed video at all** (an invented name, number, action, or
entire topic) — not just that the English texts disagree. As a
non-ASL-fluent reviewer, you normally **cannot establish this** because you
cannot rule out that some part of the prediction corresponds to something
actually signed. Prefer:

- **`reference_topic_mismatch: yes`** (above) if the English texts clearly
  disagree — that's the judgment you *can* make.
- **`uncertain`** if you don't know either way.
- **`requires_asl_review`** if you specifically believe this clip needs an
  ASL-fluent reviewer to settle whether it's a true hallucination.
- **`no`** only if you're confident everything in the prediction is at least
  a plausible misreading of something in the signing (rare for a
  non-ASL-fluent reviewer to be confident about, but possible for very
  simple/obvious clips).

A clip can have `hallucination: requires_asl_review` (or `yes`, for an
ASL-fluent reviewer) and still get `semantic_adequacy: 1` if only part of
the output is invented while the rest is on-topic.

## requires_asl_review (yes/no) — flag, default blank

A simple flag on the whole clip: set to **yes** if you believe this specific
clip needs a second pass from an ASL-fluent reviewer (e.g. you suspect a
handshape/motion/fingerspelling/facial-non-manual issue, or you couldn't
confidently answer `hallucination`, but you can't verify any of it
yourself). Leave **blank** by default — do not fill this in "just in case"
for every clip; only when there's a specific concrete reason. This field is
never auto-filled by the app.

## Temporal hypotheses — be conservative here

These two fields are the reason this taxonomy exists — but they are
deliberately the two you should mark **"uncertain"** or **"unable_to_judge"**
most often unless the evidence is clear from what you can see.

### fps_might_help

Options: **yes / no / uncertain / unable_to_judge**.

Select **yes** only when, looking at the sampled frames (video +
thumbnails, or the inspector's frame strip for the 12 priority clips), it
genuinely looks like the sampler skipped over a moment that mattered — e.g.
a fingerspelled letter's mid-transition was never captured, or a fast sign's
key handshape falls between two sampled frames with a fast blur in between.

Select **no** if the sampled frames already seem to cover the sign
adequately and the model still got it wrong for some other reason (e.g. it
hallucinated a different topic even though the frames were fine, or it's a
clear handshape-confusion error where more frames of the same blur
wouldn't help).

Select **uncertain** when you can see the frames and content well enough to
have an opinion, but genuinely can't tell which way it points — this is
common and honest; don't force a yes/no.

Select **unable_to_judge** when the judgment itself is out of reach for you
as a reviewer (e.g. it would require confirming what a specific handshape or
fingerspelled letter should look like, which needs ASL/visual expertise you
don't have) — distinct from "uncertain," which is for when you *can* assess
it but the evidence is genuinely ambiguous.

### batch_boundary_might_help

Options: **yes / no / uncertain / unable_to_judge**.

Select **yes** only when a sign or semantic unit visibly straddles an
independent 24-frame batch boundary — i.e., part of the meaning is in one
batch of frames and the rest is in the next batch, and the model's output
shows a plausible seam artifact (an idea cut off mid-thought, a duplicated
or dropped fragment right at that time). For the 12 priority clips, the
inspector marks candidate seam-adjacent frames/segments in red — use that as
a starting point, but confirm visually rather than trusting the flag alone.
Confirming that a *sign itself* (not just an error) crosses the seam is an
ASL/VISUAL judgment — if you can see the batch-boundary timing line up with
where the error occurs but can't confirm a sign straddles it, use
`uncertain` or `unable_to_judge` rather than `yes`.

Select **no** if the clip is single-batch (no seam exists) or the error is
clearly unrelated to timing (e.g. wrong topic entirely).

Select **uncertain** if you're not sure whether the error is a seam artifact
or something else but you can assess the timing/content yourself.

Select **unable_to_judge** if confirming this would require seeing whether a
specific sign (not just an error) straddles the seam, which needs ASL/visual
expertise you don't have.

## Notes

One or two short, concrete observations — not a restatement of the tags.
Good notes point at *what to look at again later*:

- "Fast fingerspelling transition is missing between sampled frames."
- "Enough visual information appears present, but the semantic unit crosses
  a 24-frame batch boundary."
- "The English is fluent but describes the wrong topic (reference_topic_mismatch=yes);
  can't confirm true hallucination without ASL review."

## What NOT to do

- Don't fill in a tag or score just because the manifest hint pill suggests
  it (e.g. "manifest hint: numbers") — that hint is about the *English
  reference text*, not confirmed visual content. Verify by watching.
- Don't derive semantic_adequacy or reference_topic_mismatch from the WER
  number alone — a high-WER clip can still be semantically adequate
  (paraphrase), and a low-WER clip can still be semantically wrong (an
  eerily plausible but incorrect sentence).
- Don't feel obligated to check every content/failure tag — most clips will
  only have one or two that clearly apply.
- **Don't mark `hallucination: yes` or check an ASL/VISUAL tag just because
  it "seems likely."** If you're not ASL-fluent, use `reference_topic_mismatch`,
  `uncertain`, `unable_to_judge`, or `requires_asl_review` instead — leaving a
  field honestly blank/uncertain is more useful than a guess dressed up as a
  visual-grounding claim.
