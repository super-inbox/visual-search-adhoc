# ASL review inspection sheet (task e)

**Status: prepared, review NOT started.** One row per clip for the 45 clips of the 10.13 manual-review package. Every
reviewer field is blank (`review_status = not_started`). Every category in this sheet is an **automatic weak label**:
nothing here says what is actually signed.

Built from existing data only, with no decoding or new model runs:
`../../10.13/asl-unisign-error-taxonomy/{manual_review/review_packet.csv, manual_review/weak_labels.csv, error_taxonomy_annotations.jsonl}`
(P0-12 T4/fp16 predictions) and the How2Sign v2 manifest. All 45 clips are `exploratory` in the P0-16 ledger; none of
them, or their source videos, are in H18 / H19.

| File | What it is |
|---|---|
| `inspection_sheet.csv` | The sheet: 45 rows, columns below |
| `inspection_sheet.html` | The same rows as a review page: video, the three texts (words that also occur in the ground truth are highlighted), AUTO evidence, HUMAN review box. Top table: concrete examples per category. Autosaves in the browser; **Export** writes `inspection_sheet.csv` with the reviewer fields filled; **Import CSV** restores an export |
| `scripts/build_inspection_sheet.py` | Builder (`python3 -I scripts/build_inspection_sheet.py`, CPU, ~1 s, byte-identical rebuilds) |
| `scripts/inspection_sheet_template.html` | Page layout |
| `videos/` (**local only, git-ignored**) | The 45 diagnostic clips as `videos/<clip_id>.mp4`, placed by `scripts/build_review_package.py`. The page plays them directly |
| `videos_manifest.csv` | Per clip: file, sha256, bytes, duration, source path (committed; the videos themselves are not) |
| `scripts/build_review_package.py` | Copies the 45 clips from the local How2Sign v2 directory after checking each against the `video_sha256` of the committed How2Sign v2 `manifest.csv`; `--zip PATH` also writes a self-contained, deterministic review package |
| `repetition_audit.md`, `repetition_audit.csv`, `scripts/repetition_audit.py` | Audit of the official-output repetition loops (below) |

## The two outputs

Both come from the **same public Uni-Sign checkpoint** (`how2sign_pose_only_slt.pth`). Neither is a new model. Only the
**input preparation** differs:

| Column | Condition | Input preparation |
|---|---|---|
| `prod_output` ("our/old output") | `B_ours_5p39` | Our old pipeline: **our pose extractor** on the **full frame**, clips cut at the **original How2Sign speech timestamps** (= P0-18 `A_old`). **Provisional** stand-in for the production output (below) |
| `unisign_output` ("official output") | `A_official` | The **official How2Sign / Uni-Sign experimental inputs**: official poses from clips cut at the **re-aligned signing timing** and cropped to the signer (the official signer-crop videos) |

The old pipeline did **not** use the re-aligned signing timing or the official signer crop. "Official preprocessing"
means those dataset-author inputs; it is not preprocessing we invented, and it is not a different model.

**`prod_output` is provisional.** `B_ours_5p39` is the historical our-pipeline baseline (P0-18 `A_old`). It has **not**
been verified as the current live production system and must not be presented as such unless that is separately
confirmed. If the actual production output for these 45 clips is identified later, replace `prod_output` (and
`prod_output_source`, `chrf_prod`, `auto_error_type_prod`) and rebuild. The same caveat is in every CSV row
(`prod_output_source`) and in the page header. P0-18 outputs are not included (P0-18 closed at development as NOT SUPPORTED; see `../../10.16/asl-p0-18-auto-preprocessing/`).

## Columns

**Context (automatic, read-only)**

| Column | Meaning |
|---|---|
| `review_id`, `clip_id` | R01–R45 (same order and IDs as the 10.13 package), How2Sign clip |
| `video_id` | How2Sign source video (`source_video_id` in the manifest) |
| `video_path`, `video_status` | Repo-relative source mp4 (git-ignored; sha256-verified), `AVAILABLE` for all 45. The page plays `videos/<clip_id>.mp4` first |
| `duration_s`, `queue_reasons` | Clip length; why the clip was queued in 10.13 |
| `ground_truth` | How2Sign English reference. It is a **translation**, not a gloss of the signing |
| `prod_output`, `unisign_output` | See above |
| `prod_output_source` | Provenance and caveat for `prod_output` (provisional; B_ours_5p39 = P0-18 A_old; not verified as live production) |
| `prod_vs_unisign` | `identical` / `differ` (normalised tokens). All 45 differ |
| `chrf_prod`, `chrf_unisign` | Sentence chrF vs ground truth |
| `auto_error_type_prod`, `auto_error_type_unisign` | Committed taxonomy primary error type (substitution / hallucination / repetition_loop / omission / over_generation) |

**Weak labels (automatic, unverified): `initial_label_source = automatic_weak`, `initial_label_status = candidate_unverified`**

| Column | Meaning |
|---|---|
| `weak_focus_candidates` | Focus categories whose item appears in the **English reference** (committed 10.13 weak labels, plus the new spatial proxy) |
| `initial_error_category` | One primary category (rule below) |
| `initial_error_categories_all` | Every focus category where at least one output loses or inserts the item, plus `general_semantic` |
| `evidence_notes` | Per category, separated by ` \|\| ` with the primary first: the reference items, what each output kept, and whether the item was `MISSED` or `INSERTED` by prod / Uni-Sign. The last line is always `general` (error type, chrF, content recall) |
| `visual_flags` | Pose-derived visual proxies (out of frame, near face, low confidence, …) |
| `showcase_example` | Category name if the row is one of the concrete examples (≤ 3 per category) |
| `asl_fluent_question` | What only an ASL-fluent reviewer can settle for the primary category |

**Human review (blank)**

| Column | Allowed values |
|---|---|
| `reviewer`, `reviewer_asl_background` | Free text. Background is required before a category can be set on the page |
| `reviewer_verified_category` | `;`-separated: `fingerspelling`, `names`, `numbers`, `negation`, `questions`, `spatial_relations`, `general_semantic`, `no_error`, `unclear`, `other` |
| `verified_label_source` | Written `human_verified` on export when a category is set; blank otherwise |
| `reviewer_comment` | Timestamps, what is actually signed, why |
| `review_status` | `not_started` (initial value; the only prefilled review field), `in_progress`, `reviewed`, `needs_second_review`, `video_unplayable` |
| `reviewed_at` | Set by the page when the status becomes `reviewed` |

A weak label never becomes a verified label. `initial_*` columns are never overwritten. Verified labels exist only
where `verified_label_source = human_verified`.

## How the initial category is chosen

For each focus category the builder checks the outputs against the reference using the committed taxonomy rules,
imported from `taxonomy.py` and cross-checked against its stored `category_checks`:

| Category | Reference-side trigger (weak) | Output check |
|---|---|---|
| fingerspelling | `fingerspelling_candidate` (acronym, single capital letter, letter-hyphen, CamelCase, name list, capitalised word not in dictionary) | evidence tokens present in the output |
| names | `named_entity_candidate` (non-initial capitalised words) | same; also lists capitalised words the output invents (e.g. "Lisa Richey" for "Les Whitley") |
| numbers | `number_candidate` (strict) | reference number values present; or a number inserted when the reference has none |
| negation | `negation_candidate` (not / no / never / n't …) | negation dropped, or inserted when the reference has none |
| questions | `question_candidate` (`?` in the reference) | `?` lost, or inserted. A `?` that occurs only inside a word (mojibake apostrophe, e.g. `you?re`, R28) is marked a likely false positive and not counted |
| spatial_relations | **New in this sheet, weakest**: strict English locative phrases (above, inside, around, center, side, next to, in front of, …; not here / there / right / over) | phrase present in the output |

Primary = the first failing category in the order negation → questions → numbers → names → fingerspelling →
spatial_relations. Fingerspelling moves ahead of names when its evidence is letter-level (acronym, single letter,
letter-hyphen, CamelCase). A loss of a reference item outranks an insertion. With no focus failure the primary is
`general_semantic`, or `no_clear_error` if both chrF ≥ 39.952 (none of the 45).

Result: general_semantic 13, negation 8 (5 lost, 3 inserted), numbers 7 (6 lost, 1 inserted), names 6, questions 5,
fingerspelling 3, spatial_relations 3.

**Limitations.** These are English-text checks. "Name missed" means the English name is not in the output. It does not
mean the name was fingerspelled, or even signed. A reference `?` does not mean a question was marked in ASL, and an
English locative does not mean signing space was used. The 45 clips are a stratified, worst-first sample (10.13), so
counts are not rates.

## Videos

The 45 diagnostic clips are How2Sign test clips (third-party dataset), so they are **not committed**. They are shipped
as a review package that is rebuilt reproducibly from the local, checksummed How2Sign v2 copies:

```
python3 -I scripts/build_review_package.py            # -> videos/<clip_id>.mp4 (git-ignored) + videos_manifest.csv
python3 -I scripts/build_review_package.py --zip ~/Desktop/curify/asl-review-package/asl_inspection_review_package.zip
```

Every clip is checked against the `video_sha256` column of the committed How2Sign v2 manifest
(`asl-translator/data/public_benchmarks/how2sign_v2/manifest.csv`) before it is copied. 45 clips, 60.2 MB, H.264 1280×720 (plays in any current browser). The zip contains the page, the sheet CSV, this
README, the repetition audit, `videos_manifest.csv`, `SHA256SUMS` and `videos/`. Share it within the How2Sign licence
terms (CC BY-NC 4.0).

**Download:** the built package is a GitHub Release asset of this (private) repository, not committed to git:
<https://github.com/super-inbox/visual-search-adhoc/releases/download/asl-review-package-2026-10-19/asl_inspection_review_package.zip>
(release `asl-review-package-2026-10-19`). Size **60,239,549 bytes**, SHA-256
`b1728e39b8d139a9160bcfc813c240521f3865668700195ef76846652deea02a`; check with
`shasum -a 256 asl_inspection_review_package.zip`. The videos are How2Sign data, **CC BY-NC 4.0** (non-commercial,
attribution required). The README inside the released zip predates this paragraph, so a `--zip` rebuild from the
current README gives a different SHA-256; the release asset is the reference copy.

The page looks for each clip at `videos/<clip_id>.mp4` next to itself first, then at the repo path
(`asl-translator/data/public_benchmarks/how2sign_v2/videos/`). If neither exists, the card says so; **Load videos…**
then plays files picked by hand.

## Repetition: official preprocessing does not eliminate it

**Official preprocessing does not eliminate repetition; repetition is not purely a long-input failure.**

- The official output (`A_official`) has the automatic `repetition_loop` label on **9 of the 45** clips (committed
  10.13 rule: a repeated word 3-gram in the output that the reference does not have, repeated-3-gram ratio ≥ 0.15). The
  our/old output has it on 10; on 5 of the 9 clips both outputs loop.
- The 9 official cases have official input lengths from **4.0 s to 32.5 s** (median 16.4 s): 1 short (≤ 5 s), 3 medium,
  5 long (> 10.67 s, Uni-Sign's 256-frame input cap). Details: `repetition_audit.md`.
- On the whole 128-clip benchmark the official arm loops on 3 / 45 short (7 %), 6 / 50 medium (12 %) and 9 / 33 long
  (27 %) clips.
- Reading: input length and preparation may raise the risk of a loop, but the Uni-Sign decoder / generation itself also
  has an intrinsic repetition failure mode, which occurs on short, correctly prepared clips too.
- These are English-text labels. They do not say whether, or why, anything was repeated in the signing.

## Review workflow

1. Build the package (above) or unzip it, and open `inspection_sheet.html` (Chrome / Edge / Firefox). Each card shows the
   video next to the ground truth, the our/old output and the official output.
2. Enter your name and **ASL background** in the header. The category boxes stay locked until both are filled.
3. Start with the **Concrete examples** table (21 rows, 3 per category), then work through all clips. Filter by
   initial category or status as needed.
4. Per clip: play the video at 1× **before** reading the AUTO evidence, then compare ground truth / our/old output /
   official output. Then tick every category that applies to what is
   **actually signed** and the outputs get wrong (`no_error` if the outputs are fine, `unclear` if the video does not
   settle it). Add timestamps and the reason in the comment, then set `review_status`.
5. **Export** at the end of each session. Save as `labels/inspection_sheet__<reviewer>.csv`, and never overwrite the
   generated `inspection_sheet.csv`. **Import CSV** continues a saved session.
6. Ideally a second reviewer works independently. Merging into the taxonomy follows the 10.13 `manual_review/README.md`
   plan: added alongside the weak labels, never replacing them.

**Who must fill what.** `reviewer_verified_category` for fingerspelling, names, numbers, negation, questions and
spatial_relations requires an **ASL-fluent reviewer** (Deaf / HoH signer, CODA, certified interpreter or equivalent).
These are judgements about the signing. A non-signer may only add text-level comments (e.g. "Uni-Sign repeats",
"prod invents a name") and should leave the category for the ASL-fluent reviewer.
