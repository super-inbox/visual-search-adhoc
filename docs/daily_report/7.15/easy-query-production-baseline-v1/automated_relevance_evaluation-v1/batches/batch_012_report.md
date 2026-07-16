# batch_012 report

Queries: 20

Label distribution: {'PARTIAL': 10, 'FAIL': 1, 'PASS': 9}

- **E221** `学生` -> PARTIAL (score=23, conf=MEDIUM, drift=NONE) — No rewrite. Education-card science topics are student-audience-adjacent but don't depict students; herbal-ingredient and species cards are unrelated.
- **E222** `student` -> PARTIAL (score=37, conf=MEDIUM, drift=NONE) — No rewrite. All 5 'template' tiles (title-bug, judged by slug) are educational-content categories that are student-audience-adjacent, except 'life journey curve' which is unrelated.
- **E223** `上班族` -> PARTIAL (score=57, conf=MEDIUM, drift=MINOR) — Rewrite matched reasonably: an office annual-meeting MBTI card and two 'Office Meeting Chaos' cards are direct office-worker hits; a France culture card and Italian cuisine card are unrelated.
- **E224** `老年人` -> FAIL (score=0, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'elderly care templates, senior lifestyle infographic' but returned a Journey-to-the-West character card, a recipe, and city travel/weather cards - zero elderly-audience content.
- **E225** `新手妈妈` -> PARTIAL (score=17, conf=MEDIUM, drift=SEVERE) — Rewrite said 'new mom resources, first-time mother guide'; rank1 'Mother' scene is direct, but rank2 matches 'first time' via a World Cup debut-team poster and rank3 matches 'mother of pearl' via a gem pendant - both wrong-sense word matches; generic guide cards are weakly beginner-adjacent.
- **E226** `宠物主人` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Pet-care-guide and pet-safe-food cards are all direct pet-owner-audience content.
- **E227** `大学生` -> PASS (score=82, conf=MEDIUM, drift=NONE) — Rewrite matched well: three 'college student' self-portrait posters are direct hits; a 'student alpaca' mascot sticker is a weaker match; a pizza card is unrelated.
- **E228** `自由职业者` -> PARTIAL (score=3, conf=MEDIUM, drift=SEVERE) — Rewrite explicitly said 'freelancer poster, freelance lifestyle infographic' but returned tech-executive MBTI cards (professional-adjacent but not freelancer-specific) and unrelated travel/hotspot cards.
- **E229** `教师` -> PARTIAL (score=45, conf=MEDIUM, drift=NONE) — No rewrite. Same English-dialogue-scene/error-correction card series confirmed (via the '儿童' calibration screenshot) to depict child characters in learning scenarios - educational context present, but centered on students, not a visible teacher/educator figure. Flagged for manual review given the audience-intent ambiguity.
- **E230** `teacher` -> PARTIAL (score=17, conf=MEDIUM, drift=MODERATE) — Rewrite said 'teacher vocabulary, education infographic, classroom poster' but delivered generic daily-essentials vocab and food-cuisine vocab cards, plus a 'Busy Student' scene (student, not teacher) - core intent (an educator) not preserved.
- **E231** `医生` -> PARTIAL (score=7, conf=MEDIUM, drift=NONE) — No rewrite. Pet-safe-food cards are veterinary-adjacent at best, not human-doctor content; popular-science health infographics are medical-themed and doctor-audience-adjacent but don't depict a doctor.
- **E232** `健身爱好者` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Rewrite matched perfectly: fat-loss plans, a home-workout guide, and a gym warmup card are all direct fitness-enthusiast content.
- **E233** `旅行者` -> PASS (score=100, conf=MEDIUM, drift=NONE) — No rewrite. Travel-series and cultural-travel-journey cards are all direct traveler-audience content.
- **E234** `手工艺人` -> PASS (score=92, conf=MEDIUM, drift=NONE) — No rewrite. Vietnam traditional-handicraft-village cards and an intangible-heritage card are direct artisan/craftsperson matches; a baking sticker sheet is a weaker hobby-craft connection.
- **E235** `收藏家` -> PASS (score=88, conf=MEDIUM, drift=NONE) — No rewrite. Vintage football-jersey posters are direct collector-item content; vintage musical-instrument illustrations are collector-adjacent via the 'vintage/collectible' theme.
- **E236** `Z世代` -> PASS (score=88, conf=MEDIUM, drift=NONE) — No rewrite. Gen-Z internet-slang recap infographics are a direct match; generation-comparison cards are thematically Gen-Z-adjacent.
- **E237** `Gen Z` -> PASS (score=88, conf=MEDIUM, drift=NONE) — No rewrite. Identical result set to 'Z世代' - a consistent zh/en pass pair.
- **E238** `二次元爱好者` -> PASS (score=100, conf=MEDIUM, drift=NONE) — Low-result(4), no rewrite. All results are 'MBTI anime character poster' cards - a direct match for anime/2D-culture enthusiasts.
- **E239** `素食者` -> PARTIAL (score=3, conf=MEDIUM, drift=SEVERE) — Rewrite said 'vegetarian food vocabulary, vegan lifestyle' but rank3 'bak kut teh' is a pork-rib soup dish and rank4 'sushi' typically includes fish - both directly contradict a vegetarian audience; Indian cuisine and a farm scene are plausibly vegetarian-adjacent but unconfirmed.
- **E240** `新婚夫妇` -> PARTIAL (score=35, conf=MEDIUM, drift=MODERATE) — Rewrite matched partially: 'marriage newlyweds' and a weddings vocab card are direct hits; Diwali and Hanami festival posters are unrelated specific festivals pulled in by over-broadening; gift-giving traditions is wedding-adjacent.
