import sys
sys.path.insert(0, ".")
from collect_pins import process

QUERY_TEXT = {
    "S016": "food packaging label design", "S017": "beverage packaging bottle design",
    "S018": "cosmetic packaging design", "S019": "electronics packaging design",
    "S020": "luxury packaging design", "S022": "unboxing experience packaging design",
}
MAP_STATUS = {k: ("mapped_full" if k == "S022" else "needs_confirmation") for k in QUERY_TEXT}

RAW = [
    ("S016", 1, "https://www.pinterest.com/pin/70931762871277308/", "packaging;food;minimal;label", "B"),
    ("S016", 2, "https://in.pinterest.com/pin/730920214561497929/", "packaging;food;logo", "B"),
    ("S017", 1, "https://www.pinterest.com/pin/367536019587542086/", "packaging;beverage;bottle", "B"),
    ("S017", 2, "https://www.pinterest.com/pin/161777811601279214/", "packaging;beverage;bottle;conceptual", "B"),
    ("S018", 1, "https://www.pinterest.com/pin/942941240706254870/", "packaging;cosmetic;luxury", "B"),
    ("S018", 2, "https://www.pinterest.com/pin/modern-skincare-packaging-box-design--317292736259390283/", "packaging;cosmetic;skincare;modern", "B"),
    ("S019", 1, "https://www.pinterest.com/pin/446560119321515272/", "packaging;electronics;sleek", "B"),
    ("S019", 2, "https://www.pinterest.com/pin/luxury-packaging-design-for-electronics--6825836926495477/", "packaging;electronics;luxury", "B"),
    ("S020", 1, "https://www.pinterest.com/pin/luxury-packaging-design-inspiration-for-perfume-brand--351280839706531391/", "packaging;luxury;perfume", "B"),
    ("S020", 2, "https://www.pinterest.com/pin/discover-the-art-of-luxury-packaging-packagingfactory-luxurybox--1196337403327242/", "packaging;luxury;box", "B"),
    ("S022", 1, "https://www.pinterest.com/pin/5-rules-for-designing-an-unforgettable-unboxing-experience-for-your-brand-crowdspring-blog--244812929731108033/", "packaging;unboxing;brand_experience", "B"),
    ("S022", 2, "https://www.pinterest.com/pin/how-to-wow-your-customers-with-the-best-unboxing-experience--291185932142560328/", "packaging;unboxing", "B"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"packaging_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source="niche_topic", topic_slug="packaging", topic_mapping_status=MAP_STATUS[qid],
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin',
        notes="",
    ))

process(candidates, "packaging", "")
