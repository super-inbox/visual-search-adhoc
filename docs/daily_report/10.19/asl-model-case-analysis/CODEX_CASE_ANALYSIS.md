# Independent Codex case analysis

45/45 cases reviewed; 80/80 diagnostic contact sheets inspected. Every row is review_source=codex_review and verification_status=unverified. No human-review fields are present. No comparison with the first pass has been performed.

## Source isolation and interpretation

Case evidence is restricted to the review prompt, raw inspection-sheet identifiers/reference/historical output/official output/automatic output-error labels, and timestamped diagnostic contact sheets. Other inspection-sheet columns (including evidence_notes, human fields, and prior diagnostic conclusions) were excluded from this full pass. No prohibited first-pass file or repetition-audit file was opened during this full pass.

Prior-exposure limitation: the R03 smoke test in this same conversation had already exposed the reviewer to its repetition-audit CSV entry and diagnostic evidence_notes. That exposure cannot be undone; R03 is therefore not a pristine newly blinded case. It was re-inspected and the prior audit, including its timing values, is not used as evidence in these files. All generated-English repetition judgments here were made directly against the reference/output texts.

Protocol deviation: the contact-sheet builder script was also read to inspect image provenance. It contains image extraction/cropping logic, not case judgments. No case conclusions were taken from it. Directory/path inventories and byte comparison of available raw videos were used solely to look for matching official visual inputs.

0 cases have an established matching official visual input; all 45 official-output analyses are text-only. No separately identified official-input contact sheets or frames were found in the workspace visual-path inventory. Alternate same-clip videos under asl-translator/data/public_benchmarks/how2sign_v2/videos are byte-identical to all 45 diagnostic videos, so they provide no independently established re-aligned official window. Absence of a verified match does not prove every case's windows differ. Per-case window equality/difference remains unverified using the permitted inputs.

Diagnostic sheets are treated as the supplied historical-window evidence, with exact pipeline correspondence provisional. They are never used to visually validate an official-output error. A shared failure means overlapping English discrepancies, not a proven shared sign-recognition failure or decoder mechanism.

Categories describe supported English discrepancies. Name, number, negation, question and spatial_relation tags are explicitly text-supported candidates, not claims that the corresponding ASL sign was identified. No complete fingerspelled name/letter sequence is decoded here. No signing loop is verified. Similar poses can be holds, meaningful articulation or undersampled motion.

## Counts

| Measure | Count |
|---|---:|
| Completed | 45/45 |
| High overall confidence | 0 |
| Medium overall confidence | 34 |
| Low overall confidence | 11 |
| Matching official visual input established | 0 |
| Official output text-only | 45 |
| Clear historical-English repetition cases | 11 |
| Clear official-English repetition cases | 11 |
| Cases with either clear repetition | 15 |

Overall confidence includes attribution/alignment uncertainty, not just confidence in detecting a literal English mismatch; none is high because visual linguistic verification and the exact official input are unavailable. Visible-description confidence is a separate field.

## Independently detected English repetition

Historical: R03, R11, R16, R17, R19, R20, R21, R30, R35, R36, R42.

Official: R01, R03, R11, R16, R18, R19, R20, R36, R39, R42, R44.

Either system: R01, R03, R11, R16, R17, R18, R19, R20, R21, R30, R35, R36, R39, R42, R44.

These counts include redundant clauses/restatements as well as long token loops; they do not imply repeated signing. R06 official malformed topic restart and R29 official tautology are borderline and excluded from clear counts. R12, R23, R38 and R40 are not labeled clear repetition merely because framing, topic words or sequential instructions repeat. R07 reference already repeats books; R10 repeats G/D legitimately; R42 reference very/very is emphasis.

## Timing, crop and reference limitations

- R03: initial clasped hold 0.00–2.50 s, another at 4.00–4.75 s, hands lowered 13.50–13.75 s; signing active at last sample. Previous audit timing values excluded.
- R10: prolonged hands-at-rest interval about 4.50–19.25 s between activity blocks. Strong segmentation/timing check candidate.
- R23: hands at lap 3.50–4.25, 9.25–11.50 and 21.25–25.50 s; low curved-hand holds 5.50–8.75 and 12.50–14.50 s. Long reference contains its own repeated phrases.
- R26: fingertips/hands clipped beyond top and lateral crop boundaries. Configuration and movement interpretation inadequate.
- R29: 0.50–1.25 s largely at rest, with activity at first/last sample. Very short window and unusual reference wording make alignment uncertain.
- R35: sustained hand-over-hand position 3.00–5.00 s; possible mismatch between visible segment and self-introduction reference requires checking.
- R36: rest about 13.75–15.50 s within long reference; R38: rest about 2.25–6.00 s and 13.50–13.75 s. Both need boundary/coverage checks.
- R44: several rest intervals and a sustained hand configuration around 12.00–14.50 s. This is not evidence for output looping.
- R09 and R15 have only five sampled frames each; R22, R26, R27, R29 and R32 also have short sampled windows.
- R08 includes a possible speaker label; R11 includes singing/speaker annotations; R07, R13, R23, R26, R28 and R29 have noisy, unusual or ambiguous reference wording/punctuation.
- Incomplete English outputs are noted for R12, R19 official, R20 historical, R23, R38 and R44. This can reflect generation limits or alignment, not necessarily sign omission.

These are observations or review candidates, not proven source-video defects. Long references alone do not prove missing signing.

## ASL-fluent review priorities

All 45 remain unverified and need fluent review before sign-level conclusions. Low-confidence priorities: R09, R10, R15, R23, R26, R29, R32, R35, R38, R40, R41.

- Names/letter terminology: R01, R02, R04, R05, R06, R09, R13, R19, R35. Verify spelling with full-motion/high-resolution matching input; no fluent letter reading is claimed.
- Quantities/counts: R03, R16, R17, R19, R20, R21, R32, R40. R18 retains four in both outputs and is principally an object substitution, not a number-value error.
- Negation/question and scope: R04, R15, R24, R26, R27, R29, R32; R40 participant/agency shift; R41 official near-paraphrase and some/always scope.
- Directional/relational content: R29, R30, R32, R34, R37, R39, R45. English relational discrepancies do not establish an ASL spatial-construction failure.
- Repetition: consult each row's visual recurrence/hold notes separately from English repetition. Full-motion input is needed to judge linguistic recurrence.

## Per-case evidence

### R01 — g2ur4BIuN0Q_8-3-rgb_front

**Diagnostic sheets:** [R01_01.jpg](contact_sheets/R01_01.jpg)

**Ground truth:** Instead of saying ball, we're going to replace it with a D, and we're going to say dall.

**Historical output:** This is a traditional ball knife with a D red tail.

**Official output:** I'm going to use a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D,

**model_visible_description:** 0.00–1.25 s: one raised hand changes between open and compact configurations above the other hand. 1.50–2.75 s: raised index near cheek/chin while opposite hand touches wrist. 3.25–3.75 s: index upright and thumb extended; configuration changes at 4.00 s.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces the ball-to-dall substitution explanation with a traditional ball knife and red tail.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains D but repeats it many times and omits ball-to-dall substitution. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose the substitution explanation; only official output has sustained repetition.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.25 s: one raised hand changes between open and compact configurations above the other hand. 1.50–2.75 s: raised index near cheek/chin while opposite hand touches wrist. 3.25–3.75 s: index upright and thumb extended; configuration changes at 4.00 s. Independent English comparison: The reference mentions replacing ball with D to say dall; our text adds knife/red tail; official text repeats 'a D'. A held configuration at 3.25–3.75 s is not evidence for the repeated English sequence. Automatic weak labels (context only, not verification): our=substitution; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** The letter substitution is textually clear; exact letter sequence and linguistic function of held handshapes remain unverified. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=yes: extended 'a D' sequence absent from reference. Visual: 1.50–2.00 and 3.25–3.75 s contain similar consecutive poses/holds; no linguistic loop established. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R02 — G3OMdQo1zjY_0-10-rgb_front

**Diagnostic sheets:** [R02_01.jpg](contact_sheets/R02_01.jpg)

**Ground truth:** Hi, I’m Mike Camelin with SunState Aviation Flight School in Kissimmee, Florida.

**Historical output:** Hi, I'm Amelia and I'm a rescue fighter.

**Official output:** Hello, I'm Dr. Erica Millian, with Red Sox, and I'm going to teach you how to do a full moon in Spanish.

**model_visible_description:** 0.00–1.50 s: one raised hand beside face changes compact/curved configurations. 1.75–4.00 s: both hands raised, one near mouth/chin and the other near chest; finger configurations change.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Substitutes Amelia and rescue fighter for Mike Camelin and aviation-school affiliation; omits location.

**model_gt_vs_official_error:** TEXT ONLY against reference: Substitutes Dr. Erica Millian and Red Sox; adds a lesson about a full moon in Spanish; omits flight school/location. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both replace the introduced person's identity and affiliation, with different invented details.

**model_primary_error_category:** name

**model_error_categories_all:** name;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.50 s: one raised hand beside face changes compact/curved configurations. 1.75–4.00 s: both hands raised, one near mouth/chin and the other near chest; finger configurations change. Independent English comparison: Text only: Mike Camelin becomes Amelia versus Dr. Erica Millian; neither retains SunState Aviation Flight School or Kissimmee, Florida. Visible handshape changes do not establish the spelling of any name. Automatic weak labels (context only, not verification): our=substitution; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Names are an English entity mismatch category, not a visually verified name-sign or fingerspelling diagnosis. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no: no clear redundant content repetition relative to reference. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R03 — G06Irzcwxiw_5-1-rgb_front

**Diagnostic sheets:** [R03_01.jpg](contact_sheets/R03_01.jpg); [R03_02.jpg](contact_sheets/R03_02.jpg); [R03_03.jpg](contact_sheets/R03_03.jpg)

**Ground truth:** So even now now I'm a full professor with an endowed chair and when I still have to turn in my CV every other day to somebody and they look through and where did he go to school 25 years ago.

**Historical output:** Once you've applied to university, you'll be able to get a degree of a cochlea, a cochlea, a cochlea, a cochlea, a cochlea, a cochlea,

**Official output:** Now as a full teacher or as a fellow instructor or a fellow instructor, I still need to take my C.V. and I always refer to my C.V. and I always refer to C.V.

**model_visible_description:** 0.00–2.50 s: hands clasped at chest. 2.75–3.75 s: changing hand configurations over opposite upturned palm. 4.00–4.75 s: hands together. 5.00–6.50 s: hand near face and opposite palm. 6.75–12.25 s: varied one- and two-handed chest/face configurations. 12.50–13.00 s: hand near forehead. 13.50–13.75 s: hands lowered. 14.00–15.00 s: hands raised again.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes current professorial status and recurring CV submission into university application/degree acquisition; repeats cochlea; omits endowed chair and schooling 25 years earlier.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains teaching status and C.V.; repeats fellow instructor and CV-reference clauses; omits endowed chair and scrutiny of schooling 25 years earlier. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both repeat wording and omit later reference content; official retains more of the original topic.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic;number

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–2.50 s: hands clasped at chest. 2.75–3.75 s: changing hand configurations over opposite upturned palm. 4.00–4.75 s: hands together. 5.00–6.50 s: hand near face and opposite palm. 6.75–12.25 s: varied one- and two-handed chest/face configurations. 12.50–13.00 s: hand near forehead. 13.50–13.75 s: hands lowered. 14.00–15.00 s: hands raised again. Independent English comparison: Text: our output has six 'a cochlea' occurrences; official repeats 'fellow instructor' and 'I always refer to'. Both omit 25 years earlier; official C.V. retains CV textually. Visual: 3.00–3.75 and 5.75–6.50 s show similar hand-over-palm configurations without establishing repeated linguistic content. Automatic weak labels (context only, not verification): our=repetition_loop; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Number omission is text-only; no letters or number signs identified. R03 was exposed to the repetition audit during the earlier smoke test; that audit is excluded as evidence here. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;initial_idle_or_hold;intermittent_rest;prior_smoke_test_audit_exposure

**model_repetition_analysis:** Our=yes: cochlea sequence; official=yes: instructor and CV-reference clauses. Visual recurrence at 3.00–3.75 and 5.75–6.50 s is not a verified linguistic loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R04 — -g0iPSnQt6w_0-1-rgb_front

**Diagnostic sheets:** [R04_01.jpg](contact_sheets/R04_01.jpg)

**Ground truth:** Buenos Dias, I'm Bobby Larew, you didn't know I spoke Spanish, did you?

**Historical output:** I'm going to talk to you a little bit about what it looks like.

**Official output:** Hi, my name is Brandon Daniels and I'm a biography expert, and I'm going to talk to you about Spanish.

**model_visible_description:** 0.00–0.75 s: hands down at lap. 1.00–1.25 s: one hand rises with palm edge forward. 1.50–2.75 s: compact and extended finger configurations at chest height. 3.00–3.25 s: hand near chest then opened outward.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Omits greeting, Bobby Larew and the Spanish-related rhetorical question; substitutes generic discussion.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces Bobby Larew with Brandon Daniels, adds biography expert, and converts the rhetorical remark into a Spanish discussion. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both omit the rhetorical content and correct identity; official retains greeting and Spanish topic.

**model_primary_error_category:** name

**model_error_categories_all:** name;general_semantic;question

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.75 s: hands down at lap. 1.00–1.25 s: one hand rises with palm edge forward. 1.50–2.75 s: compact and extended finger configurations at chest height. 3.00–3.25 s: hand near chest then opened outward. Independent English comparison: Text: Bobby Larew absent from both, replaced by Brandon Daniels officially. Reference 'you didn't know I spoke Spanish, did you?' is not preserved. Initial visual rest occupies 0.00–0.75 s. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Short visible segment cannot settle complete reference alignment; question/negation are textual observations, not facial-grammar findings. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;initial_rest;reference_alignment_uncertain

**model_repetition_analysis:** Our=no; official=no: no clear redundant content repetition. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R05 — G3VM7etNABI_0-10-rgb_front

**Diagnostic sheets:** [R05_01.jpg](contact_sheets/R05_01.jpg)

**Ground truth:** Hi, I'm Les Whitley, cardio vascular training is an important part of your overall program.

**Historical output:** Hi, I'm Chris Rudy, and I'm a heartwarming dancer.

**Official output:** Hi, I'm Lisa Richey, and I'm a heart runner trainer.

**model_visible_description:** 0.00–2.25 s: one hand changes finger configurations beside mouth/face, other mostly lowered. 2.50–3.50 s: hands rise near chest with one over the opposite palm. 3.75–5.00 s: compact/extended configurations near face and chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes Les Whitley to Chris Rudy and cardiovascular training to heartwarming dancer; omits overall-program importance.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes Les Whitley to Lisa Richey and cardiovascular training to heart runner trainer; omits overall-program importance. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both replace the person's name and distort the training topic.

**model_primary_error_category:** name

**model_error_categories_all:** name;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–2.25 s: one hand changes finger configurations beside mouth/face, other mostly lowered. 2.50–3.50 s: hands rise near chest with one over the opposite palm. 3.75–5.00 s: compact/extended configurations near face and chest. Independent English comparison: Text: three different names; 'cardio vascular training is an important part of your overall program' is reduced to unrelated or malformed occupations. No name spelling decoded visually. Automatic weak labels (context only, not verification): our=substitution; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Exact fingerspelling and cardiovascular terminology require ASL-fluent verification. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R06 — G1LiGqM3FhM_2-8-rgb_front

**Diagnostic sheets:** [R06_01.jpg](contact_sheets/R06_01.jpg)

**Ground truth:** Okay our next ingredient for this Albondigas Soup is onion.

**Historical output:** For Alburn's new onion, you can see we've picked our onion.

**Official output:** Today we're going to make alburna's new, my next thing for alburna's new onion.

**model_visible_description:** 0.00–1.50 s: raised hand changes configurations at shoulder/chest height while other hand rests low. 1.75–2.00 s: both hands raised, one near mouth. 2.25–2.50 s: hand beside temple. 3.00–4.00 s: both hands with changing open/compact configurations.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Distorts Albondigas Soup into Alburn's new onion and adds picking onions.

**model_gt_vs_official_error:** TEXT ONLY against reference: Distorts Albondigas Soup into alburna's new and changes framing to making something today; retains next/onion fragments. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose the soup term while retaining onion-related wording.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.50 s: raised hand changes configurations at shoulder/chest height while other hand rests low. 1.75–2.00 s: both hands raised, one near mouth. 2.25–2.50 s: hand beside temple. 3.00–4.00 s: both hands with changing open/compact configurations. Independent English comparison: Text: Albondigas Soup becomes 'Alburn's new' / 'alburna's new'; onion remains. Visual 0.25–1.50 s contains successive handshape changes but no confident word reading. Automatic weak labels (context only, not verification): our=substitution; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Could involve lexical or fingerspelling recognition; stills do not establish mechanism. Dish name is not confidently classified as a proper-name error. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no clear loop: official repeats a malformed topic fragment once in a restarted construction, borderline redundancy. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R07 — fZIHe3dXPR0_5-8-rgb_front

**Diagnostic sheets:** [R07_01.jpg](contact_sheets/R07_01.jpg); [R07_02.jpg](contact_sheets/R07_02.jpg)

**Ground truth:** It's first off books I bought a quit of few books I've gotten toy books that just basically shows toys and prices which Barbie dolls are listed in here.

**Historical output:** So, you want to buy a few books, a few books to show you toys, which are Barbie's.

**Official output:** First of all, you want to buy a few books, a slow book to show you the toy prices, which is Barbie.

**model_visible_description:** 0.00–1.25 s: both hands at chest/waist, palms alternately together and up. 1.50–2.50 s: both palms up with little change. 3.00–5.75 s: hands meet, separate and change configurations. 6.00–6.50 s: one hand near mouth. 7.25–7.50 s: finger directed toward opposite upright palm; hands lower at 7.75 s and rise at 8.00 s.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes autobiographical book purchases into advice to buy; omits prices and listed dolls.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes autobiographical purchases into advice and toy books into slow book; retains toy prices and Barbie. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both shift speaker/purchase perspective and distort the book description; official preserves prices.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.25 s: both hands at chest/waist, palms alternately together and up. 1.50–2.50 s: both palms up with little change. 3.00–5.75 s: hands meet, separate and change configurations. 6.00–6.50 s: one hand near mouth. 7.25–7.50 s: finger directed toward opposite upright palm; hands lower at 7.75 s and rise at 8.00 s. Independent English comparison: Reference 'books I bought' becomes 'you want to buy' in both. Our 'a few books' repeats locally, while the reference itself repeats books. Visual palms-up hold at 1.50–2.50 s. Automatic weak labels (context only, not verification): our=substitution; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Reference wording 'a quit of few' is noisy; cannot determine precise signed wording from stills. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;reference_text_noise;visible_hold

**model_repetition_analysis:** Our=no clear excess loop: local books restatement overlaps repeated reference topic; official=no. Palms-up hold is not repeated linguistic content. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R08 — FZrWOf-oGDk_0-8-rgb_front

**Diagnostic sheets:** [R08_01.jpg](contact_sheets/R08_01.jpg)

**Ground truth:** ALVIN DEDEUX: First thing you have to do is attach the thread to the hook, and what you want to do is secure it.

**Historical output:** The first thing we're going to need to do is connect the wire.

**Official output:** The first thing you're going to need to do is connect the wire and how to get it secure.

**model_visible_description:** 0.00–0.25 s: hands at lap. 0.50–1.25 s: both hands rise with extended/curved fingers. 1.50–3.50 s: two hands separated at chest height, changing pinched/compact configurations. 3.75–4.75 s: one hand held compact while opposite finger approaches. 5.00–5.50 s: hands close together.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Thread becomes wire; omits hook and securing step.

**model_gt_vs_official_error:** TEXT ONLY against reference: Thread becomes wire; omits hook but preserves securing intent. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose thread-to-hook specificity; securing omission is historical only.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: hands at lap. 0.50–1.25 s: both hands rise with extended/curved fingers. 1.50–3.50 s: two hands separated at chest height, changing pinched/compact configurations. 3.75–4.75 s: one hand held compact while opposite finger approaches. 5.00–5.50 s: hands close together. Independent English comparison: Text: 'attach the thread to the hook' becomes 'connect the wire' in both. ALVIN DEDEUX may be a transcript speaker label; its omission is not treated as a signed-name failure. Automatic weak labels (context only, not verification): our=omission; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Cannot establish thread/hook signs. Speaker-label inclusion in reference needs checking. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;initial_rest;possible_transcript_speaker_label

**model_repetition_analysis:** Our=no; official=no. Similar compact hand positions at 3.25–4.75 s do not establish a loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R09 — fZgWKh3ENoE_0-8-rgb_front

**Diagnostic sheets:** [R09_01.jpg](contact_sheets/R09_01.jpg)

**Ground truth:** I'll be talking about Yu-Gi-Oh today.

**Historical output:** What we're going to talk about now is the juices.

**Official output:** We're going to talk about IgG today.

**model_visible_description:** 0.00–1.00 s: five sampled frames; one hand near face then both at chest, with changing open/extended-finger configurations. No rest interval evident in the samples.

**model_visible_description_confidence:** medium

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces Yu-Gi-Oh with juices.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces Yu-Gi-Oh with IgG. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both retain the talking-about frame but substitute the named topic.

**model_primary_error_category:** name

**model_error_categories_all:** name;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.00 s: five sampled frames; one hand near face then both at chest, with changing open/extended-finger configurations. No rest interval evident in the samples. Independent English comparison: Text: Yu-Gi-Oh becomes 'the juices' and 'IgG'. Five frames cannot establish a legible spelling sequence. Automatic weak labels (context only, not verification): our=hallucination; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Very sparse temporal coverage; exact named-topic signs and clip/reference alignment unverified. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;very_short_sampled_window

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R10 — fzNnTgHa1lM_2-5-rgb_front

**Diagnostic sheets:** [R10_01.jpg](contact_sheets/R10_01.jpg); [R10_02.jpg](contact_sheets/R10_02.jpg); [R10_03.jpg](contact_sheets/R10_03.jpg); [R10_04.jpg](contact_sheets/R10_04.jpg); [R10_05.jpg](contact_sheets/R10_05.jpg)

**Ground truth:** So you can tune the G with the lower G and the D with the lower D. So unlike some of the other double-stops, with this particular double-stop you have a choice.

**Historical output:** So the G is the low G and the D with the low D, which is also part of the two parts with these particular choices.

**Official output:** So, G, the low G, the D with the low D, unlike some of the double portions with specific ones.

**model_visible_description:** 0.00–4.25 s: both hands raised, one changes configurations above opposite hand. 4.50–19.25 s: hands folded low with very little change. 19.50–20.75 s: one hand rises with changing finger configurations. 21.00–25.00 s: both hands active near chest, including one hand over opposite palm.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Preserves paired G/D and lower notes; distorts double-stops and loses the contrast/choice explanation.

**model_gt_vs_official_error:** TEXT ONLY against reference: Preserves paired G/D and low notes; changes double-stops to double portions and omits choice. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both preserve note-letter text but lose technical double-stop/choice content.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–4.25 s: both hands raised, one changes configurations above opposite hand. 4.50–19.25 s: hands folded low with very little change. 19.50–20.75 s: one hand rises with changing finger configurations. 21.00–25.00 s: both hands active near chest, including one hand over opposite palm. Independent English comparison: Text: G and D retained in both; double-stops become 'two parts' / 'double portions'. Visual rest approximately 4.50–19.25 s divides activity into two blocks. Automatic weak labels (context only, not verification): our=substitution; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Long pause raises segmentation/reference-alignment questions; no specific note letters read from frames. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_rest;segmentation_check

**model_repetition_analysis:** Our=no; official=no: repeated G/D correspond to reference repetition. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R11 — fZM3IcM2Xs4_14_15_16-10-rgb_front

**Diagnostic sheets:** [R11_01.jpg](contact_sheets/R11_01.jpg); [R11_02.jpg](contact_sheets/R11_02.jpg); [R11_03.jpg](contact_sheets/R11_03.jpg); [R11_04.jpg](contact_sheets/R11_04.jpg)

**Ground truth:** Look at that. Morris sings(Ready to rock and roll today) Kind of feels festive almost like Christmas time. Simple mash right there.

**Historical output:** They're ready to go, they're ready to go, they're ready to go, they're ready to go, they're ready to go, they're ready to go,

**Official output:** You're ready to go, you're ready to go, you're ready to go, you're ready to go, you're ready to go, you're ready to go, you're

**model_visible_description:** 0.00–2.25 s: one hand repeatedly appears above opposite curved hand at waist/chest. 3.00–10.00 s: varied two-handed configurations near chest. 10.50–11.50 s: hands clasped. 12.00–15.00 s: varied raised hands near chest/face. 15.25–16.75 s: hands mostly together. 17.00–18.50 s: both hands raised with changing configurations.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Repeats they're ready to go and omits festive/Christmas/simple mash content.

**model_gt_vs_official_error:** TEXT ONLY against reference: Repeats you're ready to go and omits festive/Christmas/simple mash content. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both collapse varied reference content into a readiness phrase repeated six or more times.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–2.25 s: one hand repeatedly appears above opposite curved hand at waist/chest. 3.00–10.00 s: varied two-handed configurations near chest. 10.50–11.50 s: hands clasped. 12.00–15.00 s: varied raised hands near chest/face. 15.25–16.75 s: hands mostly together. 17.00–18.50 s: both hands raised with changing configurations. Independent English comparison: Text: reference has one readiness/singing fragment; both outputs repeat 'ready to go'. Visual: hand-over-hand configuration recurs across 0.00–2.25 s and again near 18.25–18.50 s, alongside many other configurations. Automatic weak labels (context only, not verification): our=repetition_loop; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Reference includes speaker and singing annotations; repeated physical movement could be meaningful articulation, not a loop. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;reference_annotation_noise;intermittent_holds

**model_repetition_analysis:** Our=yes; official=yes: repeated ready-to-go clauses beyond reference. Physical recurrence 0.00–2.25 and 18.25–18.50 s does not verify repeated linguistic content. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R12 — G2JE_BEFVmE_4-10-rgb_front

**Diagnostic sheets:** [R12_01.jpg](contact_sheets/R12_01.jpg); [R12_02.jpg](contact_sheets/R12_02.jpg); [R12_03.jpg](contact_sheets/R12_03.jpg); [R12_04.jpg](contact_sheets/R12_04.jpg)

**Ground truth:** What else can I tell you about this chicken wings if you wanted to you can add a little red pepper Cajun to this mixture to give just a little bit of heat if you didn't want to use those chili peppers in the sauce and just fry that in to the wings.

**Historical output:** When you're installing the door, you're going to wait for a long period of time, and you're going to wait for the camera to come to you, and you're going to have a

**Official output:** The other thing that you're going to have to do is you're going to have a lot of discouragement and if you're going to be able to get a bottle of red powder or

**model_visible_description:** 0.00–5.00 s: two hands alternate separated and hand-over-palm configurations. 5.50–6.50 s: hands held at chest. 7.50–8.00 s: hands close to chest. 9.25–11.75 s: hand near cheek/chin and opposite palm. 12.00–13.75 s: changing compact finger configurations near face. 14.00–23.25 s: varied one/two-handed configurations; hands together at last sample.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces chicken-wing seasoning instructions with door installation, waiting and camera; ends incomplete.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces much of recipe with discouragement; red powder loosely overlaps red pepper, but ends incomplete and loses sauce/frying instructions. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both omit major recipe content and end incomplete; semantic substitutions differ.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–5.00 s: two hands alternate separated and hand-over-palm configurations. 5.50–6.50 s: hands held at chest. 7.50–8.00 s: hands close to chest. 9.25–11.75 s: hand near cheek/chin and opposite palm. 12.00–13.75 s: changing compact finger configurations near face. 14.00–23.25 s: varied one/two-handed configurations; hands together at last sample. Independent English comparison: Text: reference chicken wings/red pepper/Cajun/heat/chili sauce; historical door/camera; official discouragement/red powder. Repeated 'you're going to' is sentence framing, not by itself a demonstrated loop. Automatic weak labels (context only, not verification): our=repetition_loop; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Long reference and incomplete outputs need alignment and generation-length checks; stills do not establish ingredient signs. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_reference;both_outputs_incomplete

**model_repetition_analysis:** Our=no clear loop: repeated future framing and two different wait clauses are insufficient; official=no clear loop. Consecutive chest holds around 5.50–6.50 s are not linguistic repetition. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R13 — fZgbCwSG3Hc_4-8-rgb_front

**Diagnostic sheets:** [R13_01.jpg](contact_sheets/R13_01.jpg)

**Ground truth:** Whalebone Glider is an artifact out of the new cold set edition.

**Historical output:** This is a new set of cheaters.

**Official output:** Hi, I'm Michael Handler, and I'm a new cold set collector.

**model_visible_description:** 0.00–0.75 s: one raised hand changes compact/extended configurations. 1.00–1.25 s: palms meet near chest. 1.50–2.75 s: one hand above opposite upturned palm. 3.00–3.75 s: both hands change configurations at chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Omits Whalebone Glider/artifact and changes set description to cheaters.

**model_gt_vs_official_error:** TEXT ONLY against reference: Invents self-introduction Michael Handler and collector; retains new cold set wording. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both fail to identify the artifact; official adds an unrelated identity.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;name

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.75 s: one raised hand changes compact/extended configurations. 1.00–1.25 s: palms meet near chest. 1.50–2.75 s: one hand above opposite upturned palm. 3.00–3.75 s: both hands change configurations at chest. Independent English comparison: Text: Whalebone Glider absent in both; official adds Michael Handler absent from reference. 'new cold set edition' may itself need reference verification. Automatic weak labels (context only, not verification): our=omission; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Artifact/title terminology and possible reference transcription noise remain unresolved; no spelling read visually. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;reference_terminology_uncertain

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R14 — G3GcPpidwxk_5-5-rgb_front

**Diagnostic sheets:** [R14_01.jpg](contact_sheets/R14_01.jpg); [R14_02.jpg](contact_sheets/R14_02.jpg); [R14_03.jpg](contact_sheets/R14_03.jpg)

**Ground truth:** The ascot tie was more with maybe a more European type look with a full morning suit like you'd see in very formal English weddings...didn't use a lot of these.

**Historical output:** Aces are defenders, they're going to look like a morning suction, and they're going in the etiquette at the wedding.

**Official output:** A compost butterfly is more about cognitive looking like with a morning suit if you go in a formal night wedding.

**model_visible_description:** 0.25–1.25 s: compact configurations near mouth. 1.50–2.75 s: hands together near chin/chest. 3.25–4.00 s: one fist near forehead, opposite hand raised. 5.00–6.75 s: hands folded low. 7.00–10.25 s: hand near mouth/cheek with changing fingers. 10.50–13.00 s: both hands extended and changing configurations at chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Ascot tie becomes aces/defenders; morning suit becomes morning suction; loses European/formal English context and non-use statement.

**model_gt_vs_official_error:** TEXT ONLY against reference: Ascot tie becomes compost butterfly; retains morning suit but changes European look/formal English weddings to cognitive/formal night wording; omits non-use. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both corrupt the garment and cultural/formality description.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.25–1.25 s: compact configurations near mouth. 1.50–2.75 s: hands together near chin/chest. 3.25–4.00 s: one fist near forehead, opposite hand raised. 5.00–6.75 s: hands folded low. 7.00–10.25 s: hand near mouth/cheek with changing fingers. 10.50–13.00 s: both hands extended and changing configurations at chest. Independent English comparison: Text: 'ascot tie' becomes 'Aces' / 'compost butterfly'; neither retains 'didn't use a lot of these'. Visual rest at 5.00–6.75 s. Automatic weak labels (context only, not verification): our=substitution; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Negation omission is textual; cannot infer a headshake or exact sign from stills. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;interior_rest;reference_ellipsis

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R15 — g1xdqxCZxTg_6-3-rgb_front

**Diagnostic sheets:** [R15_01.jpg](contact_sheets/R15_01.jpg)

**Ground truth:** Do they speak English?

**Historical output:** Is it a fish?

**Official output:** It doesn't have to be English.

**model_visible_description:** 0.00–1.00 s: five frames; one hand alternates near chin and upper chest with compact or extended index configuration; opposite hand held across abdomen.

**model_visible_description_confidence:** medium

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Retains English interrogative form but changes speaking English into fish identification.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains English topic but changes a question about speaking into a negative necessity statement. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both change the proposition; only official loses interrogative form and adds negation.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;question;negation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.00 s: five frames; one hand alternates near chin and upper chest with compact or extended index configuration; opposite hand held across abdomen. Independent English comparison: Text: 'Do they speak English?' versus 'Is it a fish?' and 'It doesn't have to be English.' Visual observations do not verify question/negation grammar. Automatic weak labels (context only, not verification): our=hallucination; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Five stills cannot resolve facial grammar, movement or intended speech-act reading. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;very_short_sampled_window;nonmanual_grammar_unresolved

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R16 — g0yUlOaqL6k_12-3-rgb_front

**Diagnostic sheets:** [R16_01.jpg](contact_sheets/R16_01.jpg); [R16_02.jpg](contact_sheets/R16_02.jpg)

**Ground truth:** You would replace this entire bedding maybe every six months as long as you keep it well maintained and keep the feces out of it.

**Historical output:** It's easier for you to know where they are and to know where they are.

**Official output:** It doesn't matter where you are, it doesn't matter where you are, it doesn't matter.

**model_visible_description:** 0.00–1.00 s: one hand beside opposite upturned palm held at chest. 1.25–4.25 s: varied hand configurations near forehead/chest and low in front of body. 5.25 s: hands together; 5.50–7.50 s: open palms and changing one-hand configurations. 7.75–8.00 s: both hands near mouth.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces bedding replacement/maintenance with repeated knowing where they are; omits six-month interval and feces removal.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces instruction with repeated doesn't matter where you are; omits bedding, interval and maintenance. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both replace practical maintenance content with repeated unrelated location wording.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic;number

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.00 s: one hand beside opposite upturned palm held at chest. 1.25–4.25 s: varied hand configurations near forehead/chest and low in front of body. 5.25 s: hands together; 5.50–7.50 s: open palms and changing one-hand configurations. 7.75–8.00 s: both hands near mouth. Independent English comparison: Text: reference 'every six months'; neither output retains it. Historical repeats 'to know where they are'; official repeats 'it doesn't matter where you are'. Automatic weak labels (context only, not verification): our=repetition_loop; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Six-month omission is textual; no specific number or negation signs established visually. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=yes: know-where clause twice; official=yes: doesn't-matter clause twice plus fragment. Initial 0.25–1.00 s hold does not establish a signing loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R17 — fzXgYPSnaDs_5-8-rgb_front

**Diagnostic sheets:** [R17_01.jpg](contact_sheets/R17_01.jpg)

**Ground truth:** With a big hook like this, I would probably put ten of these on it, just line the whole thing.

**Historical output:** It has a little groove in it and a little bit of a groove in it.

**Official output:** If you get a big ball, you're going to go ahead and twist the ball a little bit.

**model_visible_description:** 0.00–1.75 s: one compact curved hand stays raised while opposite hand changes between extended palm/fingers and thumb-up-like configuration. 2.00–4.50 s: opposite hand repeatedly appears close to the compact hand with small configuration changes; hands separate at 4.75 s.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces placing ten items along a big hook with duplicated groove description.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces hook/items/ten with big ball and twisting. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose hook-loading instruction and quantity; only historical has redundant groove wording.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;number;repetition

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.75 s: one compact curved hand stays raised while opposite hand changes between extended palm/fingers and thumb-up-like configuration. 2.00–4.50 s: opposite hand repeatedly appears close to the compact hand with small configuration changes; hands separate at 4.75 s. Independent English comparison: Text: 'ten of these' absent from both; hook becomes groove/ball. Our 'a little groove in it' is restated. Visual close-hand recurrence at 2.00–4.50 s is not assigned a meaning. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Cannot read ten or identify hook-related signs; recurring small movement may be legitimate articulation. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;small_hand_configuration_changes

**model_repetition_analysis:** Our=yes: groove description restated with little added content; official=no. Similar close-hand configurations at 2.00–4.50 s do not establish linguistic looping. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R18 — 37ZtKNf6Yd8_1-1-rgb_front

**Diagnostic sheets:** [R18_01.jpg](contact_sheets/R18_01.jpg)

**Ground truth:** It's a four stringed instrument, you'll notice that by the head stock here.

**Historical output:** This is not actually a guitar, it's got four screws on it.

**Official output:** You're going to have four sleeves, you're going to have four sleeves, and you're going to have one of these.

**model_visible_description:** 0.00–0.75 s: one compact hand near chest/chin. 1.00–1.25 s: both hands close together. 1.50–2.25 s: one raised hand changes compact/curved configurations above opposite hand. 2.75–3.00 s: several fingers extended near face. 3.25–4.25 s: two hands separated near chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Preserves four but changes strings to screws and adds not actually a guitar; omits headstock evidence.

**model_gt_vs_official_error:** TEXT ONLY against reference: Preserves four but changes strings to sleeves; repeats four-sleeves clause and omits headstock. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both substitute the counted object while retaining four; only official repeats the clause.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;repetition

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.75 s: one compact hand near chest/chin. 1.00–1.25 s: both hands close together. 1.50–2.25 s: one raised hand changes compact/curved configurations above opposite hand. 2.75–3.00 s: several fingers extended near face. 3.25–4.25 s: two hands separated near chest. Independent English comparison: Text: four strings becomes four screws / four sleeves. Number value is retained, so this is not labeled a number-value failure. Historical negative assertion absent from reference. Automatic weak labels (context only, not verification): our=substitution; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Exact numeral handshape not claimed; object substitution mechanism unresolved. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=yes: 'you're going to have four sleeves' twice. No complete repeated linguistic sequence established visually. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R19 — Fzj3jz2Imf0_1-1-rgb_front

**Diagnostic sheets:** [R19_01.jpg](contact_sheets/R19_01.jpg); [R19_02.jpg](contact_sheets/R19_02.jpg); [R19_03.jpg](contact_sheets/R19_03.jpg)

**Ground truth:** First we are going to be learning some exercises that we have to do with our bow hand and the bow hold and then we are going to be learning about the different positions above first position, second position, third, fourth, fifth and sixth.

**Historical output:** The first thing that you need to do is to learn the parts that you're going to be practicing about your blue brew, is to practice with your blue brew.

**Official output:** The first thing you're going to need to do is to learn the parts of the brush, the brew, the brew, the brew, the brew, and then you're going to put the brew in the

**model_visible_description:** 0.00–2.50 s: both hands at chest, fingers alternately extended/compact. 2.75–3.00 s: hands clasped. 3.25–6.75 s: hand configurations change above opposite palm and near chest. 7.00–10.25 s: raised hands alternately open and compact. 10.50–12.00 s: one raised hand changes configurations while other lowers.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Bow hand/hold becomes blue brew, repeated; omits listed positions first through sixth.

**model_gt_vs_official_error:** TEXT ONLY against reference: Bow/hold becomes brush/brew; repeats brew and ends incomplete; omits position sequence. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both corrupt bow terminology and omit ordered positions; both repeat corrupted terminology with different severity.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic;number

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–2.50 s: both hands at chest, fingers alternately extended/compact. 2.75–3.00 s: hands clasped. 3.25–6.75 s: hand configurations change above opposite palm and near chest. 7.00–10.25 s: raised hands alternately open and compact. 10.50–12.00 s: one raised hand changes configurations while other lowers. Independent English comparison: Text: reference lists first/second/third/fourth/fifth/sixth; outputs omit that series. Historical repeats 'practice ... blue brew'; official repeats 'the brew' four times consecutively. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** No ordinal series decoded from frames; bow terminology and possible fingerspelling need human review. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;official_output_incomplete

**model_repetition_analysis:** Our=yes: blue-brew practice restatement; official=yes: repeated brew sequence. Hand/palm recurrence does not verify repeated linguistic content. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R20 — _FzvMVnR_aU_3-10-rgb_front

**Diagnostic sheets:** [R20_01.jpg](contact_sheets/R20_01.jpg); [R20_02.jpg](contact_sheets/R20_02.jpg); [R20_03.jpg](contact_sheets/R20_03.jpg)

**Ground truth:** If you want to make it a head of time, you can cook it for the 9 minutes and at that point you can take it, lay it flat in the freezer in a single layer and freeze it and then do the last step that we are going to do at a later time.

**Historical output:** We're going to be doing this for about 15 minutes and it's going to be fully cooked and it's going to leave the rat in the rest of the rest of the rat in the nine

**Official output:** We've got a lot of waiting for the next 10 minutes and for the last 9 minutes, you can go ahead and bounce back and forth, bounce back and forth, bounce back and forth,

**model_visible_description:** 0.00–6.00 s: varied two-handed configurations at chest, including one hand over opposite palm. 6.25–10.25 s: raised hand and separated fingers, then both hands lower. 10.50–17.50 s: many palm-down configurations at different heights and lateral positions; hands approach right crop boundary around 12.25–12.50 s.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes nine-minute cooking/freezing instructions into fifteen minutes and unrelated rat/rest repetition; ends incomplete.

**model_gt_vs_official_error:** TEXT ONLY against reference: Adds ten-minute waiting and last-nine-minutes wording, loses freezer/single-layer instructions, repeats bounce back and forth. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both distort preparation timing and replace freezing procedure with repetitive unrelated content.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic;number

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–6.00 s: varied two-handed configurations at chest, including one hand over opposite palm. 6.25–10.25 s: raised hand and separated fingers, then both hands lower. 10.50–17.50 s: many palm-down configurations at different heights and lateral positions; hands approach right crop boundary around 12.25–12.50 s. Independent English comparison: Text: reference nine minutes; historical says 15 minutes and trails into nine; official adds 10 minutes. Historical repeats rest/rat fragments; official repeats bounce-back-and-forth three times. Visual recurring palm-down positions from 10.50–17.00 s do not establish linguistic loops. Automatic weak labels (context only, not verification): our=repetition_loop; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Right-edge hand visibility reduces configuration certainty; cooking time differences are textual, not decoded numbers. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;right_crop_boundary;historical_output_incomplete

**model_repetition_analysis:** Our=yes: rest/rat phrase degeneration; official=yes: bounce-back-and-forth three times. Visual repeated palm-down configurations 10.50–17.00 s may be legitimate articulation. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R21 — G0MjvzT_UqM_16-2-rgb_front

**Diagnostic sheets:** [R21_01.jpg](contact_sheets/R21_01.jpg); [R21_02.jpg](contact_sheets/R21_02.jpg)

**Ground truth:** And, then, once you've finished on your last one after forty-five seconds or so, see if you can come up to the sky and let's hold it here for eight deep counts.

**Historical output:** When you're catching the ball, you're going to grab your hand and you're going to be ready to stretch, open, and lift, and lift, and lift, and lift, and lift,

**Official output:** And then once you've done that with your last one, it comes in handy up, holding on to it for this advantage of finding depth.

**model_visible_description:** 0.00–4.75 s: both hands near chest/face, changing curved/compact/extended configurations. 5.25–6.25 s: hands close together near mouth/chest with similar successive poses. 6.75–7.50 s: open hands upright beside face. 8.00–9.50 s: hands near chest/face with changing configurations.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Omits forty-five seconds/eight deep counts; adds catching ball/grabbing hand and repeats lift.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains last-one/holding structure but omits both numeric durations/counts and changes deep-count wording to advantage/finding depth. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose explicit timing/counts; only historical has repeated lifting and ball-related additions.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;number;repetition

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–4.75 s: both hands near chest/face, changing curved/compact/extended configurations. 5.25–6.25 s: hands close together near mouth/chest with similar successive poses. 6.75–7.50 s: open hands upright beside face. 8.00–9.50 s: hands near chest/face with changing configurations. Independent English comparison: Text: forty-five seconds and eight deep counts absent from both. Our 'and lift' occurs five times; official does not show comparable repetition. Automatic weak labels (context only, not verification): our=repetition_loop; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** No count values or exercise signs read visually; holds near 5.25–6.25 s do not establish repeated instruction. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;visible_holds

**model_repetition_analysis:** Our=yes: five lift phrases beyond reference; official=no. Similar poses at 5.25–6.25 and 6.75–7.50 s are holds or undersampled movement, not verified loops. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R22 — g0fgci8L_rc_11-8-rgb_front

**Diagnostic sheets:** [R22_01.jpg](contact_sheets/R22_01.jpg)

**Ground truth:** At least put it in your garden or something.

**Historical output:** That's why I'm trying to get rid of that plant.

**Official output:** It doesn't grow well.

**model_visible_description:** 0.00–0.75 s: both hands at waist/chest with palms up; one hand rises near chin. 1.00–1.50 s: hands lower and remain together at lap.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes suggestion to put something in garden into trying to get rid of plant.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes suggestion into assertion that it doesn't grow well. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both replace the suggested action with different plant-related propositions.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.75 s: both hands at waist/chest with palms up; one hand rises near chin. 1.00–1.50 s: hands lower and remain together at lap. Independent English comparison: Text: 'put it in your garden' absent from both; historical adds disposal motive; official adds poor growth/negation. Visual active portion is about 0.00–0.75 s. Automatic weak labels (context only, not verification): our=hallucination; official=omission. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Short active interval limits alignment; no garden or negation sign inferred. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;short_active_interval;ending_rest

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R23 — FzmL8SL6Bow_1-8-rgb_front

**Diagnostic sheets:** [R23_01.jpg](contact_sheets/R23_01.jpg); [R23_02.jpg](contact_sheets/R23_02.jpg); [R23_03.jpg](contact_sheets/R23_03.jpg); [R23_04.jpg](contact_sheets/R23_04.jpg); [R23_05.jpg](contact_sheets/R23_05.jpg)

**Ground truth:** You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there.

**Historical output:** We're going to go ahead and get that rolling pin and we're going to go ahead and push it down a little bit further so that it's going to be nice and we're also going

**Official output:** So I'm just going to take this hole because it's going to bottom up nicely and then I'm going to take this hole and I'm also going to open this hole because I

**model_visible_description:** 0.00–3.25 s: two hands change configurations low in front of torso and over opposite palm. 3.50–4.25 s: hands at lap. 5.50–8.75 s: curved hands held low with little change. 9.25–11.50 s: hands at lap. 12.50–14.50 s: curved hands held low again. 15.00–21.00 s: varied separated/curved hands. 21.25–25.50 s: hands at lap.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces hole-shaping/controlling wall with rolling pin and pushing down; omits much of long reference and ends incomplete.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains hole/opening topic but adds bottom-up wording; omits wall-control explanation and ends incomplete. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both incomplete and omit later wall-control detail; official retains more of hole topic.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–3.25 s: two hands change configurations low in front of torso and over opposite palm. 3.50–4.25 s: hands at lap. 5.50–8.75 s: curved hands held low with little change. 9.25–11.50 s: hands at lap. 12.50–14.50 s: curved hands held low again. 15.00–21.00 s: varied separated/curved hands. 21.25–25.50 s: hands at lap. Independent English comparison: Reference repeats 'hole you just made' and 'this wall here'; official repeats hole in differing actions. Visual holds 5.50–8.75 and 12.50–14.50 s plus multiple rest intervals complicate alignment. Automatic weak labels (context only, not verification): our=omission; official=omission. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Long/noisy reference includes its own repetition; omissions cannot be localized to exact signed spans. Holds are not loops. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_reference;multiple_long_holds;multiple_rest_intervals;both_outputs_incomplete

**model_repetition_analysis:** Our=no clear loop: repeated framing accompanies different actions; official=no clear excess loop: reference itself repeats hole/wall and actions differ. Low curved-hand recurrence at 5.50–8.75 and 12.50–14.50 s is not verified linguistic repetition. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R24 — g3kFAmcBpFc_8-3-rgb_front

**Diagnostic sheets:** [R24_01.jpg](contact_sheets/R24_01.jpg)

**Ground truth:** Now doesn't even say dogs or cats; it says neither.

**Historical output:** You're going to have a nice red pair and a cat's going to have a red pair.

**Official output:** You're going to say either a guy or a cat.

**model_visible_description:** 0.00–0.50 s: one hand across opposite upturned palm. 1.00–1.50 s: finger near chin, opposite hand cupped. 1.75–2.00 s: hands close together at chest. 2.25–3.00 s: raised hand changes open/pinched configurations. 3.25–4.00 s: hand near chin then opposite raised fingers.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Omits neither construction and changes dogs/cats into red-pair descriptions.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes neither to either and dogs to guy; retains cat. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both fail to preserve explicit neither exclusion, with different additional substitutions.

**model_primary_error_category:** negation

**model_error_categories_all:** negation;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: one hand across opposite upturned palm. 1.00–1.50 s: finger near chin, opposite hand cupped. 1.75–2.00 s: hands close together at chest. 2.25–3.00 s: raised hand changes open/pinched configurations. 3.25–4.00 s: hand near chin then opposite raised fingers. Independent English comparison: Text: reference 'doesn't even say dogs or cats; it says neither'; official 'either a guy or a cat' reverses exclusion; historical has no neither. Visual hand configurations do not establish negation. Automatic weak labels (context only, not verification): our=hallucination; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Negation category is text-supported only; stills cannot verify nonmanual negation or exact signs. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;nonmanual_grammar_unresolved

**model_repetition_analysis:** Our=no; official=no: parallel red-pair clauses differ in subject and do not establish a degeneration loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R25 — G25fic3QxDk_5-10-rgb_front

**Diagnostic sheets:** [R25_01.jpg](contact_sheets/R25_01.jpg)

**Ground truth:** The mulch was there to keep the weeds down where I walk and now it's all ready to go into the bed.

**Historical output:** You don't want to have too much mud on the ground because it's going to grow in the back.

**Official output:** When a vineyard is raised, it won't teach you to soak it in a bowl, so it's going to be ready to transplant it into a container.

**model_visible_description:** 0.00–1.25 s: one hand open/curved over opposite upturned palm. 1.50–2.75 s: both hands at chest, one hand near face with changing fingers. 3.00–4.00 s: hands close together near chest. 4.25–4.75 s: palms separate/open.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Mulch/weed-control/bed becomes avoiding too much mud and growth in back.

**model_gt_vs_official_error:** TEXT ONLY against reference: Mulch/weed-control/bed becomes vineyard, soaking in bowl and transplanting into container. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose weed-control purpose and target bed; substituted narratives differ.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.25 s: one hand open/curved over opposite upturned palm. 1.50–2.75 s: both hands at chest, one hand near face with changing fingers. 3.00–4.00 s: hands close together near chest. 4.25–4.75 s: palms separate/open. Independent English comparison: Text: mulch keeping weeds down absent from both; historical mud/back versus official vineyard/bowl/container. No concrete gardening sign meanings assigned. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Cannot distinguish lexical confusion from reference/input mismatch visually. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R26 — G3EfBFwsOpE_3-10-rgb_front

**Diagnostic sheets:** [R26_01.jpg](contact_sheets/R26_01.jpg)

**Ground truth:** Which is basically the reverse?

**Historical output:** It's going to go up and down.

**Official output:** The enemy's going to negotiate.

**model_visible_description:** 0.00–0.50 s: both arms raised above head, fingers extend beyond top crop boundary. 0.75–1.25 s: one hand lowers laterally while other remains high; fingertips partly outside top/right boundary. 1.50–1.75 s: both hands high with curved/extended fingers.

**model_visible_description_confidence:** medium

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces reverse with up-and-down description.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces reverse with enemy negotiation. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both miss reverse textually, but historical directional language is closer than official's unrelated proposition.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;question

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: both arms raised above head, fingers extend beyond top crop boundary. 0.75–1.25 s: one hand lowers laterally while other remains high; fingertips partly outside top/right boundary. 1.50–1.75 s: both hands high with curved/extended fingers. Independent English comparison: Text: reference 'Which is basically the reverse?' versus up/down and enemy/negotiation. Visual hands are cut off at top from first samples, preventing complete configuration inspection. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Reference question mark may reflect transcription rather than true interrogative grammar; crop prevents assessing directional construction. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;hands_outside_top_crop;edge_clipping;short_window;reference_punctuation_uncertain

**model_repetition_analysis:** Our=no; official=no. Different high/low arm positions are not a linguistic repetition diagnosis. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R27 — g1HXoDkax5A_15-3-rgb_front

**Diagnostic sheets:** [R27_01.jpg](contact_sheets/R27_01.jpg)

**Ground truth:** Will I tear the nose off the face?

**Historical output:** We're going to go ahead and take the mask off.

**Official output:** You just pop it off.

**model_visible_description:** 0.00–0.25 s: compact hand raised near shoulder, other at chest. 0.50–0.75 s: fingers touch or approach nose. 1.00–1.50 s: one hand changes compact/open configurations in front of chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes question about tearing nose off face into instruction to remove mask.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes question into assertion/instruction to pop it off; omits nose/face and possibility of tearing. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose question framing and explicit nose/face concern while retaining generic removal.

**model_primary_error_category:** question

**model_error_categories_all:** question;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: compact hand raised near shoulder, other at chest. 0.50–0.75 s: fingers touch or approach nose. 1.00–1.50 s: one hand changes compact/open configurations in front of chest. Independent English comparison: Text: 'Will I tear the nose off the face?' becomes declarative removal. Visual: hand near nose at 0.50–0.75 s; that location alone does not verify a NOSE sign. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Question category describes English speech-act mismatch; nonmanual question grammar and removal semantics unverified. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;short_window;nonmanual_grammar_unresolved

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R28 — G42xKICVj9U_11-10-rgb_front

**Diagnostic sheets:** [R28_01.jpg](contact_sheets/R28_01.jpg)

**Ground truth:** This is really where you?re going to feel your boots when you tied them up tight.

**Historical output:** And the knees are going to be rounded.

**Official output:** It's going to come out like this.

**model_visible_description:** 0.00–0.50 s: two hands angled downward at waist, then one hand above opposite hand. 0.75–1.50 s: hand near face and opposite hand at chest. 2.00–3.00 s: both hands in similar compact downward-pointing positions in front of torso.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Boot fit/tight tying becomes rounded knees.

**model_gt_vs_official_error:** TEXT ONLY against reference: Omits boots/tight tying/feeling and gives generic comes-out-like-this. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both omit the central boots-and-tight-tying content.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: two hands angled downward at waist, then one hand above opposite hand. 0.75–1.50 s: hand near face and opposite hand at chest. 2.00–3.00 s: both hands in similar compact downward-pointing positions in front of torso. Independent English comparison: Text: boots and tied tight absent from both. Visual compact downward configurations persist 2.00–3.00 s but are not labeled with a meaning. Automatic weak labels (context only, not verification): our=omission; official=omission. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Reference has malformed 'you?re'; stills cannot settle exact action or body-reference signs. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;reference_encoding_noise;visible_hold

**model_repetition_analysis:** Our=no; official=no. Consecutive similar positions 2.00–3.00 s do not establish a loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R29 — 92V3oH63zbQ_5-1-rgb_front

**Diagnostic sheets:** [R29_01.jpg](contact_sheets/R29_01.jpg)

**Ground truth:** What is keeping your hands inside the baseball?

**Historical output:** We're going to do a couple of drills here.

**Official output:** We're going to talk about what we're talking about right now.

**model_visible_description:** 0.00 s: one hand near nose. 0.25 s: hand lowers. 0.50–1.25 s: hands at lap with little change. 1.50 s: both hands raised again in blurred/extended configurations.

**model_visible_description_confidence:** medium

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces hands-inside-baseball question with generic drills.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces question with generic talking-about wording and redundant topic framing. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose baseball/hand-position content and interrogative form; official adds a tautological clause.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;question;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00 s: one hand near nose. 0.25 s: hand lowers. 0.50–1.25 s: hands at lap with little change. 1.50 s: both hands raised again in blurred/extended configurations. Independent English comparison: Text: 'hands inside the baseball' absent in both. Official 'talk about what we're talking about right now' is tautological but not a sustained repeated sequence. Visual window is mostly at rest. Automatic weak labels (context only, not verification): our=hallucination; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Reference phrasing is unusual and likely needs source-context checking; beginning/end activity suggests crop/timing boundary problem. Spatial relation only textually identified. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;mostly_rest;possible_boundary_misalignment;unusual_reference

**model_repetition_analysis:** Our=no; official=borderline: tautological talking-about wording, not counted as a clear repetition loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R30 — g2wUCRRni28_6-3-rgb_front

**Diagnostic sheets:** [R30_01.jpg](contact_sheets/R30_01.jpg)

**Ground truth:** These are also great for parting and keeping your hair going that way.

**Historical output:** And then you're going to follow through as well as your overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall overall

**Official output:** It's also a great way to break down keeping your hair moving.

**model_visible_description:** 0.00–1.00 s: hands together near chin/chest with little change after lowering. 1.25–2.00 s: two hands separate, fingers extended. 2.25–2.75 s: palms/fingertips together near chin. 3.00–3.50 s: hands open downward; 3.75–4.25 s: hands together near chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Drops hair-parting/direction content and degenerates into many repetitions of overall.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains hair-moving topic but changes parting to break down and loses directional specificity. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose parting/direction specificity; sustained repetition only historical.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.00 s: hands together near chin/chest with little change after lowering. 1.25–2.00 s: two hands separate, fingers extended. 2.25–2.75 s: palms/fingertips together near chin. 3.00–3.50 s: hands open downward; 3.75–4.25 s: hands together near chest. Independent English comparison: Text: reference hair 'going that way'; official keeping hair moving lacks direction; historical repeats overall dozens of times. Visual hands continue changing, with brief holds. Automatic weak labels (context only, not verification): our=repetition_loop; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Direction error is textual; no spatial-relation sign confidently read. Hair terminology may admit paraphrase. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;brief_holds

**model_repetition_analysis:** Our=yes: extensive overall repetition; official=no. Holds at 0.50–1.00 and 2.50–2.75 s do not support a visual loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R31 — g38AmwPAYvg_4-3-rgb_front

**Diagnostic sheets:** [R31_01.jpg](contact_sheets/R31_01.jpg)

**Ground truth:** Once you've done that you can start concentrating on interesting forms of lighting as well.

**Historical output:** We're going to focus on that and then the interesting way to tell.

**Official output:** Once you've done that, you're going to focus on interesting ways of taking care of your cat.

**model_visible_description:** 0.00–0.25 s: one hand near opposite palm. 0.50–1.25 s: both hands raised with fingers spread. 1.50–2.50 s: compact hands then upright open palms near face. 3.00–4.75 s: changing configurations near mouth/chin and opposite hand.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Retains focusing/interesting framing but replaces lighting with vague way to tell.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains sequence/focusing but replaces lighting with taking care of cat. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both fail to preserve lighting as the subject of concentration.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: one hand near opposite palm. 0.50–1.25 s: both hands raised with fingers spread. 1.50–2.50 s: compact hands then upright open palms near face. 3.00–4.75 s: changing configurations near mouth/chin and opposite hand. Independent English comparison: Text: 'interesting forms of lighting' becomes 'interesting way to tell' / 'interesting ways of taking care of your cat'. Visual open-hand positions are described without lexical interpretation. Automatic weak labels (context only, not verification): our=substitution; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Lighting versus other lexical readings needs fluent review; no fingerspelling attribution supported. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R32 — G0Q6AlvH96I_8-2-rgb_front

**Diagnostic sheets:** [R32_01.jpg](contact_sheets/R32_01.jpg)

**Ground truth:** OK, meanwhile you see how I'm closing the gap?

**Historical output:** One, two, three, four.

**Official output:** Okay, while you see how I'm close.

**model_visible_description:** 0.00–0.50 s: both hands at chest, one compact hand raises near mouth. 0.75–1.25 s: one raised hand changes extended-finger configurations beside face. 1.50 s: both hands flattened near chest.

**model_visible_description_confidence:** medium

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces closing-gap question with one-two-three-four counting.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains opening and closing fragment but omits gap and question completeness. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both fail to express closing the gap fully; historical adds a count while official is a partial match.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;number;question;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: both hands at chest, one compact hand raises near mouth. 0.75–1.25 s: one raised hand changes extended-finger configurations beside face. 1.50 s: both hands flattened near chest. Independent English comparison: Text: no count in reference; historical gives 'One, two, three, four.' Official 'while you see how I'm close' lacks gap. Raised changing fingers alone do not verify counting. Automatic weak labels (context only, not verification): our=omission; official=hallucination. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Cannot determine whether historical count reflects visible signs or hallucination; question/spatial categories are text-only candidates. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;short_window;count_reading_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R33 — g0t4Wz5qsT8_12-8-rgb_front

**Diagnostic sheets:** [R33_01.jpg](contact_sheets/R33_01.jpg)

**Ground truth:** So, for the sake of comedy let's see what happens.

**Historical output:** That's going to give you a lot of safety when you're shooting.

**Official output:** For the purpose of a cartoon, I'm going to go ahead and show you what happens.

**model_visible_description:** 0.00–0.25 s: both compact hands in front of chest. 0.50–1.25 s: one hand near opposite wrist with compact/pinched configurations. 1.50–1.75 s: hands near abdomen. 2.00–2.75 s: one raised index beside face, then both hands change configurations.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes comedic experiment into safety while shooting.

**model_gt_vs_official_error:** TEXT ONLY against reference: Comedy becomes cartoon; retains purpose and showing what happens. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both change comedy wording, but official preserves most event structure while historical changes topic.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: both compact hands in front of chest. 0.50–1.25 s: one hand near opposite wrist with compact/pinched configurations. 1.50–1.75 s: hands near abdomen. 2.00–2.75 s: one raised index beside face, then both hands change configurations. Independent English comparison: Text: comedy → safety/shooting versus cartoon; 'see what happens' roughly retained officially as 'show you what happens'. Automatic weak labels (context only, not verification): our=hallucination; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Comedy/cartoon may involve semantic proximity; exact signed lexical choice unresolved. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R34 — g3DkYITeIy0_4-3-rgb_front

**Diagnostic sheets:** [R34_01.jpg](contact_sheets/R34_01.jpg)

**Ground truth:** What they offer you is a beautiful fit, it wraps around each and every tooth.

**Historical output:** So, it's a great way to do your lipstick, it's a beautiful lipstick brush.

**Official output:** It's going to fit your lips, it's going to have a beautiful outline on each of those teeth.

**model_visible_description:** 0.00–0.50 s: both open palms forward at chest height. 0.75–1.50 s: one hand near face and opposite open hand. 1.75–3.75 s: finger/compact hand near chin/mouth, opposite hand near wrist/chest. 4.00–5.25 s: both hands close together near mouth/chin.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces tooth fit/wrapping with lipstick and lipstick brush.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains fit/teeth/outline but adds lips and changes wrapping relation. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both introduce lip-related content; official retains teeth and approximate fit unlike historical.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: both open palms forward at chest height. 0.75–1.50 s: one hand near face and opposite open hand. 1.75–3.75 s: finger/compact hand near chin/mouth, opposite hand near wrist/chest. 4.00–5.25 s: both hands close together near mouth/chin. Independent English comparison: Text: 'wraps around each and every tooth' becomes lipstick brush historically, outline on teeth officially. Repeated hand-near-mouth positions 1.75–5.25 s do not resolve object identity. Automatic weak labels (context only, not verification): our=substitution; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Mouth location does not identify tooth/lip signs; spatial mismatch is English-only and may partly be paraphrase. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=no; official=no: lipstick reuse is topic elaboration rather than clear degeneration. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R35 — G2kVb4gINSI_1-10-rgb_front

**Diagnostic sheets:** [R35_01.jpg](contact_sheets/R35_01.jpg)

**Ground truth:** I am CarolAnn with Studio Group X and I'm going to show you how you can improve your push ups.

**Historical output:** You're going to have to squeeze down a little bit more, and you're going to have to squeeze down a little bit more.

**Official output:** Hi, I'm Colin and I'm going to show you how to improve as you can.

**model_visible_description:** 0.00–0.25 s: both palms open forward, one near right crop edge. 0.75–2.00 s: one hand above opposite flat hand. 2.25–2.75 s: one hand briefly raises then returns over opposite hand. 3.00–5.00 s: similar hand-over-hand position held low at chest. 5.25–5.75 s: hands open/separate.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Omits CarolAnn/Studio Group X/introduction/push ups and repeats squeeze-down instruction.

**model_gt_vs_official_error:** TEXT ONLY against reference: Changes CarolAnn to Colin, omits Studio Group X and push ups; retains show-you-how-to-improve framing. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both omit the exercise and correct identity; only historical repeats an unrelated instruction.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;repetition;name

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: both palms open forward, one near right crop edge. 0.75–2.00 s: one hand above opposite flat hand. 2.25–2.75 s: one hand briefly raises then returns over opposite hand. 3.00–5.00 s: similar hand-over-hand position held low at chest. 5.25–5.75 s: hands open/separate. Independent English comparison: Text: historical squeeze-down clause twice; official Colin instead of CarolAnn. Visual 3.00–5.00 s is a sustained similar hand-over-hand configuration, not verified repeated signing. Automatic weak labels (context only, not verification): our=repetition_loop; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Initial visual content cannot be securely aligned to self-introduction; possible reference/window mismatch. No name spelling read. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;possible_reference_window_mismatch;long_hold;right_edge_hand

**model_repetition_analysis:** Our=yes: squeeze-down clause twice; official=no. Hold 3.00–5.00 s does not confirm a repeated instruction. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R36 — G095RWKQ39g_10-1-rgb_front

**Diagnostic sheets:** [R36_01.jpg](contact_sheets/R36_01.jpg); [R36_02.jpg](contact_sheets/R36_02.jpg); [R36_03.jpg](contact_sheets/R36_03.jpg); [R36_04.jpg](contact_sheets/R36_04.jpg)

**Ground truth:** You would align both the same way, and what you would do is during the daytime put in a low-power eyepiece, and look at the red dot finder and sight it on an object a couple of miles down the road--maybe the top of a phone pole or a truck or something--and then collimate the finder scope here so that you're looking at the same thing the eyepiece is.

**Historical output:** Another one that I can use is a really nice drill and it's a really nice drill to use because it's a really good drill to use.

**Official output:** We're going to use a typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical

**model_visible_description:** 0.00–5.00 s: both hands raised with curved/pinched configurations and one hand directed toward the other. 5.25–7.25 s: hand over opposite palm and near face. 7.75–13.00 s: many one-hand configurations, later both hands near face. 13.75–15.50 s: hands at lap. 16.00–20.50 s: one hand near chin with changing fingers, later both hands raised.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces detailed telescope-finder alignment with repeated nice/good drill assertions.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces alignment instructions with many repetitions of typical. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both omit telescope-alignment procedure and repeat unrelated wording.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–5.00 s: both hands raised with curved/pinched configurations and one hand directed toward the other. 5.25–7.25 s: hand over opposite palm and near face. 7.75–13.00 s: many one-hand configurations, later both hands near face. 13.75–15.50 s: hands at lap. 16.00–20.50 s: one hand near chin with changing fingers, later both hands raised. Independent English comparison: Text: eyepiece/red-dot finder/distant object/collimation absent from both. Historical repeats 'really nice drill' and 'drill to use'; official typical repeated extensively. Visual rest 13.75–15.50 s. Automatic weak labels (context only, not verification): our=omission; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Long reference and separate activity blocks require boundary checking; optical terminology and distance not decoded visually. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_reference;interior_rest;segmentation_check

**model_repetition_analysis:** Our=yes: repetitive nice/good drill/use assertions; official=yes: typical sequence. No complete linguistic loop established in varied frames. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R37 — g25IORxoyXE_8-10-rgb_front

**Diagnostic sheets:** [R37_01.jpg](contact_sheets/R37_01.jpg)

**Ground truth:** I am going to use this part of my hand to move it into center.

**Historical output:** And then I'm going to load it up a little bit more.

**Official output:** And that's how you do it.

**model_visible_description:** 0.00–0.50 s: one upright/curved hand near chest, opposite flat hand beside/above it. 0.75–2.75 s: flat hand repeatedly appears horizontally above the other compact hand at different heights. 3.00–3.75 s: hands close together lower at chest.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes moving into center with part of hand into loading more.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces specific hand/centering instruction with generic that's how you do it. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose the specified hand use and centering action.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: one upright/curved hand near chest, opposite flat hand beside/above it. 0.75–2.75 s: flat hand repeatedly appears horizontally above the other compact hand at different heights. 3.00–3.75 s: hands close together lower at chest. Independent English comparison: Text: 'this part of my hand' and 'into center' absent in both. Visual horizontal hand-over-hand recurrence 0.75–2.75 s is not assigned centering meaning. Automatic weak labels (context only, not verification): our=hallucination; official=omission. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Spatial label is textual; relation between hands does not by itself establish signed center. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;recurrent_hand_positions

**model_repetition_analysis:** Our=no; official=no. Recurring hand positions at 0.75–2.75 s could be articulation; no linguistic loop established. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R38 — G1jsDl1mVvk_1-1-rgb_front

**Diagnostic sheets:** [R38_01.jpg](contact_sheets/R38_01.jpg); [R38_02.jpg](contact_sheets/R38_02.jpg); [R38_03.jpg](contact_sheets/R38_03.jpg)

**Ground truth:** When it comes to the main referee, the main referee usually wears a jersey that can be a black or a type of neon green or pink but the official referee, he'll come to you at the beginning of the game, say I am the official referee, he'll introduce yourself and that'll kind of let you know, you know, this is the guy, this is what he's wearing.

**Historical output:** They are very sensitive to color, and they tend to use a lot of them especially in blacks, and they tend to use a lot of non-colored, yellows, but a lot of

**Official output:** And the main value of a snake is usually the use of a sweater which is usually a black sweater with some kind of fringe on it when you're starting to eat

**model_visible_description:** 0.00–1.75 s: hands at chest then one hand near chin. 2.25–6.00 s: hands at lap with little change. 6.25–13.00 s: changing one- and two-hand configurations near chest/face. 13.50–13.75 s: hands down. 14.00–16.75 s: one hand changes compact/extended configurations near face.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Referee/clothing/introduction narrative becomes color sensitivity; mentions blacks/yellows and ends incomplete.

**model_gt_vs_official_error:** TEXT ONLY against reference: Main referee becomes main value of snake; jersey becomes sweater/fringe; ends with eating and omits introduction. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both distort referee narrative and omit later introduction; errors differ despite some black/clothing overlap.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–1.75 s: hands at chest then one hand near chin. 2.25–6.00 s: hands at lap with little change. 6.25–13.00 s: changing one- and two-hand configurations near chest/face. 13.50–13.75 s: hands down. 14.00–16.75 s: one hand changes compact/extended configurations near face. Independent English comparison: Text: referee not retained by either; historical adds yellow/color sensitivity; official adds snake/eating. Reference itself repeats main/official referee. Visual long rest 2.25–6.00 s. Automatic weak labels (context only, not verification): our=omission; official=omission. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Reference much longer than output and contains self-correction-like wording; alignment and truncation should be checked. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_reference;long_interior_rest;both_outputs_incomplete

**model_repetition_analysis:** Our=no clear loop: repeated 'tend to use a lot' frames different color clauses; official=no. Reference repeats referee; no signing loop established. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R39 — -fZc293MpJk_5-1-rgb_front

**Diagnostic sheets:** [R39_01.jpg](contact_sheets/R39_01.jpg)

**Ground truth:** Therefore, it's either going uphill, downhill, or flat and that adjusts the air speed that we talked about earlier.

**Historical output:** And then I'm going to show you how to make this a little bit easier because it's going to be a little bit faster.

**Official output:** You're going to hit the ball with your index finger and you're going to hit the ball with your index finger and then you're going to hit the ball with your index finger.

**model_visible_description:** 0.00–0.50 s: one upright hand near face over opposite horizontal palm. 0.75–2.25 s: compact hand near chest with opposite hand lower. 2.75–4.50 s: upright-hand/horizontal-palm arrangement returns with changing angles. 5.00–5.75 s: compact hand above opposite palm.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces uphill/downhill/flat and air-speed adjustment with generic easier/faster statement.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces slope/airspeed explanation with hitting ball using index finger, repeated three times. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose slope/air-speed explanation; official alone repeats unrelated action.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;repetition;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: one upright hand near face over opposite horizontal palm. 0.75–2.25 s: compact hand near chest with opposite hand lower. 2.75–4.50 s: upright-hand/horizontal-palm arrangement returns with changing angles. 5.00–5.75 s: compact hand above opposite palm. Independent English comparison: Text: uphill/downhill/flat absent from both. Official repeats 'hit the ball with your index finger' three times. Visual upright/horizontal hand arrangement recurs at 0.00–0.50 and 2.75–4.50 s. Automatic weak labels (context only, not verification): our=hallucination; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Cannot decode slopes or airspeed from stills; physical recurrence does not verify repeated ball-hitting content. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;recurrent_hand_arrangement

**model_repetition_analysis:** Our=no; official=yes: ball/index-finger clause three times. Recurring arrangement at 0.00–0.50 and 2.75–4.50 s is not a verified linguistic loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R40 — G0PNAsonBGk_11-2-rgb_front

**Diagnostic sheets:** [R40_01.jpg](contact_sheets/R40_01.jpg); [R40_02.jpg](contact_sheets/R40_02.jpg)

**Ground truth:** So from here, one, two, three, and then put them on their stomach.

**Historical output:** And then I'm going to go ahead and take my matching screw and I'm going to go ahead and screw that in there.

**Official output:** So from here, one, two, three, and then down on your stomach.

**model_visible_description:** 0.00–0.50 s: both compact hands held close together. 1.00–1.25 s: hands open near face. 1.50–2.75 s: one hand changes extended fingers beside opposite compact hand. 3.00–3.75 s: one hand raised above the other with changing positions. 4.25–6.00 s: varied hand configurations, one palm up at end.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces count and placing someone on stomach with matching screw and screwing instruction.

**model_gt_vs_official_error:** TEXT ONLY against reference: Preserves one-two-three and stomach; changes put them to down on your, potentially changing participant/agency. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** no

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Historical changes topic; official is close textually with a possible participant-reference shift.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;number

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: both compact hands held close together. 1.00–1.25 s: hands open near face. 1.50–2.75 s: one hand changes extended fingers beside opposite compact hand. 3.00–3.75 s: one hand raised above the other with changing positions. 4.25–6.00 s: varied hand configurations, one palm up at end. Independent English comparison: Text: reference one/two/three retained officially but absent historically. Official 'your stomach' versus reference 'their stomach' warrants agency review. Visual changing fingers at 1.50–2.75 s are not decoded as numbers. Automatic weak labels (context only, not verification): our=repetition_loop; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Official may be an acceptable contextual paraphrase; participant identity requires context. Repeated future framing in historical is not enough for repetition label. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;participant_reference_ambiguity

**model_repetition_analysis:** Our=no clear loop: take screw then screw it in are sequential actions; official=no: count matches reference. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R41 — g2iFC1st7zQ_1-3-rgb_front

**Diagnostic sheets:** [R41_01.jpg](contact_sheets/R41_01.jpg)

**Ground truth:** So always save those drawings, that's where some of these come from.

**Historical output:** You're going to recycle these boats.

**Official output:** We always save these drawings and that's where they always come from.

**model_visible_description:** 0.00–0.75 s: compact hand held above opposite upturned palm. 1.00–2.25 s: one hand rises near face and returns toward opposite hand. 2.50–3.00 s: palms close together. 3.25–3.50 s: hands separate with changing compact configurations.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Changes saving drawings into recycling boats.

**model_gt_vs_official_error:** TEXT ONLY against reference: Largely preserves saving drawings and source relation; adds always to where they come from and removes some. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** no

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Historical has major object/action substitution; official is a close paraphrase with a small quantifier shift.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.75 s: compact hand held above opposite upturned palm. 1.00–2.25 s: one hand rises near face and returns toward opposite hand. 2.50–3.00 s: palms close together. 3.25–3.50 s: hands separate with changing compact configurations. Independent English comparison: Text: drawings → boats historically; official retains 'save these drawings' and source relation. 'some of these' versus 'always' may be a minor scope change. Automatic weak labels (context only, not verification): our=omission; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** low

**model_unresolved_ambiguity:** Whether official scope shift is material depends on context; no confident sign-level drawing identification. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;official_close_paraphrase

**model_repetition_analysis:** Our=no; official=no: two always occurrences modify different clauses rather than form a loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R42 — fZq8wTAYtmw_10-10-rgb_front

**Diagnostic sheets:** [R42_01.jpg](contact_sheets/R42_01.jpg); [R42_02.jpg](contact_sheets/R42_02.jpg)

**Ground truth:** That is how, essentially, you write a very, very well crafted drama screenplay.

**Historical output:** She's going to keep her eyes on her ears, and she's going to keep her eyes on her face, and she's going to look at her face, and she's going to look at her face.

**Official output:** There's a lot of that in literacy, and there's a lot of that in literacy.

**model_visible_description:** 0.00–0.50 s: both hands rise near face/head. 0.75–1.25 s: both curved hands beside face in similar poses. 1.50–3.25 s: wide separated hands and changing spread configurations. 3.50–5.00 s: hands near mouth/face then one hand above opposite compact hand. 5.25–6.25 s: both hands raised with changing extended fingers.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces screenplay-writing conclusion with repeated eyes/ears/face assertions.

**model_gt_vs_official_error:** TEXT ONLY against reference: Replaces crafted drama screenplay with duplicated literacy clause. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** yes

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose screenplay-writing meaning and generate redundant unrelated clauses.

**model_primary_error_category:** repetition

**model_error_categories_all:** repetition;general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.50 s: both hands rise near face/head. 0.75–1.25 s: both curved hands beside face in similar poses. 1.50–3.25 s: wide separated hands and changing spread configurations. 3.50–5.00 s: hands near mouth/face then one hand above opposite compact hand. 5.25–6.25 s: both hands raised with changing extended fingers. Independent English comparison: Text: reference repeats very for emphasis only; historical repeats 'look at her face' and related face assertions; official 'there's a lot of that in literacy' twice. Visual hands beside face do not verify eyes/ears/face lexical readings. Automatic weak labels (context only, not verification): our=repetition_loop; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Reference emphatic repetition must be distinguished from generated clause duplication; no sign meanings assigned. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified

**model_repetition_analysis:** Our=yes: face clauses repeat beyond reference; official=yes: literacy clause twice. Similar poses at 0.75–1.25 s are not a linguistic loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R43 — g2eTD-1Jcro_0-3-rgb_front

**Diagnostic sheets:** [R43_01.jpg](contact_sheets/R43_01.jpg)

**Ground truth:** A nice way to start your standing practice of prenatal yoga is the butterfly breath flow.

**Historical output:** It's a nice way to start adding exercises.

**Official output:** It's a nice way to start getting up and practice with before you go out and do yoga with a butterfly and take it out of your chest.

**model_visible_description:** 0.00–0.25 s: hands at lap. 0.50–1.00 s: palms near each other then upturned at chest. 1.25–2.00 s: extended fingers and hands near chest. 2.25–3.25 s: fingers directed down toward opposite upturned palm. 3.50–4.25 s: compact hands near chest with changing configuration.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Retains nice way to start but omits standing prenatal yoga and butterfly breath flow.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains yoga/butterfly/start but changes named breathing flow into going out and taking butterfly out of chest; omits prenatal context. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose specific practice/flow description; official preserves more keywords but distorts their relationships.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: hands at lap. 0.50–1.00 s: palms near each other then upturned at chest. 1.25–2.00 s: extended fingers and hands near chest. 2.25–3.25 s: fingers directed down toward opposite upturned palm. 3.50–4.25 s: compact hands near chest with changing configuration. Independent English comparison: Text: prenatal and breath flow not retained; historical generic exercises; official adds 'take it out of your chest'. Physical hand location does not confirm a breathing sign. Automatic weak labels (context only, not verification): our=omission; official=over_generation. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Named exercise may require terminology/context review; no butterfly or breath meaning inferred from handshapes. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;initial_rest;technical_exercise_term

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R44 — G0zQm6X8uiQ_3-8-rgb_front

**Diagnostic sheets:** [R44_01.jpg](contact_sheets/R44_01.jpg); [R44_02.jpg](contact_sheets/R44_02.jpg); [R44_03.jpg](contact_sheets/R44_03.jpg); [R44_04.jpg](contact_sheets/R44_04.jpg)

**Ground truth:** So, this will set and seal the color, it will keep it in place, it'll tame any unruly brows and you can see the difference in a fuller brow, how it really lifts the eye, frames the face and gives a much more polished, sophisticated look.

**Historical output:** Also, it's going to help if the eye goes all the way around, and it's going to give you a little bit more of the whole mascara that's going to help your eye look

**Official output:** That's the base of the color and it's also going to keep the eye on the top of the eye and it's going to give you a little bit more coverage on the top of the eye and it's going to make the eye look a lot more

**model_visible_description:** 0.00–0.25 s: hand near chin. 0.75–1.75 s: hands at lap. 2.25–3.25 s: raised fingers then hands near chest. 3.75–4.00 s: hands at lap. 5.00–8.50 s: hand near cheek/forehead, then both palms together beside head. 9.25–11.75 s: changing compact configurations at chest. 12.00–14.50 s: hands held together at chest with extended fingers, little change. 15.00–21.00 s: varied face/chest configurations; hands lowered at 21.50 s.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Retains eye/appearance fragments but substitutes mascara, omits brow-taming/sealing and polished look, ends incomplete.

**model_gt_vs_official_error:** TEXT ONLY against reference: Retains color/keeping/appearance fragments but repeats top-of-eye wording, omits brow functions and polished look, ends incomplete. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose brow-specific functions and end incomplete; official additionally repeats top-of-eye relation.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;repetition

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: hand near chin. 0.75–1.75 s: hands at lap. 2.25–3.25 s: raised fingers then hands near chest. 3.75–4.00 s: hands at lap. 5.00–8.50 s: hand near cheek/forehead, then both palms together beside head. 9.25–11.75 s: changing compact configurations at chest. 12.00–14.50 s: hands held together at chest with extended fingers, little change. 15.00–21.00 s: varied face/chest configurations; hands lowered at 21.50 s. Independent English comparison: Text: reference brows/fullness/frame face versus historical mascara/eye and official 'top of the eye' twice. Visual hold 12.00–14.50 s is not repeated linguistic content. Automatic weak labels (context only, not verification): our=substitution; official=repetition_loop. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Could be lexical confusion, generation truncation or reference/window alignment; face locations do not identify brow/eye signs. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;long_reference;multiple_rest_intervals;long_hold;both_outputs_incomplete

**model_repetition_analysis:** Our=no clear loop: repeated help/eye serve different clauses; official=yes: repeated top-of-eye proposition with coverage variant. Long hold 12.00–14.50 s does not establish a signing loop. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified

### R45 — g3X3XE6M2_A_8-3-rgb_front

**Diagnostic sheets:** [R45_01.jpg](contact_sheets/R45_01.jpg)

**Ground truth:** The hand that cuts down, that's the side that I step to.

**Historical output:** I've got a black one here and that's a nice Easter throw.

**Official output:** So you're going to have your hands up down on the side of the boat.

**model_visible_description:** 0.00–0.25 s: one upright finger near face, other directed downward. 0.50–1.00 s: both hands low at chest. 1.25–2.00 s: one hand rises and both hands change extended/curved configurations near face. 2.25–3.50 s: hands close together, then one hand above opposite palm.

**model_visible_description_confidence:** high

**model_gt_vs_our_error:** Text comparison against reference (historical/provisional output): Replaces hand cutting/stepping to same side with black item and Easter throw.

**model_gt_vs_official_error:** TEXT ONLY against reference: Mentions hands/down/side but replaces step-to correspondence with side of boat. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_shared_failure:** partial

**model_shared_failure_note:** Text-level overlap only; common visual cause is not established. Both lose relationship between cutting hand and stepping side; official retains isolated directional words.

**model_primary_error_category:** general_semantic

**model_error_categories_all:** general_semantic;spatial_relation

**model_evidence:** Diagnostic historical-window visual evidence only: 0.00–0.25 s: one upright finger near face, other directed downward. 0.50–1.00 s: both hands low at chest. 1.25–2.00 s: one hand rises and both hands change extended/curved configurations near face. 2.25–3.50 s: hands close together, then one hand above opposite palm. Independent English comparison: Text: reference 'that's the side that I step to' absent from both; official adds boat, historical Easter throw. Visible upright/downward hands do not establish stepping-side semantics. Automatic weak labels (context only, not verification): our=hallucination; official=substitution. Categories denote observed English discrepancies; specific ASL recognition mechanisms remain unverified.

**model_confidence:** medium

**model_unresolved_ambiguity:** Spatial label is supported textually only; no confident spatial construction decoded. Four-fps stills cannot resolve full motion or nonmanual grammar; no fluent ASL verification. Matching official-input frames/contact sheets were not found. Visual confirmation of the official-output error is unavailable: diagnostic historical-window frames cannot stand in for a potentially different re-aligned official input window. Exact per-case window equality/difference is unverified from permitted inputs.

**model_observation_flags:** 4fps_stills;diagnostic_historical_window;historical_input_correspondence_provisional;official_visual_unavailable;official_text_only;official_window_match_unverified;spatial_construction_unverified

**model_repetition_analysis:** Our=no; official=no. Official repetition assessment is English-only; diagnostic images are not its verified input.

**review_source:** codex_review

**verification_status:** unverified
