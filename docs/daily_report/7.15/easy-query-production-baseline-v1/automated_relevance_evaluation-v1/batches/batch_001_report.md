# batch_001 report

Queries: 20

Label distribution: {'PARTIAL': 14, 'FAIL': 5, 'PASS': 1}

- **E001** `鲜花` -> PARTIAL (score=44, conf=HIGH, drift=MINOR) — Query '鲜花'(fresh flowers) expects flower photography/arrangement. Rank1 directly matches; ranks2-3 use cherry blossom only as a fashion/nail-art motif; ranks4-5 are generic brand-template tiles. Example thumbnails were blank/unrendered in the screenshot, so ranks1-3 rely on title+slug text, not confirmed pixels.
- **E002** `flower` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — No rewrite. Ranks1-3 are flower-themed phonics coloring cards (direct match); ranks4-5 are unrelated city-landmark fridge-magnet sets.
- **E003** `猫` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Results are a generic comparison-infographic series (dad vs mom, introvert vs extrovert), a giant panda, and a non-cat Ghibli character - zero cats returned for '猫'.
- **E004** `cat` -> PARTIAL (score=20, conf=HIGH, drift=NONE) — No rewrite. Ranks1-3 are the same generic comparison-infographic noise; ranks4-5 (British Shorthair pet-care, cat-safe-food) are genuine cat matches, confirmed via screenshot.
- **E005** `狗` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — No rewrite. Ranks1-3 are dog-breed cards (bulldog/husky/labrador, direct); ranks4-5 are the recurring generic comparison-infographic noise.
- **E006** `书` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Ranks1-3 are city travel posters (no book content); ranks4-5 are 'Journey to the West' book-series cards, a direct match.
- **E007** `book` -> PARTIAL (score=35, conf=MEDIUM, drift=NONE) — No rewrite. All 5 are 'template' category tiles sharing a known title-extraction bug (title repeats 'Phonics Learning Poster' for every tile); judged from URL slug instead - book-minimalist and book-recommendation-grid-poster are book-relevant, the other 3 slugs are not.
- **E008** `咖啡杯` -> PARTIAL (score=42, conf=MEDIUM, drift=MINOR) — Low-result(2). Coffee mug appears as one icon within a larger office-supplies icon grid, not the primary subject; rank2 is the same generic template category.
- **E009** `蜡烛` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All 4 results are 'product poster' templates for the wrong specific product (diffuser/speaker/coffee maker/generic category tile) - none are candles.
- **E010** `candle` -> PARTIAL (score=42, conf=MEDIUM, drift=MINOR) — Low-result(2). Aromatherapy/spa bedroom decor is scent-adjacent but no candle is clearly depicted by title/slug; rank2 is the generic parent template category.
- **E011** `相机` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Ranks1-3 are an unrelated 'evolution timeline' series (bicycles/snacks/phones); ranks4-5 are direct camera matches.
- **E012** `眼镜` -> PARTIAL (score=26, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. 'glasses for face shape' (rank3) is a direct hit within a fashion-shape-guide series otherwise about belts/earrings; rank4 is the same generic template category.
- **E013** `背包` -> PARTIAL (score=42, conf=MEDIUM, drift=MINOR) — Low-result(2). A hiking-packing-guide infographic is backpack-adjacent (backpacks typically shown in hiking gear layouts) but not a dedicated backpack product shot.
- **E014** `雨伞` -> PARTIAL (score=42, conf=MEDIUM, drift=MINOR) — Low-result(2), rewrite to 'umbrella design, rainy day accessories, weather protection gear'. 'rainy day' word-scene card is thematically adjacent to umbrella but a rainy scene doesn't guarantee a visible umbrella; rank2 is the generic parent template category.
- **E015** `自行车` -> FAIL (score=15, conf=MEDIUM, drift=NONE) — No rewrite. Rank1 'bicycles' (evolution-timeline-infographic) is a direct match, but ranks2-5 are unrelated tourist-map and evolution-timeline noise (Central Park, snacks, phones, Rome) - the same noise-template pattern seen in other object queries.
- **E016** `钢笔` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All 4 results are a 'personal journey / wolf path' motivational-illustration series (career/dreams/finance/generic category) - no pen or writing-instrument content at all.
- **E017** `地球仪` -> PARTIAL (score=35, conf=MEDIUM, drift=MODERATE) — Rewrite pivoted specific 3D-object query ('地球仪'=desk globe) to generic 'map' content; all results are flat/illustrated country maps or landmark collages, not an actual globe object.
- **E018** `台灯` -> PARTIAL (score=23, conf=MEDIUM, drift=MODERATE) — Interior mood-board scenes (bedroom/dining/office) are lamp-adjacent at best, no lamp foregrounded; rank5 'Aromatherapy Diffuser' is a wrong specific product.
- **E019** `镜子` -> FAIL (score=0, conf=HIGH, drift=SEVERE) — Rewrite added 'vanity mirror' etc. but production matched entirely unrelated Chinese-intangible-heritage/solar-term posters; confirmed via screenshot - no mirror content anywhere.
- **E020** `花瓶` -> PASS (score=74, conf=MEDIUM, drift=MINOR) — Low-result(2), rewrite to 'vase design, ceramic vase, flower vase'. Rank1 literally titled 'Ming vase as coffee shop barista' - a stylized but direct vase depiction; rank2 is the parent template category that produced it.
