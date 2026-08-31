# Public ASL dataset research — for continuous ASL→English translation evaluation

**Date:** 2026-08-30. **Scope:** research only — no downloads, no training, no model calls.
Every claim below is sourced from an official project page, official GitHub repository, or
the original paper (arXiv / ACL Anthology / NeurIPS proceedings / official project site).
Where a primary source did not state something directly, this document says **UNKNOWN**
rather than inferring or estimating it. Sources are linked inline; a link list is repeated
at the end of each dataset's section.

**Why this document exists.** We just spent a full workstream (`CONTAMINATION.md`,
2026-08-30) discovering that two of our own 13 corpus videos had their answer burned into
the model's input. The same category of mistake — trusting a dataset's framing without
checking what its "ground truth" actually is and how it was produced — applies directly to
public datasets too. Every entry below states its annotation **provenance** and, where the
source discusses it, its **production direction** (was the English written first and then
signed, or was the ASL signed first and then captioned/translated into English) — because
that question is exactly what caused our 1320 case to sit unresolved for a week.

---

## A. Continuous ASL→English translation datasets (the actual task we need)

### 1. How2Sign

- **Official site:** https://how2sign.github.io/
- **Paper:** Duarte et al., *"How2Sign: A Large-scale Multimodal Dataset for Continuous
  American Sign Language,"* CVPR 2021. [arXiv:2008.08143](https://arxiv.org/abs/2008.08143) /
  [CVPR Open Access](https://openaccess.thecvf.com/content/CVPR2021/html/Duarte_How2Sign_A_Large-Scale_Multimodal_Dataset_for_Continuous_American_Sign_Language_CVPR_2021_paper.html)
- **Task:** continuous ASL video → English sentence-level translation, plus depth, 3D pose,
  gloss, and speech (multimodal).
- **Continuous or isolated:** continuous, sentence-level clips.
- **ASL:** yes.
- **English sentence translation ground truth:** yes.
- **Production direction — read this before treating it as gold:** the ASL video is **not**
  the original content. How2Sign re-uses the pre-existing **How2** instructional-video
  corpus: a signer watches the *original English* instructional video with its subtitles and
  performs an ASL translation of it, at 0.75× speed, while being recorded (paper §3.1). The
  English text in the dataset is therefore the **source** script, and the ASL is a
  human interpretation of it — the reverse of what we need to assume when scoring a model
  that is supposed to go ASL→English. This is a real, stated methodological choice (11
  signers, 5 hearing/4 Deaf/2 hard-of-hearing, professional ASL interpreters or ASL-fluent),
  not a defect, but it means How2Sign measures "can the model recover the English script a
  fluent signer was performing," not "can the model transcribe spontaneous, unscripted ASL."
- **Annotation/reference provenance:** English transcript inherited from the original How2
  dataset's uploader-provided subtitles, time-realigned at sentence level by the How2Sign
  team; gloss separately annotated by ASL linguists using ELAN (paper §3.3–3.4).
- **Approximate size:** 80 hours raw / **79.12 h** total in the primary Green-Screen release;
  **35,191** sentence-level clips; vocabulary **16,644** words (paper Table 1/2).
- **Train/dev/test splits (Green Screen studio, the primary release; paper Table 2):**

  | Split | Clips | Duration |
  |---|---|---|
  | train | 31,128 | 69.62 h |
  | val | 1,741 | 3.91 h |
  | test | 2,322 | 5.59 h |

  (A separate, much smaller Panoptic 3D-studio subset exists for val/test only — 642/940
  clips, ~3h — with no train partition; not relevant here.)
- **Video availability:** direct Google Drive links per split/modality, listed on the
  official site, **no registration form required**. File sizes 1.2 GB–290 GB per
  split/modality, per the site.
- **Current download/access status (checked today):** live. The official page currently
  reads "This section is under construction. We will be releasing the other modalities
  soon!" for some *additional* modalities, but the core RGB video + English-transcript links
  are present and directly downloadable.
- **License / research-use restrictions:** **CC BY-NC 4.0** — non-commercial research use,
  attribution required (per official site).
- **Raw video actually downloadable today:** **yes**, verified via the official site — this
  is the most access-reliable dataset in this comparison because nothing depends on a
  third-party video host staying up.
- **Pretrained open-source models supporting it:** yes — it is the field's standard held-out
  test set. YouTube-ASL (below) fine-tunes on its own corpus and **reports a new
  state-of-the-art of 12.39 BLEU evaluated on How2Sign's test split** (Uthus et al. 2023).
  Multiple other SLT papers (OpenASL included) cite How2Sign numbers for comparison.
- **Suitable for inference-only evaluation:** yes — the 2,322-clip / 5.59h test split is
  exactly the right shape to pull a small clean subset from without training anything.
- **Fit for Curify's ASL→English product:** high for *methodology validation* (it is the
  field's standard benchmark, with a citable SOTA number to compare any OSS baseline or
  Curify's own model against); moderate for *content realism* — it's studio-recorded,
  scripted-then-signed content, not organic self-expression like Curify's real user uploads.
- **Recommendation: `PRIMARY_TRANSLATION_BENCHMARK`**

---

### 2. OpenASL

- **Official code/data repo:** https://github.com/chevalierNoir/OpenASL
- **Paper:** Shi, Brentari, Shakhnarovich, Livescu, *"Open-Domain Sign Language Translation
  Learned from Online Video,"* EMNLP 2022.
  [arXiv:2205.12870](https://arxiv.org/abs/2205.12870) /
  [ACL Anthology](https://aclanthology.org/2022.emnlp-main.427/)
- **Task:** continuous ASL video → English sentence-level translation.
- **Continuous or isolated:** continuous.
- **ASL:** yes.
- **English sentence translation ground truth:** yes.
- **Production direction — the opposite case from How2Sign, and closer to what we need:**
  the paper explicitly distinguishes this from interpreted content: *"Unlike prior datasets,
  OpenASL contains a mix of spontaneous and (presumably) interpreted signing videos... the
  videos used in OpenASL are 'self-generated' rather than interpreted, so the English
  subtitles are already aligned to the video accurately"* (paper §3). The content is ASL news
  (TheDailyMoth, Sign1News channels) and NAD sign-vlogs — people signing their own content,
  with English subtitles produced from/for that same signing, not a pre-existing English
  script performed into ASL. This is the direction Curify's product actually needs to be
  evaluated on.
- **Annotation/reference provenance — train vs. dev/test are NOT the same quality tier.**
  All **98,417** pairs come from auto-aligned subtitles (NLTK sentence segmentation matched
  to clip boundaries). Of these, **966 validation and 975 test pairs were manually
  proofread and corrected by professional ASL interpreters** who watched the actual video
  clip (paper §3, "The annotation of the validation and test sets is manually verified").
  The remaining ~96,476 training pairs are **not** manually verified — the paper states
  training data was not proofread "to save annotation effort." **Only the dev/test pairs are
  human-verified gold; do not treat the training pairs as such.**
- **Approximate size:** **288 hours**; **98,417** translation pairs total; vocabulary
  **33,549** words; **~220 signers** (paper Table 1 — signer count is approximate because
  identity could not be determined for all videos).
- **Train/dev/test splits:** **966** validation pairs and **975** test pairs are explicitly
  stated (randomly selected and manually verified); the remaining **≈96,476** pairs are
  training data (98,417 − 966 − 975, computed from the stated totals — the paper does not
  give an explicit training-pair count or an hours-per-split breakdown, so treat the
  per-split **hour** figures as **UNKNOWN**).
- **Video availability:** **not directly hosted.** The repo ships `openasl-v1.0.tsv`
  (timestamps into source YouTube videos) plus a download script; users run `yt-dlp`
  themselves against the original YouTube videos.
- **Current download/access status:** the official repo states plainly: **"Some videos may
  no longer be publicly available."** Real link-rot risk exists; the exact current
  attrition rate is **UNKNOWN** without actually attempting the bulk download.
  channels are still active as of this research, which lowers the *expected* risk (news
  channels tend to keep back-catalog up) but does not confirm current per-video status.
- **License / research-use restrictions:** **CC BY-NC-ND 4.0** — non-commercial, **and no
  derivative works**. The "ND" clause matters practically: it likely restricts republishing
  even a trimmed/re-encoded subset of the clips, which affects how freely we could mirror a
  small evaluation slice internally. Confirm with legal/manager before redistributing any
  derivative (e.g., a masked or re-encoded clip) beyond private internal use.
- **Raw video actually downloadable today:** **partially / UNKNOWN exact rate** — depends on
  per-video YouTube availability at fetch time; not verified in this research pass (no
  download was attempted, per this task's read-only-research instruction).
- **Pretrained open-source models supporting it:** the paper's own reference implementation
  and baselines are released with the repo; it is not as widely adopted as How2Sign as a
  cross-paper standard benchmark, though YouTube-ASL and later SLT papers cite it.
- **Suitable for inference-only evaluation:** yes in principle — **if** enough of the 975
  human-verified test pairs are still downloadable; this needs a fresh per-video
  availability check before committing to it as the eval set.
- **Fit for Curify's ASL→English product:** **high** for *content realism* — self-generated,
  spontaneous-signing content (deaf vloggers, ASL news) is much closer in spirit to Curify's
  real user-submitted clips than How2Sign's studio-scripted content. Weaker on access
  reliability and redistribution rights.
- **Recommendation: `SECONDARY_TRANSLATION_BENCHMARK`** — larger and more naturalistic than
  How2Sign, with genuinely human-verified dev/test references, but real link-rot exposure
  and an ND license that limits how we can share/derive from it.

---

### 3. YouTube-ASL

- **Official repo:** https://github.com/google-research/google-research/tree/master/youtube_asl
- **Paper:** Uthus, Tanzer, Georg, *"YouTube-ASL: A Large-Scale, Open-Domain American Sign
  Language-English Parallel Corpus,"* NeurIPS 2023 Datasets & Benchmarks.
  [arXiv:2306.15162](https://arxiv.org/abs/2306.15162) /
  [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/file/5c61452daca5f0c260e683b317d13a3f-Paper-Datasets_and_Benchmarks.pdf)
- **Task:** continuous ASL video → English caption, used chiefly as a large **pretraining/
  fine-tuning** corpus for SLT models (it is the corpus behind the 12.39 BLEU How2Sign SOTA
  cited above).
- **Continuous or isolated:** continuous.
- **ASL:** yes, in-the-wild.
- **English sentence translation ground truth:** present, but **weaker per-item provenance
  than OpenASL's dev/test.** Captions are drawn from YouTube uploader-provided/auto captions;
  the dataset's quality control is "native Deaf annotators reviewed these videos to filter
  out videos with poor quality or misaligned captions" (i.e., filtering at the *video* level),
  not sentence-by-sentence human re-verification of every caption the way OpenASL's dev/test
  was. Treat individual captions as "found and quality-filtered," not "expert-verified
  translation."
- **Annotation/reference provenance:** mined by searching YouTube's machine-generated
  Knowledge-Graph tags for ASL-related content, up to January 2022, then Deaf-annotator
  video-level filtering (paper, dataset-mining section).
- **Approximate size:** **~1,000 hours** (984 h stated in the paper), **11,093** videos,
  **610,193** English captions, **>2,500 unique signers** — by a wide margin the largest
  ASL-English resource found in this research pass.
- **Train/dev/test splits:** this corpus is used as a **pretraining/fine-tuning** source, not
  a held-out benchmark in its own right — the paper's own evaluation reports results on
  **How2Sign's** test split, not on an internal YouTube-ASL held-out set. Any
  YouTube-ASL-native split breakdown for translation benchmarking is **UNKNOWN** from the
  sources retrieved.
- **Video availability:** **video IDs only** ("as with the similar YouTube-8M dataset, we are
  releasing the video IDs" — official README), hosted via Google Cloud Storage as an index;
  actual video content must be downloaded per-ID by the user.
- **Current download/access status:** not directly stated in the README; given this is
  individual-creator YouTube content (not a curated broadcaster archive like OpenASL's news
  channels), link-rot exposure is plausibly **higher**, but the exact current attrition rate
  is **UNKNOWN** — not verified in this pass.
- **License / research-use restrictions:** one secondary summary encountered during search
  stated CC BY 4.0, but the official README fetched directly in this research pass **did not
  state a license**. Treat the license as **UNKNOWN pending direct confirmation** from the
  official repo's LICENSE file before relying on this for anything beyond private internal
  research use.
- **Raw video actually downloadable today:** **UNKNOWN** exact rate — would require attempting
  the ID list; not done in this read-only pass.
- **Pretrained open-source models supporting it:** **yes** — this is literally the corpus
  behind the current published SOTA (12.39 BLEU on How2Sign), and multiple follow-on papers
  (e.g., YouTube-SL-25) build on it.
- **Suitable for inference-only evaluation:** **not its intended role.** The field's own
  convention (including this corpus's own paper) is to fine-tune *on* YouTube-ASL and
  *evaluate on How2Sign*, not to hold out a YouTube-ASL-native test set. Using it as our
  evaluation slice would fight the grain of how it's meant to be used and inherits its
  weaker per-caption provenance.
- **Fit for Curify's ASL→English product:** excellent as a future **pretraining/fine-tuning**
  source if Curify ever trains or adapts an OSS ASL model; weak as an **evaluation** set for
  exactly the reasons above.
- **Recommendation: `SECONDARY_TRANSLATION_BENCHMARK`** — real, large-scale, genuine ASL↔English
  data, but better suited to training than to being our small inference-only comparison slice;
  use How2Sign/OpenASL for that instead.

---

### 4. DailyMoth-70h (auxiliary continuous-translation resource, found during the broader search)

- **Official repo:** https://github.com/facebookresearch/ssvp_slt (Meta/FAIR, "SSVP-SLT")
- **Paper:** *"Towards Privacy-Aware Sign Language Translation at Scale,"* ACL 2024.
  [arXiv:2402.09611](https://arxiv.org/abs/2402.09611) /
  [ACL Anthology PDF](https://aclanthology.org/2024.acl-long.467.pdf)
- **Task:** continuous ASL video → English translation.
- **Continuous or isolated:** continuous.
- **ASL:** yes.
- **English sentence translation ground truth:** yes — aligned English captions from
  TheDailyMoth ASL news channel.
- **Annotation/reference provenance:** obtained "through a license agreement" with the source
  channel (per the paper), not a bare scrape — this is a materially different, more durable
  provenance path than OpenASL/YouTube-ASL's YouTube-scrape approach.
- **Approximate size:** **70+ hours**, **496** raw videos, **48,386** segmented clips — but
  from a **single native ASL signer**.
- **Train/dev/test splits:** manifest TSVs exist in the repo for train/val/test, but exact
  counts are **UNKNOWN** from the documentation retrieved (would require reading the manifest
  files themselves).
- **Video availability:** downloadable directly via the repo's own
  `scripts/download_dm70.sh`, which provides **both raw and unblurred segmented clips** —
  this is a real download mechanism, not a bare YouTube-ID list, per the repo's own
  documentation.
- **Current download/access status:** appears actively maintained (Meta/FAIR repository);
  not independently re-verified by attempting a download in this pass.
- **License / research-use restrictions:** **UNKNOWN precise terms** for the dataset itself —
  it was obtained via a specific license agreement with the source channel, which is not the
  same thing as the code repository's own license and was not directly confirmed in this
  pass. Do not assume open/permissive use without reading the actual license file first.
- **Raw video actually downloadable today:** **yes, via the official script**, per repo
  documentation (not independently re-verified by running it).
- **Pretrained open-source models supporting it:** yes — this dataset is the subject of its
  own paper's pretraining/fine-tuning experiments, with released code.
- **Suitable for inference-only evaluation:** possible, but **single-signer, single-domain
  (news) content severely limits how much any conclusion generalizes** — this is explicitly
  the survey's own caveat (see §C below) and matches the same "framing/limited-generalization"
  problem we already flagged internally for our own 1466/1467 pair.
- **Fit for Curify's ASL→English product:** limited as a stand-alone evaluation benchmark
  because of the single-signer restriction; more useful as an auxiliary/training-adjacent
  resource or a secondary sanity check, not as the primary generalizable eval set.
- **Recommendation: `SECONDARY_TRANSLATION_BENCHMARK`** — genuine, reliably-downloadable
  continuous ASL→English data, but flag the single-signer limitation every time it's cited,
  the same way we flag 1466/1467's head-crop limitation internally.

---

## B. Isolated sign recognition datasets — NOT translation benchmarks

**Do not equate these with A.** Both datasets below have no continuous signing and no
English sentence-level ground truth at all — only single-word gloss/sign labels. Using
either to validate a continuous ASL→English translator would measure the wrong task
entirely, the same way scoring a sentence-translation system against a flashcard quiz would.

### 5. WLASL (Word-Level American Sign Language)

- **Official repo:** https://github.com/dxli94/WLASL
- **Paper:** Li et al., *"Word-level Deep Sign Language Recognition from Video: A New
  Large-scale Dataset and Methods Comparison,"* WACV 2020 (Best Paper Honourable Mention,
  Applications). [arXiv:1910.11006](https://arxiv.org/abs/1910.11006)
- **Task:** isolated sign/gloss video classification (which single sign is this?).
- **Continuous or isolated:** **isolated.**
- **ASL:** yes.
- **English sentence translation ground truth:** **no** — single-word gloss labels only.
- **Annotation/reference provenance:** videos collected from educational sign-language
  websites (ASLU, ASL-LEX) and YouTube tutorials, from 20 different source websites;
  **68,129** videos of **20,863** glosses originally collected, curated into standard
  top-K subsets (WLASL100/300/1000/2000).
- **Approximate size:** WLASL2000 (the most-used subset) targets the 2,000 most common
  glosses; exact per-subset video counts are given in the repo's `index.md`/JSON but were
  **not extracted with exact numbers** in this pass — mark exact split counts as **UNKNOWN**
  pending a direct read of the JSON metadata.
- **Train/dev/test splits:** a `split` field exists per video in the dataset JSON; exact
  counts **UNKNOWN** from the README alone.
- **Video availability:** YouTube URL list + `video_downloader.py`; the maintainers state
  directly: **"Videos can disappear over time due to expired urls, so you may find the
  downloaded videos incomplete"** — with a request-form fallback (~1 week turnaround) for
  missing or pre-processed videos.
- **Current download/access status:** **partial** — known incompleteness acknowledged by
  the maintainers themselves.
- **License / research-use restrictions:** **Computational Use of Data Agreement (C-UDA)** —
  explicitly **"No commercial usage is allowed."**
- **Raw video actually downloadable today:** partially; known gaps, request-based fallback
  exists.
- **Pretrained open-source models supporting it:** yes, extensively — I3D, ST-GCN, TGCN and
  many others; this is the standard ISLR benchmark. (Relevant internal context: `curify-studio`'s
  own prior evaluation already ran a TGCN model against WLASL-derived poses and scored 0/12
  top-5 in-domain — a real negative result already on file internally, not new information.)
- **Suitable for inference-only evaluation:** only for isolated-sign classification — **wrong
  task shape** for sentence-level translation.
- **Fit for Curify's ASL→English product:** **low** as an evaluation benchmark — task
  mismatch. Only relevant as a component/pretraining signal for a hand-built pipeline (e.g., a
  sign-spotting sub-module), never as a stand-in for translation accuracy.
- **Recommendation: `AUXILIARY_SIGN_RECOGNITION`**

### 6. ASL Citizen

- **Official project page:** https://www.microsoft.com/en-us/research/project/asl-citizen/
- **Official code repo:** https://github.com/microsoft/ASL-citizen-code
- **Paper:** Desai et al., *"ASL Citizen: A Community-Sourced Dataset for Advancing Isolated
  Sign Language Recognition,"* NeurIPS 2023 Datasets & Benchmarks.
  [arXiv:2304.05934](https://arxiv.org/abs/2304.05934)
- **Task:** isolated sign language **dictionary retrieval** — a user demonstrates one sign to
  a webcam, the system returns the closest-matching dictionary entries.
- **Continuous or isolated:** **isolated.**
- **ASL:** yes.
- **English sentence translation ground truth:** **no** — isolated sign labels only (mapped
  to one of 2,731 target signs), no continuous video, no sentence-level content at all.
- **Annotation/reference provenance:** crowdsourced from **52 everyday signers** (not
  professional interpreters) under **IRB-approved consent**, in a variety of everyday
  recording environments — deliberately not a studio dataset.
- **Approximate size:** **83,399 videos** / **2,731 distinct signs** / 52 signers.
- **Train/dev/test splits:** **UNKNOWN** exact counts — not stated in the project page or
  code-repo overview fetched in this pass; would require the full paper PDF/appendix.
- **Video availability:** single direct archive download —
  `wget https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip`
  — **no per-video scraping needed at all.**
- **Current download/access status:** **live and directly hosted** — the most
  access-reliable dataset in this entire comparison; no third-party video host dependency.
- **License / research-use restrictions:** dataset usage terms are set by Microsoft Research
  (research use permitted; **commercial use requires contacting
  ASL_Citizen@microsoft.com**). The baseline **code** repository (`ASL-citizen-code`) is
  separately MIT-licensed — **do not conflate the code license with the dataset's own usage
  terms**; they are two different things covering two different artifacts.
- **Raw video actually downloadable today:** **yes**, verified via the official project page.
- **Pretrained open-source models supporting it:** yes — I3D and ST-GCN baselines ship with
  the official code repo.
- **Suitable for inference-only evaluation:** only for isolated-sign recognition/retrieval —
  **wrong task shape** for sentence-level translation, same as WLASL.
- **Fit for Curify's ASL→English product:** **low** for the same task-mismatch reason as
  WLASL.
- **Recommendation: `AUXILIARY_SIGN_RECOGNITION`**

---

## C. Broader landscape check (2024–2026)

A recent survey, *"Sign-Language Datasets at Scale: A Comprehensive Survey on Resources,
Benchmarks, and Annotation Standards"* (2026,
[arXiv:2606.19352](https://arxiv.org/abs/2606.19352)), was used to check whether anything
newer or larger than How2Sign/OpenASL/YouTube-ASL has since displaced them for ASL-English
continuous translation specifically. Per that survey (as summarized via direct fetch of the
paper's HTML in this research pass):

- **YouTube-ASL remains the largest** ASL-English continuous-translation resource found
  (~1,000 hours), with the survey itself flagging the same access weakness identified above:
  *"only YT IDs (link-rot, geo-blocks) limit reproducibility."*
- **No dataset larger or more suitable than How2Sign, OpenASL, or YouTube-ASL for this
  specific task was identified** in the 2024–2026 window, per the survey.
- **DailyMoth-70h (2024)** was the one genuinely new continuous-translation resource
  surfaced — covered separately above, with its single-signer limitation noted by the survey
  itself.
- Two other 2025 items surfaced in general search were checked and are **not relevant** to
  this task: **FSboard** (2025) is a fingerspelling-only dataset (>3M characters, smartphone-
  collected) — isolated/character-level, not sentence translation; **SignMusketeers** (2025)
  is a modeling *approach* paper, not a new dataset. Neither changes the recommendation
  above.

---

## Sources (primary, cited inline above)

- How2Sign: https://how2sign.github.io/ · https://arxiv.org/abs/2008.08143 · https://openaccess.thecvf.com/content/CVPR2021/html/Duarte_How2Sign_A_Large-Scale_Multimodal_Dataset_for_Continuous_American_Sign_Language_CVPR_2021_paper.html
- OpenASL: https://github.com/chevalierNoir/OpenASL · https://arxiv.org/abs/2205.12870 · https://aclanthology.org/2022.emnlp-main.427/
- YouTube-ASL: https://github.com/google-research/google-research/tree/master/youtube_asl · https://arxiv.org/abs/2306.15162 · https://proceedings.neurips.cc/paper_files/paper/2023/file/5c61452daca5f0c260e683b317d13a3f-Paper-Datasets_and_Benchmarks.pdf
- DailyMoth-70h / SSVP-SLT: https://github.com/facebookresearch/ssvp_slt · https://arxiv.org/abs/2402.09611 · https://aclanthology.org/2024.acl-long.467.pdf
- WLASL: https://github.com/dxli94/WLASL · https://arxiv.org/abs/1910.11006
- ASL Citizen: https://www.microsoft.com/en-us/research/project/asl-citizen/ · https://github.com/microsoft/ASL-citizen-code · https://arxiv.org/abs/2304.05934
- Landscape survey: https://arxiv.org/abs/2606.19352
