# batch_013 report

Queries: 20

Label distribution: {'PARTIAL': 6, 'FAIL': 8, 'PASS': 6}

- **E248** `中秋节` -> PARTIAL (score=25, conf=HIGH, drift=MODERATE) — [from Calibration Set] Rewrite's 'Chinese cultural celebration' pulled in Songkran (Thai) and Gawai (Dayak) - unrelated cultures/festivals.
- **E241** `数字游民` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Generic travel-series and top-10-destination cards are digital-nomad-lifestyle-adjacent but don't depict remote-work/nomad life specifically.
- **E242** `家庭主妇` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'housewife lifestyle, family roles infographic, domestic life poster' but returned only unrelated food/cuisine cards - zero housewife/domestic-life content.
- **E243** `创业者` -> PASS (score=80, conf=MEDIUM, drift=NONE) — Rewrite matched well: 'One-Person Companies', 'founders', and 'employee vs entrepreneur' are direct hits; 'operator' and 'hacker' tech-professional MBTI cards are entrepreneur-adjacent.
- **E244** `留学生` -> PARTIAL (score=35, conf=MEDIUM, drift=MODERATE) — Rewrite said 'international student poster, study abroad infographic' but delivered generic East-Asian culture-comparison cards and China/Chengdu culture cards - cross-cultural/study-abroad-adjacent but not explicitly depicting international students.
- **E245** `宝妈` -> PASS (score=65, conf=MEDIUM, drift=MINOR) — Rewrite matched reasonably: 'parenting families' and 'dad vs mom' are direct family/parenting hits; a corgi pet-care card is unrelated; gardening and park scenes are lifestyle-adjacent.
- **E246** `猫奴` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All results are the recurring 'dual-character-comparison-infographic' noise series - zero cat content for '猫奴'.
- **E247** `春节` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Chinese-dish recipe cards are festive-food-adjacent; two 'spring festival' high-speed-rail MBTI cards directly reference the well-known Spring Festival travel-rush ('春运') cultural phenomenon.
- **E249** `端午节` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — Rewrite matched very well: two Dragon Boat Festival cards and a Zongzi recipe are direct hits; wedding traditions and Christmas cards are unrelated.
- **E250** `圣诞节` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: all 5 results are explicitly Christmas-themed.
- **E251** `christmas` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Identical Christmas-themed result set to '圣诞节' - a consistent zh/en pass pair.
- **E252** `万圣节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Halloween celebration poster...' but only rank1 (Halloween vocab) is on-topic; ranks2-5 are a recurring generic-festival 'filler' set (Christmas, a solar-term card, an amusement-park MBTI card) unrelated to Halloween.
- **E253** `halloween` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'halloween celebration poster...'; identical filler pattern to '万圣节' - only the direct vocab-card hit is on-topic.
- **E254** `情人节` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. 'MBTI in love' cards and 'One Piece Valentine' character posters are all direct Valentine's Day matches.
- **E255** `母亲节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said "Mother's Day celebration poster, Mother's Day vocabulary" but delivered zero Mother's-Day content - Day of the Dead, Christmas, a solar-term card, and generic MBTI-animal cards (the recurring festival-filler set).
- **E256** `父亲节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said "Father's Day celebration, Father's Day vocabulary" but every result appears to match only on the word 'day' (Day of the Dead, wedding day, sick day, 'a day at school' x2) - zero actual Father's Day content, a clear word-sense collision.
- **E257** `感恩节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Thanksgiving celebration poster...'; only the direct vocab-card hit is on-topic, rest is the recurring festival-filler set (Christmas, solar term, amusement park, spring festival).
- **E258** `thanksgiving` -> PARTIAL (score=15, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Thanksgiving celebration poster...'; direct vocab-card hit plus a 'Chinese traditional foods' card (traditional-food theme, weakly Thanksgiving-adjacent) - slightly better than the Chinese '感恩节' pairing but still mostly unrelated.
- **E259** `复活节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Easter celebration poster...'; only the direct vocab-card hit is on-topic, rest is the recurring festival-filler set.
- **E260** `元宵节` -> PARTIAL (score=13, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Lantern Festival poster...'; direct 'lantern festival' scene hit; 'spring festival' MBTI card is culturally proximate (Lantern Festival follows Chinese New Year); Christmas and Songkran (Thai New Year) cards are unrelated.
