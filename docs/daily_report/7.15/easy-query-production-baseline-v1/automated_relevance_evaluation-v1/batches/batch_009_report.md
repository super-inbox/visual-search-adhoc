# batch_009 report

Queries: 20

Label distribution: {'FAIL': 8, 'PASS': 7, 'PARTIAL': 5}

- **E161** `教育培训` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Results are unrelated professional-category guides (coffee brewing, interior design, plant care) - no education/training content for '教育培训'.
- **E162** `医疗健康` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: healthcare-technology, doctor/hospital scenes, and hospital dialogue/vocab cards across three languages - an unambiguous match.
- **E163** `金融` -> PASS (score=80, conf=MEDIUM, drift=NONE) — No rewrite. Currency-evolution, investor MBTI, and bank dialogue cards are direct finance matches; a corporate-layoff news graphic and its generic template tile are business-adjacent.
- **E164** `旅游` -> PARTIAL (score=35, conf=MEDIUM, drift=NONE) — No rewrite. Direct Beijing/Sanya travel-destination cards are on-topic, but 3 of 5 results are weather-forecast cards (same city names, wrong category - weather not tourism).
- **E165** `travel` -> PASS (score=82, conf=MEDIUM, drift=NONE) — No rewrite. All 5 are 'template' tiles (title-bug affected, judged by slug) - travel, cultural-travel-journey, and best-cities-travel are direct; souvenir and dos-and-donts guides are travel-adjacent. Cleaner than the Chinese '旅游' pairing, which was diluted by weather cards.
- **E166** `餐饮` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Recipe and food cards are all direct food & beverage industry matches.
- **E167** `家居` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Home-organization and soft-decoration-design-guide cards are all direct home-furnishing matches.
- **E168** `3C数码` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '3C数码' (3C digital electronics).
- **E169** `游戏` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Journey-to-the-West and anime character-analysis cards are about the characters themselves, not gaming-industry content - no title confirms a gaming context for '游戏'.
- **E170** `gaming` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Historical-general 'battle' cards and Naruto MBTI character cards are combat/anime-themed and gaming-adjacent, but none are confirmed gaming-industry content (no game UI, controller, or explicit game branding).
- **E171** `出版` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Ethnic-costume boards and animation-studio comparison cards - no publishing-industry (books/print) content for '出版'.
- **E172** `农业` -> PASS (score=95, conf=MEDIUM, drift=NONE) — No rewrite. Gardening how-to cards (peppers/carrots/lettuce) and a farmer-farm scene are direct agriculture matches; the 'guyu' (Grain Rain) solar-term card is agriculturally-themed but not a farming scene itself.
- **E173** `花艺` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'floral design, flower arrangement, flower art' but returned an unrelated watercolor-tutorial series (butterfly/lemon/mushrooms) and vocabulary posters (animals, fruits) - zero floristry content.
- **E174** `摄影` -> PARTIAL (score=20, conf=MEDIUM, drift=NONE) — No rewrite. Recipe cards are unrelated; portrait-retouching-blueprint cards are a direct photography-industry match.
- **E175** `二手交易` -> FAIL (score=0, conf=LOW, drift=NONE) — Zero result for '二手交易' (secondhand trading).
- **E176** `物流` -> PASS (score=77, conf=MEDIUM, drift=NONE) — Low-result(2). Direct 'courier logistics' scene card plus its generic parent template tile.
- **E177** `美发美甲` -> PARTIAL (score=35, conf=MEDIUM, drift=MODERATE) — Low-result(4). Rewrite said 'hair and nail design, hair styling and manicure, beauty salon services'; two hairstyle-recommendation template tiles are direct hits (hair only, no nail-salon content), but a café-ordering dialogue card and a generic dialogue-scene template tile are unrelated.
- **E178** `瑜伽` -> PARTIAL (score=75, conf=MEDIUM, drift=NONE) — No rewrite. Pain-relief yoga cards (back/knee/lower-back) are direct hits; unrelated lifestyle-info cards (coffee, dog care) dilute the tail.
- **E179** `潮玩` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Food-photo stickers and World Cup team stickers - no designer-toy/collectible-toy industry content for '潮玩'.
- **E180** `茶饮` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Results are Chinese solar-term seasonal cards - zero tea-beverage content for '茶饮'.
