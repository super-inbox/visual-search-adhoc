# batch_010 report

Queries: 20

Label distribution: {'PASS': 7, 'PARTIAL': 6, 'FAIL': 7}

- **E182** `海报` -> PASS (score=100, conf=HIGH, drift=NONE) — [from Calibration Set] '海报' is a pure format query; all top5 are genuinely poster-formatted designs regardless of varied subject matter.
- **E181** `香氛` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — Rewrite matched well: two aroma-diffuser products and an aromatherapy spa-corner mood board are direct fragrance-industry hits; a kitchen scene and a sandwich card are unrelated food content.
- **E183** `poster` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. All 5 'template' tiles (title-bug affected, judged by slug) explicitly contain 'poster' in their category name - an unambiguous format match regardless of subject variety, consistent with the Chinese '海报' pairing.
- **E184** `贴纸` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Kawaii character-profile cards are sticker-adjacent in style but not explicitly sticker-format; food-photo 'doodle sticker overlay' cards are a direct format match.
- **E185** `sticker` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. All 5 results explicitly contain 'sticker' in their template name - an unambiguous format match, cleaner than the Chinese '贴纸' pairing.
- **E186** `名片` -> PASS (score=58, conf=MEDIUM, drift=NONE) — No rewrite. Kawaii 'profile card' format is card-shaped but for character bios, not real business cards; rank4 'business card etiquette' is a direct topical hit.
- **E187** `信封` -> PASS (score=85, conf=MEDIUM, drift=MINOR) — Rewrite matched well: three lunar-new-year 'red envelope' sets are a direct format match (a specific cultural sub-type of envelope); post-office scene and stationery vocab are envelope-adjacent.
- **E188** `明信片` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All results are 'vintage stamp collection' illustrations - a closely related but distinct philatelic format, not postcards themselves.
- **E189** `请柬` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. East-Asian culture-comparison and relationship-advice cards - no invitation-card format content for '请柬'.
- **E190** `菜单` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. Recipe cards show dish content that would appear on a menu but aren't menu-format themselves; meat-cut anatomy guides are food-industry-adjacent but unrelated to menu format.
- **E191** `menu` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Same pattern as '菜单' - recipe and regional-drinks cards are menu-content-adjacent but not menu-format matches.
- **E192** `包装盒` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'packaging design, box design templates, gift box illustration' but returned unrelated food-sticker and World-Cup-sticker cards - zero packaging/box content.
- **E193** `packaging` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Historical-battle cards are unrelated; two 'food product packaging design' cards are a direct match - notably, this un-rewritten English query outperformed the rewritten Chinese '包装盒' query, which returned zero relevant results.
- **E194** `手提袋` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'tote bag design, handbag illustration, shopping bag template' but only rank1 'bag' fashion-ecommerce card is on-topic; the rest are unrelated food-sticker and World-Cup-sticker cards.
- **E195** `标签` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Herbal-ingredient and solar-term cards - no label/tag-format content for '标签'.
- **E196** `台历` -> PASS (score=92, conf=MEDIUM, drift=NONE) — Rewrite matched well: three Chikawa 'monthly calendar' cards and an 'annual event calendar' infographic are direct format hits; a World Cup schedule flyer is calendar-adjacent but a different format.
- **E197** `书签` -> PARTIAL (score=30, conf=MEDIUM, drift=MODERATE) — Rewrite said 'bookmark design, literary bookmark, custom bookmarks'; a writers-profile card is literary-themed but not bookmark-format; cultural-goods mockups plausibly include bookmark-shaped merchandise but unconfirmed; a character poster card is unrelated.
- **E198** `徽章` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Historical-figure 'VS' comparison infographics and random product posters - no badge/emblem-format content for '徽章'.
- **E199** `badge` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to '徽章' - zero badge-format content; a consistent zh/en failure pair.
- **E200** `横幅` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Generic lifestyle-watercolor and animation-studio-comparison cards - no banner-format content for '横幅'.
