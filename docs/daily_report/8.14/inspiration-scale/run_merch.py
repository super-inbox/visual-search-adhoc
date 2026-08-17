import sys
sys.path.insert(0, ".")
from collect_pins import process

TOPIC = {
    "S002": "merch;character-ip;fan-art", "S004": "merch;character-ip;fan-art",
    "S005": "merch", "S007": "merch;character-ip", "S008": "mascots",
    "S009": "fan-art", "S010": "original-ip", "S011": "dunhuang",
    "S012": "mogao-caves", "S013": "silk-road", "S014": "modernized-artifact",
    "S015": "cultural-fusion",
}
MAP_STATUS = {k: ("mapped_full" if k == "S005" else "mapped_stub") for k in TOPIC}
SRC = {k: ("exploration_jsonl" if k in ("S002", "S004") else "niche_topic") for k in TOPIC}
QUERY_TEXT = {
    "S002": "Marvel character poster merch design", "S004": "Chiikawa character lifestyle merch design",
    "S005": "IP character merch flatlay design", "S007": "character sprite sheet merch design",
    "S008": "brand mascot character design", "S009": "fan art character IP poster design",
    "S010": "original IP character merch design", "S011": "Dunhuang museum merch design",
    "S012": "Mogao Caves museum souvenir design", "S013": "Silk Road cultural merch design",
    "S014": "modernized cultural artifact product design", "S015": "cultural fusion product design",
}

RAW = [
    ("S002", 1, "https://www.pinterest.com/pin/marvel-poster-design--1477812373959364/", "merch;fanart;poster", "B"),
    ("S002", 2, "https://www.pinterest.com/pin/772930354781067144/", "merch;fanart;poster", "C"),
    ("S004", 1, "https://www.pinterest.com/pin/chiikawa-hachiware-usagi-stickers-fan-merch-etsy-in-2024--809662839293380096/", "merch;kawaii;sticker", "B"),
    ("S004", 2, "https://www.pinterest.com/pin/374080312818050703/", "merch;kawaii", "B"),
    ("S005", 1, "https://www.pinterest.com/pin/ip-characters-design-on-behance--1132585006259500560/", "merch;character_design;flatlay", "B"),
    ("S005", 2, "https://www.pinterest.com/pin/309833649383142953/", "merch;character_design;cute_style", "B"),
    ("S007", 1, "https://www.pinterest.com/pin/game-character-art--920986192521166524/", "sprite_sheet;chibi;game_asset", "C"),
    ("S007", 2, "https://www.pinterest.com/pin/434808539014119617/", "sprite_sheet;retro;game_asset", "C"),
    ("S008", 1, "https://www.pinterest.com/pin/mascot-design-character--3377768467564514/", "mascot;brand_character", "B"),
    ("S008", 2, "https://in.pinterest.com/pin/brand-mascot-character-design-for-wires-cables--611152611976239366/", "mascot;brand_character;industrial", "B"),
    ("S009", 1, "https://www.pinterest.com/pin/fan-art-character-design-on-behance--585608757826823069/", "fan_art;character_design", "B"),
    ("S009", 2, "https://in.pinterest.com/pin/952300283714234817/", "fan_art;poster", "C"),
    ("S010", 1, "https://www.pinterest.com/pin/z--351914158405015510/", "original_ip;sculpture;3d_toy", "B"),
    ("S010", 2, "https://www.pinterest.com/pin/713187290994519789/", "original_ip;character_design", "C"),
    ("S011", 1, "https://id.pinterest.com/pin/4593460585011405824/", "cultural_creative;dunhuang;tableware", "A"),
    ("S011", 2, "https://www.pinterest.com/pin/dunhuang-murals-washi-tape-set-in-2024--605171268713850806/", "cultural_creative;dunhuang;stationery", "B"),
    ("S013", 1, "https://www.pinterest.com/pin/silk-road-design-logo-with-dragon--469711436137838630/", "cultural_creative;silk_road;logo", "C"),
    ("S013", 2, "https://www.pinterest.com/pin/journey-into-history-textiles-from-the-silk-road--80572280828553304/", "cultural_creative;silk_road;textile", "B"),
    ("S014", 1, "https://www.pinterest.com/pin/291467407144490853/", "cultural_artifact;art_print", "C"),
    ("S015", 1, "https://www.pinterest.com/pin/669136457168762520/", "cultural_fusion;streetwear", "B"),
    ("S015", 2, "https://www.pinterest.com/pin/cultural-fusion-in-fashion-by-avrier-2025-trends--14284923812869868/", "cultural_fusion;fashion", "B"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"merch_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source=SRC[qid], topic_slug=TOPIC[qid], topic_mapping_status=MAP_STATUS[qid],
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin',
        notes="S012 (Mogao Caves) yielded no on-topic souvenir/merch-design pins -- only travel photography of the caves themselves; skipped rather than forcing a weak match.",
    ))

process(candidates, "merch", "")
