# batch_005 report

Queries: 20

Label distribution: {'PASS': 2, 'FAIL': 13, 'PARTIAL': 5}

- **E081** `bohemian` -> PASS (score=74, conf=MEDIUM, drift=MINOR) — Low-result(2). Direct 'bohemian' outfit-breakdown hit plus the generic parent template tile.
- **E082** `工业风` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'industrial style design, industrial decor templates, industrial aesthetic' but returned random fashion-ecommerce items (eyemask, musical instrument, pendant) and a diffuser poster; only rank5's industrial-design-concept-sketch (VTOL drone) is a genuine match.
- **E083** `industrial` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Ranks1-3 are the recurring Breaking Bad MBTI noise template; ranks4-5 are direct industrial-design-concept-sketch matches - notably better than the Chinese '工业风' pairing despite no rewrite assist.
- **E084** `田园` -> PARTIAL (score=30, conf=MEDIUM, drift=NONE) — No rewrite. 'Farmer farm' word-scene and a classical farmers poem are direct pastoral matches; 'cottagecore' is a rural-aesthetic-adjacent fashion style; 'academia' and 'bohemian' outfit styles are wrong.
- **E085** `未来感` -> PARTIAL (score=20, conf=MEDIUM, drift=MODERATE) — Rewrite said 'futuristic design/aesthetic' but delivered a historic Art Deco building (irrelevant) and three steampunk constellation cards (retro-futuristic, only a partial style match) plus an AI-themed MBTI card (thematically futuristic but not visually confirmed).
- **E086** `赛博朋克` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Results are wildlife-species conservation cards (baiji dolphin, panda, tiger) - zero cyberpunk aesthetic content.
- **E087** `cyberpunk` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Identical result set to '赛博朋克' - wildlife species cards, zero cyberpunk content; a consistent zh/en failure pair.
- **E088** `水彩` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Results are food cards and 'what-if history' cards with no watercolor-style indication for '水彩'.
- **E089** `watercolor` -> PARTIAL (score=65, conf=MEDIUM, drift=NONE) — No rewrite. All 5 are 'template' tiles sharing the title-extraction bug; judged by slug - 3 of 5 explicitly say 'watercolor', matching well, in contrast to the Chinese '水彩' query which failed completely with the same underlying intent.
- **E090** `手绘` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Results are travel-destination and food cards - zero hand-drawn-style indication for '手绘'.
- **E091** `hand-drawn` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to '手绘' - travel and food cards, zero hand-drawn content; a consistent zh/en failure pair.
- **E092** `扁平化` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '扁平化' (flat design).
- **E093** `涂鸦` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Kawaii-style character cards (soft/cute aesthetic, the opposite of graffiti/street-art) and anime-studio comparison charts - no graffiti-style content for '涂鸦'.
- **E094** `卡通` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Science-education infographics (DNA, plate tectonics) and NBA-player MBTI cards - no title confirms a cartoon-illustration style for '卡通'; treated as unconfirmed rather than assumed.
- **E095** `写实` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. Species-science cards (baiji, panda, tiger) plausibly use detailed/realistic rendering to depict real animals accurately; simple fruit-illustration cards are more likely graphic/vector style, not confirmed photorealistic.
- **E096** `极繁` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'maximalist design/style/aesthetic' but delivered three portrait-retouching tutorial cards (photo-editing technique, not a maximalist visual style) and a tech-news cover; only 'cottagecore' is even weakly maximalist-adjacent.
- **E097** `侘寂` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'wabi-sabi aesthetic/design/philosophy' and rank1 literally has 'wabi sabi' in its title, but ranks2-5 are an unrelated watercolor-painting tutorial series and a vocabulary card - only 1/5 genuinely on-topic despite a direct rewrite match being available.
- **E098** `wabi-sabi` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Identical result set to '侘寂' - only rank1 is genuinely wabi-sabi; a consistent zh/en failure pair despite matching rewrites.
- **E099** `法式` -> PASS (score=90, conf=MEDIUM, drift=NONE) — No rewrite. French dishes, French vocabulary, and French croissant are all direct matches for '法式'; the mille-crepe cake is a French-derived but Japanese-fusion dessert, weaker but adjacent. Note the matched intent narrows to French cuisine specifically, not French interior-design style, a secondary sense of the query.
- **E100** `美式` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(1), no rewrite. Only result is an ASL (American Sign Language) tutorial template - a wordplay-adjacent match on 'American' but not American aesthetic/style content.
