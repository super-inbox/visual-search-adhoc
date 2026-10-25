# Model review comparison — 45 ASL diagnostic cases

Comparison performed only after the independent Codex pass was completed. **Neither model review is ASL-fluent human verification.** All diagnoses remain unverified; agreement does not establish what was signed.

## Three distinct sources

| Source | Identity and scope | Authority/limits |
|---|---|---|
| Automatic weak-label / rule-based audit | inspection_sheet.csv initial categories and automatic output-error types; repetition_audit.csv/.md frozen selection | English-text rules and diagnostic metadata, not human review or visual truth. The official 9-case result is preserved. |
| Claude model_review | model_case_analysis.csv; MODEL_CASE_ANALYSIS.md; reviewer claude-opus-5-5; model_label_source=model_review; unverified | First model pass; saw diagnostic sheets and prior automatic diagnostics/audit. Its causal/lexical readings remain hypotheses. |
| Codex codex_review | codex_case_analysis.csv; CODEX_CASE_ANALYSIS.md; review_source=codex_review; verification_status=unverified | Independent full pass excluded first-pass outputs and repetition audit. All official-output judgments were text-only; no matching official visuals established. R03 had earlier smoke-test audit exposure, disclosed in Codex report. |

Source files are linked at the end. Existing originals are not edited. This report adds comparison judgments and suggested priorities only; it writes no human-review fields.

The passes are not equivalent evidence conditions: Claude used automatic timing/repetition context; Codex deliberately excluded it during the full pass and avoided confident sign meanings. Codex also disclosed reading the sheet-builder script for provenance. R03 is not a pristine newly blinded case because its earlier smoke test exposed an audit row and diagnostic notes. Do not treat the automatic audit plus two models as three independent votes.

## Reproducible agreement definition

The following is **coding agreement**, not a semantic-accuracy score:

- **Full:** identical primary category, identical unordered full category set, identical shared-failure value, and identical overall confidence.
- **Partial:** not full, but primary category matches or the unordered full category set matches. This includes category-priority differences and differing shared-failure/confidence judgments.
- **Disagreement:** primary categories differ and full category sets differ. Shared broad general_semantic content may still overlap; this does not mean incompatible translations or wholly opposing observations.

Secondary category order is ignored; primary order is preserved. Timing/crop/reference observations are compared separately below because free-text descriptions and timestamps cannot be given an honest exact-match score. Full coding agreement therefore does not mean every visual interpretation agrees (R27 is an example). Confidence concerns overall diagnosis, not the separate visible-description-confidence field.

| Claude vs Codex measure | Count / 45 |
|---|---|
| Full coding agreement | 4 |
| Partial coding agreement | 28 |
| Coding disagreement | 13 |
| Exact primary category agreement | 21 |
| Different primary categories | 24 |
| Identical unordered full category sets | 21 |
| Exact shared-failure agreement | 24 |
| Exact overall-confidence agreement | 24 |

Full: R27, R41, R42, R43.

Disagreement: R01, R02, R06, R09, R14, R17, R18, R22, R25, R26, R32, R35, R40.

Partial: R03, R04, R05, R07, R08, R10, R11, R12, R13, R15, R16, R19, R20, R21, R23, R24, R28, R29, R30, R31, R33, R34, R36, R37, R38, R39, R44, R45.

These counts are rubric-dependent. The 13 disagreements are chiefly category specificity/priority disagreements, not 13 proven model mistakes. Every row still needs human verification before sign-level use.

## Confidence and category distributions

| Overall confidence | Automatic weak-label audit | Claude model_review | Codex codex_review |
|---|---|---|---|
| high | No comparable confidence scale | 0 | 0 |
| medium | No comparable confidence scale | 23 | 34 |
| low | No comparable confidence scale | 22 | 11 |

| Confidence transition, Claude → Codex | Cases |
|---|---|
| medium → medium | 18 |
| low → low | 6 |
| low → medium | 16 |
| medium → low | 5 |

Codex's higher medium count is not evidence of better ASL competence: it generally rates English discrepancy coding while withholding lexical visual interpretation. Neither pass has any high-confidence overall diagnoses.

| Primary category | Claude | Codex |
|---|---|---|
| fingerspelling | 5 | 0 |
| name | 4 | 4 |
| number | 6 | 0 |
| negation | 3 | 1 |
| question | 4 | 1 |
| spatial_relation | 3 | 0 |
| repetition | 9 | 9 |
| general_semantic | 11 | 30 |

Claude favors proposed linguistic mechanisms (five fingerspelling, six number, three spatial_relation primaries). Codex favors general_semantic (30 primaries), retains cautious text-supported secondary categories, and does not decode spelling or number signs. Both have nine repetition primaries, but this is **not** the number of official-output repetitions: primary is one label per case across both system outputs.

| Shared-failure judgment | Claude | Codex |
|---|---|---|
| yes | 22 | 18 |
| partial | 16 | 25 |
| no | 7 | 2 |

| Claude → Codex shared-failure values | Count |
|---|---|
| yes → yes | 12 |
| yes → partial | 10 |
| partial → yes | 6 |
| partial → partial | 10 |
| no → partial | 5 |
| no → no | 2 |

There are 21 shared-failure-value differences but **no direct yes↔no reversal**. Most are boundary choices between common missing content and different error severity/content. For example R04 and R08 are yes→partial because Codex emphasizes what official retains; R07/R10/R31 are partial→yes because Codex emphasizes the shared missing meaning. R15/R30/R32/R33/R45 are no→partial: official is closer, but Codex still records a common residual discrepancy.

## Repetition: frozen automatic nine versus model eleven

**Frozen rule-based official result: 9 cases.** This remains the audit result and is not replaced or corrected by either model judgment.

| Source / definition | Official repetition count | Case IDs |
|---|---|---|
| Automatic audit: primary repetition_loop | 9 | R03, R11, R16, R18, R20, R36, R39, R42, R44 |
| Claude: explicit English repetition judgments in row text, including extras outside automatic nine | 11 | R01, R03, R11, R16, R18, R19, R20, R36, R39, R42, R44 |
| Codex: independently assessed English repetition relative to reference | 11 | R01, R03, R11, R16, R18, R19, R20, R36, R39, R42, R44 |
| Automatic ∩ Codex | 9 | R03, R11, R16, R18, R20, R36, R39, R42, R44 |
| Codex extras outside automatic nine | 2 | R01, R19 |
| Automatic cases omitted by Codex | 0 | None |

Claude already notes both R01 and R19 outside the automatic nine in its per-case text and summary. Thus the 9-versus-11 difference is **automatic selection versus model judgment**, not a Claude-versus-Codex disagreement about the existence of these two English repeats. Claude's summary heading about nine follows the automatic subset; it is not an exhaustive count of all repetition it noticed.

### Exact definition/threshold explanation

The audit script reads frozen taxonomy primary types; it does not newly classify the outputs. The taxonomy code uses lowercased whitespace-split word trigrams, retaining punctuation, with:

1. repetition flag = prediction has any repeated trigram **and reference has no repeated trigram anywhere**;
2. repetition_loop primary = that flag is true **and** output rep3_ratio ≥ 0.15;
3. otherwise subsequent omission/hallucination/other rules choose the primary type.

rep3_ratio = 1 − distinct trigram count / total trigram count. The reference exclusion is global, not a comparison of whether the *same* repeated phrase appears in the reference. This suppresses a generated loop even if unrelated ordinary reference framing repeats.

| Case | Frozen official primary type | Output ratio, diagnostic recomputation | Reference repeated trigrams disabling flag | Model English-repeat evidence |
|---|---|---|---|---|
| R01 | hallucination | 0.875000 (≥0.15) | we're going to | a D repeated extensively |
| R19 | hallucination | 0.151515 (≥0.15) | we are going; are going to; going to be; to be learning | the brew repeated four times |

Therefore **neither extra is excluded by falling below the numeric threshold**. R19 is just above it (0.151515); R01 is far above it (0.875000). Both are excluded by the reference-repeat condition and remain classified hallucination in the frozen automatic data. This is a definition/eligibility difference, not evidence that Codex used a lower 0.15 threshold. Codex applies no fixed numeric threshold and distinguishes excess content repetition from ordinary framing. The diagnostic calculations above do not regenerate or modify the committed audit.

Codex excluded borderline official cases R06 (malformed topic restart) and R29 (tautological talking-about clause) from its clear 11. It did not count repetition merely from repeated poses. No model English-repeat label proves a loop in signing.

### Historical-output repetition differences

| Comparison | Cases |
|---|---|
| Frozen historical automatic primary repetition_loop (10/45) | R03, R11, R12, R16, R20, R21, R30, R35, R40, R42 |
| Codex historical English repetition judgments (11/45) | R03, R11, R16, R17, R19, R20, R21, R30, R35, R36, R42 |
| Overlap (8) | R03, R11, R16, R20, R21, R30, R35, R42 |
| Codex extras (3) | R17, R19, R36 |
| Automatic-only historical cases (2) | R12, R40 |

R12: Claude explicitly calls the historical you're-going-to wording a loop; Codex sees repeated framing with differing clauses and no clear degeneration. R40: Claude calls the screw instruction repetitive; Codex reads taking a screw and screwing it in as sequential actions. R17: Claude explicitly notes groove wording twice; Codex counts the redundancy. R36: both reviews describe the historical drill wording as repetitive despite automatic primary omission. R19: Codex also counts the historical blue-brew practice restatement; Claude's explicit repetition note focuses on official brew. These are English-definition judgments and should be reported separately from signing recurrence.

## Timing, crop and reference issue overlap

The following table compares actual description/evidence text, not just flag strings. Absence of an automatic audit entry means not selected into its official-repetition subset; it is not evidence that a case has no timing issue.

| Case | Automatic audit / metadata | Claude model_review | Codex codex_review | Overlap / unresolved difference |
|---|---|---|---|---|
| R10 | No audit entry | Rest 4.50–19.50 s; approximately 15 seconds | Rest 4.50–19.25 s; segmentation check; low | Strong rest agreement; 0.25 s endpoint difference is sampling-scale, not a material contradiction. |
| R23 | No audit entry | Rests 3.50–4.25, 9.25–11.50, 21.25–25.8 s; low clawed hands called action dominant | Same rest blocks through last sampled 25.50 s; curved-hand holds 5.50–8.75 and 12.50–14.50 s; low | Strong timing agreement. Linguistic/action interpretation and later clause coverage unresolved. |
| R38 | No audit entry | Long rest 2.25–6.00 s, additional 13.50–14.00 s; reference may exceed signing; low | Long rest 2.25–6.00 s, brief 13.50–13.75 s; boundary/coverage concern; low | Strong main interval agreement; minor sampled endpoints. Neither proves reference mismatch. |
| R26 | No audit entry; automatic reference category questions | Hands partly leave top crop; suggests degraded pose input | Hands clipped beyond top/lateral boundary; no causal pose claim | Both see clipping. Pose-quality consequences and overhead meaning require actual full input. |
| R29 | No audit entry | Mostly idle 0.25–1.25 s; claims full question cannot fit | Mostly at rest 0.50–1.25 s; activity at boundaries; possible mismatch | Both see mostly resting window; Codex qualifies alignment claim rather than declaring impossibility. |
| R35 | No audit entry; automatic historical repetition_loop | Hand rises/returns on palm, proposed push-up depiction; unsure names in window | 3.00–5.00 s sustained configuration, possible introduction/reference-window mismatch | Both question name coverage; meaningful motion/repetition versus hold and mismatch is a key unresolved disagreement. |
| R44 | Official 23.39 s; diagnostic 21.71 s | Explicit 12.00–14.50 s crossed-hand hold; ties loop to recurrent eye-region locations | Explicit 12.00–14.50 s hold; no linguistic loop or official visual causality inferred | Hold observation agrees. Official causal interpretation is not supported by diagnostic frames as exact input. |

All seven requested cases share a physical limitation/coverage concern at some level; R35 is only partial issue overlap because Codex explicitly raises mismatch while Claude proposes a push-up interpretation. This is not a count of seven identical diagnoses. All 45 Codex rows have official-input visual confirmation unavailable; Claude's audit-derived timing information does not supply those missing frames.

Additional overlap: R03 initial rest; R04 initial rest; R14 interior rest; R36 interior rest; R08 possible transcript speaker label; R11 parenthetical lyric; R28 encoding noise; R09/R15 five-frame limitation. Claude is often stronger in saying a reference cannot fit; Codex treats these as hypotheses pending boundary/context verification.

### Official-window facts now visible from the automatic audit

| Case | Official input seconds (automatic metadata) | Historical input seconds (automatic metadata) | Duration relation; exact boundary/crop match |
|---|---|---|---|
| R03 | 19.52 | 15.26 | Unequal durations; diagnostic clip not exact official temporal input |
| R11 | 18.20 | 18.67 | Unequal durations; diagnostic clip not exact official temporal input |
| R16 | 8.32 | 8.32 | Equal rounded duration; exact boundaries/crop NOT established |
| R18 | 5.91 | 4.4 | Unequal durations; diagnostic clip not exact official temporal input |
| R20 | 16.42 | 17.73 | Unequal durations; diagnostic clip not exact official temporal input |
| R36 | 32.54 | 20.78 | Unequal durations; diagnostic clip not exact official temporal input |
| R39 | 5.76 | 5.88 | Unequal durations; diagnostic clip not exact official temporal input |
| R42 | 4.02 | 6.53 | Unequal durations; diagnostic clip not exact official temporal input |
| R44 | 23.39 | 21.71 | Unequal durations; diagnostic clip not exact official temporal input |

Eight of the nine audit rows have unequal durations; R16 has equal rounded durations. Similar duration is not identical boundaries or crop: R39 is 5.76 versus 5.88 seconds, not a verified same-window control. Even equal R16 durations do not independently establish identical input content. Claude's discussion of R16/R39 as ruling out window effects is stronger than these metadata alone support.

Particularly important asymmetry: R03 19.52 vs 15.26 s, R36 32.54 vs 20.78 s, R42 4.02 vs 6.53 s. The official English loop on a short input is a valid descriptive counterexample to a claim that *only* long inputs loop, but not proof of a specific decoder cause. Similar outputs under different preparations (R11) do not by themselves rule out preprocessing contributions.

Claude links official repetition to visible movement/locations especially R20/R44 and possibly R16/R39; Codex deliberately withholds these causal interpretations. Without matching official frames, retain those Claude statements as hypotheses rather than visual confirmation. Audit durations now inform this comparison only; the completed Codex original is not retroactively edited.

## All 45 cases: coding, confidence and shared-failure matrix

Automatic focus is the frozen initial weak category (original spelling preserved); automatic O/U = historical/official primary English error type. These belong to different taxonomies from model linguistic categories. Confidence and shared values are always Claude → Codex. Full-set details and per-case human-review questions follow.

| Case | Automatic focus | Automatic O / U | Claude primary | Codex primary | Primary equal | Overall coding | Confidence C → K | Shared C → K |
|---|---|---|---|---|---|---|---|---|
| R01 | general_semantic | substitution / hallucination | fingerspelling | repetition | no | disagreement | low → medium | partial → partial |
| R02 | fingerspelling | substitution / hallucination | fingerspelling | name | no | disagreement | medium → medium | yes → yes |
| R03 | numbers | repetition_loop / repetition_loop | number | repetition | no | partial | low → medium | partial → partial |
| R04 | negation | hallucination / hallucination | name | name | yes | partial | medium → medium | yes → partial |
| R05 | names | substitution / hallucination | name | name | yes | partial | medium → medium | yes → yes |
| R06 | names | substitution / substitution | fingerspelling | general_semantic | no | disagreement | medium → medium | yes → yes |
| R07 | names | substitution / substitution | general_semantic | general_semantic | yes | partial | medium → medium | partial → yes |
| R08 | fingerspelling | omission / substitution | general_semantic | general_semantic | yes | partial | medium → medium | yes → partial |
| R09 | names | hallucination / substitution | fingerspelling | name | no | disagreement | low → low | partial → yes |
| R10 | numbers | substitution / hallucination | general_semantic | general_semantic | yes | partial | medium → low | partial → yes |
| R11 | names | repetition_loop / repetition_loop | repetition | repetition | yes | partial | medium → medium | yes → yes |
| R12 | negation | repetition_loop / substitution | general_semantic | general_semantic | yes | partial | low → medium | partial → partial |
| R13 | names | omission / substitution | name | general_semantic | no | partial | medium → medium | partial → partial |
| R14 | negation | substitution / substitution | fingerspelling | general_semantic | no | disagreement | low → medium | yes → yes |
| R15 | questions | hallucination / substitution | question | general_semantic | no | partial | low → low | no → partial |
| R16 | numbers | repetition_loop / repetition_loop | repetition | repetition | yes | partial | low → medium | yes → yes |
| R17 | numbers | hallucination / hallucination | number | general_semantic | no | disagreement | low → medium | yes → partial |
| R18 | negation | substitution / repetition_loop | repetition | general_semantic | no | disagreement | medium → medium | partial → partial |
| R19 | numbers | hallucination / hallucination | number | repetition | no | partial | low → medium | yes → yes |
| R20 | general_semantic | repetition_loop / repetition_loop | repetition | repetition | yes | partial | low → medium | partial → yes |
| R21 | numbers | repetition_loop / hallucination | number | general_semantic | no | partial | low → medium | yes → partial |
| R22 | negation | hallucination / omission | negation | general_semantic | no | disagreement | low → medium | partial → partial |
| R23 | negation | omission / omission | general_semantic | general_semantic | yes | partial | medium → low | yes → partial |
| R24 | negation | hallucination / substitution | negation | negation | yes | partial | low → medium | partial → yes |
| R25 | negation | hallucination / hallucination | negation | general_semantic | no | disagreement | low → medium | yes → partial |
| R26 | questions | hallucination / hallucination | question | general_semantic | no | disagreement | low → low | yes → partial |
| R27 | questions | hallucination / hallucination | question | question | yes | full | medium → medium | yes → yes |
| R28 | general_semantic | omission / omission | general_semantic | general_semantic | yes | partial | low → medium | yes → yes |
| R29 | questions | hallucination / hallucination | question | general_semantic | no | partial | medium → low | yes → partial |
| R30 | general_semantic | repetition_loop / substitution | repetition | repetition | yes | partial | medium → medium | no → partial |
| R31 | general_semantic | substitution / substitution | general_semantic | general_semantic | yes | partial | medium → medium | partial → yes |
| R32 | questions | omission / hallucination | number | general_semantic | no | disagreement | medium → low | no → partial |
| R33 | general_semantic | hallucination / substitution | general_semantic | general_semantic | yes | partial | low → medium | no → partial |
| R34 | spatial_relations | substitution / substitution | spatial_relation | general_semantic | no | partial | medium → medium | partial → partial |
| R35 | fingerspelling | repetition_loop / substitution | name | general_semantic | no | disagreement | low → low | partial → partial |
| R36 | general_semantic | omission / repetition_loop | repetition | repetition | yes | partial | medium → medium | yes → yes |
| R37 | spatial_relations | hallucination / omission | spatial_relation | general_semantic | no | partial | medium → medium | yes → yes |
| R38 | general_semantic | omission / omission | general_semantic | general_semantic | yes | partial | low → low | partial → partial |
| R39 | general_semantic | hallucination / repetition_loop | repetition | general_semantic | no | partial | low → medium | yes → partial |
| R40 | numbers | repetition_loop / substitution | number | general_semantic | no | disagreement | medium → low | no → no |
| R41 | general_semantic | omission / substitution | general_semantic | general_semantic | yes | full | low → low | no → no |
| R42 | general_semantic | repetition_loop / repetition_loop | repetition | repetition | yes | full | medium → medium | yes → yes |
| R43 | general_semantic | omission / over_generation | general_semantic | general_semantic | yes | full | medium → medium | partial → partial |
| R44 | general_semantic | substitution / repetition_loop | repetition | general_semantic | no | partial | medium → medium | yes → partial |
| R45 | spatial_relations | hallucination / substitution | spatial_relation | general_semantic | no | partial | low → medium | no → partial |

For descriptive comparison only, normalizing automatic plurals (numbers→number, names→name, questions→question, spatial_relations→spatial_relation) gives automatic-focus/Claude-primary matches in 24/45 and automatic-focus/Codex-primary matches in 12/45. These are not accuracy rates: the automatic category is weak, Claude had access to it, and Codex uses a more conservative category policy.

## All 45 cases: category sets, concerns and human-verification questions

Category lists below retain each source's primary-first order. Every case needs an ASL-fluent reviewer before linguistic verification. P1/P2/P3 are proposed comparison triage priorities, not completed human reviews.

### R01 — g2ur4BIuN0Q_8-3-rgb_front

- **Claude categories:** fingerspelling;repetition;general_semantic.
- **Codex categories:** repetition;general_semantic.
- **Concern comparison:** Both see held/contrasted hand configurations; Claude proposes letter contrast, Codex declines letter decoding.
- **Shared-failure rationale, Claude:** both keep the letter D; both lose the B->D substitution meaning ('dall').
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose the substitution explanation; only official output has sustained repetition.
- **Human verification (P2, pending):** Verify spelling/substitution and official loop separately.

### R02 — G3OMdQo1zjY_0-10-rgb_front

- **Claude categories:** fingerspelling;name;general_semantic.
- **Codex categories:** name;general_semantic.
- **Concern comparison:** Claude flags reference longer than visible signing; Codex leaves name spelling unresolved without declaring a proven duration mismatch.
- **Shared-failure rationale, Claude:** both keep a greeting + invented name; both lose every name/place (Mike Camelin, SunState, Kissimmee, Florida).
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both replace the introduced person's identity and affiliation, with different invented details.
- **Human verification (P2, pending):** Verify name/affiliation coverage before scoring missing entities.

### R03 — G06Irzcwxiw_5-1-rgb_front

- **Claude categories:** number;repetition;general_semantic.
- **Codex categories:** repetition;general_semantic;number.
- **Concern comparison:** Both note initial clasped hold/rest; Claude cites audit's different official duration. Codex excluded that metadata in blind pass and discloses prior smoke-test exposure.
- **Shared-failure rationale, Claude:** both drop the number 25 and the final clause; both repeat (ours much worse).
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both repeat wording and omit later reference content; official retains more of the original topic.
- **Human verification (P2, pending):** Verify number/CV coverage in each exact input window; account for prior exposure.

### R04 — -g0iPSnQt6w_0-1-rgb_front

- **Claude categories:** name;fingerspelling;negation;question;general_semantic.
- **Codex categories:** name;general_semantic;question.
- **Concern comparison:** Both note initial rest; Claude makes stronger reference-too-long claim, Codex treats alignment as uncertain.
- **Shared-failure rationale, Claude:** both lose the name, the negation and the question.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both omit the rhetorical content and correct identity; official retains greeting and Spanish topic.
- **Human verification (P2, pending):** Locate introduction and rhetorical clause in matching windows.

### R05 — G3VM7etNABI_0-10-rgb_front

- **Claude categories:** name;fingerspelling;general_semantic.
- **Codex categories:** name;general_semantic.
- **Concern comparison:** Both cannot read name spelling; Claude proposes initial-letter recovery, Codex records only textual identity mismatch.
- **Shared-failure rationale, Claude:** both substitute a plausible-looking invented name; both keep 'heart' (cardio).
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both replace the person's name and distort the training topic.
- **Human verification (P2, pending):** Verify complete name and training terminology.

### R06 — G1LiGqM3FhM_2-8-rgb_front

- **Claude categories:** fingerspelling;name;general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Same malformed dish term; Claude proposes partial spelling/ONION reading, Codex makes no lexical visual claim.
- **Shared-failure rationale, Claude:** both emit an 'Albur(n)-' fragment for 'Albondigas' and keep 'onion'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose the soup term while retaining onion-related wording.
- **Human verification (P2, pending):** Check dish-term spelling and lexical meaning.

### R07 — fZIHe3dXPR0_5-8-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both retain Barbie textually and find semantic errors; Codex emphasizes speaker-to-advice perspective shift.
- **Shared-failure rationale, Claude:** both keep the gist and the name; both lose 'listed in here'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both shift speaker/purchase perspective and distort the book description; official preserves prices.
- **Human verification (P3, pending):** Check perspective and whether listed/prices omissions matter; noisy reference.

### R08 — FZrWOf-oGDk_0-8-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both identify possible transcript speaker-label artifact; Claude states artifact categorically, Codex leaves it provisional.
- **Shared-failure rationale, Claude:** both render 'thread' as 'wire' and drop 'hook'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose thread-to-hook specificity; securing omission is historical only.
- **Human verification (P3, pending):** Separate speaker label from translated content; thread/hook/secure.

### R09 — fZgWKh3ENoE_0-8-rgb_front

- **Claude categories:** fingerspelling;name;general_semantic.
- **Codex categories:** name;general_semantic.
- **Concern comparison:** Both flag five-frame window and unreadable spelling; both low confidence.
- **Shared-failure rationale, Claude:** both keep 'talk about'; both lose the name; official produces a letter-level token.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both retain the talking-about frame but substitute the named topic.
- **Human verification (P1, pending):** Establish complete input coverage and named topic.

### R10 — fzNnTgHa1lM_2-5-rgb_front

- **Claude categories:** general_semantic;number.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both identify approximately 15 seconds of rest between signing blocks; Codex gives 4.50–19.25 s, Claude 4.50–19.50 s.
- **Shared-failure rationale, Claude:** both get the note names; both garble 'double-stop'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both preserve note-letter text but lose technical double-stop/choice content.
- **Human verification (P1, pending):** Inspect segmentation and reference alignment before translation attribution.

### R11 — fZM3IcM2Xs4_14_15_16-10-rgb_front

- **Claude categories:** repetition;name;general_semantic.
- **Codex categories:** repetition;general_semantic.
- **Concern comparison:** Both note reference lyric/annotation and early recurring hand-over-hand action; Claude proposes decoder lock-in.
- **Shared-failure rationale, Claude:** near-identical 'ready to go' loop in both; Morris, festive, Christmas, mash all lost.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both collapse varied reference content into a readiness phrase repeated six or more times.
- **Human verification (P3, pending):** Separate transcript lyric from signing; no causal loop diagnosis without matching official frames.

### R12 — G2JE_BEFVmE_4-10-rgb_front

- **Claude categories:** general_semantic;negation;name;repetition.
- **Codex categories:** general_semantic.
- **Concern comparison:** Claude assigns possible negation/name/repetition tags and says historical loops; Codex rejects a clear historical loop and leaves recipe signs unread.
- **Shared-failure rationale, Claude:** both lose wings/Cajun/chili and the negated clause; official keeps 'other thing' and 'red'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both omit major recipe content and end incomplete; semantic substitutions differ.
- **Human verification (P2, pending):** Review framing repetition versus content loop, negated clause, output truncation.

### R13 — fZgbCwSG3Hc_4-8-rgb_front

- **Claude categories:** name;general_semantic.
- **Codex categories:** general_semantic;name.
- **Concern comparison:** Both note invented official introduction and missing artifact; Codex additionally questions terminology/reference noise.
- **Shared-failure rationale, Claude:** both lose 'Whalebone Glider'; both keep 'new ... set'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both fail to identify the artifact; official adds an unrelated identity.
- **Human verification (P3, pending):** Verify artifact/title terminology and invented identity.

### R14 — G3GcPpidwxk_5-5-rgb_front

- **Claude categories:** fingerspelling;negation;name;general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both note interior rest around 5–7 s; Claude proposes ascot spelling/necktie reading; Codex declines those meanings.
- **Shared-failure rationale, Claude:** both keep morning suit/wedding; both garble 'ascot tie' into an A-initial word; both drop 'European', 'English' and 'didn't use a lot of these'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both corrupt the garment and cultural/formality description.
- **Human verification (P2, pending):** Verify garment term and closing negative clause coverage.

### R15 — g1xdqxCZxTg_6-3-rgb_front

- **Claude categories:** question;negation;general_semantic.
- **Codex categories:** general_semantic;question;negation.
- **Concern comparison:** Both have five frames and low confidence; official keeps English while historical keeps interrogative form.
- **Shared-failure rationale, Claude:** complementary errors: ours keeps the question, official keeps 'English'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both change the proposition; only official loses interrogative form and adds negation.
- **Human verification (P1, pending):** Verify proposition and nonmanual question/negation, not punctuation alone.

### R16 — g0yUlOaqL6k_12-3-rgb_front

- **Claude categories:** repetition;number;negation;general_semantic.
- **Codex categories:** repetition;general_semantic;number.
- **Concern comparison:** Both see recurring palms-up configurations and missing six-month text; Claude suggests a visual seed, Codex declines causal inference.
- **Shared-failure rationale, Claude:** both loop on a 'where ... are' frame; both lose bedding, 'every six months', feces.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both replace practical maintenance content with repeated unrelated location wording.
- **Human verification (P2, pending):** Verify quantity/maintenance and actual linguistic recurrence in exact inputs.

### R17 — fzXgYPSnaDs_5-8-rgb_front

- **Claude categories:** number;general_semantic.
- **Codex categories:** general_semantic;number;repetition.
- **Concern comparison:** Both see recurrent close-hand configurations; Claude proposes TEN, Codex adds historical redundant groove wording without decoding ten.
- **Shared-failure rationale, Claude:** both lose 'ten' and 'line the whole thing'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose hook-loading instruction and quantity; only historical has redundant groove wording.
- **Human verification (P2, pending):** Verify number and distinguish useful restatement from excess English repetition.

### R18 — 37ZtKNf6Yd8_1-1-rgb_front

- **Claude categories:** repetition;negation;general_semantic.
- **Codex categories:** general_semantic;repetition.
- **Concern comparison:** Both note object substitution while four is retained textually; Claude identifies FOUR-like shape, Codex does not.
- **Shared-failure rationale, Claude:** both get 'four'; both miss 'stringed instrument' and 'head stock'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both substitute the counted object while retaining four; only official repeats the clause.
- **Human verification (P2, pending):** Check counted object and official input's additional coverage; no number-value error established.

### R19 — Fzj3jz2Imf0_1-1-rgb_front

- **Claude categories:** number;repetition;general_semantic.
- **Codex categories:** repetition;general_semantic;number.
- **Concern comparison:** Both see list-like/changing hand configurations and official brew repetition; Codex prioritizes repetition over omitted ordinals.
- **Shared-failure rationale, Claude:** both map 'bow' to 'brew/brush'; both drop the list of positions (first..sixth).
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both corrupt bow terminology and omit ordered positions; both repeat corrupted terminology with different severity.
- **Human verification (P2, pending):** Verify position list and bow terminology; assess historical restatement separately.

### R20 — _FzvMVnR_aU_3-10-rgb_front

- **Claude categories:** repetition;number;general_semantic.
- **Codex categories:** repetition;general_semantic;number.
- **Concern comparison:** Both note recurring flat-hand configurations; Claude proposes NINE and visually seeded official repetition, Codex declines linguistic/causal identification.
- **Shared-failure rationale, Claude:** both partly recover 9 (with spurious 15/10); both lose freezer / lay flat / single layer; both loop.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both distort preparation timing and replace freezing procedure with repetitive unrelated content.
- **Human verification (P2, pending):** Inspect official re-aligned window before attributing English repetition to depicting movement.

### R21 — G0MjvzT_UqM_16-2-rgb_front

- **Claude categories:** number;repetition;general_semantic.
- **Codex categories:** general_semantic;number;repetition.
- **Concern comparison:** Both note missing 45/eight and historical lift repetition; Claude proposes exercise meanings, Codex leaves them unread.
- **Shared-failure rationale, Claude:** both lose 'forty-five seconds' and 'eight deep counts'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose explicit timing/counts; only historical has repeated lifting and ball-related additions.
- **Human verification (P2, pending):** Verify numeric values and exercise instruction; separate historical loop.

### R22 — g0fgci8L_rc_11-8-rgb_front

- **Claude categories:** negation;general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Claude proposes NOT from chin location and possible reference/weak-label false positive; Codex declines that sign reading.
- **Shared-failure rationale, Claude:** both move into a plant/garden domain; both lose 'at least put it in your garden'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both replace the suggested action with different plant-related propositions.
- **Human verification (P2, pending):** High-value negation adjudication with motion/context; neither reading verified.

### R23 — FzmL8SL6Bow_1-8-rgb_front

- **Claude categories:** general_semantic;negation;spatial_relation.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both note several rests and low curved-hand holds; Claude calls action dominant, Codex treats reference/window alignment more cautiously.
- **Shared-failure rationale, Claude:** both lose the wall / 'I'm not going to let it' / hands-there content.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both incomplete and omit later wall-control detail; official retains more of hole topic.
- **Human verification (P1, pending):** Verify coverage of later wall/negative clause before scoring omission.

### R24 — g3kFAmcBpFc_8-3-rgb_front

- **Claude categories:** negation;general_semantic.
- **Codex categories:** negation;general_semantic.
- **Concern comparison:** Both identify neither/either textual difference; Claude proposes SAY/CAT/EITHER signs, Codex no lexical decoding.
- **Shared-failure rationale, Claude:** both lose the negation ('doesn't', 'neither'); both keep 'cat'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both fail to preserve explicit neither exclusion, with different additional substitutions.
- **Human verification (P2, pending):** Verify actual negative marking with full motion.

### R25 — G25fic3QxDk_5-10-rgb_front

- **Claude categories:** negation;general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** No visually identified negation in either review; Claude makes negation primary, Codex general semantic.
- **Shared-failure rationale, Claude:** both insert a negation the reference does not have; both lose mulch/weeds/bed.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose weed-control purpose and target bed; substituted narratives differ.
- **Human verification (P2, pending):** Check whether output negation changes meaning or reflects suppression paraphrase.

### R26 — G3EfBFwsOpE_3-10-rgb_front

- **Claude categories:** question;spatial_relation;general_semantic.
- **Codex categories:** general_semantic;question.
- **Concern comparison:** Both flag hands above/outside crop; Claude infers likely degraded pose input, Codex only documents visible clipping.
- **Shared-failure rationale, Claude:** both lose 'which ... reverse' and the question.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both miss reverse textually, but historical directional language is closer than official's unrelated proposition.
- **Human verification (P1, pending):** Recover full hands and inspect exact model inputs; pose degradation remains unverified.

### R27 — g1HXoDkax5A_15-3-rgb_front

- **Claude categories:** question;general_semantic.
- **Codex categories:** question;general_semantic.
- **Concern comparison:** Both see hand near nose and question-form change; Claude claims nose content directly, Codex only describes location.
- **Shared-failure rationale, Claude:** both capture the pulling-off action; both lose 'nose' and the question.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose question framing and explicit nose/face concern while retaining generic removal.
- **Human verification (P2, pending):** Verify nose/removal semantics and nonmanual question despite full coding agreement.

### R28 — G42xKICVj9U_11-10-rgb_front

- **Claude categories:** general_semantic;spatial_relation.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both note reference mojibake and downward configurations; Claude proposes lower-body classifier, Codex no lexical interpretation.
- **Shared-failure rationale, Claude:** both lose boots / tied tight.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both omit the central boots-and-tight-tying content.
- **Human verification (P3, pending):** Resolve reference text and boots/tied-tight meaning.

### R29 — 92V3oH63zbQ_5-1-rgb_front

- **Claude categories:** question;spatial_relation;general_semantic.
- **Codex categories:** general_semantic;question;spatial_relation.
- **Concern comparison:** Both describe a mostly resting short window; Claude says reference cannot fit, Codex treats boundary mismatch as possible.
- **Shared-failure rationale, Claude:** both lose the whole question.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose baseball/hand-position content and interrogative form; official adds a tautological clause.
- **Human verification (P1, pending):** Inspect source boundaries and unusual hands-inside-baseball wording.

### R30 — g2wUCRRni28_6-3-rgb_front

- **Claude categories:** repetition;general_semantic.
- **Codex categories:** repetition;general_semantic;spatial_relation.
- **Concern comparison:** Both find historical overall loop and closer official output; Codex also flags missing direction.
- **Shared-failure rationale, Claude:** official mostly right; ours degenerate.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose parting/direction specificity; sustained repetition only historical.
- **Human verification (P2, pending):** Check parting/directional detail; no signing loop established.

### R31 — g38AmwPAYvg_4-3-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both find lighting lost; Claude proposes focus/CAT-location confusion, Codex declines lexical explanation.
- **Shared-failure rationale, Claude:** both keep focus/interesting; both lose 'lighting'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both fail to preserve lighting as the subject of concentration.
- **Human verification (P3, pending):** Verify lighting and exclude unsupported location-driven causal account.

### R32 — G0Q6AlvH96I_8-2-rgb_front

- **Claude categories:** number;question;general_semantic.
- **Codex categories:** general_semantic;number;question;spatial_relation.
- **Concern comparison:** Both see changing fingers; Claude suggests counting trigger/closing-gap reading, Codex leaves count unverified and rates low.
- **Shared-failure rationale, Claude:** official close; ours unrelated counting.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both fail to express closing the gap fully; historical adds a count while official is a partial match.
- **Human verification (P2, pending):** Verify count versus closing-gap question; relation and grammar require motion.

### R33 — g0t4Wz5qsT8_12-8-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both find official closer; Claude proposes SAFE confusion, Codex no lexical explanation.
- **Shared-failure rationale, Claude:** official close; ours unrelated.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both change comedy wording, but official preserves most event structure while historical changes topic.
- **Human verification (P3, pending):** Adjudicate comedy/cartoon paraphrase and historical topic change.

### R34 — g3DkYITeIy0_4-3-rgb_front

- **Claude categories:** spatial_relation;general_semantic.
- **Codex categories:** general_semantic;spatial_relation.
- **Concern comparison:** Both describe mouth/chin-region hands; Claude interprets tracing-around teeth, Codex records text-only spatial mismatch.
- **Shared-failure rationale, Claude:** both fixate on mouth vocabulary; neither renders 'wraps around'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both introduce lip-related content; official retains teeth and approximate fit unlike historical.
- **Human verification (P2, pending):** Verify tooth/lip and wrapping relation with motion.

### R35 — G2kVb4gINSI_1-10-rgb_front

- **Claude categories:** name;fingerspelling;repetition;general_semantic.
- **Codex categories:** general_semantic;repetition;name.
- **Concern comparison:** Both note hand over opposite palm and no confidently readable name; Claude calls repeated push-up depiction, Codex emphasizes 3–5 s hold and possible window mismatch.
- **Shared-failure rationale, Claude:** both lose 'Studio Group X' and 'push ups'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both omit the exercise and correct identity; only historical repeats an unrelated instruction.
- **Human verification (P1, pending):** First establish whether introduction is in clip; then adjudicate motion and repeated squeeze-down wording.

### R36 — G095RWKQ39g_10-1-rgb_front

- **Claude categories:** repetition;fingerspelling;general_semantic.
- **Codex categories:** repetition;general_semantic.
- **Concern comparison:** Both see varied configurations and interior rest, with unrelated repetitive outputs; audit shows official duration much longer.
- **Shared-failure rationale, Claude:** both unrelated to the telescope/finder content; both repetitive.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both omit telescope-alignment procedure and repeat unrelated wording.
- **Human verification (P1, pending):** Obtain matching official frames; verify long reference coverage and reject unsupported causal conclusions.

### R37 — g25IORxoyXE_8-10-rgb_front

- **Claude categories:** spatial_relation;general_semantic.
- **Codex categories:** general_semantic;spatial_relation.
- **Concern comparison:** Both see hand-over-hand recurrence and missing center text; Claude reads spatial action, Codex no signed-center claim.
- **Shared-failure rationale, Claude:** both lose 'this part of my hand' and 'into center'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose the specified hand use and centering action.
- **Human verification (P2, pending):** Verify centering relation and hand-part specification.

### R38 — G1jsDl1mVvk_1-1-rgb_front

- **Claude categories:** general_semantic;fingerspelling.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both note long rest about 2.25–6.00 s and reference-coverage concern; both low.
- **Shared-failure rationale, Claude:** both keep 'black'; both lose 'referee', 'neon green or pink', the introduction.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both distort referee narrative and omit later introduction; errors differ despite some black/clothing overlap.
- **Human verification (P1, pending):** Inspect boundaries/coverage and referee/clothing reference; no confirmed color/spelling reads.

### R39 — -fZc293MpJk_5-1-rgb_front

- **Claude categories:** repetition;spatial_relation;general_semantic.
- **Codex categories:** general_semantic;repetition;spatial_relation.
- **Concern comparison:** Both see recurring upright/horizontal hand configuration; Claude suggests visual seed, Codex declines official-input linkage.
- **Shared-failure rationale, Claude:** both lose uphill / downhill / flat / air speed.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose slope/air-speed explanation; official alone repeats unrelated action.
- **Human verification (P2, pending):** Verify slope/airspeed relation on each input before causal repetition claims.

### R40 — G0PNAsonBGk_11-2-rgb_front

- **Claude categories:** number;repetition;general_semantic.
- **Codex categories:** general_semantic;number.
- **Concern comparison:** Both find official close and historical unrelated; Claude calls historical loop, Codex reads screw actions as sequential and flags participant shift.
- **Shared-failure rationale, Claude:** official nearly right; ours unrelated.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Historical changes topic; official is close textually with a possible participant-reference shift.
- **Human verification (P2, pending):** Verify count/agency and repetition definition; Codex low, Claude medium.

### R41 — g2iFC1st7zQ_1-3-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both find official near-paraphrase; Codex adds some/always scope concern; both low.
- **Shared-failure rationale, Claude:** official nearly right; ours unrelated.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Historical has major object/action substitution; official is a close paraphrase with a small quantifier shift.
- **Human verification (P2, pending):** Adjudicate whether official scope change is a material error.

### R42 — fZq8wTAYtmw_10-10-rgb_front

- **Claude categories:** repetition;general_semantic.
- **Codex categories:** repetition;general_semantic.
- **Concern comparison:** Both find English repetition and dense head/face configurations; Claude links lexical errors to location, Codex no causal claim.
- **Shared-failure rationale, Claude:** both fail and both repeat; reference about writing a drama screenplay.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose screenplay-writing meaning and generate redundant unrelated clauses.
- **Human verification (P3, pending):** Inspect official short input, screenplay meaning and transcript emphasis versus duplication.

### R43 — g2eTD-1Jcro_0-3-rgb_front

- **Claude categories:** general_semantic.
- **Codex categories:** general_semantic.
- **Concern comparison:** Both find prenatal/breath-flow specificity lost; Claude proposes BUTTERFLY reading, Codex no sign meaning assigned.
- **Shared-failure rationale, Claude:** both keep 'nice way to start'; both lose 'prenatal' and 'breath flow'.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose specific practice/flow description; official preserves more keywords but distorts their relationships.
- **Human verification (P3, pending):** Verify exercise terminology and whether official is paraphrase or added literal scene.

### R44 — G0zQm6X8uiQ_3-8-rgb_front

- **Claude categories:** repetition;general_semantic.
- **Codex categories:** general_semantic;repetition.
- **Concern comparison:** Both explicitly note 12–14.5 s sustained configuration and other rests; Claude links official loop to eye-region locations, Codex treats as unverified.
- **Shared-failure rationale, Claude:** both fixate on 'eye'; both lose brow, seal, tame, frames the face, polished.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose brow-specific functions and end incomplete; official additionally repeats top-of-eye relation.
- **Human verification (P1, pending):** Obtain official window and distinguish prolonged hold, recurrent articulation and English clause duplication.

### R45 — g3X3XE6M2_A_8-3-rgb_front

- **Claude categories:** spatial_relation;general_semantic.
- **Codex categories:** general_semantic;spatial_relation.
- **Concern comparison:** Both find stepping-side relation lost; Claude gives directional reading and official partial alignment, Codex no signed relation claim.
- **Shared-failure rationale, Claude:** official partially aligned; ours unrelated.
- **Shared-failure rationale, Codex:** Text-level overlap only; common visual cause is not established. Both lose relationship between cutting hand and stepping side; official retains isolated directional words.
- **Human verification (P2, pending):** Verify hand-cut/step-side correspondence with full motion.

## All eleven Codex low-confidence cases

| Case | Claude confidence / primary | Codex confidence / primary | Coding / shared C → K | Specific verification priority |
|---|---|---|---|---|
| R09 | low / fingerspelling | low / name | disagreement / partial → yes | Establish complete input coverage and named topic. |
| R10 | medium / general_semantic | low / general_semantic | partial / partial → yes | Inspect segmentation and reference alignment before translation attribution. |
| R15 | low / question | low / general_semantic | partial / no → partial | Verify proposition and nonmanual question/negation, not punctuation alone. |
| R23 | medium / general_semantic | low / general_semantic | partial / yes → partial | Verify coverage of later wall/negative clause before scoring omission. |
| R26 | low / question | low / general_semantic | disagreement / yes → partial | Recover full hands and inspect exact model inputs; pose degradation remains unverified. |
| R29 | medium / question | low / general_semantic | partial / yes → partial | Inspect source boundaries and unusual hands-inside-baseball wording. |
| R32 | medium / number | low / general_semantic | disagreement / no → partial | Verify count versus closing-gap question; relation and grammar require motion. |
| R35 | low / name | low / general_semantic | disagreement / partial → partial | First establish whether introduction is in clip; then adjudicate motion and repeated squeeze-down wording. |
| R38 | low / general_semantic | low / general_semantic | partial / partial → partial | Inspect boundaries/coverage and referee/clothing reference; no confirmed color/spelling reads. |
| R40 | medium / number | low / general_semantic | disagreement / no → no | Verify count/agency and repetition definition; Codex low, Claude medium. |
| R41 | low / general_semantic | low / general_semantic | full / no → no | Adjudicate whether official scope change is a material error. |

Both low: R09, R15, R26, R35, R38, R41 (6). Claude medium → Codex low: R10, R23, R29, R32, R40 (5). All eleven are explicitly included in the priorities; R41 remains low even though its coding agrees fully because the official output may be an acceptable paraphrase.

## Prioritized ASL-fluent human verification

| Priority | Cases | What to resolve first |
|---|---|---|
| P1 — input integrity / visual adequacy (10) | R09, R10, R15, R23, R26, R29, R35, R36, R38, R44 | R26 clipped hands; R29 mostly rest; R10/R23/R38 segmentation; R35 introduction coverage versus held/repeated action; R44 prolonged hold and official window; R36 large official-duration difference; R09/R15 five-frame inadequacy. |
| P2 — meaning / category / threshold adjudication (26) | R01, R02, R03, R04, R05, R06, R12, R14, R16, R17, R18, R19, R20, R21, R22, R24, R25, R27, R30, R32, R34, R37, R39, R40, R41, R45 | Resolve model category disagreements, unreadable spelling/counts, negation/question/spatial constructions; R12/R40 repetition threshold; R22 NOT hypothesis; R32 counting versus closing gap; R41 paraphrase scope. R03 prior-exposure limitation and official coverage. |
| P3 — remaining cases, still unverified (9) | R07, R08, R11, R13, R28, R31, R33, R42, R43 | Check reference artifacts, technical terms, perspective and omissions. Agreement never substitutes for fluent review. |

Recommended initial sequence: **R26, R29, R35, R10, R23, R38, R44, R36, R09, R15**, then **R22, R32, R40, R41**, then the remaining P2/P3 cases. Obtain full-motion matching historical and official inputs, boundary/crop provenance and source context first. Have the human record evidence independently before consulting model interpretations where practical.

## Strongest agreement and most important disagreements

- **Strong physical agreement:** R10/R23/R38 rest intervals, R26 clipping, R29 mostly resting and R44 12–14.5 s hold. These justify input-integrity checks, not a particular ASL interpretation.
- **Strong English agreement:** all nine frozen official repetition cases plus R01/R19; both find official near-paraphrase for R40/R41 and historical substantially worse; recurring semantic losses such as names/affiliations, bow terminology and technical content.
- **Full coding agreement:** R27, R41, R42, R43. R27 still differs in the strength of visual nose/question claims; R41 needs paraphrase/scope adjudication.
- **Category policy disagreement:** Claude proposes fingerspelling/number/spatial mechanisms; Codex usually assigns general_semantic or textual name mismatch and withholds sign recognition. Primary category differs in 24/45, even though many full category sets or English findings overlap.
- **Most consequential interpretation differences:** R35 movement/push-up reading versus hold/mismatch; R22 proposed NOT versus unread sign; R20/R44 official-output visual grounding versus unavailable exact official input; R12/R40 ordinary framing/sequential action versus English loop.
- **Shared-failure coding:** 21 differences are all adjacent yes/partial or no/partial; there is no direct yes/no contradiction. Treat strength of common failure separately from whether official is closer.

Do not adopt a proposed ASL meaning, causal decoder account, or automatic weak category as verified because multiple sources repeat it. The two model reviews are unverified, and the automatic audit is frozen rule output.

## Source links and preservation

- [Automatic inspection sheet](../../10.18/asl-review-inspection-sheet/inspection_sheet.csv)
- [Frozen repetition audit CSV](../../10.18/asl-review-inspection-sheet/repetition_audit.csv) and [audit report](../../10.18/asl-review-inspection-sheet/repetition_audit.md)
- [Claude model_review CSV](model_case_analysis.csv) and [Claude report](MODEL_CASE_ANALYSIS.md)
- [Codex codex_review CSV](codex_case_analysis.csv) and [Codex report](CODEX_CASE_ANALYSIS.md)
- [Audit selection code](../../10.18/asl-review-inspection-sheet/scripts/repetition_audit.py) and [taxonomy rule code](../../10.13/asl-unisign-error-taxonomy/scripts/taxonomy.py)

The rule code was read only to explain existing rule behavior; no audit/taxonomy script was run. The eight original prompt/review/inspection/audit files used in this comparison were checked by SHA-256 before and after report creation and remained byte-identical. No H18/H19 or P0-18 frozen file was modified. No commit or push performed.

## Final comparison result

1. **Agreement:** 4 full / 28 partial / 13 coding disagreements under the stated rubric; primary matches 21/45.
2. **Official repetition:** frozen automatic 9 overlap with Codex in all 9: R03, R11, R16, R18, R20, R36, R39, R42, R44. Codex extras: R01, R19; Claude also explicitly identifies them. Reference-repeat eligibility, not a below-threshold output ratio, explains their exclusion.
3. **Strongest agreements:** physical rest/crop limitations and clear excess English repetition; major missing technical/identity content.
4. **Most important disagreements:** R35 visual/action interpretation, R22 negation hypothesis, R12/R40 English repetition definition, and official visual-causal interpretations without matching input.
5. **Human priorities:** input integrity first (P1 list above), then R22/R32/R40/R41 and remaining category/meaning disputes. All 45 remain unverified.
6. **Exact file created:** docs/daily_report/10.19/asl-model-case-analysis/MODEL_REVIEW_COMPARISON.md.
