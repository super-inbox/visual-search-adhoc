# Candidate Curify pipelines: visual production

Date: 2026-10-05. All pipelines below are **[INF] proposals**, built from the evidence in `academic_methods.csv` (A##) and `practitioner_workflows.csv` (P##). None has been built or tested on Curify customer cases. The failure IDs (F##) refer to `failure_solution_matrix.csv`.

**Design principle (the main finding of this research):** professional production gets reliability by restricting *where* the generator is allowed to change pixels. Each generative step's output then passes through deterministic composites and checks. Revision reliability comes from that structure, not from a better prompt or more rounds with a stronger model.

- Evidence:
  - P01: Redux+Fill with stitch-back.
  - P05: protected zones, PS finalization, and a checklist.
  - P07/P08: retouching done as non-destructive layers.
  - P09: deterministic detail transfer after relight.
  - P10: unmasked pixels never pass through the VAE.
  - A22: SPICE, an iterative-editing workflow.

---

## CP1 — Locked-pixel revision loop (model-agnostic; wraps GPT, Astra, Kontext, or any model)

**Fixes:** F01 (drift outside the region), F02 (cumulative degradation), F07 (face drift), F15 (resolution).

```
accepted master vN  ──►  revision request ("fix the collar")
        │                         │
        │                 [manual/semi-auto] region mask  (SAM click or named region → segmentation)
        │                         │
        │             [deterministic] crop region + context, upscale to model res
        │                         │
        │             [generative]   any editor (GPT Image / Kontext / Qwen-Edit / Fill)
        │                         │
        │             [deterministic] stitch back ONLY the masked region into vN
        │                         │      (outside-mask pixels copied bit-exact from vN)
        │             [deterministic] seam blend; optional PixPerfect-style refiner (A21)
        │                         │
        │             [deterministic] checks: outside-mask diff = 0 by construction;
        │                             region-level checks from CP5
        ▼                         ▼
                 human review of the region only → vN+1 (new master)
```

- **Generative:** one region edit per request.
- **Deterministic:** crop, stitch, blend, checks.
- **Manual:** confirming the region; final acceptance.
- **Why it should help (hypothesis):** GPT Image's own docs say a mask is "guidance" and "may not follow its exact shape" (A18). Every revision therefore risks changing approved areas. CP1 makes approved areas immutable.
- **Cost:** a wrapper around existing generators. No new model.

## CP2 — Ecommerce model dressing / try-on with fidelity gates

**Fixes:** F03–F09, F13.

1. **Intake.** The client supplies a high-res flat-lay or ghost-mannequin garment image and a color swatch photo.
   - **[manual]** Mark protected zones (logo, print, buttons, neckline), as in P05 step 1.
   - If only an on-model photo exists, use try-off (A27) to recover the garment. Flag it as lower confidence.
2. **Model base.** Use the client's model photo, or a fixed Curify virtual model kept consistent by an ID adapter (A19) and a locked seed/preset per batch (F13).
3. **[generative] Try-on pass.** Pick the generator by A/B on Curify cases, not from the literature. Evidence is mixed:
   - OpenVTON-Bench human ratings put general editors (Nano Banana, Qwen-Editor) near the top (A13).
   - Specialist papers report the opposite on their own benchmarks.

   Candidate arms:
   - the current GPT/Astra pipeline
   - Kontext or Qwen-Edit with a try-on LoRA (P03/P04)
   - FASHN API (P06, hosted, commercial)
   - Leffa (A04, MIT code + weights)

   CatVTON and InfiniteYou weights are non-commercial, so research only. **No verified model reliably preserves small text/logos** (A03/A04 limitations), which is why steps 5–6 exist regardless of the arm chosen.
4. **[deterministic] Locks.**
   - Paste the face and background from the source model photo.
   - Use one garment per pass for outfits (F09).
5. **[deterministic] Fidelity checks**, one per DAT dimension (A14):
   - **color:** ΔE between the garment region and the swatch
   - **logo/text:** OCR plus crop similarity
   - **print/texture:** aligned crop LPIPS
   - **silhouette/length:** mask-shape comparison
6. **[deterministic] Repair on failure.**
   - Color: color-match within the garment mask.
   - Logo: warp the original logo patch onto the output, then blend. **[manual]** Strong folds still need a retoucher.
   - Everything else: send a targeted re-generation of only the failing region through CP1.
7. **[manual] Final checklist and client sign-off** (CP5).

## CP3 — Professional retouching as parameters, not pixels

**Fixes:** F11 (plastic skin), F12 (revisions that can't be dialed), F01.

1. **[deterministic]** Base corrections: exposure, white balance, lens.
2. **AI-predicted adjustment layers.** Dodge & burn (双曲线/中性灰) and frequency-separation layers come from a plugin-style model (P07) or a parametric agent that emits tool parameters (A26: JarvisArt with Lightroom tools, MonetGPT with slider values). Output is a **layer stack plus a parameter file**, not a flattened image.
3. **[generative, local only]** Blemish, stray-hair, and object removal through CP1 (crop-inpaint-stitch).
4. **Revision handling.** A revision is a parameter change ("less smoothing" → lower the opacity or frequency-blend factor), re-rendered deterministically. No new sampling unless a region needs new content.
5. **[manual]** Final 20%: hair, eyes, brand grading (the practitioner norm, P07/P08).

**Why it should help (hypothesis):** Practitioners keep retouching in reversible layers precisely so clients can say "a bit less" (P07/P08). One-shot generative retouching removes that ability.

## CP4 — Product-in-scene (non-apparel ecommerce, campaign shots)

**Fixes:** F04, F10.

1. **[deterministic]** Cut out the product with BiRefNet (P14; commercial-usable).
2. **[generative]** Generate the background/scene.
3. **[generative]** Relight with IC-Light (A23).
4. **[deterministic]** Run `DetailTransfer` (P09; a frequency blend with `blur_sigma`, verified in `kijai/ComfyUI-IC-Light/nodes.py`). Then paste back the label/logo region from the original.
5. **[deterministic]** Check the label with OCR; the composition rules from prior Curify research apply (≥60% product body, 3:4, white-background variant; 8.8 `ecommerce_001`).

## CP5 — Acceptance contract + pre-delivery QC (wraps CP1–CP4)

**Fixes:** F14, which is the root of "repeated revisions still don't pass".

- **Before generation:**
  - Agree a per-order checklist with the client, built from the DAT 7 dimensions (A14) and OpenVTON-Bench's 5 dimensions (A13): garment color / print / logo / structure / identity / background / realism.
  - Record the client's reference assets (swatch, logo file, model photo).
- **Before every delivery:**
  - Run the automated pre-checks from CP1/CP2.
  - A human fills the checklist.
- **On every revision request:** Map the client's feedback to a named checklist item and region. This feeds CP1 directly.
- **Prior Curify precedent:** the repo already uses explicit versioned rubrics (8.19 inspiration rubric). This applies the same discipline to delivery.

---

## Recommended order [INF]

1. **CP5 + CP1 first.** They are model-agnostic, cheap, and target the reported symptom (revisions that don't converge).
2. **CP2 generator A/B** (current GPT/Astra vs. Kontext/Qwen try-on LoRA vs. FASHN vs. Leffa) on real failed cases.
3. **CP3** if retouching orders are a significant share.
4. **CP4** after that.

## Open questions for the team

- What is "Astra" exactly? It is not described anywhere in this repo, and it may or may not support hard masks. It should be classified like A18.
- Which licenses can we use commercially? Several open try-on models are released non-commercial; FLUX dev weights have their own license.
- Do customers supply flat-lays, swatches, and logo files? CP2's checks depend on them.
