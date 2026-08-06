# Query Schema Profile (AUTHORITATIVE)

## Source of truth

| Field | Value |
|---|---|
| Repository | `super-inbox/curify-studio` (verified via `git remote -v` in local `curify-studio` clone) |
| Ref | `origin/main` |
| Commit | `c74d990903d193a4c78814759bd117bfa98f4817` |
| File path | `dev/jayw/design-agent-v0/eval/queries.jsonl` |
| SHA-256 | `5384474f8334f352f6ce157331b7d96c68721179f5da2049fcdc8c8e0ffe2e3d` |
| Line count | 118 |
| Retrieval method | `git cat-file -e origin/main:...` (existence check) then `git show origin/main:...` (read-only, no checkout, no branch switch) |

This profile was built **only** from the content retrieved via `git show origin/main:dev/jayw/design-agent-v0/eval/queries.jsonl` inside the `curify-studio` clone. No other copy was used to derive the structure described below.

Cross-check: a local worktree at `/Users/baobaoli/Desktop/curify-studio-brand-direction-explorer` (itself a `git worktree` of the same `curify-studio` repository, checked out in detached HEAD at commit `c74d990`, i.e. exactly `origin/main`) contains a byte-identical copy of the same file (same SHA-256, same 118 lines, `diff` reports no differences). See `SCHEMA_MAPPING.md` and the audit's `SCHEMA_COMPARISON` output for the full comparison record.

---

## Structure

The file mixes **two distinct record shapes** under one `layer` field — this is not one schema, it is two.

| `layer` value | count | `id` prefix |
|---|---|---|
| `routing_benchmark` | 100 | `TIQ-xxx` |
| `agent_route` | 18 | `AR-xxx` |

### Fields common to all 118 records
`id` (str), `query` (str), `language` (str), `layer` (str), `has_reference` (bool)

### `routing_benchmark` layer — fields present in all 100 records
`theme` (str), `tool_intent` (str), `specificity` (str), `reference_image` (str), `expected_route_intents` (list[str]), `coverage` (str), `candidate_templates` (list[str]), `source_refs` (list[str])

### `agent_route` layer — fields present in all 18 records
`expected_route` (str), `note` (str)

---

## Value distributions

- `theme`: 品牌 34 / 文创 33 / 电商设计 33
- `tool_intent`: 100 records, almost entirely distinct values — functions as a per-record topic label, **not** a closed enum
- `specificity`: specific 47 / medium 46 / broad 7
- `reference_image`: none 55 / optional 36 / required 9
- `coverage`: adjacent 42 / direct 35 / gap 23
- `expected_route_intents` (closed enum, list length 1–3): `ecommerce`, `merch`, `lifestyle`, `education` — only these 4 values appear
- `candidate_templates`: template-slug strings, list length 0–2, 23 records have an empty list
- `source_refs` (enum-like provenance tags, list length 1–3): `CURIFY_TEMPLATE_CATALOG` (73), plus `ZCOOL_BRAND_UPGRADE` (13), `ZCOOL_ECOM_BRANDING` (14), `ZCOOL_PACKAGING` (7), `ZCOOL_NEW_CULTURAL` (24), `ZCOOL_MODERN_BRAND` (3), `ZCOOL_GLOBAL_BRAND` (1), `ZCOOL_COCREATE_ECOM` (1), and `LIBLIB_NATIONAL_TREND` (9), `LIBLIB_PRODUCT_RETOUCH` (12), `LIBLIB_3D_IP` (8), `LIBLIB_CULTURAL_IP` (5), `LIBLIB_ECOM_DETAIL` (18), `LIBLIB_ECOM_POSTER` (3)
- `expected_route` (closed enum, `agent_route` layer, 3 records each): `image_edit_variants`, `design_vote`, `virtual_tryon`, `factory_export`, `creative_explore`, `ask`
- `language`: `zh-CN` 97 / `mixed` 12 / `en` 9

No tokens, API keys, or secrets were found anywhere in this file — every field is either a short natural-language query or an enum-style tag.

---

## Representative records

**`routing_benchmark`, broad/gap, empty candidate_templates:**
```json
{"id":"TIQ-001","query":"品牌设计","language":"zh-CN","theme":"品牌","tool_intent":"开放式品牌设计","specificity":"broad","reference_image":"none","expected_route_intents":["ecommerce","merch"],"coverage":"gap","candidate_templates":[],"source_refs":["CURIFY_TEMPLATE_CATALOG","ZCOOL_BRAND_UPGRADE"],"layer":"routing_benchmark","has_reference":false}
```

**`routing_benchmark`, medium/adjacent, `ZCOOL_NEW_CULTURAL` tag:**
```json
{"id":"TIQ-017","query":"城市文旅品牌logo和辅助图形","theme":"品牌","tool_intent":"城市品牌视觉","specificity":"medium","coverage":"adjacent","candidate_templates":["template-national-theme-map-infographic","template-country-souvenirs-watercolor"],"source_refs":["CURIFY_TEMPLATE_CATALOG","ZCOOL_NEW_CULTURAL"],"layer":"routing_benchmark","has_reference":false}
```

**`routing_benchmark`, e-commerce theme, three source_refs:**
```json
{"id":"TIQ-068","query":"电商设计","theme":"电商设计","tool_intent":"开放式电商设计","specificity":"broad","reference_image":"optional","expected_route_intents":["ecommerce"],"coverage":"adjacent","candidate_templates":["template-product-theme-promotional-poster","template-fashion-ecommerce"],"source_refs":["CURIFY_TEMPLATE_CATALOG","ZCOOL_ECOM_BRANDING","LIBLIB_ECOM_DETAIL"],"layer":"routing_benchmark","has_reference":true}
```

**`agent_route`, image-edit instruction:**
```json
{"id":"AR-001","query":"把海报的标题放大一点","has_reference":true,"expected_route":"image_edit_variants","note":"reference image + edit instruction","layer":"agent_route"}
```

**`agent_route`, candidate comparison / vote:**
```json
{"id":"AR-004","query":"这4款包装，站在消费者角度哪款更有质感？","has_reference":true,"expected_route":"design_vote","note":"candidate comparison / vote","layer":"agent_route"}
```
