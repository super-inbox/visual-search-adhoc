# batch_017 report

Queries: 8

Label distribution: {'PARTIAL': 3, 'PASS': 4, 'FAIL': 1}

- **E321** `拍照` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — Rewrite matched well: three 'portrait retouching blueprint' cards are direct photo/portrait-taking matches; two hairstyle-color-recommendation cards are grooming-guide content unrelated to the act of taking photos.
- **E322** `手工制作` -> PARTIAL (score=62, conf=MEDIUM, drift=NONE) — No rewrite. A Cricut/SVG crafting-tutorial card and a 'paper cutting' intangible-heritage card (a traditional Chinese handicraft) are direct hits; a baking hobby-sticker sheet is craft-adjacent but food-focused; two individual food-dish cards (roujiamo, taco) are unrelated to handmade crafting.
- **E323** `旅行` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. All results are destination-specific 'travel' series cards (Beijing, Sanya, Xi'an, Netherlands) - a direct match for '旅行'.
- **E324** `撸铁` -> PASS (score=85, conf=MEDIUM, drift=NONE) — Rewrite matched well: 'gym' warmup, 'home workout plan', 'arm day' (classic weightlifting-split terminology), and a 'training types' education card are direct strength-training hits; a fat-loss plan card is fitness-adjacent but centers on weight loss rather than lifting.
- **E325** `冥想` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'meditation practices, mindfulness techniques, relaxation methods' but delivered zero explicit meditation content - two yoga cards are mindfulness-adjacent at best; a generic morning-routine card and two unrelated herbal-ingredient cards carry no meditation content.
- **E326** `阅读` -> PARTIAL (score=7, conf=MEDIUM, drift=NONE) — No rewrite. Two India-space-mission hotspot-news cards and an 'asset hedge' finance card carry no reading theme; two CVC English-phonics word-coloring cards are early-literacy/reading-practice content, weakly on-topic for '阅读'.
- **E327** `烹饪` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Regional-dish 'food' cards and explicit 'premium recipe card' infographics are all cooking/recipe content - a direct match for '烹饪'.
- **E328** `野餐` -> PASS (score=58, conf=MEDIUM, drift=NONE) — No rewrite. 'Spring picnic' is a direct hit; park-scene vocabulary cards and a spring-meadow lifestyle photo grid are picnic-adjacent outdoor settings without an explicit picnic depiction.
