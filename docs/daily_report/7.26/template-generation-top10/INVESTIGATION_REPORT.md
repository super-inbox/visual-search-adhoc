# Investigation Report — Curify Top 10 Template Generation (Phase 1)

Date: 2026-07-26
Scope: read-only investigation only. No writes outside this new output directory occurred during Phase 1.

## 1. Discovery source of truth

Searched `docs/daily_report/7.22`, `7.23` (no `7.24`/`7.25` directories exist yet as of 2026-07-26). Found two
candidate discovery packages under `docs/daily_report/7.23/`:

- `template-discovery-top10-2026-07-23/` — original v1 package.
- `template-discovery-top10-2026-07-23-v2/` — a manager-requested correction pass over v1 (targeted fixes to
  ranking order, score-label disambiguation, and honest visual-evidence labeling). **This is the final, most
  authoritative version.** Its `00_REVISION_CONTEXT.md` explicitly documents what changed and why, and the v1
  package is preserved unmodified as `working_input_v1/` inside the v2 folder for audit purposes.

Verified (not just by filename/date) by reading `00_REVISION_CONTEXT.md`, `MANIFEST.json` (87 files,
SHA256-verified), `13_MANAGER_REVIEW_SUMMARY.md`, and the full `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`. The v2
package cites its own upstream inputs as read-only: the Task A 326-query benchmark from
`docs/daily_report/7.22/cluster-ab-latest-fix-full326-2026-07-22/` (not re-run) and a tested frontend commit
`0e794cd91396a96cd56fd1d8f7f1495909f3adc5`.

**Decision: use `docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/` as the sole source of truth.**
No template discovery was re-run; no candidate was invented or substituted.

## 2. Final 10 templates (ranked, from `13_MANAGER_REVIEW_SUMMARY.md` + `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv`)

| Rank | ID | Name | Priority | Status | Evidence-Adj. Score |
|---|---|---|---|---|---|
| 1 | T03 | Workbook & Practice-Book Cover Collection | P0 | CONFIRMED | 86.0 |
| 2 | T04 | Flyer & Promotional-Flyer Templates | P0 | CONFIRMED | 85.0 |
| 3 | T02 | STEM Classroom Teaching-Aid Illustrations | P0 | CONFIRMED | 66.4 |
| 4 | T05 | Price Tag & Product Label Templates | P1 | CONFIRMED | 62.2 |
| 5 | T01 | Certificates & Achievement Awards Collection | P1 | CONFIRMED | 50.2 |
| 6 | T07 | Perfume & Cosmetic Bottle Packaging Mockups | P1 | PROVISIONAL | 71.0 |
| 7 | T06 | Chocolate & Specialty Gift-Box Packaging | P1 | PROVISIONAL | 43.5 |
| 8 | T08 | Puzzle & Jigsaw Collectible Templates | P2 | PROVISIONAL | 29.5 |
| 9 | T09 | Discount Coupon & Promotional Voucher Templates | P2 | PROVISIONAL | 20.1 |
| 10 | T10 | Fridge Magnet & Small Merch-Item Templates | P2 | PROVISIONAL | 16.8 |

Full fields (target user, use case, content gap, benchmark queries, competitor evidence, visual direction, variants)
extracted directly from `10_TOP10_TEMPLATE_RECOMMENDATIONS.csv` — carried into each `template.json` in Phase 3.
Six of ten (T01, T02, T05, T08, T09, T10) have **no exact-match competitor reference image on file** — the v2
package is explicit and honest about this ("REFERENCE IMAGE NEEDED"); we preserve that honesty rather than
fabricating references.

## 3. Curify repos surveyed

- `/Users/baobaoli/Desktop/curify-frontend` — the live product frontend (Next.js). Contains the actual template
  and generation system referenced by the discovery screenshots (`V042_magnet.png` etc. are frontend
  screenshots of `curify-frontend`'s live search/catalog UI).
- `/Users/baobaoli/Desktop/curify-studio` — a separate, broader company monorepo (GTM tooling, dubbing/ASL
  services, admin portal, background job workers). Not the template/design generation product; only
  `curify_background` hosts the **production** DB-backed generation route, used for cross-reference only.
- Several `curify-frontend-*` snapshot/baseline directories on Desktop — confirmed to be point-in-time copies
  used for prior evaluation work, not a distinct implementation. Not used.

### Template data model
- `curify-frontend/public/data/nano_templates.json` — 308 templates. Each has `id`, per-locale (`zh`/`en`)
  `base_prompt` with `{param}` placeholders, and a `parameters[]` array (name/label/type/placeholder).
- `curify-frontend/public/data/nano_inspiration.json` — 3209 generated "example" records, each with `id`,
  `template_id` (FK), `asset.{image_url,preview_image_url}`, `params`, `locales.*.title`, `tags`. This is the
  existing example/generation-result schema, used as the structural reference for our own `example` records.

### Generation pipeline (three real paths found)
1. **Demo API routes** (`app/api/progseo-demo/generate/route.ts`, `app/api/illustrator-demo/generate/route.ts`):
   POST `{template_id, params, slug}` → fills `{param}` into a template's `base_prompt` → calls
   `@google/genai` (`gemini-3-pro-image-preview`) → writes to `/tmp`. Explicitly commented "Not metered. Not
   authed. Demo-only." No DB write. **Constraint: looks up `template_id` in the existing 308-entry
   `nano_templates.json`, so it cannot be used unmodified for our 10 new candidate templates without editing
   that production file — which we will not do.**
2. **Production route** (`curify-studio/curify_background/app/routers/nano_templates.py`,
   `generate_nano_template`): requires `Depends(get_current_user)` (login/session), does a credit check, and
   writes a project row to Postgres. **Not used** — writes to production DB.
3. **CLI batch script** (`curify-frontend/scripts/generate_template_examples.cjs`): `node
   scripts/generate_template_examples.cjs --config=... [--dry-run] [--sync] [--pack=...]`. Same Gemini call
   pattern; on success copies into `curify-frontend/public/images/nano_insp/` and appends to
   `nano_inspiration.json` (product repo files, git-tracked). `--sync` additionally runs `gsutil rsync` to the
   production CDN bucket `gs://curify-static`. **Not used directly** — even without `--sync`, it writes into
   the product repo's own tracked files, which the task instructions prohibit modifying.

### Chosen approach
Write a **standalone** Node script inside our own output directory
(`template-generation-top10/scripts/generate_examples.mjs`) that:
- Reuses the same `@google/genai` SDK already installed in `curify-frontend/node_modules` (via `NODE_PATH`,
  read-only) and reads `GEMINI_API_KEY` from `curify-frontend/.env.local` (read-only env borrow — the key value
  is never written to disk by us, never logged, never committed).
- Uses the identical `{param}` prompt-fill pattern and the same model (`gemini-3-pro-image-preview`).
- Writes **only** into `template-generation-top10/templates/**` — never into any file inside `curify-frontend`
  or `curify-studio`.
- Never calls `gsutil`/CDN sync, never touches Postgres, never creates a DB row, never requires a login session.

**Smoke-tested and confirmed working**: a direct call to `gemini-3-pro-image-preview` via this exact pattern
(env from `curify-frontend/.env.local`, SDK from `curify-frontend/node_modules`) returned a valid, decodable PNG
in the scratchpad during Phase 1 investigation. Both `GEMINI_API_KEY` and `OPENAI_API_KEY` are present and
non-empty in `.env.local`.

## 4. Answers to the required Phase 1 questions

- **Can generation be invoked directly from the command line?** Yes — confirmed working via a standalone script
  using the `@google/genai` SDK and `GEMINI_API_KEY`, independent of any product route.
- **Requires login session?** No — the safe path used here needs no auth/session.
- **Requires an API key?** Yes, `GEMINI_API_KEY` — already present in `curify-frontend/.env.local` and verified
  working.
- **Depends on browser operation?** No.
- **Would it write to production database?** No — our script never touches Postgres, never calls the
  `nano_templates.py` production route, and never modifies `curify-frontend`'s own tracked files
  (`nano_templates.json`, `nano_inspiration.json`, `public/images/`).
- **Safe local/dev/test generation path exists?** Yes — described above; fully isolated to our own output
  directory.
- **Can generated images be auto-downloaded/saved locally?** Yes — the Gemini response returns inline base64
  image bytes directly; the script writes them straight to local disk, no separate download step needed.
- **Highest level of automation currently achievable?** Full: template spec authoring, prompt construction,
  batch image generation, structural QA, and gallery/report generation can all run non-interactively from the
  command line.

## Terminal summary

```
DISCOVERY_SOURCE: docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/
TEMPLATE_COUNT: 10
GENERATION_PIPELINE_FOUND: YES
SAFE_TO_AUTOMATE: YES
BLOCKERS: None blocking. Note (non-blocking): 6/10 templates (T01,T02,T05,T08,T09,T10) have no exact-match
  competitor reference image on file in the discovery package itself — this is a known, honestly-documented gap
  in the source data, not a generation-pipeline blocker.
RECOMMENDED_EXECUTION_MODE: Standalone CLI script reusing curify-frontend's @google/genai SDK + GEMINI_API_KEY
  (read-only borrow, no product-repo writes), writing exclusively into this output directory. No DB writes, no
  CDN sync, no auth/session required.
```
