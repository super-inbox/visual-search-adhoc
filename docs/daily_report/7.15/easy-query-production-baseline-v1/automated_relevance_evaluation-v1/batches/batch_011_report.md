# batch_011 report

Queries: 20

Label distribution: {'PASS': 6, 'FAIL': 8, 'PARTIAL': 6}

- **E217** `儿童` -> PASS (score=100, conf=HIGH, drift=NONE) — [from Calibration Set] All top5 are children's-education dialogue/error-correction cards clearly featuring child characters.
- **E201** `banner` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to '横幅' - generic lifestyle-watercolor and animation-studio-comparison cards, zero banner-format content.
- **E202** `展架` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '展架' (display/exhibition stand).
- **E203** `折页` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'brochure design, folded leaflet, pamphlet template' but returned Journey-to-the-West/Crayon-Shinchan character cards and social-issue analysis infographics - zero brochure-format content.
- **E204** `画册` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. Fashion outfit-style-variation cards could plausibly be part of a fashion 'album' spread but aren't confirmed album-format; World-Cup fan-outfit posters are unrelated.
- **E205** `卡片` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Education-card and MBTI-comparison-card templates are all genuinely card-formatted, regardless of subject variety - a direct format match.
- **E206** `card` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Character, education, and herbal cards are all genuinely card-formatted - consistent with the Chinese '卡片' pairing.
- **E207** `头像` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Battle-poster character portraits are avatar-adjacent but designed as full posters; kawaii 'profile card' portraits are a closer, more direct avatar-style match.
- **E208** `avatar` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite reinterpreted 'avatar' as the movie title rather than the profile-picture format, then failed even that: World Cup squad posters are unrelated to any 'Avatar' sense, and the two movie-poster hits (Forrest Gump, La La Land) are movie posters but not the film 'Avatar' - the query's core intent (a user profile picture) is lost entirely.
- **E209** `壁纸` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All results are 'media-theme wallpaper poster' cards or their parent template tile - a direct, unambiguous format match.
- **E210** `wallpaper` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — No rewrite. Three direct wallpaper-poster hits consistent with '壁纸'; two Chikawa monthly-calendar cards are a different format (calendar, not wallpaper).
- **E211** `表情包` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. MBTI athlete cards and historical-figure 'VS' infographics - no meme/reaction-image format content for '表情包'.
- **E212** `手账` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'bullet journal templates, planner design, scrapbook layout' but returned East-Asian culture-comparison and relationship-advice cards - zero journal/planner-format content.
- **E213** `planner` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Kids-hobby infographics and a Netherlands travel-photo series - no planner-format content for 'planner'.
- **E214** `抱枕` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. 'Cultural goods mockup set' plausibly includes pillow-shaped merchandise among its IP products, but unconfirmed; character-profile poster cards are unrelated to pillow format.
- **E215** `帆布袋` -> PARTIAL (score=23, conf=MEDIUM, drift=NONE) — No rewrite. Museum-gift merchandise displays plausibly include tote bags among the shown products, but unconfirmed; food-sticker cards are unrelated.
- **E216** `马克杯` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Cultural-goods and museum-gift merchandise mockups plausibly include mugs (a very common gift-shop item) but no title explicitly confirms mug format.
- **E218** `children` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Generic vocabulary cards are plausibly kid-oriented educational content but don't explicitly feature children; the dialogue-scene cards are the same template series visually confirmed (in the '儿童' calibration query) to depict child characters.
- **E219** `青少年` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Sport-rules and pro-athlete infographics are youth-interest-adjacent but not explicitly targeted at or featuring teenagers.
- **E220** `婴儿` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. 'Generation comparison' infographics (gaming consoles, music eras) are a word-sense mismatch on 'generation', not about babies/infants; Disney color-grid cards are also unrelated - zero baby content for '婴儿'.
