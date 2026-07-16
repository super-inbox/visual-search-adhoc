# batch_014 report

Queries: 20

Label distribution: {'PARTIAL': 2, 'FAIL': 11, 'PASS': 7}

- **E276** `护肤品` -> PARTIAL (score=13, conf=HIGH, drift=NONE) — [from Calibration Set] Implicit broadening from 'skincare products' to generic 'beauty' category (hair/nail/outfit noise) without an explicit rewrite banner.
- **E261** `七夕` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'Qixi Festival poster, Chinese Valentine's Day' but returned Christmas, a Spring Festival card, the movie Coco, Day of the Dead, and Diwali - zero Qixi content.
- **E262** `儿童节` -> PARTIAL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said "Children's Day celebration, kids festival poster" but delivered a World Cup trivia card, Day of the Dead, and Christmas; Shin-chan (a children's cartoon) and an amusement-park card are only weakly child-audience-adjacent.
- **E263** `教师节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said "Teacher's Day celebration, Teacher's Day poster" but every result matches only the word 'day' (Day of the Dead, wedding day, sick day, 'a day at school' x2) - the same word-collision pattern as '父亲节', zero Teacher's Day content.
- **E264** `国庆节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'National Day celebration poster, China National Day infographic' but returned five unrelated food/dessert cards (crepe cake, Vietnamese cuisine, custard tart, ice cream, Brazilian feijoada) - zero National Day content.
- **E265** `双十一` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'Double Eleven shopping, Singles' Day celebration' but returned Day of the Dead, two unrelated recipes, and two solar-term cards - zero shopping-festival content.
- **E266** `black friday` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'Black Friday deals, Black Friday shopping, holiday sales' but returned generic fashion-outfit-style cards with no sale/deal/shopping-event indication - core 'shopping event' intent lost.
- **E267** `新年` -> PASS (score=92, conf=MEDIUM, drift=NONE) — No rewrite. Three lunar-new-year red-envelope sets and a direct 'new year' scene card are strong hits; a 'lichun' (start-of-spring) solar-term card is seasonally adjacent.
- **E268** `光棍节` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said "Singles' Day celebration..." but returned the same 'day'-word-collision and generic festival-filler pattern seen elsewhere - zero Singles' Day content.
- **E269** `冬至` -> PASS (score=62, conf=MEDIUM, drift=MINOR) — Rewrite matched well: 'dongzhi' is the direct literal match; other solar-term cards and a Winter Olympics poster are seasonally/thematically adjacent to winter solstice.
- **E270** `光明节` -> FAIL (score=15, conf=MEDIUM, drift=MODERATE) — Rewrite reinterpreted '光明节' (the standard Chinese term for Hanukkah) as Diwali - a defensible but debatable reading of 'Festival of Lights'; even granting that interpretation, only rank1 actually delivers Diwali content, the rest is Christmas/Spring-Festival/Coco/Hanami noise.
- **E271** `香水` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'fragrance design, perfume variety, scented products' but returned country-manufacturing map cards and unrelated recipe cards - only a generic 'beauty products' card is even weakly on-topic.
- **E272** `perfume` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'scented perfume infographic, fragrance poster...' but returned weather, architecture, Christmas, and cultural-relic cards - only an aromatherapy-bedroom card is weakly fragrance-adjacent, consistent with the Chinese '香水' pairing.
- **E273** `茶叶` -> PASS (score=95, conf=MEDIUM, drift=NONE) — Rewrite matched very well: tea-basics, matcha, tea-ceremony, and a tea-themed mascot are direct hits; bubble tea is a related but distinct tea-beverage format.
- **E274** `咖啡豆` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: every result is directly coffee-bean-related content.
- **E275** `巧克力` -> PASS (score=95, conf=MEDIUM, drift=NONE) — Rewrite matched very well: four results are explicitly chocolate-themed; 'swiss' cuisine vocab is chocolate-adjacent (Switzerland's chocolate reputation) but not chocolate-specific.
- **E277** `skincare` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(3), no rewrite. All 3 'template' tiles (title-bug, judged by slug) are hair/nail-related, not skincare - zero skincare content, worse than the Chinese '护肤品' pairing.
- **E278** `口红` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'lipstick designs, cosmetic products, makeup essentials' but returned baby products, nail art, a kitchen scene, and a hairdryer - none are lipstick or even close cosmetic matches beyond a generic 'beauty products' card.
- **E279** `首饰` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: diamond/emerald jewelry, a ring, earrings, and a 'Jewelry Look' card are all direct jewelry matches.
- **E280** `手表` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Smartwatch ads, industrial design sketches, and a bilingual watch-labeling card are all direct watch/smartwatch matches.
