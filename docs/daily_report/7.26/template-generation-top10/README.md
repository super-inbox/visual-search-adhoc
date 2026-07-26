# Curify Top 10 Template Generation (2026-07-26)

Manager ask: "基于 template discovery 结果生成这 10 个 template，每个 template 生成 3–4 个 example，我们看一下。"

**Start here:** open `gallery.html` directly in a browser (offline, no server needed) for a visual overview, or
read `TEMPLATE_GENERATION_SUMMARY_ZH.md` for the narrative summary.

## What this is

10 templates, sourced verbatim from the final (v2, manager-corrected) template discovery package at
`docs/daily_report/7.23/template-discovery-top10-2026-07-23-v2/`, each with 4 fully-specified examples (40 total),
all 40 successfully generated via `gemini-3-pro-image-preview`.

## Contents

| File/dir | What it is |
|---|---|
| `gallery.html` | Offline visual gallery of all 10 templates x 40 examples, with stats, thumbnails, and links to spec/prompt/input |
| `TEMPLATE_GENERATION_SUMMARY_ZH.md` | Chinese-language narrative summary answering the manager's review questions |
| `INVESTIGATION_REPORT.md` | Phase 1 read-only investigation: discovery source verification + generation-pipeline safety analysis |
| `PILOT_REVIEW.md` | Manual visual QA of the first 10 pilot generations (one per template) |
| `QUALITY_REVIEW.md` | Automated structural QA across all 40 generated images |
| `template_manifest.json` | Machine-readable spec for all 10 templates |
| `example_manifest.json` | Machine-readable index of all 40 examples with status |
| `generation_log.jsonl` | Append-only log of every generation attempt (no secrets) |
| `MANIFEST.json` | Full file inventory with size + SHA-256 for every deliverable file |
| `RUN_LOG.md` | Chronological log of the commands executed to produce this package |
| `scripts/generate_examples.mjs` | Standalone Gemini-based batch generator (dry-run/pilot/resume/retry support) |
| `scripts/validate_outputs.py` | Automated QA script (dimensions, decodability, blank-image / duplicate detection) |
| `scripts/build_gallery.py` | Builds `gallery.html` from the manifests |
| `templates/template-NN-<slug>/` | Per-template: `TEMPLATE_SPEC.md`, `template.json`, and `example-01..04/` (each with `input.json`, `prompt.txt`, `metadata.json`, `output.png`) |

## What this is NOT

- Not a re-run of template discovery — the 10 templates and their priority/status are taken as-is from the v2
  discovery package.
- No production files were modified. No database rows were created. No CDN sync occurred. No git commit/push was
  made from this task.
- The `@google/genai` SDK and `GEMINI_API_KEY` were read-only borrowed from `curify-frontend` (see
  `INVESTIGATION_REPORT.md` for the safety analysis); no file inside `curify-frontend` or `curify-studio` was
  written to.

## Result

40 / 40 examples generated successfully. See `QUALITY_REVIEW.md` for automated QA and `PILOT_REVIEW.md` for
manual visual QA of the pilot batch. Full detail in `TEMPLATE_GENERATION_SUMMARY_ZH.md`.
