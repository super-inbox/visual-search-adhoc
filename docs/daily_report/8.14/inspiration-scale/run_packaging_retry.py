import sys
sys.path.insert(0, ".")
from collect_pins import process

QUERY_TEXT = {"S019": "electronics packaging design", "S020": "luxury packaging design", "S022": "unboxing experience packaging design"}
MAP_STATUS = {"S019": "needs_confirmation", "S020": "needs_confirmation", "S022": "mapped_full"}

RAW = [
    ("S019", 2, "https://www.pinterest.com/pin/luxury-packaging-design-for-electronics--6825836926495477/", "packaging;electronics;luxury", "B"),
    ("S020", 1, "https://www.pinterest.com/pin/luxury-packaging-design-inspiration-for-perfume-brand--351280839706531391/", "packaging;luxury;perfume", "B"),
    ("S020", 2, "https://www.pinterest.com/pin/discover-the-art-of-luxury-packaging-packagingfactory-luxurybox--1196337403327242/", "packaging;luxury;box", "B"),
    ("S022", 1, "https://www.pinterest.com/pin/5-rules-for-designing-an-unforgettable-unboxing-experience-for-your-brand-crowdspring-blog--244812929731108033/", "packaging;unboxing;brand_experience", "B"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"packaging_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source="niche_topic", topic_slug="packaging", topic_mapping_status=MAP_STATUS[qid],
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin', notes="",
    ))
process(candidates, "packaging", "")
