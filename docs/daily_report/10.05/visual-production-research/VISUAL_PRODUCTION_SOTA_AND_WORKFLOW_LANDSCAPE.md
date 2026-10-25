# Visual Production: SOTA and workflow landscape

Date: 2026-10-05. Scope: (1) ecommerce model dressing / virtual try-on, and (2) professional retouching, viewed through **delivery reliability and controllable iterative revision**. Analysis only; **no new pipeline was built and no customer case was replayed.**

Every claim is tagged:

- **[CURIFY]** = prior Curify evidence
- **[EXT]** = new external research done for this report
- **[INF]** = new inference / recommendation

Companion files:

| File | Contents |
|---|---|
| `academic_methods.csv` | 27 methods (A01–A27) |
| `practitioner_workflows.csv` | 14 workflows (P01–P14) |
| `failure_solution_matrix.csv` | 16 failures (F01–F16) |
| `candidate_curify_pipelines.md` | candidate pipelines CP1–CP5 |
| `sources.md` | all sources |

## 0. What prior Curify work covers, and what it doesn't

**[CURIFY] Already covered, reused rather than redone:**

- **Ecommerce domain workflow (8.8, `ecommerce_001` / ECOM-01 Meitu Tmall).** Detail-page image-suite rules: ≥7 images in 4 categories, a mandatory white-background image, ≥60% product-body composition, 3:4 ratio. These are reused as delivery-spec constraints in CP4/CP5.
- **ECOM-02 PerfectCorp try-on roundup (8.8).** Vendor-reported conversion lifts for makeup/eyewear AR try-on. It is about business value, not production workflow, so it adds nothing to the reliability question.
- **The `virtual_tryon` agent route** exists in the 8.7 query schema (`QUERY_SCHEMA_PROFILE.md`). That is a routing label only, with no method behind it.
- **Generic ZCOOL / creative-exploration research (8.7, 8.16–8.22)** is about ideation and design systems, and is out of scope here. One lesson carries over: the earlier ZCOOL work found that most posts show *finished results, not process*. The same pattern appeared again here (P11).
- **Earlier access blockers.** The 8.16 work never accessed Xiaohongshu either.

**Not covered anywhere in the repo:**

- try-on / retouching methods
- revision reliability
- garment/identity fidelity checks
- any analysis of Curify's own customer delivery failures

That last gap is the biggest evidence gap. **[INF]** No customer case, failure log, or GPT/Astra pipeline description exists in this repo, so the mapping from methods to Curify's actual failures below is a hypothesis until the cases are tagged (§6).

## 1. Core finding

**[INF, supported by EXT]** The literature and practitioner workflows converge on one point. **Reliable delivery comes from limiting *where* the generator may change pixels, then running deterministic composites and named checks after each generative step.** We infer that a better model, prompt, or more revision rounds will not produce it on their own. That inference is untested on Curify cases.

The evidence:

- **[EXT, verified at source] GPT Image treats masks as soft guidance.** OpenAI's guide: "Masking with GPT Image is entirely prompt-based. The model uses the mask as guidance, but may not follow its exact shape with complete precision."
  - The docs give no hard guarantee that unmasked pixels stay unchanged.
  - `input_fidelity="high"` is recommended for faces and logos, but it is a preservation aid, not a lock (A18).
- **[EXT, verified] Even the best editors drift over many turns.**
  - The FLUX.1 Kontext paper states: "Excessive multi-turn editing can introduce visual artifacts." Its drift advantage over GPT-Image/Gen-4 is vendor-run and shown only in a figure (A17).
  - SPICE keeps unedited regions intact via masks plus edge control. Its 100+-step stability is shown qualitatively; its quantitative evaluation is single-step (A22).
- **[EXT, verified] Specialist try-on models still lose small text/logos and color.**
  - Leffa's paper: "struggles to preserve extremely fine-grained details, such as small text, due to the 8× resolution compression" (A04).
  - CatVTON's paper: VAE decoding causes "detail loss and color discrepancies" (A03).
  - So logo/text fidelity needs a deterministic step, whichever model is used.
- **[EXT, verified] Model choice is not a clear-cut win for specialists.** On OpenVTON-Bench's human ratings, general editors sit near the top:
  - Nano Banana 4.595 and Qwen-Editor 4.545 are close behind the commercial try-on product YingHui (4.608).
  - The older specialist OOTD scores 3.790.
  - The benchmark authors still report a "Texture-Realism Gap": models look photoreal but hallucinate fine garment details (A13).
  - The first draft's snippet-level claim that specialists beat general editors is **downgraded**. It comes from specialists' own papers and is not confirmed by the independent benchmark read here.
- **[EXT, verified] Garment fidelity is measurable per attribute.**
  - DAT scores 7 garment attributes. A prompted Gemini judge is almost as accurate as their trained model (75.9% vs. 76.6% balanced accuracy).
  - Using the scores as an RL reward improved logo preservation most (+0.57 on a 1–5 scale) (A14).
- **[EXT] Practitioner workflows enforce locks deterministically.**
  - Crop-and-Stitch leaves unmasked pixels "not even passing through VAE encode and decode" (P10).
  - The Redux+Fill try-on stitches back only the garment (P01).
  - The PS-AI apparel SOP marks protected zones before generation and ends with a checklist that returns failing images (P05).
  - Retouchers keep work in reversible D&B / frequency-separation layers (P07/P08).
- **[EXT, abstract-level] Production try-on at scale uses dedicated systems.** Tstars-Tryon is deployed in the Taobao app (A07). Oxygen-TryOn trains with fidelity RL (A08). Both report results on their own benchmarks.

**[INF] HYPOTHESIS (unverified until real customer cases are tagged): why Curify/Astra revisions may not converge.**

- We do not know how the current GPT/Astra pipeline handles masks or regions; nothing about it is in the repo.
- If it re-edits the full image per request without locked regions or named acceptance checks, then each fix can disturb approved areas, and vague rejections never become specific fixable items.
- Equally plausible alternatives that the case review must check:
  - the failures are mainly garment-fidelity limits of the generator (F03/F04/F06)
  - the inputs are insufficient (low-res garment photos, no swatch)
  - client expectations are undefined

## 1b. Deep-verified methods (8 most relevant to Curify delivery)

Read at paper or project level, with code and license checked via the GitHub API or HF pages on 2026-10-05. The remaining 19 academic rows stay abstract- or snippet-level.

| Method | Production failure addressed | Verified results | Code / weights / license | Curify use |
|---|---|---|---|---|
| **Leffa** (CVPR 2025) | Garment texture/pattern drift (F03) | VITON-HD paired FID 4.54 vs. CatVTON 5.42 / IDM-VTON 5.76; DressCode FID 2.06 vs. 3.99 / 6.82. The paper itself says small text fails | Code + weights, MIT. Training-dataset terms unchecked | Best open arm for the try-on A/B; pair with logo paste-back |
| **CatVTON** (ICLR 2025) | Cheap try-on baseline | VITON-HD paired SSIM 0.870 / FID 5.43. VAE detail and color loss stated | Weights CC BY-NC-SA 4.0 (**non-commercial**) | Research arm only |
| **FLUX.1 Kontext** (BFL 2025) | Drift across revisions (F01/F07) | KontextBench (1,026 pairs). Multi-turn drift advantage shown in a vendor figure; "excessive multi-turn editing" causes artifacts | [dev] weights non-commercial; [pro]/[max] API | Candidate revision engine, still wrapped in CP1 |
| **InfiniteYou** (2025) | Identity drift of a generated virtual model (F07/F13) | ID loss 0.209 vs. PuLID-FLUX 0.225; 72.8% user preference (n=16) | Code Apache-2.0; weights CC BY-NC 4.0 + FLUX-dev (**non-commercial**) | Only for generated models; for client photos, paste the face back |
| **SPICE** (NeurIPS Creative AI 2025) | Quality decay over many local edits (F01/F02) | Unedited regions kept intact; 100+ steps shown qualitatively; single-step EditEval CLIPdir 0.221 vs. 0.193–0.210 | Repo MIT (paper says CC BY 4.0); uses FLUX-dev | Design validation for CP1 |
| **CatV2TON** (CVPRW 2025) | Video try-on flicker and color drift between clips (F16) | ViViD-S VFID-I3D 13.60 vs. ViViD 17.29; authors say 832×624 clarity is below application needs | Repo has no license file | Defer video |
| **OpenVTON-Bench** (2026) | No objective QA (F14) | 5 dims; region-eroded metric τ=0.833 vs. SSIM 0.611; general editors rank near the top | Repo + ~100K pairs; research-only | Template for Curify QA dimensions |
| **DAT** (2026) | Per-attribute garment QA (F03–F06, F14) | 76.6% balanced accuracy vs. Gemini-3.1 75.9%; RL logo +0.57 | No release found | Use the 7 dims as the checklist; a prompted VLM judge is a near-equal substitute |

## 2. Failure → solution → workflow → Curify applicability

The highest-priority rows are below; the full set is in `failure_solution_matrix.csv`.

| Failure | Academic solution | Practitioner workflow | Deterministic safeguard | Still manual | Curify applicability [INF] |
|---|---|---|---|---|---|
| **F01** A revision changes things outside the requested region | Kontext lower drift (A17); SPICE masking (A22) | Crop-and-Stitch (P10); Redux+Fill + stitch (P01) | Copy every outside-mask pixel bit-exact from the last accepted version | Naming/drawing the region | **CP1**. Model-agnostic wrapper; highest expected impact on revision success |
| **F02** Quality decays over revision rounds | SPICE (A22); PixPerfect seam/color refiner (A21) | Never round-trip unmasked pixels through the VAE (P10) | Always revise from the master; composite | — | **CP1** |
| **F04** Logo/text corrupted | No verified model solves small text (Leffa and CatVTON papers both state detail loss, A03/A04); DAT logo dimension measures it and RL improves it (A14); RefAdGen (A24, abstract-level) | Redux+Fill: text "not fully applied at the first attempt" (P01); IC-Light + DetailTransfer (P09) | OCR + crop comparison; deterministic logo-patch paste-back | Warping the logo over deep folds | **CP2/CP4**. Brand clients notice this first |
| **F06** Garment/product color ≠ real item | Tone shifts documented for Leffa (darker) and FitDiT (brighter) | PS color-correction step (P05) | ΔE against the client swatch; auto color-match within the mask | Swatch capture | **CP2**. FASHN warns mismatches cause returns (P06) |
| **F07** Model's face changes across revisions or SKUs | InstantID / PuLID / InfiniteYou (A19) | Keep the real model photo; edit only the garment (P01) | Paste the face from the source; ID-similarity check | Choosing the model | **CP1/CP2** |
| **F11** "Plastic" skin | Frequency-aware retouching (A25) | 中性灰 / 双曲线 / 高低频 (P08); Retouch4me/Evoto D&B layers (P07) | Retouch as adjustment layers | Taste | **CP3** |
| **F12** Retouch can't be dialed ("a bit less") | MonetGPT / JarvisArt / RetouchIQ: an MLLM emits tool parameters (A26) | Plugin layers with opacity (P07) | Revision = parameter change, deterministic re-render | Final sign-off | **CP3** |
| **F14** No objective acceptance criteria | OpenVTON-Bench 5 dimensions, VLM + segmentation metric with τ=0.833 vs 0.611 for SSIM (A13); DAT 7 garment dimensions (A14) | PS-AI compliance checklist (P05) | Per-order checklist + automated pre-checks | Client sign-off | **CP5**. Turns vague rejections into named failed checks |
| **F03/F05** Print or structure drift | Leffa (A04); FitDiT (A05); FitVTON size control (A09) | Protected zones + checklist (P05) | Aligned-crop LPIPS; mask-shape comparison | Fit judgment | **CP2** model A/B |
| **F09** Multi-item outfits/layering | Garments2Look: SOTA and general editors still fail (A12) | Qwen-Edit multi-garment panel (P03) | One item per locked pass | Layering decisions | Set expectations; price as a hard tier |
| **F16** Video try-on flicker | CatV2TON, MagicTryOn, etc. (A15/A16) | None accessible | — | — | Defer |

## 3. Academic / SOTA landscape (summary)

Details are in `academic_methods.csv`.

**Image try-on, roughly by generation:**

- **Generation 1 (2024, SD-era):** IDM-VTON and OOTDiffusion, which need a mask and pose. Superseded.
- **Generation 2 (2025):** CatVTON (lightweight concatenation, ICLR 2025), Leffa (CVPR 2025, targets fine-texture distortion; its own limitations section says small text still fails), and FitDiT (DiT, frequency texture).
  - [EXT] A comparison paper notes Leffa runs darker and FitDiT runs brighter in tone. Color fidelity remains unsolved even for specialists.
- **Generation 3 (2025–26):**
  - Mask-free and any-item models: OmniTry, MFP-VTON, TAMF-VTON.
  - Kontext-based models: RefTon, FitVTON.
  - Industrial multi-reference systems with data engines and RL: Tstars-Tryon (deployed on Taobao), Oxygen-TryOn (claims parity with Nano Banana Pro / GPT-Image-2).

**Evaluation (the most useful part for Curify):**

- OpenVTON-Bench (5 region-aware dimensions; better human agreement than SSIM)
- DAT (7 garment attributes, also used as RL rewards)
- Garments2Look (outfit level; shows the open problems)

**Local editing:**

- BrushNet / FLUX Fill. FLUX Fill has documented color drift outside the mask.
- PixPerfect: pixel-space cleanup of seams and color shift.
- SPICE: iterative workflow.
- Kontext: low multi-turn drift.

**Identity:** InstantID, PuLID, InfiniteYou. Trade-off: stronger ID means weaker prompt following.

**Relighting / product:**

- IC-Light (ICLR 2025 oral; changes only illumination by construction).
- Product-fidelity recontextualization (Amazon), RefAdGen, DreamPainter.

**Retouching:**

- Paired-data models: FFHQR / RetouchFormer / ICCV'25 spectral restorement.
- **Parametric agents**: MonetGPT, JarvisArt (200+ Lightroom tools), RetouchIQ. **[INF]** The agents matter more for revision reliability than the pixel models do.

**Video try-on:** CatV2TON, MagicTryOn, RealVVT, SwiftTry, DPIDM, FlowVVTON. Still research-grade.

## 4. Practitioner landscape (summary)

Details are in `practitioner_workflows.csv`.

- **Western open-source / ComfyUI:**
  - Redux+Fill with crop-and-stitch (P01). The 9elements post is the best-documented, including its failures: patterns, text, and body type.
  - CatVTON and IDM-VTON nodes (P02).
  - Qwen-Image-Edit and Kontext try-on LoRAs (P03/P04).
  - Crop-and-Stitch as the universal local-edit wrapper (P10).
  - IC-Light + `DetailTransfer`, a deterministic frequency blend that restores detail after relight. Code verified (P09).
- **Hosted specialists:** FASHN (P06). It publishes its limits: 864×1296 native, can alter body proportions or drop details, and tells users to "compare each image with the real product before publishing".
- **Chinese practitioner content:**
  - The PS AI Plugin 5-step SOP (P05) is the clearest *production* workflow found: risk-classify sources and mark protected zones, then run 2–4 AI variants in PS layers, a 10–20 pilot before 50+ SKUs, PS finalization (edges/color/texture), and a checklist that returns failures.
  - ZCOOL article P11 (accessible) is a logo-overlay mockup flow, not a fidelity workflow.
  - CN ComfyUI tutorials (Bilibili/CSDN/Zhihu, P12) converge on the same Redux+Fill and Qwen-Edit 换装 patterns. They were only partially readable.
- **Retouching craft:** 中性灰 / 双曲线 (D&B) / 高低频 (P08) and AI plugins that output those same layers (Retouch4me, Evoto; P07). The industry norm is "AI does the boring 80%, the retoucher finishes 20%", and edits stay layered and reversible.

## 5. Evidence quality and blockers

- **Xiaohongshu: BLOCKED.** The search page returns a UI shell with no notes unless logged in; a `site:` search returned nothing relevant. Nothing from Xiaohongshu is used in this report. A team member with an account must browse it manually.
- **Zhihu: BLOCKED (HTTP 403).** One CSDN page returned HTTP 521. Bilibili tutorials are video and can't be read. These sources are used only as search-snippet corroboration (P08, P12), labeled as such.
- **ZCOOL:** Accessible. Only one relevant workflow article was found (P11), and it shows outcomes rather than process, the same pattern found in 8.7.
- **Read depth:**
  - **8 methods were verified at paper level** (§1b). The other 19 academic rows remain abstract- or snippet-level.
  - The snippet-level claim that general editors fail on try-on (Seedream/Qwen/Nano Banana/GPT-Image-1.5) was **not confirmed** by the independent OpenVTON-Bench ranking, where general editors rank near the top. It is downgraded to "reported by specialist papers only".
  - Vendor claims (Oxygen-TryOn parity, Retouch4me/Evoto quality, FASHN) are self-reported.
- **No Curify case data.** The customer cases, revision histories, and the GPT/Astra pipeline are not in this repo, and "Astra" is not described anywhere I could find. Every applicability claim in §2 is therefore **[INF]**.

## 6. Proposed next experiment (concrete, small)

**"Locked revision replay" on real failed cases.** Tests whether CP1+CP5 fix the reported symptom before anyone builds a model pipeline.

1. Collect 10–15 real delivered-but-rejected cases: about half try-on, half retouching, each with its revision history and the client's feedback.
2. **Tag every rejection** against `failure_solution_matrix.csv` (F01–F15). This alone answers "which failures dominate". It costs about half a day with no generation.
3. Replay the 2–3 most demanding revision requests per case in two arms, using the same underlying generator (GPT/Astra):
   - **A:** the current loop (whole-image re-edit).
   - **B:** CP1 (crop → generate → stitch-back) plus CP5 automated pre-checks (outside-mask diff, ΔE against the reference color, logo OCR, face ID similarity).
4. **Metrics:**
   - unrequested-change rate (pixel diff outside the requested region)
   - per-dimension checklist pass rate
   - rounds needed to reach internal acceptance, judged blind by a reviewer
   - time per round
5. **Decision rule:**
   - If B cuts unrequested changes and rounds, build CP1/CP5 into delivery now.
   - If the remaining failures are mostly F03/F04/F06 (garment fidelity), run the CP2 generator A/B next: FASHN vs. Leffa/CatVTON vs. Kontext/Qwen try-on LoRA vs. GPT.

**Blocker:** this needs the customer cases and permission to use them internally.
