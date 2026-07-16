# batch_007 report

Queries: 20

Label distribution: {'FAIL': 5, 'PASS': 11, 'PARTIAL': 4}

- **E121** `卧室` -> FAIL (score=10, conf=MEDIUM, drift=NONE) — No rewrite. Only rank2 'bedroom' room-vocabulary card is a direct hit; ranks1,3 are wrong rooms and ranks4-5 are unrelated 3D keycap-diorama art.
- **E122** `花园` -> PASS (score=65, conf=MEDIUM, drift=NONE) — No rewrite. Direct 'garden' room-vocabulary card and 'garden birds' stamp collection are strong hits; flower/lily cards and an F4-drama poster referencing a garden setting are garden-adjacent.
- **E123** `海滩` -> PASS (score=58, conf=MEDIUM, drift=NONE) — No rewrite. Beach-destination travel cards (Sanya/Indonesia/Greece/Thailand) are plausibly beach-themed but not confirmed beach-scene imagery; rank4's 'beach' dialogue-scene card is a direct hit.
- **E124** `beach` -> PASS (score=68, conf=MEDIUM, drift=NONE) — No rewrite. Two direct 'beach' scene cards plus beach-destination travel cards (Sanya/Greece/Phuket) - consistent with the Chinese '海滩' pairing.
- **E125** `山间` -> PASS (score=88, conf=MEDIUM, drift=NONE) — Rewrite matched very well: 4 of 5 results explicitly feature 'mountain' in title/slug across ink-wash art, stamp illustration, travel journal, and ecosystem infographic formats.
- **E126** `森林` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. 'Explorer forest' scene, Ghibli characters San and Totoro (both strongly forest-associated in their source films), a trees vocab card, and forest-animals vocab - an unambiguous match.
- **E127** `图书馆` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Book-recommendation and manga-artist cards are book/literary-themed but none depict an actual library scene/setting - thematically adjacent, not a direct scene match.
- **E128** `市集` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'market poster, local market guide, city market infographic' but returned random fashion-ecommerce items and a speaker poster; only rank4's 'At the Market' scene card is on-topic.
- **E129** `展览` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — No rewrite. Species-science cards and architecture-landmark cards - no exhibition-scene content for '展览'.
- **E130** `演唱会` -> PASS (score=95, conf=MEDIUM, drift=NONE) — Rewrite matched well: a Blackpink tour poster, a musical-performance guide, and two Coachella festival posters are direct concert/live-event hits; a Mozart figure card is music-adjacent but not a concert scene.
- **E131** `concert` -> PASS (score=55, conf=MEDIUM, drift=NONE) — No rewrite. Music-score art posters are music-themed but not concert-scene imagery; a K-pop-fan-tourist scene is concert-culture-adjacent; rank5 'musical performance' is a direct hit.
- **E132** `游乐园` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: every result explicitly features 'amusement park' or the closely related 'waterpark' in title/slug.
- **E133** `餐厅` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Rank2 'restaurant' dialogue-scene card is a direct hit within a broader dialogue-scene series (greeting/shopping); recipe cards are restaurant-menu-adjacent but not scene imagery.
- **E134** `restaurant` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. All 5 results are recipe/food cards - restaurant-menu-adjacent but none depict a restaurant scene itself, unlike the Chinese '餐厅' pairing which surfaced an actual restaurant dialogue-scene card.
- **E135** `健身房` -> PASS (score=62, conf=MEDIUM, drift=NONE) — No rewrite. Fat-loss-plan infographics are fitness-adjacent but not gym-scene imagery; two direct 'gym' scene/MBTI cards confirm the match.
- **E136** `机场` -> PASS (score=75, conf=MEDIUM, drift=NONE) — No rewrite. 'Family airport' and 'airport' scene cards plus two plane-themed MBTI cards are direct hits; the cafe card is an unrelated mismatch from the same MBTI series.
- **E137** `校园` -> FAIL (score=0, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. Results are basketball/football-player MBTI cards and a generic template tile - zero campus/school-scene content for '校园'.
- **E138** `农场` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. 'Eco farm' product-label cards show farm-branded goods (not a farm scene itself); Yellowstone MBTI cards are ranch/farm-setting-adjacent via the show's setting, not confirmed farm imagery.
- **E139** `夜市` -> PARTIAL (score=20, conf=MEDIUM, drift=MODERATE) — Rewrite said 'night market poster, street food culture' but delivered generic country-cuisine vocabulary cards (street-food-adjacent, not night-market-scene) plus two unrelated single-dish cards (coffee, Neapolitan pizza).
- **E140** `阳台` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite said 'balcony decor, outdoor living space, terrace design' but returned closet/living-room organization cards and an unrelated solar-term card - no balcony/terrace content; only the 'biophilic living room' card is weakly plant/nature-adjacent.
