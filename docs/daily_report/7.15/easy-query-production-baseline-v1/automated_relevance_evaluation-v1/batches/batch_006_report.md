# batch_006 report

Queries: 20

Label distribution: {'PARTIAL': 9, 'PASS': 4, 'FAIL': 7}

- **E118** `生日派对` -> PARTIAL (score=50, conf=HIGH, drift=MODERATE) — [from Calibration Set] Rewrite's generic 'celebration poster' pulled in Christmas and a solar-term card, wrong occasions.
- **E101** `韩系` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched extremely well: Korean hanbok costumes, Korean clothing-evolution, a Korean design-student portrait, and Seoul travel content - all direct.
- **E102** `中古` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '中古' (vintage/secondhand).
- **E103** `童趣` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'childlike fun, playful childhood, whimsical play' but delivered two unrelated travel-city cards, an astronaut scene, and a student-laboratory scene; only rank1's 'child park' is genuinely on-topic.
- **E104** `奢华` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Celebrity/movie posters (ranks1-3) don't carry a luxury aesthetic; 'old money style' name cards (ranks4-5) are a genuine luxury-aesthetic match.
- **E105** `清新` -> PARTIAL (score=15, conf=MEDIUM, drift=NONE) — No rewrite. English vocabulary-upgrade cards are unrelated; a 'fresh green' color-lab card is a direct match for '清新'(fresh/clean aesthetic), 'golden moments' is a weaker color-aesthetic adjacency.
- **E106** `暗黑` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'dark fantasy/aesthetic/themes'; rank1 'dark academia' is a direct hit, but ranks2-5 are all 'template' tiles with no dark-style indicator in their slugs (men's lifestyle guide, ethnic costume board, MBTI-in-love, old-money-style).
- **E107** `梦幻` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Generic top-10 travel-destination cards and mental-health self-care illustration cards - no dreamy/fantastical aesthetic content for '梦幻'.
- **E108** `街头` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Fashion-outfit-breakdown cards (academia/bohemian/cottagecore) are wrong styles; football-player 'graffiti poster' cards are a genuine street-art-style match.
- **E109** `cottagecore` -> PARTIAL (score=26, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Only rank3 is the direct 'cottagecore' hit within a fashion-style-outfit series otherwise showing academia/bohemian.
- **E110** `dark academia` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Rank1 'academia' captures half the two-word query (missing 'dark'); ranks2-3 (bohemian, cottagecore) are wrong styles. Notably, the Chinese '暗黑' query for the same 'dark' concept did surface the actual 'dark academia' template directly - this English two-word query did not, a retrieval inconsistency.
- **E111** `Y2K` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Fashion-outfit-breakdown cards, a child-park scene, and a physics education card - no Y2K/2000s-aesthetic content anywhere.
- **E112** `教室` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Room-vocabulary cards for the wrong rooms (bathroom/bedroom/garden, no classroom) and world-map illustrations - zero classroom-scene content for '教室'.
- **E113** `classroom` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. All 5 are 'template' tiles (title-bug affected, judged by slug) for generic educational-content categories (word-pair posters, cheat sheets, vocabulary) - none actually depict a classroom scene/setting, same failure as the Chinese '教室' pairing.
- **E114** `咖啡馆` -> PASS (score=48, conf=MEDIUM, drift=NONE) — No rewrite. Food-photo sticker cards (brunch, coffee, etc.) are cafe-menu-adjacent but not a cafe scene itself; rank5 'cafe 1' MBTI card is a direct hit; rank4 seafood-bistro menu is unrelated.
- **E115** `cafe` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Three direct 'cafe' MBTI-animal cards plus two cafe-ordering dialogue scenes - a clean, unambiguous match, stronger than the Chinese '咖啡馆' pairing.
- **E116** `婚礼` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Traditional wedding costumes (Han/Tang dynasty) and bridal hairstyle/wedding-dress cards - an unambiguous direct match for '婚礼'.
- **E117** `wedding` -> PARTIAL (score=7, conf=MEDIUM, drift=NONE) — No rewrite. Musical-score art posters (ballet, winter scene, Christmas cartoon) are unrelated; ballroom dance-step tutorials are only weakly wedding-adjacent (first-dance prep, not confirmed). A striking contrast with the Chinese '婚礼' query, which got a clean direct-match PASS with the same underlying intent.
- **E119** `办公室` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. 'Office Meeting Chaos' is a direct office-scene hit; 'Group Chat Dynamics' and 'Party Socializing' are workplace/social-adjacent but not explicitly office; ranks4-5 are the recurring dual-character-comparison noise template.
- **E120** `厨房` -> PARTIAL (score=23, conf=MEDIUM, drift=NONE) — No rewrite. Cheese-tasting and coffee-brewing guides are kitchen/food-prep-adjacent but not an explicit kitchen scene; indoor-plant-care and bathroom/bedroom room-vocabulary cards are wrong rooms/topics.
