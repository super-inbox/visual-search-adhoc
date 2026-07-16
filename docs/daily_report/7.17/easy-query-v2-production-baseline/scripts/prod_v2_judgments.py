JUDGMENTS = {}
def add(vid, labels, drift, intent, note):
    JUDGMENTS[vid] = dict(labels=labels, drift=drift, intent=intent, note=note)

# ---- V001-V053 (batch 1) ----
add("V001", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "camera/computer/game console are 'nostalgic first item' electronics (toy-adjacent childhood items); badminton/basketball are sports gear, unrelated.")
add("V002", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY", "Identical results for English term.")
add("V003", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "4 results (low-result). Tang-horse figurine and 3 'modernized artifact' 3D chibi/diorama/keycap templates -- figurine/diorama concept genuinely close to '手办', though not literal action-figure product shots.")
add("V004", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 'chinese figure' illustrated mythological-figure cards (legitimate but different 'figure' word-sense) are weak matches; 2 body-movement-verb vocab cards are unrelated.")
add("V005", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'woody buzz toy story' is plush-merchandise-adjacent; socks/watch/shoes/forest-botanicals are unrelated fashion/nature ecommerce cards.")
add("V006", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "4 results (low-result). None show plush toys -- generic phrase card, idiom flashcard, homograph poster, all unrelated.")
add("V007", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'woody buzz toy story' and a phonics card showing 'doll' as a vocabulary item are doll-adjacent; 3 IP gift-box/stationery mockup templates are generic merch, not doll-specific.")
add("V008", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "5 IP character/mascot merchandise cards (busan boogi duck, curi ai robot set, boogi alpaca) plus a phonics 'doll' vocab card and a gift-box mockup -- character-merch-adjacent, no literal doll product shots.")
add("V009", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "brain/heart/liver are organ-health infographics, same failure mode observed on the candidate branch; graduation alpaca and empress cow cat are actual mascot-character cards.")
add("V010", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "graduation alpaca / empress cow cat / vietnamese orange cat are direct mascot characters; coca cola fizz is a brand mascot too (partially relevant); 'curify ai curi' is the product's own mascot, borderline meta but on-topic.")
add("V011", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "covid-anxiety/sleep-disorder/sugar-free health infographics are unrelated; carnage and adventurer-max are illustrated cartoon characters, on-topic.")
add("V012", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 results all titled 'Kpop Idol Profile Vintage Passport Poster' (likely a UI display quirk repeating the top title) across different template slugs (world-cup poster, football sticker set, anime-crew infographic, mbti-nba) -- all illustrated-character-adjacent but not a clean 'character' concept match.")
add("V013", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "adventurer/artist/athlete are illustrated character-profile cards (sticker-adjacent); brunch/coffee-pasta are food-doodle-sticker cards, off-topic content though same 'sticker' template family.")
add("V014", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "NO",
    "brunch/coffee-pasta/korean food stickers and World Cup team sticker posters -- template family matches 'sticker' but none show a generic/reusable sticker product, all narrow food or sports themes.")
add("V015", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 IP-character mascot cards (blessing dragon, bronze rabbit, deer travel journal, busan boogi duck, nicoco) -- character-merch-adjacent, keychain not specifically confirmed.")
add("V016", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical results for English term.")
add("V017", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated athlete-portrait cards (Phelps/Djokovic/Curry/Iverson/Ginobili) -- sports biography content, no collectible-object depiction.")
add("V018", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated herbal/solar-term science cards -- word collision on template naming, zero collectible content.")
add("V019", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MINOR", "PARTIALLY",
    "van gogh mystery box, blessing dragon, and bronze-beast merch collection are blind-box/mystery-box-adjacent; lifting box (posture comparison, word collision on 'box') and brunch sticker are unrelated.")
add("V020", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "van gogh mystery box is on-topic; lifting-box (word collision) and 3 food-sticker cards are unrelated.")
add("V021", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "5 unrelated historical/celebrity biography portraits (Bruce Lee, Steve Jobs, Freud, Mozart, Warhol) -- zero action-figure content despite the rewrite banner mentioning 'figurine collection'.")
add("V022", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 body-movement-verb vocab cards show stick-figure action poses (action-figure-adjacent, weak); Bruce Lee portrait and a historical-figure-biography template are action/figure-adjacent but not product shots.")
add("V023", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "bear/panda are teddy-bear-adjacent; 'teddy' and 'poodle teddy' are direct teddy-bear illustration hits; IP character design sheet is merch-adjacent.")
add("V024", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT","IRRELEVANT"], "MINOR", "YES",
    "panda/bear teddy-adjacent, 'teddy'/'poodle teddy' direct hits, octopus unrelated.")
add("V025", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 generic action-vocabulary cards (hobbies/outdoor/physical actions) are unrelated; van gogh mystery box and toy-story woody/buzz are gachapon/blind-box-adjacent.")
add("V026", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated fashion-ecommerce/nature cards (socks/watch/shoes/botanicals/birds) -- zero capsule-toy content.")
add("V027", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "5 unrelated MBTI/video-game-character cards (Genshin Impact, Gambit) -- character-card concept but not a physical trading-card product depiction.")
add("V028", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 basketball-star portrait cards (Durant/Bryant/James) are sports-trading-card-adjacent; 2 sports-equipment segment cards are unrelated.")
add("V029", ["IRRELEVANT"]*5, "MODERATE", "NO", "5 unrelated city-travel cards (Beijing/NY/Paris/Egypt/France) -- word collision, no model-kit content.")
add("V030", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated business-strategy/travel/AI-job cards -- rewrite drifted completely off-topic, zero model-kit content.")
add("V031", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "4 results (low-result). Anime-studio-comparison infographic cards ('ghibli vs mappa' etc) -- recurring noise template, zero statue content.")
add("V032", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'statue of liberty' is a direct hit; socks/watch/outfit-styling/art-styles are unrelated fashion cards.")
add("V033", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "van gogh merch mockups are tote-bag-plausible; 3 food-sticker cards are unrelated.")
add("V034", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "IP character card and 3 brand-identity-moodboard posters -- brand-merch-adjacent, no literal tote bag depicted.")
add("V035", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "NONE", "PARTIALLY",
    "4 results (low-result). 3 IP character mockups are merch-adjacent; explicit 'IP Cultural & Stationery Merchandise Mockup' template is the closest direct hit for a phone-case-style product mockup.")
add("V036", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 IP character mockups are merch-adjacent; 2 celebrity-meme-merch cards are unrelated to phone cases specifically.")
add("V037", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "NO",
    "3 historical-figure-vs-infographic cards and 2 generic product-poster cards (diffuser/speaker) -- zero badge/pin content.")
add("V038", ["IRRELEVANT"]*5, "MODERATE", "NO", "Identical composition for English term.")
add("V039", ["RELEVANT","RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "diamond/emerald jewelry and 'Jewelry Look' are direct brooch/jewelry hits; earrings and qing-dynasty-costume cards are jewelry-adjacent.")
add("V040", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for 'enamel pin' (English) despite Chinese pair returning results -- bilingual asymmetry / catalog gap for this specific English phrasing.")
add("V041", ["IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "landmark-city cards are unrelated (word collision); 'morning routine' and 'kitchen' are weakly fridge/kitchen-adjacent, no literal magnet depicted.")
add("V042", ["IRRELEVANT","IRRELEVANT","RELEVANT"], "MINOR", "PARTIALLY",
    "3 results (low-result). 2 landmark-city cards are unrelated; explicit 'City Landmark Fridge Magnet Collection' template is a direct hit.")
add("V043", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "4 results (low-result). IP character/stationery merch mockups -- merch-adjacent, lanyard not specifically confirmed.")
add("V044", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY", "Identical composition for English term.")
add("V045", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated city-travel/yoga-studio cards -- word collision on 'mini/miniature' as city-scale, zero mini-figure content.")
add("V046", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated footballer-portrait/business/dinosaur cards -- rewrite drifted completely off-topic.")
add("V047", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "Tang-horse figurine and 4 'modernized artifact' 3D chibi/diorama templates -- figurine/diorama concept adjacent to trendy collectible figures.")
add("V048", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "3 footballer portraits are unrelated; Bruce Lee is action-figure-adjacent (weak); byzantine/tang is unrelated historical content.")
add("V049", ["PARTIALLY_RELEVANT"]*5, "MINOR", "PARTIALLY", "Same figurine/diorama composition as V047.")
add("V050", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 celebrity-meme-merch cards and the explicit celebrity-meme-merchandise template are pop-figure-adjacent; michael jackson portrait is weak.")
add("V051", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated food-sticker/World-Cup cards -- rewrite drifted off-topic, zero surprise-box content.")
add("V052", ["RELEVANT","RELEVANT"], "NONE", "YES", "2 results (low-result). van gogh mystery box and the explicit museum-gift-merchandise-display template are direct mystery-box hits.")
add("V053", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "3 results (low-result). 'pendant' is a direct charm/pendant hit; 2 ornate-pendant-design-sheet cards are jewelry-adjacent.")

# ---- V054-V100 (batch 2) ----
add("V054", ["IRRELEVANT"]*4, "SEVERE", "NO",
    "4 results (low-result). 'friends' unrelated; Ghibli movie posters (word collision on 'charming'); wallpaper-poster template unrelated -- matches the 'charming character' collision found on the candidate branch.")
add("V055", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 IP character/museum merch mockups -- merch-adjacent, no literal mug depicted.")
add("V056", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'Office stationery... coffee mug...' explicitly depicts a mug -- direct; 4 unrelated food-sticker/World-Cup cards.")
add("V057", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 IP character merch mockups -- merch-adjacent, no pillow specifically confirmed.")
add("V058", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated Chinese-culture/solar-term cards -- rewrite drifted off-topic, zero pillow content.")
add("V059", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "van gogh merch mockups are jigsaw/museum-merch-adjacent (weak); Journey-to-the-West character cards and Crayon Shinchan are unrelated.")
add("V060", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated infographic/travel cards -- rewrite drifted completely off-topic.")
add("V061", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "SEVERE", "NO",
    "Empire State Building and 'blood building foods' are word collisions on 'building'; Meta-layoffs cardboard-box card is weakly box-adjacent; woody/buzz toy story is toy-adjacent.")
add("V062", ["IRRELEVANT"]*4, "SEVERE", "NO", "4 results (low-result). Unrelated ocean-animal cards and a color-palette template -- zero building-block content.")
add("V063", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "van gogh mystery box is box-adjacent; lifting-box (word collision) and 3 food-sticker cards are unrelated.")
add("V064", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "graduation-alpaca character and curi-ai-robot icon set are sticker/icon-adjacent; 2 sports-equipment cards are unrelated; bronze-worker-mythical-beast character is sticker-adjacent.")
add("V065", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "blessing-dragon IP figure is figurine-adjacent; 4 unrelated Chinese-dish recipe cards.")
add("V066", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 historical-figure portrait cards (Cleopatra/Himiko, Confucius, Han dynasty, painters, architects) -- cultural-figure-adjacent, but portraits/biography content rather than a relic/figurine object.")
add("V067", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "Dunhuang grottoes and 2 bronze-artifact cards are direct museum-relic hits; blessing dragon and bronze rabbit are IP-merch, souvenir-adjacent.")
add("V068", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT","RELEVANT"], "MINOR", "YES",
    "2 landmark-city cards are weak; van gogh museum-merch cards and terracotta warriors are direct museum-souvenir/relic hits.")
add("V069", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Tang-horse figurine, van gogh mystery box, and a Luffy-themed poster are figure/IP-adjacent; 2 footballer cards are unrelated.")
add("V070", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 'chinese figure' illustrated mythological-figure cards are a legitimate but different figure sense; body-movement-verbs and Galileo-vs-Copernicus are unrelated.")
add("V071", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 Ghibli movie-poster cards are anime-adjacent but posters not merch; busan-boogi-duck is direct character merch; captain-tsubasa poster is anime-adjacent.")
add("V072", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "busan-boogi-duck is direct character merch; captain-tsubasa/looney-tunes/slam-dunk are anime-poster-adjacent; december-christmas-dinner is unrelated.")
add("V073", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 IP full-merch-collection cards and 2 red-envelope festival-stationery cards -- merch/stationery-adjacent, no literal postcard set confirmed.")
add("V074", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "deer travel journal and greeting-customs cards are postcard/travel-adjacent; 2 dinosaur-facts cards are unrelated; curi-ai merch collection is weak.")
add("V075", ["IRRELEVANT"]*5, "SEVERE", "NO", "World Cup team posters and IP character merch -- rewrite drifted off-topic, zero art-print content.")
add("V076", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "3 landmark vintage-info-poster cards (colosseum/eiffel/great wall) are literal wall-art print format, direct; autumn-harvest and cozy-winter-tea illustrations are print-adjacent.")
add("V077", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "'chinese figure mudan ting' is figure-adjacent; 3 body-movement-verb cards and a byzantine-tang card are unrelated to bobblehead.")
add("V078", ["PARTIALLY_RELEVANT"]*4, "MINOR", "PARTIALLY",
    "4 results (low-result). Tang-horse figurine and 3 modernized-artifact 3D chibi/diorama templates -- figurine/diorama concept adjacent to bobblehead, not a literal bobblehead product shot.")
add("V079", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated city/holiday/business cards -- rewrite drifted completely off-topic, zero scene-model content.")
add("V080", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "NONE", "YES",
    "4 results (low-result). 'ESC keycap cyber micro-house 3D diorama' and the explicit 'Keycap Micro-Diorama 3D Art Poster' template are direct diorama hits; 2 coder-workspace cards are weak.")
add("V081", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 illustrated character-profile cards and 2 mascot cards -- sticker/character-adjacent, no literal sticker-sheet product confirmed.")
add("V082", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "graduation alpaca, curi-ai icon set, bronze-worker character, tang-horse figurine, and office-plant mascot -- all character/sticker-adjacent, no literal sticker-pack product confirmed.")
add("V083", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "5 city/landmark cards (Beijing/Nanjing/Wuhan/Empire State/pagoda) -- word-sense collision (landmark vs. brand logo), matches the candidate-branch finding exactly.")
add("V084", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 anime-studio-comparison cards are unrelated; 2 food-packaging cards (oats/cookies) may carry a brand logo on-pack, weak.")
add("V085", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 historical-figure cards are unrelated; 2 explicit food-product-packaging cards (oats/cookies) are direct package hits.")
add("V086", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "All 5 are 'ISTJ vs ENFP package' MBTI-comparison cards/templates -- word collision on 'package', matches the candidate-branch finding exactly.")
add("V087", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated herbal-science cards -- template-family word collision, matches the candidate-branch finding exactly.")
add("V088", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated city-name/historical-figure cards -- zero label content, matches the candidate-branch finding exactly.")
add("V089", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY",
    "4 results (low-result). French/Japanese/Korean regional-drinks cards and the explicit regional-alcoholic-drinks-infographic template -- drinks-in-bottles-adjacent, no literal bottle object confirmed.")
add("V090", ["RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "2 results (low-result). 'smart hydration water bottle' is a direct hit; the generic Amazon product-infographic template is format-adjacent.")
add("V091", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 Chinese-dish recipe cards are menu-content-adjacent; 2 meat-cut anatomy-guide cards are format-mismatched (wrong content type for 'menu').")
add("V092", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 dish-recipe cards are menu-content-adjacent; French/Japanese regional-cuisine cards are cuisine-adjacent, not menu-format.")
add("V093", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 illustrated character-profile cards are unrelated; 'business card etiquette' is a direct topical hit; East-Asian-culture-comparison is weak.")
add("V094", ["IRRELEVANT"]*5, "NONE", "NO",
    "3 'Microsoft AI dilemma' comic-series cards and 2 unrelated history cards -- zero business-card content, matches the candidate-branch finding exactly.")
add("V095", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "4 IP character merch mockups and van gogh mystery box -- merch/box-adjacent, no generic product box confirmed.")
add("V096", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 IP character merch mockups are box-adjacent; 2 science myth-bust cards (carrot/giraffe) are unrelated.")
add("V097", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MINOR", "YES",
    "espresso and arabica coffee-bean cards are direct packaging-design hits; coffee-brewing, riseup-coffee brand, and BREW&CO moodboard are coffee-adjacent, not packaging-specific.")
add("V098", ["PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MINOR", "YES", "Same composition as V097 for the English term.")
add("V099", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "3 meat/coffee-anatomy-guide cards are format-mismatched; French/Japanese cuisine cards are weakly menu-adjacent.")
add("V100", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 dish-recipe cards are menu-content-adjacent; French/Japanese cuisine cards are cuisine-adjacent, not menu-format.")

# ---- V101-V149 (batch 3) ----
add("V101", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "4 results (low-result). Water bottle is a literal-but-wrong-type bottle; Kubernetes/tech-architecture cards are unrelated noise.")
add("V102", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "Water bottle is weak; 4 unrelated character/social cards -- rewrite drifted off-topic.")
add("V103", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated food-sticker/World-Cup cards -- rewrite drifted off-topic, zero perfume-box content.")
add("V104", ["IRRELEVANT"]*5, "SEVERE", "NO", "Identical composition for English term.")
add("V105", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "matcha-powder packaging-design is direct; panda-tea-master, bubble-tea-shop, tea-basics, cozy-winter-tea are tea-topic-adjacent, not packaging-specific.")
add("V106", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES", "Same pattern for English term.")
add("V107", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MINOR", "YES",
    "espresso and arabica coffee-bean cards are direct; coffee-brewing/riseup-coffee/BREW&CO are coffee-adjacent, not packaging-specific.")
add("V108", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "arabica coffee-bean packaging is direct; 4 other coffee-subject cards are on-topic but not packaging-specific.")
add("V109", ["RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "chocolate and Double Chocolate Cookies packaging-design cards are direct; 3 unrelated food-sticker cards.")
add("V110", ["RELEVANT","PARTIALLY_RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "chocolate and Double Chocolate Cookies are direct; 'swiss' is chocolate-country-adjacent; 2 unrelated food-sticker cards.")
add("V111", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "4 beauty/skincare-adjacent cards, no packaging specifically confirmed; hairdryer is wrong product.")
add("V112", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "4 beauty/skincare-adjacent cards; blessing-dragon IP character is unrelated.")
add("V113", ["IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "eyemask/hairdryer are wrong products; 3 beauty/skincare cards are cosmetic-adjacent.")
add("V114", ["IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "hairdryer is wrong product; 4 beauty/food-packaging cards are cosmetic-adjacent (weak).")
add("V115", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "White Wine, Red Wine, Champagne are direct wine-variety hits; 2 generic bilingual vocab cards are unrelated.")
add("V116", ["RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "White Wine is direct; label-printer is format-adjacent; 3 generic vocab cards are unrelated.")
add("V117", ["RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "Double Chocolate Cookies and choco-chip-cookies packaging cards are direct; summer-snack-festival, coffee-beans, and cheese cards are snack/packaging-format-adjacent (wrong specific product).")
add("V118", ["PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "summer-snack-festival is on-topic; choco-chip-cookies packaging is direct; Evolution-of-Snacks is topic-adjacent; apple/en-ko vocab cards are unrelated.")
add("V119", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "busan-boogi-duck IP merch is box-adjacent; 4 unrelated food-sticker/World-Cup cards.")
add("V120", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "4 IP character merch mockups are box-adjacent; carrot-night-vision science card is unrelated.")
add("V121", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'bag' is a direct generic-bag hit; curi-ai-robot merch and 3 brand-identity-moodboard templates are brand-asset-adjacent.")
add("V122", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "3 brand-identity-moodboard cards are brand-asset-adjacent; 'bag' is direct; curi-ai-robot merch is weak.")
add("V123", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "YES",
    "apple/bicycle/hamburger are explicit bilingual object-structure-labeling cards -- direct format match; hairstyle-tutorial/nail-art are unrelated.")
add("V124", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "Same explicit labeling-format hits; aroma-diffuser/bluetooth-speaker are generic product-showcase cards, label not confirmed.")
add("V125", ["PARTIALLY_RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Double-chocolate-cookies is weak; French-croissant is a direct bakery-item hit; diffuser/roujiamo cards are unrelated.")
add("V126", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "mika-cat-bakery, Golden-Crust-Bakery moodboard, and temp-bakery-cartoon-food are direct bakery-brand hits; en-zh vocab is unrelated; the brand-identity-moodboard template is weak.")
add("V127", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "A seafood-bistro-menu-sketch card, an 'Ordering at a Café' dialogue scene, and 3 drink-recipe/infographic templates -- cafe/menu-adjacent, no literal cafe-menu layout confirmed.")
add("V128", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "Ordering-at-a-Café, Ordering-Coffee, coffee-lovers, espresso-beans, and 'cafe 1' -- all cafe/coffee-topic-adjacent, no literal menu layout confirmed.")
add("V129", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "pet-shop-happy-paws and 2 brand cards (GreenBasket, riseup coffee) are shop-brand-adjacent; en-es vocab and 'how to sign great' (ASL word collision on 'sign') are unrelated -- matches the candidate-branch collision.")
add("V130", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY",
    "4 results (low-result). 3 brand-identity-moodboard cards and the explicit moodboard template -- brand-asset-adjacent, no literal shop sign confirmed.")
add("V131", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Same composition as V129 for the storefront-signage variant.")
add("V132", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "'how to sign great' (ASL word collision), 2 unrelated promotional-poster cards (baby care, spring beauty), summer-beach-sale, and aging-society-impact -- zero storefront-sign content.")
add("V133", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "camping-fruit-event, christmas-party-event, and mika-cat-bakery brand-VI mockups are tag/brand-asset-adjacent; 2 jewelry-pendant cards are wrong category for a product tag.")
add("V134", ["IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "tie/shirt are wrong fashion products; bag and tech-gadget-sale are weak; 'Organic Rolled Oats' (explicit product-label template) is a direct hit for the 'tag/label' concept.")
add("V135", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for '价格标签' (price tag, Chinese) -- catalog gap.")
add("V136", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for 'price tag' (English) -- catalog gap, both language pairs fail.")
add("V137", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "4 dynasty-costume cards and a jeans-ecommerce card -- clothing-subject but no tag/label object confirmed.")
add("V138", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "Identical composition for English term.")
add("V139", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 jewelry-category cards are on-topic but no box confirmed; 2 unrelated food-sticker cards.")
add("V140", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 jewelry cards and earrings are on-topic; 'lifting box' (word collision on 'box') and brunch sticker are unrelated.")
add("V141", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "4 results (low-result). 3 generic product-poster cards (diffuser/speaker/coffee-maker) are wrong products; the 'Cozy Product Poster' template is weakly format-adjacent.")
add("V142", ["IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "'Bedroom' is unrelated; label-printer and 3 eco-farm product-label cards (coffee/cheese/olive-oil) are label-format-adjacent but wrong product category.")
add("V143", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "'beast soap dish' is weakly soap-adjacent; label-printer is format-adjacent; 3 food-sticker cards are unrelated.")
add("V144", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY", "Same composition for English term.")
add("V145", ["IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "honeysuckle and an internet-meme card are unrelated; tea-culture-traditions, tea-basics, and cozy-winter-tea are tea-topic-adjacent, no canister/jar confirmed.")
add("V146", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "2 results (low-result). panda-tea-master and the IP cultural/stationery merch template -- tea-merch-adjacent, no literal tea box confirmed.")
add("V147", ["RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "2 results (low-result). The office-stationery clay-icon card explicitly depicts a coffee mug -- direct; the clay-icon-grid template is the same family, generic.")
add("V148", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 coffee-subject cards (drinks/machine/history/brewing/maker) -- on-topic but no literal cup object confirmed. Notably no 'World Cup' word-collision flooding on production, unlike the candidate branch.")
add("V149", ["RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "office-stationery card shows a coffee mug (weak sleeve match); eyemask is unrelated; 3 clay-icon-grid template variants are generic, same family.")

# ---- V150-V198 (batch 4) ----
add("V150", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 coffee-subject cards -- on-topic but no cup-sleeve object confirmed.")
add("V151", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 food-subject cards -- on-topic but no takeout container depicted.")
add("V152", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 food-sticker cards are weakly food-adjacent; panda-tea-master and a generic IP merch template are unrelated to takeout.")
add("V153", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "PARTIALLY",
    "spanish/australian regional-drinks cards are weak; smart-hydration-water-bottle is direct; 2 generic product/drinks-infographic templates are format-adjacent.")
add("V154", ["RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "smart-hydration-water-bottle is direct; portable-blender is drink-appliance-adjacent; 3 food-sticker cards are unrelated.")
add("V155", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "water-bottle infographic is direct; label-printer, lemon/orange vintage-fruit-label cards, and arabica-coffee-beans are label-format-adjacent but wrong product.")
add("V156", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES", "Identical composition for English term.")
add("V157", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "NONE", "YES",
    "3 red-envelope cards and the explicit red-envelope-set template are direct envelope hits; post-office is context-adjacent.")
add("V158", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). All 4 are red-envelope cards/template -- direct.")
add("V159", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'bag' is a direct generic-bag hit; 4 unrelated food-sticker/World-Cup cards.")
add("V160", ["RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'bag' is direct; curi-ai-robot merch is weak; 3 food-sticker cards are unrelated.")
add("V161", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 cake-subject cards (strawberry/lava/mille-crepe) are on-topic but no box confirmed; 2 unrelated food-sticker cards.")
add("V162", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 unrelated food-sticker/World-Cup cards; 'baking' is cake-process-adjacent.")
add("V163", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated food-sticker/World-Cup cards -- rewrite drifted completely off-topic, zero mooncake content.")
add("V164", ["IRRELEVANT"]*5, "SEVERE", "NO", "Identical composition for English term.")
add("V165", ["IRRELEVANT"]*5, "NONE", "NO", "3 wellness-infographic cards and 2 anime-studio-comparison cards -- wrong format entirely, no banner content.")
add("V166", ["IRRELEVANT"]*5, "NONE", "NO", "Identical composition for English term.")
add("V167", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "'fifa world cup 2026 opening ceremony' (explicit flyer-poster template) is direct; 4 unrelated city/holiday/relic cards.")
add("V168", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "All 5 share the display title 'World Cup Knockout Matchup Poster' (a poster/flyer-format signal) across differing underlying template slugs -- format-adjacent but content is inconsistent with a literal flyer.")
add("V169", ["IRRELEVANT"]*5, "NONE", "NO", "5 fashion-outfit-lookbook cards -- wrong format, not a catalog/album layout.")
add("V170", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MINOR", "PARTIALLY",
    "3 results (low-result). 2 van-gogh museum-merch cards are catalog-adjacent; the explicit museum-gift-merchandise-display template is a direct hit.")
add("V171", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). 3 explicit promotional-poster cards and the product-theme-promotional-poster template -- direct.")
add("V172", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "summer-beach-sale and baby-care-brand promotional-poster cards are direct; 3 Marvel MBTI character cards are unrelated.")
add("V173", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "van-gogh merch, a watch, and a battery card are product-photo-adjacent; labrador is unrelated.")
add("V174", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 vegetable how-to-guide cards show real product-style photos but in a gardening-guide context; cat/dog cards are unrelated.")
add("V175", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). Same explicit promotional-poster composition as V171 -- direct.")
add("V176", ["IRRELEVANT"]*5, "NONE", "NO", "3 Journey-to-the-West book covers and 2 city-travel cards -- unrelated, zero promotional content.")
add("V177", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"], "MINOR", "YES",
    "3 generic product-poster cards are ad-format-adjacent; 2 luxury/jewelry Russian 'product ad poster' cards are direct advertisement-format hits.")
add("V178", ["RELEVANT","RELEVANT"], "NONE", "YES", "2 results (low-result). Both are the explicit 'Einstein Russian Product Ad Poster' -- direct advertisement-format hit.")
add("V179", ["IRRELEVANT"]*5, "NONE", "NO", "3 city-landmark cards and 2 basketball-player cards -- unrelated, no social-media-post format.")
add("V180", ["IRRELEVANT"]*5, "NONE", "NO", "'chinese social changes' is a word collision on 'social'; 3 Journey-to-the-West covers and an eyemask card are unrelated.")
add("V181", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 history/evolution-infographic cards are unrelated; eyemask and musical-instrument (explicit fashion-ecommerce product-display format) are direct.")
add("V182", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "eyemask/musical-instrument/pendant (fashion-ecommerce product-display format) are direct; 2 red-envelope cards are unrelated.")
add("V183", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "5 restaurant/cafe-adjacent cards (ordering dialogue, sauce, bubble-tea brand, cuisine, sushi-chef) -- topic-adjacent, no flyer format confirmed.")
add("V184", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 restaurant-dialogue/food cards -- restaurant-topic-adjacent, no flyer format confirmed.")
add("V185", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 unrelated Chinese-dish cards; forrest-gump and la-land are explicit movie-poster hits.")
add("V186", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit movie-poster templates -- direct.")
add("V187", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 unrelated travel-packing-guide cards; 2 promotional-poster cards are banner-format-adjacent but not product-specific.")
add("V188", ["IRRELEVANT"]*5, "MODERATE", "NO", "3 unrelated travel-packing-guide cards and 2 unrelated red-envelope cards.")
add("V189", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 explicit promotional-poster cards are direct; an AI-content-factory card and a 9-traits-infographic template are unrelated.")
add("V190", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). Same explicit promotional-poster composition -- direct.")
add("V191", ["PARTIALLY_RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "The flyer-poster template matches format but wrong subject; 2 sale-promotional-poster cards are direct discount-content hits; 2 city/landmark cards are unrelated.")
add("V192", ["PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 results (low-result). flyer-poster format-adjacent wrong subject; explicit event-flyer-poster template is direct; a dance-tutorial card shares the display title 'Event Flyer' but content mismatches.")
add("V193", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 unrelated red-envelope cards; badminton-rackets is ecommerce-product-adjacent; amoled-gps-smartwatch (explicit ecommerce product template) is direct.")
add("V194", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "3 explicit amazon-product-infographic cards are direct ecommerce-format hits; 2 promotional-poster cards are format-adjacent.")
add("V195", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "SEVERE", "NO",
    "3 unrelated holiday/animal cards; eyemask and musical-instrument are product-showcase-adjacent (weak).")
add("V196", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "van-gogh merch, denim, jewelry, and wedding-dress cards -- product-showcase-adjacent, no catalog/booklet layout confirmed.")
add("V197", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "fifa-world-cup flyer-poster is direct; 3 landmark vintage-info-poster cards are event/travel-poster-adjacent; artists card is unrelated.")
add("V198", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "fifa-world-cup flyer-poster and the explicit universal-event-flyer-poster template are direct; 3 ballroom-dance-tutorial cards are wrong format.")

# ---- V199-V248 (batch 5) ----
add("V199", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Canada World Cup squad photos are unrelated; 2 promotional-poster cards are opening-promo-adjacent.")
add("V200", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY", "Identical composition for English term.")
add("V201", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "spring-beauty/summer-snack-festival and summer-beach-sale promotional posters are festival/sale-adjacent; 2 World Cup group cards are unrelated.")
add("V202", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "summer-beach-sale and 2 festival-promo cards are on-topic; Game-of-Thrones/Stranger-Things cards are unrelated.")
add("V203", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 explicit promotional-poster cards are direct; New Zealand World Cup squad and Marvel Black Widow card are unrelated.")
add("V204", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY", "Same composition for English term.")
add("V205", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "tech-gadget-sale is direct; 4 unrelated language-learning/history/culture cards dominate.")
add("V206", ["RELEVANT","RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 explicit sale-promotional-poster cards are direct; fifa-flyer-poster is format-adjacent; 2 city/landmark cards are unrelated.")
add("V207", ["RELEVANT","IRRELEVANT","RELEVANT","RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 explicit sale/promo-poster cards are direct; ikaris MBTI card and a Spain World Cup squad photo are unrelated.")
add("V208", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "summer-beach-sale is direct; 4 unrelated Marvel-character cards (domino/valkyrie/thena/superheroes) dominate.")
add("V209", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit Amazon product-infographic/six-grid-listing cards -- direct product-detail-image format match.")
add("V210", ["RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "The Amazon six-grid listing card is direct; labrador is unrelated; watch/battery/drone cards are product-concept-adjacent.")
add("V211", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 explicit promotional-poster cards are direct; domino/valkyrie Marvel cards are unrelated.")
add("V212", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY", "Same composition for English term.")
add("V213", ["IRRELEVANT"]*5, "NONE", "NO", "3 city-landmark cards and 2 basketball-player cards -- unrelated, no social-ad content.")
add("V214", ["IRRELEVANT"]*5, "NONE", "NO", "Same composition as V180 (social-media-post) -- unrelated.")
add("V215", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 fashion-ecommerce product cards and 2 supermarket-context cards -- product-showcase/shopping-adjacent, no literal recommendation-post format confirmed.")
add("V216", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 fashion-ecommerce product cards are showcase-adjacent; 2 MBTI-comparison cards are unrelated.")
add("V217", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "Colombia World Cup squad, 3 portrait-retouching-blueprint cards, and a lifestyle-portrait card -- zero unboxing content.")
add("V218", ["IRRELEVANT"]*5, "SEVERE", "NO", "2 portrait-retouching-blueprint cards and 3 lifestyle-photo-grid cards -- zero unboxing content.")
add("V219", ["RELEVANT"]*5, "NONE", "YES", "3 explicit portrait-retouching-blueprint cards and 2 home-organization-before-after cards -- direct format match.")
add("V220", ["RELEVANT","RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "4 explicit before-after cards (closet/desk/kitchen/bridal-hairstyle) are direct; casual-denim is weak.")
add("V221", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for '优惠券' (coupon, Chinese) -- catalog gap.")
add("V222", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for 'discount coupon' (English) -- catalog gap, both language pairs fail.")
add("V223", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for '会员卡' (membership card, Chinese) -- catalog gap.")
add("V224", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "'Club Sandwich' is a word collision on 'club'; 4 unrelated demographic/culture cards -- rewrite drifted off-topic, matches candidate-branch finding.")
add("V225", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated character/demographic/heritage cards -- word collision on generic 'card' template naming, matches candidate-branch finding.")
add("V226", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated character/science cards -- matches candidate-branch finding exactly.")
add("V227", ["IRRELEVANT"]*3, "NONE", "NO", "3 results (low-result). Sports-equipment segment cards -- word collision on 'card' (flashcard template), matches candidate-branch finding.")
add("V228", ["IRRELEVANT"]*5, "NONE", "NO", "2 sports-equipment cards and 3 classical-painting cards -- unrelated, matches candidate-branch finding.")
add("V229", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 promotional-poster cards are banner-adjacent; ikaris MBTI card and a Spain World Cup squad photo are unrelated.")
add("V230", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 promotional-poster cards are banner-adjacent; domino/valkyrie Marvel cards are unrelated.")
add("V231", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 promotional posters and van-gogh mystery box are display-adjacent; Andrew Tate meme-merch card is unrelated.")
add("V232", ["RELEVANT","RELEVANT","RELEVANT","RELEVANT","RELEVANT"], "NONE", "YES",
    "2 explicit product-poster (diffuser) cards and 3 fashion-ecommerce cards -- all direct product-display-format matches.")
add("V233", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated herbal/furniture/lifestyle cards -- rewrite drifted completely off-topic, zero exhibition-stand content.")
add("V234", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated Marvel-character cards -- rewrite drifted completely off-topic.")
add("V235", ["PARTIALLY_RELEVANT","IRRELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "fifa-flyer-poster is format-adjacent; 3 'Ethnic Costume Deconstruction Board' cards (costume/dance-tutorial/costume slugs) are unrelated; one shares an explicit universal-event-flyer-poster slug despite the misleading display title, direct.")
add("V236", ["PARTIALLY_RELEVANT","IRRELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY", "Same pattern as V235 for the English term.")
add("V237", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). 3 explicit promotional-poster cards and the product-theme-promotional-poster template -- direct.")
add("V238", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"], "MINOR", "YES",
    "3 brand-VI-event mockups are launch-event-adjacent; baby-care-brand and spring-beauty-festival promotional posters are direct.")
add("V239", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). Same explicit promotional-poster composition -- direct.")
add("V240", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 explicit seasonal-sale promotional-poster cards are direct; 2 World Cup team cards are unrelated.")
add("V241", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "summer-beach-sale is direct sale-content; 'marvel blackwidow.jp' is a word collision on 'black'; 3 unrelated character cards.")
add("V242", ["IRRELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "'marvel blackwidow.jp' is a word collision on 'black'; summer-beach-sale and baby-care-brand are direct sale-content; winter-soldier/ikaris are unrelated.")
add("V243", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "tech-gadget-sale is direct; 'Chinese' language-learning cards, a cookie card, and a massive unrelated World-Cup-fixtures text card dominate.")
add("V244", ["RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 explicit sale-promotional-poster cards are direct; 3 world-landmark vintage-info-poster cards are unrelated.")
add("V245", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character-portrait cards (Toriyama/Game-of-Thrones/Marvel/Spider-Man/domino) -- rewrite drifted completely off-topic.")
add("V246", ["IRRELEVANT"]*5, "SEVERE", "NO", "Identical composition for English term.")
add("V247", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "NONE", "YES",
    "4 results (low-result). A dolphin compound-word card and the explicit 'Chinese Compound Word Literacy Cartoon' template are direct; dolphin/gecko vocab cards are format-adjacent.")
add("V248", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 share the display title 'Cartoon English Word Card' across genuine vocabulary/flashcard-format template slugs (word-card, vocab-poster, cuisine-vocab, confusing-word-pair, phonics-blend) -- direct.")

# ---- V249-V297 (batch 6) ----
add("V249", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated country-overview/self-improvement cards -- rewrite drifted off-topic, no worksheet format.")
add("V250", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "3 explicit kids-fill-in-worksheet cards are direct; 2 word-difference educational-poster cards are education-adjacent, not worksheet-format-specific.")
add("V251", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "The alphabet-phonics card is direct; 4 vocabulary/mindmap cards are learning-card-format-adjacent, not letter-specific.")
add("V252", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES", "Same pattern for English term.")
add("V253", ["RELEVANT"]*5, "NONE", "YES",
    "All 5 share the display title '3D Landmark Map' across genuine map-format template slugs (region-landmark-map, travel-map, watercolor-world-map, tourist-map, world-travel-map) -- direct.")
add("V254", ["RELEVANT"]*5, "NONE", "YES", "Identical composition for English term.")
add("V255", ["IRRELEVANT"]*5, "NONE", "NO", "5 unrelated Chinese-dish/solar-term cards -- no diagram/illustrated-guide format.")
add("V256", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "A cartoon-character card and 2 herbal cards are unrelated; 2 demographic-trend infographic cards are diagram-format-adjacent.")
add("V257", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 international sporting-event promotional posters are a word-sense mismatch (event calendar, not calendar object); resort (annual-event-calendar-infographic) and local-festival-schedule are direct.")
add("V258", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "Same event-poster mismatch for 3 results; resort is direct; fifa-opening-ceremony is unrelated.")
add("V259", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character/demographic cards -- rewrite drifted off-topic, zero certificate content.")
add("V260", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for 'certificate' (English) -- catalog gap.")
add("V261", ["RELEVANT"]*5, "NONE", "YES", "3 herbal-science cards and 2 explicit science-fact cards -- direct science-poster content match.")
add("V262", ["RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 herbal-science cards are direct; 3 city-weather-illustration cards are unrelated.")
add("V263", ["RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "3 historical-figure educational portrait cards (artists/composers/philosophers) are direct classroom-decoration hits; 2 manga-artist portraits are a related but narrower concept.")
add("V264", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 'evolution' history-infographic cards are classic classroom posters, direct; 2 solar-term cards are unrelated.")
add("V265", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY",
    "4 results (low-result). 3 historical-figure educational portraits and the explicit historical-figure-educational template -- textbook-content-adjacent, not a literal textbook page/cover.")
add("V266", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY",
    "3 historical-figure portraits and 2 nature-science cards -- educational-content-adjacent, textbook format not confirmed.")
add("V267", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "world-countries-geography-mindmap is direct; 4 unrelated solar-term/leader/city cards dominate.")
add("V268", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "5 unrelated solar-term/pizza/'leader' MBTI cards -- rewrite drifted completely off-topic, matches the candidate-branch finding exactly (drift to 'leader' character cards).")
add("V269", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "NONE", "PARTIALLY",
    "3 species-infographic cards (baiji/panda/tiger) are chart-format-adjacent; 2 city-miniature cards are unrelated.")
add("V270", ["IRRELEVANT"]*5, "NONE", "NO", "4 'Journey to the West' character/architecture cards -- no chart format.")
add("V271", ["RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MINOR", "YES",
    "school-timetable, local-festival-schedule, and community-events cards are direct schedule-format hits; resort is calendar-adjacent; fifa-world-cup is unrelated.")
add("V272", ["RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "2 results (low-result). school-timetable is direct; the detailed-vocab-flashcard template is language-learning-adjacent, containing timetable-style content per the candidate-branch finding.")
add("V273", ["IRRELEVANT"]*5, "SEVERE", "NO", "3 unrelated animal-character cards and 2 celebrity-meme-merch cards -- rewrite drifted completely off-topic, zero number-chart content.")
add("V274", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "SEVERE", "NO",
    "3 Ghibli 'matching chart' cards are a word collision on 'chart' template naming; weather-pinyin is unrelated; 'Gender and Number Agreement' is weakly number-adjacent (grammar, not a numeric chart).")
add("V275", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Breaking Bad character cards are unrelated; 'chemistry d block elements' is a direct periodic-table-adjacent hit; the cheat-sheet-poster template is format-adjacent.")
add("V276", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 Breaking Bad cards are unrelated; 'chemistry periodic table tricks trends' is direct; the cheat-sheet-poster template is format-adjacent.")
add("V277", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"], "NONE", "YES",
    "3 world-landmark vintage-info-poster cards are travel/geography-adjacent, not literal maps; china/egypt (world-travel-map-illustration format) are direct.")
add("V278", ["RELEVANT","RELEVANT","RELEVANT","RELEVANT","RELEVANT"], "NONE", "YES",
    "3 explicit world-travel-map-illustration cards and 2 word-origins-map-infographic cards -- all direct map-format matches.")
add("V279", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "alphabet-phonics card is direct; 4 vocab/mindmap cards are learning-card-format-adjacent.")
add("V280", ["RELEVANT"]*5, "NONE", "YES", "3 explicit CVC phonics cards (am/ap/at/ir) and 2 alphabet-phonics cards -- direct.")
add("V281", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated cultural-heritage cards (lantern/paper-cutting/cloisonne/solar-terms) -- rewrite drifted off-topic, zero exam content.")
add("V282", ["IRRELEVANT"]*5, "SEVERE", "NO", "Identical composition for English term.")
add("V283", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 'academic'-themed cards are weakly academic-context-adjacent; dna-helix/plate-tectonics are unrelated generic science cards.")
add("V284", ["IRRELEVANT"]*5, "NONE", "NO",
    "5 generic 'education-card' science-topic cards (DNA helix, plate tectonics, resource capacity, coral reef, solar system) -- word collision on template naming, matches candidate-branch finding.")
add("V285", ["IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "2 'AI dilemma...case' cards are a word collision on 'case'; 'Stationery' is weakly topic-adjacent; label-printer and en-zh vocab are unrelated.")
add("V286", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "2 'AI dilemma...case' cards are a word collision; en-zh is unrelated; 2 'school supplies' cards are stationery-adjacent.")
add("V287", ["IRRELEVANT"]*5, "NONE", "NO", "5 generic 'education-card' science-topic cards -- no blackboard depicted, matches candidate-branch finding.")
add("V288", ["IRRELEVANT"]*5, "NONE", "NO", "Identical composition for 'chalkboard'.")
add("V289", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character/demographic cards -- rewrite drifted off-topic, zero whiteboard content.")
add("V290", ["IRRELEVANT"], "NONE", "NO", "ZERO_RESULT for 'whiteboard' (English) -- catalog gap.")
add("V291", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated city/food/herb/book cards -- matches candidate-branch finding exactly, zero microscope content.")
add("V292", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "dna-helix/plate-tectonics are weakly science-topic-adjacent; nanjing/resource-capacity/pizza are unrelated.")
add("V293", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated food-dish cards -- rewrite drifted off-topic, zero bookmark content.")
add("V294", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MODERATE", "PARTIALLY",
    "3 fashion-ecommerce product cards (socks/watch/shoes) are wrong products; 2 library-context cards are weakly bookmark-adjacent.")
add("V295", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character/demographic cards -- rewrite drifted off-topic, zero abacus content.")
add("V296", ["PARTIALLY_RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "en-ko vocab card is weakly numbers-adjacent; resource-capacity/kitchen-utensils/content-creation/creativity are unrelated.")
add("V297", ["PARTIALLY_RELEVANT"]*4, "NONE", "PARTIALLY",
    "4 results (low-result). IP-merch mockup cards (moyu zhong, panda tea master, rabbit ding feng, curi-ai robot set) -- generic merch, notebook only weakly implied.")

# ---- V298-V326 (batch 7, final) ----
add("V298", ["IRRELEVANT"]*5, "SEVERE", "NO", "2 unrelated travel-city cards and 3 'Journey to the West' book covers -- rewrite drifted off-topic, zero workbook content.")
add("V299", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "MINOR", "YES",
    "'Calabash Brothers' explicit vocabulary-list card is direct; 4 other vocab/CVC cards are format-adjacent, not word-card-specific.")
add("V300", ["RELEVANT"]*5, "NONE", "YES", "Same 'Cartoon English Word Card' composition as V248 -- direct.")
add("V301", ["PARTIALLY_RELEVANT"]*5, "NONE", "PARTIALLY", "5 vocabulary learning cards (kitchen/desserts/fruits/body/activities) -- vocab-card-format but not spelling-specific.")
add("V302", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT"], "MINOR", "YES",
    "3 word-scene vocab cards and a business-terms card are format-adjacent; 'am' (CVC phonics) is direct spelling-format.")
add("V303", ["IRRELEVANT"]*5, "SEVERE", "NO", "4 sports-action cards and a warm-up-routine template -- rewrite drifted off-topic, zero math content.")
add("V304", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "SEVERE", "NO",
    "3 vocabulary cards have no math content; 2 kids-fill-in-worksheet cards are worksheet-format-adjacent, not math-specific.")
add("V305", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "hsk2-golden-millet-dream is direct Chinese-literature reading content; 3 library-context cards are reading-adjacent; gym is unrelated.")
add("V306", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT"], "MINOR", "YES",
    "3 kids-fill-in-worksheet cards are format-adjacent; the explicit 'HSK1 reading worksheet' and hsk2-golden-millet-dream cards are direct.")
add("V307", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 explicit science myth-bust infographic cards are direct; 2 musical-instrument cards are unrelated.")
add("V308", ["RELEVANT"]*5, "NONE", "YES", "3 herbal-science cards and 2 nature-ecosystem cards -- direct science-content match.")
add("V309", ["RELEVANT"]*5, "NONE", "YES", "All 5 are explicit human-body/anatomy cards -- direct.")
add("V310", ["IRRELEVANT"]*5, "MODERATE", "NO",
    "3 architecture-infographic cards (word collision on 'anatomy' tag) and 2 zodiac-sign cards -- no body-anatomy content.")
add("V311", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "apple/book vocab cards are wrong topic but card-format; dog is a direct animal-card hit; egret/ginkgo-tree are animal/nature-topic-adjacent species cards.")
add("V312", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","RELEVANT","RELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "apple/book are wrong-topic vocab cards; dog and the animal-learning-card-mindmap are direct; the flashcard-ontology template is format-adjacent.")
add("V313", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "3 explicit phonics-consonant-blend letter cards are direct; 2 MBTI personality-group cards are unrelated.")
add("V314", ["RELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT","IRRELEVANT"], "SEVERE", "NO",
    "alphabet-phonics card is direct; 4 unrelated vocab/weather/chemistry cards dominate.")
add("V315", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character/demographic cards -- rewrite drifted off-topic, zero certificate content.")
add("V316", ["IRRELEVANT"]*5, "SEVERE", "NO", "5 unrelated character/science cards -- rewrite drifted off-topic.")
add("V317", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "graduation-alpaca is graduation-theme-adjacent; 3 'academic'-themed literature cards are weakly academic-context-adjacent; sun-wukong is unrelated.")
add("V318", ["PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY", "Same pattern for English term.")
add("V319", ["RELEVANT","IRRELEVANT","RELEVANT","RELEVANT","IRRELEVANT"], "MODERATE", "PARTIALLY",
    "resort (calendar-infographic) and 2 schedule cards are direct; fifa-world-cup and a Christmas-dinner card are unrelated.")
add("V320", ["RELEVANT"]*4, "NONE", "YES", "4 results (low-result). resort, local-festival-schedule, community-events, and the explicit annual-event-calendar-infographic template -- all direct.")
add("V321", ["RELEVANT","RELEVANT","RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "YES",
    "3 continent watercolor-world-map cards are classic classroom wall-decor, direct; bedroom is wrong room type; room-vocabulary-infographic is decor-adjacent.")
add("V322", ["RELEVANT","PARTIALLY_RELEVANT","PARTIALLY_RELEVANT","IRRELEVANT","PARTIALLY_RELEVANT"], "NONE", "PARTIALLY",
    "composers (historical-figure-educational) is a direct classroom-decor hit; physics/word-comparison/word-pair cards are educational-poster-adjacent; kitchen-utensils is unrelated.")
add("V323", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 unrelated dialogue-scene cards; 2 explicit Chinese-verb-opposite-infographic (learning-chart format) cards are direct.")
add("V324", ["IRRELEVANT","IRRELEVANT","IRRELEVANT","RELEVANT","RELEVANT"], "MODERATE", "PARTIALLY",
    "3 architecture cards are off-topic despite a 'learning' tag; action-words/daily-words (verb-opposite-infographic) are direct.")
add("V325", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "A food-doodle-sticker card (word collision on 贴纸/sticker) and 3 celebrity-meme-merch-sticker cards, plus an unrelated food card -- zero reward-chart content.")
add("V326", ["IRRELEVANT"]*5, "SEVERE", "NO",
    "3 Ghibli 'matching chart' cards (word collision on 'chart') and 2 unrelated weather cards -- zero reward-chart content.")
