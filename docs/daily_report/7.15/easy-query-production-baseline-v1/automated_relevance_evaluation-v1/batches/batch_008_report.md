# batch_008 report

Queries: 20

Label distribution: {'PASS': 6, 'FAIL': 5, 'PARTIAL': 9}

- **E154** `母婴` -> PASS (score=62, conf=HIGH, drift=MINOR) — [from Calibration Set] 2 genuine parenting-content Examples; ranks 3-5 are generic template-category browse tiles, not baby-specific matches.
- **E141** `书房` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'home office decor, study room design' but all 5 results are other room types (dining bar, living room x2, kitchen) - zero study/home-office content.
- **E142** `温室` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'greenhouse design, botanical greenhouse' but returned generic flower/plant content (rose painting, flower coloring card, sunflower nail art, flower vocab) with no greenhouse structure depicted.
- **E143** `便利店` -> PARTIAL (score=17, conf=MEDIUM, drift=MODERATE) — Rewrite said 'convenience store' but results are 'grocery store' dialogue-scene cards (closely related but not identical retail format) plus an unrelated boutique and pet-shop card.
- **E144** `茶馆` -> PARTIAL (score=22, conf=MEDIUM, drift=MODERATE) — Low-result(3). Rewrite said 'tea house poster, Chinese tea culture' but returned a bubble-tea-shop brand mockup (tea-adjacent but a different retail concept) and its generic template tile; rank3 template tile is from an unrelated category.
- **E145** `寺庙` -> PASS (score=64, conf=MEDIUM, drift=MINOR) — Low-result(4). 'Giant wild goose pagoda' is a direct Buddhist-temple landmark match; Thailand travel-map and generic template tiles are temple/heritage-adjacent but not confirmed temple-specific.
- **E146** `湖畔` -> PARTIAL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'lakefront travel poster, watercolor lakeside, scenic lake view' but delivered a generic road-trip scene, a bridges-vocab card, an Oaxaca city card, and a generic travel-destination chart; only 'famous bridges' (water-adjacent) and 'Dali spring' (Dali is a real lakeside destination) are even weakly on-topic.
- **E147** `咖啡` -> PARTIAL (score=35, conf=MEDIUM, drift=NONE) — No rewrite. Two direct 'coffee brewing' hits within lifestyle-info-card and vintage-guide series otherwise showing unrelated topics (dog care, wine, cheese) from the same series.
- **E148** `coffee` -> PARTIAL (score=35, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to '咖啡' - same pattern of 2 direct coffee hits amid unrelated series noise.
- **E149** `烘焙` -> PARTIAL (score=37, conf=MEDIUM, drift=NONE) — No rewrite. Direct 'baking' action-guide hit; body-language/dance-styles cards from the same series are unrelated; dessert-color-lab cards are baking-adjacent but not baking-specific.
- **E150** `美妆` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Portrait-retouching guides are beauty-adjacent (photo editing) but not cosmetics-specific; hairstyle-tutorial and nail-art cards are direct beauty-industry matches.
- **E151** `珠宝` -> PASS (score=48, conf=MEDIUM, drift=NONE) — No rewrite. Ethnic-costume deconstruction boards plausibly include traditional jewelry/ornament detail; 'earrings for face shape' is a direct jewelry match; 'belts for body type' is a wrong accessory.
- **E152** `服装` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Anime-character portrait cards focus on character identity, not clothing/apparel design; portrait-retouching guides are also unrelated - no clothing-industry content for '服装'.
- **E153** `宠物` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Dog-breed and pet-care-guide cards are all direct pet-industry matches.
- **E155** `健身` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Fat-loss-plan and gym/running warmup-routine cards are all direct fitness-industry matches.
- **E156** `房地产` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '房地产' (real estate).
- **E157** `汽车` -> PARTIAL (score=7, conf=MEDIUM, drift=NONE) — No rewrite. Evolution-timeline cards for bicycles/snacks/phones are not cars; a family-road scene and an EV solid-state-battery card are automotive-adjacent but not car-industry-specific imagery.
- **E158** `酒店` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. Tourist-spot watercolor map cards are travel/hospitality-adjacent but not hotel-specific; coffee-brewing and interior-design-styles guides are unrelated specific topics.
- **E159** `hospitality` -> PARTIAL (score=33, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to '酒店' - same travel-adjacent-but-not-hotel-specific pattern.
- **E160** `婚庆` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Results are general East-Asian business/social etiquette comparison cards and relationship-advice cards - none specific to wedding services/events industry for '婚庆'.
