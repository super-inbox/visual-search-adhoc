#!/usr/bin/env python3
"""Independent relevance judgments for the Easy Query v2 benchmark, applied using the
SAME LOCKED rubric-v1.1 (scoring.py, unchanged) that was used for the prior 328-query
easy-query evaluations in this project. Evidence: title/template_id/tags/engine-score/
strict-or-relaxed tier from each query's real collected top5 results (no screenshots --
this collection method has none, same disclosed limitation as the prior Run B evaluation).
Zero-result queries are handled directly in the build script (FAIL/score=0/ZERO_RESULT).
"""

JUDGMENTS = {}

def add(vid, labels, drift, intent, note):
    JUDGMENTS[vid] = dict(labels=labels, drift=drift, intent=intent, note=note)

# ---- V001-V044 (batch 1: creative_merch) ----
add("V001", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are 'nostalgic first item' posters (camera/computer/console/music player/TV) -- childhood-nostalgia-adjacent electronics, not literal toys.")
add("V002", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "Identical nostalgic-item results for the English term.")
add("V003", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are manga-artist biography cards (Toriyama, Oda, Shinkai, Kishimoto, Takahashi) -- author profiles, not collectible figures, despite a reasonable rewrite.")
add("V004", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are titled 'chinese figure X' (guofeng-scroll illustrated mythological figures) -- a legitimate 'figure' word-sense (illustrated character), but not the intended collectible-merch product sense.")
add("V006", ["IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "NO",
    "An idiom-learning card and a homograph poster are unrelated; 'Woody & Buzz Toy Story' is toy-adjacent (Toy Story merchandise is commonly plush) but not plush-specific.")
add("V007", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "Single result 'Woody & Buzz Toy Story' -- toy-story characters (dolls/action figures), doll-adjacent.")
add("V008", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY",
    "All 4 are cultural-IP merch mockup sets -- character mascot merchandise, doll-adjacent but not doll-specific.")
add("V009", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are organ-health food-guide infographics (brain/heart/liver/lungs/stomach) -- zero mascot content.")
add("V010", ["RELEVANT"]*5, "NONE", "YES",
    "Alpaca/cat character mascots and 2 explicit brand-IP-mascot-design-board cards (Coca-Cola, Curify's own mascot) -- direct. Striking zh/en asymmetry with 吉祥物 (V009).")
add("V011", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 health-infographic cards are unrelated; an anthropomorphic-animal card and a Marvel-villain MBTI card are character-adjacent but weak.")
add("V012", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 are Journey-to-West character-analysis cards -- direct.")
add("V013", ["IRRELEVANT"]*5, "NONE", "NO",
    "Same kawaii character-persona-card series identified in the prior Run B evaluation for this exact query -- no sticker-format signal.")
add("V014", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 are explicitly 'sticker'-templated food-doodle cards -- direct, matching the prior evaluation's identical finding.")
add("V015", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are cultural-IP merch mockups -- keychain-plausible merch category, not confirmed keychain-specific.")
add("V016", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical merch-mockup results for the English term.")
add("V017", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are pro-athlete stat infographics -- sports-trading-card-like format, a reasonable collectible adjacency.")
add("V018", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are herbal/TCM information cards -- zero collectible content.")
add("V020", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only 'van gogh mystery box' (museum merch, mystery-box concept) is direct; 4 unrelated food-sticker cards fill the rest.")
add("V021", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "'Bruce Lee' biography and 'blockbuster action legends' are weakly action-figure-adjacent; 3 'body movement verbs' stick-figure vocab cards are a wrong-entity word collision on 'figure'.")
add("V022", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "NONE", "NO",
    "4 stick-figure vocab cards are the same word-collision issue; only 'Bruce Lee' is weakly relevant.")
add("V023", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Generic 'bear' character card is teddy-bear-adjacent; 'teddy'/'poodle teddy' are a dog-breed guide (wrong entity -- a real dog, not a plush toy).")
add("V024", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Identical wrong-entity composition for the English term.")
add("V025", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are Journey-to-West book-series cards -- zero capsule-toy content.")
add("V026", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "Single result 'Woody & Buzz Toy Story' -- toy-adjacent but not capsule-toy-specific.")
add("V027", ["RELEVANT"], "MINOR", "YES",
    "Single result 'Gambit' (MBTI-Marvel card format) -- MBTI cards are literally trading-card-style content, direct.")
add("V028", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 are NBA-player MBTI cards -- direct trading-card-style content.")
add("V029", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 are city 'miniature' model cards (Beijing/NY/Paris/Shanghai/Tokyo) -- direct match for '模型'/model.")
add("V030", ["IRRELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only a city-miniature card (Lyon) is model-adjacent; an AI strategy infographic, a systems-architecture diagram, and 2 World Cup fan-outfit posters are unrelated.")
add("V031", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are animation-studio comparison infographics (Ghibli vs Mappa etc.) -- zero statue content.")
add("V032", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only 'Statue of Liberty' is direct; 4 unrelated Journey-to-West character cards fill the rest.")
add("V033", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 museum-gift-merchandise cards are tote-bag-plausible; 3 unrelated food-sticker cards fill the rest.")
add("V034", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 character-merch posters are tote-bag-adjacent; 3 brand-identity-moodboard cards (unrelated businesses) fill the rest.")
add("V035", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "All 5 are cultural-IP merch mockups -- phone-case-plausible, not confirmed.")
add("V036", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical merch-mockup results for the English term.")
add("V037", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are 'historical figure vs' comparison infographics -- zero badge content.")
add("V038", ["IRRELEVANT"]*5, "NONE", "NO", "Identical historical-figure comparison cards for the English term.")
add("V039", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are jewelry-category cards (rings/earrings/pendant) -- jewelry-adjacent but no brooch specifically confirmed.")
add("V041", ["RELEVANT", "RELEVANT"], "MINOR", "YES",
    "Both results explicitly 'fridge-magnet'-templated (city landmark collections) -- direct.")
add("V042", ["RELEVANT", "RELEVANT"], "MINOR", "YES", "Identical fridge-magnet template results for the English term.")
add("V043", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "All 5 are cultural-IP merch mockups -- lanyard-plausible, not confirmed.")

# ---- V044-V082 (batch 2: creative_merch continued) ----
add("V044", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical merch-mockup results for the English term.")
add("V045", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are 'city miniature' landmark cards (Shanghai/Tokyo/Sydney/Rome/Barcelona) -- word collision on 'miniature', wrong entity (cities not character figures).")
add("V046", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only 'Bruce Lee' biography is weakly figure-adjacent; 4 unrelated 'what-if-history' comparison cards fill the rest.")
add("V047", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are fashion-ecommerce/outfit cards (tie/bag/denim/streetwear/vintage fashion) -- wrong category entirely, zero figure/toy content.")
add("V048", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "'van gogh mystery box' and 'Woody & Buzz Toy Story' are collectible/toy-adjacent, not vinyl-toy-specific.")
add("V049", ["IRRELEVANT"]*5, "MODERATE", "NO", "Identical fashion-ecommerce results as V047 -- wrong category.")
add("V050", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "4 celebrity-meme-sticker-merchandise posters and a biography card -- merch/sticker collections of real people, pop-figure-adjacent but not literal collectible figures.")
add("V051", ["IRRELEVANT"]*5, "MODERATE", "NO", "All 5 are unrelated food-sticker-overlay cards.")
add("V052", ["RELEVANT"], "MINOR", "YES", "Single result 'van gogh mystery box' -- direct mystery-box concept match.")
add("V053", ["RELEVANT", "RELEVANT", "RELEVANT"], "NONE", "YES",
    "All 3 results (2 gem-pendant design sheets, 1 fashion-ecommerce 'pendant') are direct.")
add("V054", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are anime wallpaper posters -- word collision ('charming' character vs literal jewelry charm), zero charm/pendant content.")
add("V055", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Cultural-IP merch mockups -- mug-plausible, not confirmed.")
add("V056", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 IP-goods-mockup cards and 2 cat-character emoji-sheet cards -- character merch, mug-plausible.")
add("V057", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Cultural-IP merch mockups -- pillow-plausible, not confirmed.")
add("V058", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "A paper-cutting heritage card, 3 solar-term cards, and a guofeng-scroll card -- completely unrelated cultural content, zero pillow content.")
add("V059", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "2 museum-gift-merchandise cards -- puzzle-plausible (museum shops sell jigsaw puzzles), not confirmed.")
add("V062", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are 'theme color palette card' design references (beach/ocean/flamingo/fish/resort) -- zero building-block content.")
add("V063", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only 'van gogh mystery box' is box-merch-adjacent; 4 unrelated food-sticker cards fill the rest.")
add("V064", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "PARTIALLY",
    "3 results (character-sprite-emoji-sheet x2, original-character-sticker-pack) are direct; 2 sports-equipment product-showcase cards are unrelated. Mechanically blocked from PASS by irrelevant_rate=0.40>0.20.")
add("V065", ["IRRELEVANT"]*5, "MODERATE", "NO", "All 5 are unrelated food-sticker-overlay cards.")
add("V066", ["PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'Simu Wu Ding' and 'Yuewang Goujian Sword' (cultural-relic templates) are direct; a historical-figure comparison, an IP-goods-mockup, and a painters' profile card are relic/figure-adjacent.")
add("V067", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are cultural-relic educational infographics (Dunhuang, terracotta warriors, etc.) -- relic-themed but educational content, not confirmed as sellable museum-shop merchandise.")
add("V068", ["RELEVANT", "RELEVANT", "RELEVANT"], "NONE", "YES",
    "2 city-landmark fridge-magnet cards and a museum-gift-merchandise card -- all literal souvenir merchandise, direct.")
add("V070", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "Same 'chinese figure' guofeng-scroll illustrated-mythological-figure results as V004 -- a legitimate but different sense of 'figure'.")
add("V071", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are anime wallpaper posters -- IP-derivative content, but wallpaper rather than physical merch.")
add("V072", ["RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'busan boogi duck' (gift-box stationery merch) is direct; 4 comic-strip posters (Captain Tsubasa, Looney Tunes, Slam Dunk, Simpsons) are anime/cartoon-adjacent but not merch products.")
add("V073", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "2 IP gift-box stationery-set mockups -- postcard-adjacent, not postcard-specific.")
add("V074", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "Only 'deer travel journal' is postcard/travel-adjacent; 4 unrelated brand-VI-mockup cards (camping, Christmas, bakery, bubble tea) fill the rest.")
add("V075", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 character-analysis cards are unrelated; 2 intangible-heritage cards and an art-evolution card are traditional-art/print-adjacent.")
add("V076", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are 'world landmark vintage info poster' cards -- vintage-illustrated-poster format genuinely resembles an art print, subject (landmarks) is incidental.")
add("V078", ["PARTIALLY_RELEVANT"]*5, "MODERATE", "PARTIALLY",
    "2 whimsical character-figurine cards and 3 MBTI persona cards -- character/figurine-adjacent but not bobblehead-specific; 1777-result flooding case.")
add("V079", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "A DNA-helix education card is unrelated; 4 'word scene' bilingual vocab cards are scene-adjacent (literal 'scene' depictions) but for language learning, not diorama models.")
add("V081", ["IRRELEVANT"]*5, "NONE", "NO",
    "Same kawaii character-persona-card series as V013 -- no sticker-format signal despite explicit sticker request.")
add("V082", ["RELEVANT"]*5, "NONE", "YES",
    "2 character-sprite-emoji-sheet cards and 3 explicitly 'original-character-sticker-pack'-templated cards -- direct.")

# ---- V083-V089 (batch 3: brand_business begins) ----
add("V083", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are city weather/architecture illustration cards -- word collision (标志 read as 'landmark' sense, not 'brand logo' sense), zero logo content.")
add("V084", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are animation-studio comparison infographics -- completely unrelated, zero logo content.")
add("V085", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are character 'battle' comparison cards -- completely unrelated, zero packaging content.")
add("V086", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "All 3 are 'ISTJ vs ENFP package' MBTI-contrast cards -- word collision (personality 'package' concept, not product packaging).")
add("V087", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are herbal/TCM information cards -- unrelated, matches the identical finding from the prior Run B evaluation for this exact template.")
add("V088", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are 'city MBTI' personality-quiz cards -- completely unrelated, zero label content.")
add("V089", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 are regional-alcoholic-drinks infographics (French/Japanese/Korean...) -- drinks come in bottles, but no bottle object specifically confirmed as the visual focus.")

# ---- V090-V139 (batch 4: brand_business continued) ----
add("V090", ["RELEVANT"], "MINOR", "YES", "Single result 'smart hydration water bottle' -- direct.")
add("V091", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "All 5 are Chinese recipe/dish cards -- menu-content-adjacent (dishes that would appear on a menu), same logic as the prior 餐饮/restaurant reasoning.")
add("V092", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical recipe-card results for the English term.")
add("V093", ["IRRELEVANT"]*5, "NONE", "NO", "Same kawaii character-profile-card series -- no business-card-format signal.")
add("V094", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'Microsoft AI Dilemma' comic-strip cards -- completely unrelated, zero business-card content.")
add("V095", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Cultural-IP merch mockups -- box-plausible, not confirmed.")
add("V096", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical merch-mockup results for the English term.")
add("V097", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT"], "MINOR", "PARTIALLY",
    "'espresso coffee beans' (explicit packaging-design template) is direct; 4 other coffee-subject cards are on-topic but not packaging-format-specific.")
add("V098", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "Espresso-bean packaging and a brand-VI coffee mockup are direct; brewing/maker/brand-identity cards are coffee-adjacent but not packaging-specific.")
add("V099", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are meat-cut anatomy-diagram cards -- wrong format entirely, zero restaurant-menu content.")
add("V100", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Same recipe-card composition as V091.")
add("V101", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'smart hydration water bottle' -- a literal bottle but wrong bottle type (water not perfume).")
add("V102", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Identical wrong-bottle-type result for the English term.")
add("V103", ["IRRELEVANT"]*5, "MODERATE", "NO", "All 5 are unrelated food-sticker-overlay cards.")
add("V104", ["IRRELEVANT"]*5, "MODERATE", "NO", "A bedroom-decor card, a posture-comparison card (word collision on 'box'), and 3 unrelated food-sticker cards.")
add("V105", ["RELEVANT"], "MINOR", "YES", "Single result 'matcha powder' (explicit food-product-packaging-design template) -- direct.")
add("V106", ["RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'matcha powder' packaging is direct; a tea-themed IP mockup, a bubble-tea brand card, a tea-collage illustration, and a tea-basics info card are on-topic but not packaging-specific.")
add("V107", ["RELEVANT", "RELEVANT"], "NONE", "YES", "Both results are explicit coffee-bean packaging/label templates -- direct.")
add("V108", ["RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'arabica coffee beans' product-label is direct; 4 other coffee-subject cards (vocab/varieties/history/brewing) are on-topic but not packaging-specific.")
add("V109", ["PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT"], "MINOR", "YES",
    "3 explicit chocolate food-product-packaging-design cards are direct; a lava-cake recipe is chocolate-adjacent; a generic food-sticker card is unrelated.")
add("V110", ["RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "2 explicit chocolate packaging-design cards are direct; a lava-cake recipe is adjacent; 2 unrelated food-sticker cards fill the rest.")
add("V111", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 beauty/skincare cards (products, comparison-infographic with cosmetic-packaging tag, routine guide, baby-care brand, eyemask) -- on-topic but no result confirms skincare-specific packaging as the visual focus.")
add("V112", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Skincare-routine and beauty-skincare-comparison cards are on-topic; 3 'ISTJ vs ENFP package' MBTI cards are a word collision on 'package'.")
add("V113", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "4 beauty/cosmetic-adjacent cards (baby-care brand, beauty products, skincare routine, matcha packaging) are on-topic but not cosmetic-specific; a hairdryer ecommerce card is unrelated.")
add("V114", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "Same composition as V113 for the English term; a hairdryer card is unrelated, 4 beauty-adjacent cards remain.")
add("V115", ["PARTIALLY_RELEVANT", "IRRELEVANT", "RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'White Wine' (wine-variety-intro) is direct; a label-printer card and 2 wrong-product label templates (coffee/cheese) are label-format-adjacent; a generic vocab card is unrelated.")
add("V116", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY",
    "'White Wine' is direct; a label-printer card is format-adjacent; 3 generic bilingual vocab cards are unrelated.")
add("V117", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'Evolution of Snacks' -- snack-subject but not packaging-format.")
add("V118", ["PARTIALLY_RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "'choco chip cookies' packaging-design is direct; a summer-snack promo poster and an evolution-of-snacks card are on-topic; 2 vocab-flashcards are unrelated.")
add("V119", ["RELEVANT"], "MINOR", "YES", "Single result 'busan boogi duck' -- explicit gift-box-stationery-set-mockup template, direct.")
add("V120", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Cultural-IP merch mockups -- gift-box-plausible, not as directly confirmed as V119.")
add("V121", ["RELEVANT"], "MINOR", "YES", "Single result 'bag' (fashion-ecommerce) -- a generic bag, shopping-bag-adjacent, direct.")
add("V122", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are 'brand identity moodboard visual system poster' cards (coffee shop/bakery/grocery/bookstore/pet store brands) -- wrong specific object, no shopping bag depicted.")
add("V123", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicitly 'bilingual object structure labeling' templated -- direct format match.")
add("V124", ["RELEVANT"]*5, "NONE", "YES", "Identical labeling-template results for the English term.")
add("V126", ["RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "3 bakery-brand cards (mika cat bakery, Golden Crust VI, temp bakery) are direct; 2 unrelated fashion-ecommerce cards fill the rest. Mechanically blocked from PASS by irrelevant_rate=0.40>0.20.")
add("V128", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "2863-result flooding case. Cafe-ordering dialogue scenes, a cafe-themed artifact poster, a cafe brand-identity card, and a travel-infographic -- cafe-adjacent but no literal menu depiction confirmed.")
add("V129", ["IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "4 results. A generic vocab card and an ASL-tutorial card (word collision on 'sign') are unrelated; 2 shop-brand-identity cards are signage-adjacent.")
add("V130", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 brand-identity-moodboard cards -- brand-asset-adjacent, not literal storefront signage.")
add("V131", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "3 'PAW PARADISE' brand-identity cards are signage-adjacent; a generic vocab card and an ASL-tutorial card are unrelated.")
add("V132", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "An ASL-tutorial card (word collision), a Meta-layoffs corporate-news card, and 3 unrelated fashion-ecommerce cards -- zero storefront-sign content.")
add("V133", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 brand-VI-full-visual-pack-mockup cards -- brand-asset-adjacent, tag not specifically confirmed.")
add("V134", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicitly 'product-label'-templated -- direct format match for 'product tag'.")
add("V135", ["PARTIALLY_RELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "A shopping dialogue scene and 3 object-structure-labeling cards are price-tag-adjacent (generic labeling, not price-specific); a logistics word-scene is unrelated.")
add("V137", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "4 dynasty-costume cards and a jeans-ecommerce card -- clothing-subject but no tag/label object confirmed.")
add("V138", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Similar costume/fashion composition as V137 for the English term.")
add("V139", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "3 jewelry-category cards are on-topic but no box confirmed; 2 unrelated food-sticker cards fill the rest.")
add("V140", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Jewelry/pendant-design cards are on-topic but no box object confirmed.")

# ---- V141-V193 (batch 5: brand_business tail + marketing_ecommerce) ----
add("V141", ["IRRELEVANT"]*5, "NONE", "NO", "5 generic 'product poster' cards (diffuser/speaker/coffee-maker/lamp/label-printer) -- no candle, no label content.")
add("V142", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "A label-printer card and 4 explicit eco-farm product-label cards -- label-format matches but wrong product category (food, not candle).")
add("V143", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "A cultural-fusion 'soap dish' mockup is weakly on-topic; 4 fashion-ecommerce cards (eyemask/instrument/pendant/ring) are wrong products entirely.")
add("V144", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "Soap-dish mockup and a label-printer card are weakly on-topic; 3 unrelated food-sticker-overlay cards fill the rest.")
add("V146", ["PARTIALLY_RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "3 results. 'matcha powder' packaging-design is direct; a tea-themed IP mockup and a bubble-tea brand card are tea-adjacent, not tea-box-specific.")
add("V147", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "NO",
    "A coffee-pasta sticker card is weakly coffee-adjacent; 4 World Cup team sticker-poster cards are a word collision on 'cup' (World Cup, not coffee cup).")
add("V148", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 coffee-subject cards (doodle/vocab/equipment-labeling/history/brewing-guide) -- on-topic but no literal cup object confirmed.")
add("V149", ["IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Stadium/social-change/landmark-map cards are unrelated; 2 coffee-subject cards are weakly on-topic, no sleeve object confirmed.")
add("V150", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 coffee-subject cards -- on-topic but no cup-sleeve object confirmed.")
add("V151", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 food-doodle-sticker cards (brunch/pasta/korean/thai/western) -- food-subject but no takeout container depicted.")
add("V152", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical food-sticker composition for the English term.")
add("V154", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'smart hydration water bottle' is a direct hit, but is outweighed by a waterpark word-scene card and 3 unrelated Chinese recipe cards (irrelevant_rate=0.80).")
add("V155", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "Water-bottle infographic is direct; an 'aquarius' constellation card (word collision) and a logistics card are unrelated; 2 object-labeling cards are label-format-adjacent but wrong product.")
add("V156", ["RELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "Water-bottle infographic is direct; a waterpark card is unrelated; a label-printer card and 2 vintage fruit-label cards are label-format-adjacent but wrong product. Meets PASS band (irrelevant_rate=0.20).")
add("V157", ["RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "2 results. 'Koi Fish Red Envelopes' is a direct envelope-template hit; a post-office dialogue scene is envelope-context-adjacent.")
add("V158", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit red-envelope-set templates -- direct.")
add("V159", ["IRRELEVANT"]*5, "NONE", "NO", "5 food-doodle-sticker cards -- no bag object depicted.")
add("V160", ["RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Generic 'bag' ecommerce card is direct; an IP merch-collection card is bag-plausible but unconfirmed; 3 food-sticker cards are unrelated.")
add("V161", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "A lava-cake recipe card is cake-adjacent; 4 unrelated food-sticker-overlay cards fill the rest.")
add("V162", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "Cake-labeling, lava-cake recipe, cake-varieties, and baking-guide cards are cake-topic-adjacent; a generic brunch-sticker card is unrelated.")
add("V163", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "A mid-autumn-festival vocab card is weakly culture-adjacent; 4 unrelated food-sticker cards fill the rest.")
add("V164", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "A festival-merch dragon mockup is weakly on-topic; 4 unrelated World Cup team sticker-poster cards fill the rest.")
add("V165", ["IRRELEVANT"]*5, "NONE", "NO", "5 'lifestyle watercolor infographic' wellness cards (habits/mindfulness/morning routine/productivity/self-care) -- wrong format entirely, no banner content.")
add("V166", ["IRRELEVANT"]*5, "NONE", "NO", "Identical wellness-infographic results for the English term.")
add("V167", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'fifa world cup 2026 opening ceremony' (explicit flyer-poster template) is direct; architecture/weather/word-scene/cultural-relic cards are unrelated.")
add("V168", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Same flyer-poster template hit is direct; 4 ballroom-dance-step tutorial cards are wrong format entirely.")
add("V169", ["IRRELEVANT"]*5, "NONE", "NO", "5 fashion-outfit-variation lookbook cards -- wrong format, not a catalog/album layout.")
add("V170", ["RELEVANT", "RELEVANT"], "NONE", "YES", "Both results are 'museum gift merchandise collection display' cards -- direct catalog-format match.")
add("V171", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'product theme promotional poster' templates -- direct promotional-banner-intent match.")
add("V172", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Marvel MBTI character cards are unrelated; 2 promotional-poster cards (baby care brand, spring beauty festival) are direct sale-banner-format hits.")
add("V173", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated hot-event-analysis / AI-dilemma-comic infographic cards -- no product photo content.")
add("V174", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 'gardening how-to infographic' cards (bell peppers/carrots/lettuce/pineapple/strawberries) -- real product/food photos but wrong context (gardening guide, not ecommerce product photo).")
add("V175", ["RELEVANT"]*5, "NONE", "YES", "Same explicit promotional-poster templates as V171 -- direct.")
add("V176", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'Journey to the West' book-series cards -- completely unrelated, no promotional content.")
add("V177", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 generic 'product poster' showcase cards -- product-showcase-adjacent but ad-format not confirmed.")
add("V179", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'MBTI Naruto' anime character cards -- no social-media-post format, unrelated content.")
add("V180", ["IRRELEVANT"]*5, "NONE", "NO", "A 'chinese social changes' card is a word collision on 'social'; 4 'Journey to the West' book-series cards are unrelated.")
add("V181", ["IRRELEVANT"]*5, "NONE", "NO", "5 'evolution' history-infographic cards (industrial revolution/art/social changes/currency/transportation) -- no product-display format.")
add("V182", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'fashion ecommerce' mockup cards -- direct product-display format match.")
add("V183", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 restaurant/cafe-adjacent cards (sauce packaging, brand mockup, ordering dialogue, coffee cards) -- topic-adjacent, no flyer format confirmed.")
add("V184", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 restaurant-ordering-dialogue and food-packaging cards -- restaurant-topic-adjacent, no flyer format confirmed.")
add("V185", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'movie poster' templates -- direct.")
add("V186", ["RELEVANT"]*5, "NONE", "YES", "Identical movie-poster results for the English term.")
add("V187", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated 'travel packing guide infographic' cards -- no product/banner content.")
add("V188", ["IRRELEVANT"]*5, "NONE", "NO", "Identical travel-packing-guide results for the English term.")
add("V189", ["RELEVANT"]*5, "NONE", "YES", "Same explicit 'product theme promotional poster' templates as V171 -- direct.")
add("V190", ["RELEVANT"]*5, "NONE", "YES", "Identical promotional-poster results for the English term.")
add("V191", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'supermarket' dialogue scene -- shopping-context-adjacent, no flyer depicted.")
add("V192", ["PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "The flyer-poster template matches format but wrong subject; 2 sale-promotional-poster cards are direct discount-content hits; 2 city/landmark cards are unrelated.")
add("V193", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'red envelope set' festival cards -- unrelated to ecommerce banners.")

# ---- V194-V248 (batch 6: marketing_ecommerce tail + education start) ----
add("V194", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'amazon long-scroll product infographic' templates -- direct ecommerce-banner-format match.")
add("V195", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "A 'product thinker' MBTI meme card is a word collision on 'product'; 4 fashion-ecommerce mockup cards are product-showcase-adjacent, catalog-plausible.")
add("V196", ["RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "2 museum-merchandise-collection-display cards are direct catalog-format hits; 3 product-showcase cards are on-topic but not catalog-layout-specific.")
add("V197", ["RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT"], "MINOR", "YES",
    "World Cup flyer-poster and Beijing art-season promotional-poster are direct event-flyer hits; 3 other event-themed cards are on-topic but format-weaker.")
add("V198", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "The explicit flyer-poster template is direct; 4 unrelated ballroom-dance-tutorial cards dominate (irrelevant_rate=0.80).")
add("V199", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 Canada World Cup squad photos are unrelated; 2 promotional-poster cards are opening-promo-adjacent.")
add("V200", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Canada squad photos and a manga-artist card are unrelated; the flyer-poster template is event-format-adjacent but wrong subject (irrelevant_rate=0.80).")
add("V201", ["PARTIALLY_RELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "A Christmas word-scene and 3 cultural-festival-poster cards (Day of the Dead/Diwali/Duanwu) are festival-adjacent; a 'music festival' MBTI card is a word collision on 'festival'.")
add("V202", ["RELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'summer beach sale' promotional-poster is direct; a 'roman holiday' movie poster is a word collision on 'holiday'; a Christmas-party brand mockup is weakly on-topic; 2 unrelated character/celebrity cards fill the rest.")
add("V203", ["RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT"], "MINOR", "YES",
    "4 explicit 'product theme promotional poster' cards are direct new-product-banner hits; a New Zealand World Cup squad photo is unrelated.")
add("V204", ["RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT"], "MINOR", "YES", "Same composition as V203 for the English term.")
add("V205", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'tech gadget sale' promotional-poster is direct; 4 unrelated history/culture-infographic cards dominate (irrelevant_rate=0.80).")
add("V206", ["RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 explicit sale-promotional-poster cards are direct; 3 world-landmark vintage-info-poster cards (colosseum/eiffel/great wall) are unrelated.")
add("V207", ["RELEVANT", "RELEVANT", "IRRELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "YES",
    "4 explicit sale-promotional-poster cards are direct; an 'ikaris' MBTI-marvel card is unrelated.")
add("V208", ["RELEVANT", "RELEVANT", "IRRELEVANT"], "MINOR", "YES",
    "3 results. 2 sale-promotional-poster cards are direct; a manga-artist infographic card is unrelated.")
add("V209", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'amazon long-scroll product infographic' templates -- direct product-detail-page format match.")
add("V210", ["RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT"], "MINOR", "YES",
    "Watch/cycling-computer/eyemask ecommerce-product cards are direct; a drone concept-sketch and a jewelry before-after card are product-adjacent but not listing-photo-format.")
add("V211", ["PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "YES",
    "4 explicit promotional-poster cards are direct online-store-banner hits; a jeans-ecommerce card is weakly on-topic.")
add("V212", ["RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES", "Same composition as V211 for the English term.")
add("V213", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated word-scene/MBTI-animal cards (party/amusement-park/cafe/plane) -- no social-media-ad content.")
add("V214", ["IRRELEVANT"]*5, "NONE", "NO", "Same 'social changes'/'Journey to the West' composition as V180 -- unrelated.")
add("V215", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 fashion-ecommerce product-mockup cards -- product-showcase-adjacent, recommendation-post format not confirmed.")
add("V216", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical fashion-ecommerce composition for 'influencer post'.")
add("V217", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'portrait retouching blueprint' before-after cards -- unrelated to unboxing.")
add("V218", ["IRRELEVANT"]*5, "NONE", "NO", "A Colombia World Cup squad photo and 4 portrait-retouching-blueprint cards -- unrelated to unboxing.")
add("V219", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'portrait retouching blueprint' before-and-after cards -- direct format match.")
add("V220", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'home organization before-after' / 'fashion before-after' cards -- direct.")
add("V223", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated cards (cartoon character, hot-event-analysis, intangible-heritage) -- no membership-card format.")
add("V224", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated hot-event-analysis / intangible-heritage / weather cards.")
add("V225", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated 'education-card' / 'species-science' cards (DNA helix, plate tectonics, egret, ginkgo, baiji) -- word collision on template naming 'card', content unrelated.")
add("V226", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated cartoon-character / education-card / herbal cards.")
add("V227", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated 'science myth-bust infographic' cards.")
add("V228", ["IRRELEVANT"]*5, "NONE", "NO", "2 sports-equipment flashcard cards (word collision on 'card') and 3 classical-painting-analysis cards -- all unrelated to gift cards.")
add("V229", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 shop/pet-brand-identity and team-banner cards -- brand/banner-format-adjacent, storefront not confirmed.")
add("V230", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY", "4 results. Explicit promotional-poster cards -- promo-banner-format-adjacent, storefront not confirmed.")
add("V231", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "4 celebrity-meme-merchandise-collection-poster cards (Tate/Ronaldo/Musk/Haaland) are unrelated; an 'At the Museum' word-scene card is display-context-adjacent (weak).")
add("V232", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "A generic vocab card is unrelated; shop-brand and product-poster cards are display-context-adjacent, window-display not confirmed.")
add("V234", ["IRRELEVANT"]*5, "NONE", "NO", "'The Truman Show' and 'show villains' are word collisions on 'show'; 3 AI-outfit-try-on cards are unrelated fashion content.")
add("V235", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'At the Museum' word-scene -- exhibition-context-adjacent, no flyer depicted.")
add("V236", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "The flyer-poster template matches format but wrong subject; 4 world-landmark vintage-info-poster cards are exhibition/travel-adjacent, weak.")
add("V237", ["IRRELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "YES",
    "4 explicit promotional-poster cards are direct product-launch-poster hits; a 'new year' word-scene card is a word collision on 'new'.")
add("V238", ["RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "IRRELEVANT"], "MINOR", "YES",
    "4 explicit promotional-poster cards are direct; a Christmas word-scene card is unrelated.")
add("V239", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'product theme promotional poster' templates -- direct.")
add("V240", ["RELEVANT"], "NONE", "YES", "Single result 'summer beach sale' promotional-poster -- direct.")
add("V241", ["IRRELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY",
    "'marvel blackwidow.jp' is a word collision on 'black'; 2 sale-promotional-poster cards are direct; 2 unrelated MBTI-marvel cards fill the rest.")
add("V242", ["IRRELEVANT"]*5, "NONE", "NO", "'marvel blackwidow.jp' is a word collision on 'black'; 4 unrelated fashion/outfit cards fill the rest.")
add("V243", ["RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 sale-promotional-poster cards are direct; 3 Chinese-character-learning-poster cards are a word collision on 'poster' (learning poster, not sale poster).")
add("V244", ["RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 sale-promotional-poster cards are direct; 3 world-landmark vintage-info-poster cards are unrelated.")
add("V246", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Marvel/MBTI cards are unrelated; 2 promotional-poster cards are livestream-promo-adjacent.")
add("V247", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'phonics consonant blend' flashcard templates -- direct.")
add("V248", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit vocabulary/action-learning flashcard templates -- direct.")

# ---- V249-V310 (batch 7: education body) ----
add("V249", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "YES",
    "2 explicit 'kids theme fill-in-worksheet' cards are direct; 3 vocabulary flashcard cards are learning-material-adjacent but not worksheet-format.")
add("V250", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'kids theme fill-in-worksheet' templates -- direct.")
add("V251", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit phonics-consonant-blend letter cards -- direct alphabet-card format match.")
add("V252", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 general vocabulary/learning-card templates -- card-format matches but none show letters/alphabet specifically.")
add("V253", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 travel-itinerary cards are map-adjacent; 2 word-scene dialogue cards (child park, zootopia) show no map content.")
add("V254", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Identical composition for the English term.")
add("V255", ["IRRELEVANT"]*5, "NONE", "NO", "4 Chinese recipe cards and a solar-term card -- no diagram/illustrated-guide format.")
add("V256", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "A cartoon-character card and 2 herbal cards are unrelated; 2 hot-event-analysis infographic cards are diagram-format-adjacent.")
add("V257", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY",
    "4 international-event-promotional-poster cards (World Cup/Olympics/Asian Games/Coachella) are a word-sense mismatch (event calendar, not a calendar object); the explicit 'annual event calendar infographic' card is direct.")
add("V258", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY", "Identical composition for the English term.")
add("V261", ["RELEVANT"]*5, "NONE", "YES", "All 5 are herbal-science education cards -- direct science-content match.")
add("V262", ["RELEVANT", "RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 herbal-science cards are direct; 3 city-weather-illustration cards are unrelated.")
add("V263", ["RELEVANT"]*5, "NONE", "YES", "5 'historical figure educational' portrait cards (artists/composers/philosophers/scientists/writers) -- classic classroom-decoration educational posters, direct topical fit.")
add("V264", ["RELEVANT"]*5, "NONE", "YES", "5 'evolution' history-infographic cards -- classic classroom educational posters, direct topical fit.")
add("V265", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 historical-figure educational portrait cards -- textbook-content-adjacent, not a literal textbook page/cover.")
add("V266", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical composition for the English term.")
add("V268", ["IRRELEVANT"]*5, "NONE", "NO", "A solar-term card, a pizza card, and 3 unrelated 'leader' MBTI-generic character cards -- no globe content.")
add("V269", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT"], "NONE", "PARTIALLY",
    "3 species-infographic cards (baiji/panda/tiger) are chart-format-adjacent; 2 city-miniature cards show no chart content.")
add("V270", ["IRRELEVANT"]*5, "NONE", "NO", "4 'Journey to the West' character-analysis cards and an architecture card -- no chart format.")
add("V272", ["RELEVANT"], "NONE", "YES", "Single result 'school timetable' (explicit vocab-flashcard-with-timetable-content template) -- direct.")
add("V273", ["IRRELEVANT"]*5, "NONE", "NO", "5 'fashion-inspired gown design sheet' cards -- a word-sense mismatch (表=chart vs. fashion 'sheet'), unrelated content.")
add("V274", ["IRRELEVANT"]*5, "NONE", "NO", "5 'pop-culture matching chart' cards (Ghibli/Harry Potter/Pokemon zodiac) -- word collision on 'chart' template naming, content is character-matching not numbers.")
add("V275", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'MBTI Breaking Bad' character cards -- completely unrelated.")
add("V276", ["IRRELEVANT"]*5, "NONE", "NO", "Identical composition for the English term.")
add("V277", ["RELEVANT"]*5, "NONE", "YES", "4 explicit 'word origins map infographic' cards and a watercolor world-map card -- direct.")
add("V278", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'world travel map illustration' templates -- direct.")
add("V279", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'CVC English word coloring flower card' (phonics) templates -- direct.")
add("V280", ["RELEVANT"]*5, "NONE", "YES", "Identical phonics-card results for the English term.")
add("V282", ["RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'ielts synonym vocab' (exam-vocabulary template) is direct; 4 unrelated intangible-heritage cultural cards dominate (irrelevant_rate=0.80).")
add("V284", ["IRRELEVANT"]*5, "NONE", "NO",
    "5 'education-card' science-topic cards (DNA helix/plate tectonics/resource capacity/electromagnetic induction/energy conservation) -- word collision on generic 'card' template naming, no report-card/grade content.")
add("V286", ["IRRELEVANT", "IRRELEVANT"], "NONE", "NO", "2 results. 'Microsoft AI dilemma...case Google Gemini' cards -- word collision on 'case' (AI use-case, not pencil case).")
add("V287", ["IRRELEVANT"]*5, "NONE", "NO", "Same generic 'education-card' science-topic composition as V284 -- no blackboard depicted.")
add("V288", ["IRRELEVANT"]*5, "NONE", "NO", "Identical composition for 'chalkboard'.")
add("V291", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated cards (city weather, pizza, TCM herbs, sci-fi book grid) -- no microscope content.")
add("V294", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 fashion-ecommerce product cards (socks/watch/shoes) are wrong products; 2 library-context cards are weakly bookmark-adjacent.")
add("V295", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated cards (character-analysis, intangible-heritage, architecture) -- no abacus content.")
add("V296", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'en-ko' vocabulary card with a numbers-and-counting tag -- numbers-adjacent, no abacus depicted.")
add("V297", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 IP-merch-mockup-set / gift-box-stationery-set cards -- generic merch mockups, notebook not specifically confirmed.")
add("V299", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'vocabulary' flashcard templates -- direct.")
add("V300", ["RELEVANT"]*5, "NONE", "YES", "Identical vocabulary-card results for the English term.")
add("V301", ["RELEVANT", "RELEVANT", "RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "4 explicit 'children English vocab spelling' cards are direct; a word-difference infographic is spelling-adjacent.")
add("V302", ["IRRELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "A 'sushi' character card is unrelated; 4 bilingual word-scene cards are vocab-adjacent but not spelling-card format.")
add("V303", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 numbers/counting-tagged vocabulary cards -- math-adjacent but not confirmed workbook format.")
add("V304", ["IRRELEVANT"]*5, "NONE", "NO", "5 general-vocabulary cards (animals/desserts/colors/family/food) -- worksheet format matched but zero math content.")
add("V305", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT", "RELEVANT"], "MINOR", "YES",
    "2 book-recommendation-grid cards are direct reading-content hits; 3 library-context cards are reading-adjacent.")
add("V306", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 'kids theme fill-in-worksheet' cards -- worksheet-format matches but no reading-specific content confirmed.")
add("V307", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'science myth-bust infographic' cards -- direct.")
add("V308", ["RELEVANT"]*5, "NONE", "YES", "All 5 are herbal-science education cards -- direct.")
add("V309", ["RELEVANT", "RELEVANT", "RELEVANT"], "NONE", "YES", "3 results, all explicit 'human body' labeling/education-card/mindmap templates -- direct.")
add("V310", ["IRRELEVANT"]*5, "NONE", "NO", "4 architecture-infographic cards (word collision on 'anatomy' tag, content is buildings) and a constellation card -- no body-anatomy content.")

# ---- V311-V326 (batch 8: education tail, final) ----
add("V311", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 species-science info-cards (egret/ginkgo/baiji/panda/tiger) -- animal-topic matches but format is species-info-card, not confirmed literacy-flashcard.")
add("V312", ["PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'dog' (detailed-vocab-flashcard) is a direct animal-flashcard hit; apple/book/high-speed-rail/timetable share the flashcard format but wrong (non-animal) topic.")
add("V313", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit phonics-consonant-blend letter cards -- direct alphabet-poster format match.")
add("V314", ["PARTIALLY_RELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT"], "MODERATE", "PARTIALLY",
    "A chemistry cheat-sheet poster is educational-poster-format-adjacent; architecture/Christmas/cultural-relic/solar-term cards are unrelated (irrelevant_rate=0.80).")
add("V318", ["PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Single result 'graduation alpaca' character-sprite sheet -- graduation-theme-adjacent, not a diploma document.")
add("V320", ["RELEVANT"]*4, "NONE", "YES", "4 results, all explicit 'annual event calendar infographic' templates -- direct.")
add("V321", ["RELEVANT"]*5, "NONE", "YES", "5 'watercolor world map illustration' continent cards -- classic classroom wall-decor maps, direct topical fit.")
add("V322", ["RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT", "PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'composers' historical-figure-educational card is a direct classroom-decor hit; 4 other learning-card/comparison-poster cards are educational-content-adjacent.")
add("V323", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit 'Chinese verb opposite infographic' learning-chart templates -- direct.")
add("V324", ["IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "IRRELEVANT", "RELEVANT"], "MODERATE", "PARTIALLY",
    "4 architecture-infographic cards are off-topic despite a 'learning' tag; 'action words' (verb-opposite-infographic) is the one direct learning-chart hit.")
add("V325", ["IRRELEVANT"]*5, "NONE", "NO",
    "All 5 are 'food photo doodle sticker overlay' cards -- word collision on 贴纸/sticker (food stickers, not reward-chart stickers).")
add("V326", ["IRRELEVANT"]*5, "NONE", "NO", "All 5 are 'brand identity moodboard visual system poster' cards -- completely unrelated to a reward chart.")
