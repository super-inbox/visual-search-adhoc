# Image Access Validation

Small-scale technical validation of zcool image access, scoped to the 3 cases already migrated into `baseline_pilot/structured_cases/raw_cases/` (`case_001`, `case_002`, `case_003`). No new cases were searched or scraped; no login, captcha bypass, or access-control evasion was used.

See `IMAGE_ACCESS_VALIDATION_REPORT.md` for the full write-up, findings, and status recommendation.

## Contents

```text
image_access_validation/
├── README.md                          this file
├── test_cases.csv                     per-case summary across all 3 test methods
├── browser_logs/                      Playwright network response logs (image + document only), one JSONL per case
├── screenshots/                       full-page Playwright screenshots (internal research use only)
├── extracted_image_urls/              per-case candidate real-image URLs + direct-access HEAD check result
└── IMAGE_ACCESS_VALIDATION_REPORT.md  full report and status recommendation
```

## Method summary

- **Method A — plain HTML fetch** (`curl`, no JS execution): confirmed each case's real content images are exposed via the `<img class="lazyload photoImage" data-src="...">` attribute, not the `src` attribute (which holds a site-wide placeholder, `bg-placeholder.jpg`). This is the likely root cause of the 8.5 pilot's `source_quality: text_ok_images_blocked` conclusion — that pilot's asset manifest only recorded `src`, never `data-src`.
- **Method B — real browser rendering** (Playwright/Chromium, headless, already present as a project dependency in `scripts/external-screenshot-p0-12/` and `scripts/curify-search-collect/`; installed only into this session's scratchpad, not into the repo): all 3 pages rendered successfully, scrolled to trigger lazyload, and produced non-blank full-page screenshots.
- **Method C — browser network log**: recorded every `image`/`document` response Playwright observed during load + scroll for each case.
- **Direct image access check**: HTTP `HEAD` request (no body download) against every `data-src` URL found for each case — 84/84 (17 + 27 + 40) returned `200 OK` with `image/jpeg` or similar content-type, with no authentication, cookies, or session state.

## Scope notes

- Screenshots and extracted URLs are for internal workflow-evidence research only, not for publication or redistribution.
- No bulk image bytes were downloaded; only HTTP headers were checked via `HEAD` requests.
- No cookies, `Authorization` headers, or session tokens were logged.
