import sys
sys.path.insert(0, ".")
from collect_pins import process

TOPIC = {"S023": "ecommerce", "S024": "ecommerce", "S025": "ecommerce",
         "S026": "ecommerce", "S027": "showcase", "S028": "showcase", "S029": "ecommerce"}
MAP_STATUS = {k: "mapped_full" for k in TOPIC}
SRC = {k: "niche_topic" for k in TOPIC}
QUERY_TEXT = {
    "S023": "ecommerce hero banner design", "S024": "product lifestyle shot ecommerce design",
    "S025": "product flat lay ecommerce photography", "S026": "product detail image ecommerce design",
    "S027": "product launch mood board design", "S028": "product lineup promotional poster design",
    "S029": "DTC product campaign visual design",
}

RAW = [
    ("S023", 1, "https://www.pinterest.com/pin/13721973844126773/", "ecommerce;hero_banner", "B"),
    ("S024", 1, "https://www.pinterest.com/pin/creating-winning-branded-lifestyle-product-photography-for-ecommerce--477522366737741186/", "ecommerce;lifestyle_shot", "B"),
    ("S024", 2, "https://www.pinterest.com/pin/823947694361456531/", "ecommerce;lifestyle_shot", "B"),
    ("S025", 1, "https://www.pinterest.com/pin/362680576245282867/", "ecommerce;flatlay;photography", "B"),
    ("S025", 2, "https://www.pinterest.com/pin/color-blocking-flat-lay-food-product-photography--11540542787456784/", "ecommerce;flatlay;color_blocking", "B"),
    ("S026", 1, "https://www.pinterest.com/pin/product-detail-page--89931323797054320/", "ecommerce;detail_image;ui", "B"),
    ("S026", 2, "https://in.pinterest.com/pin/e-commerce-website-product-detail-page-design--185069865929518595/", "ecommerce;detail_image;ui", "B"),
    ("S027", 1, "https://www.pinterest.com/pin/mood-boards-for-product-designers--1040542688875934694/", "showcase;mood_board", "B"),
    ("S027", 2, "https://www.pinterest.com/pin/moodboard-design-for-high-end-brands-by-coupled-with-grace--200269514669605127/", "showcase;mood_board;luxury", "B"),
    ("S028", 1, "https://www.pinterest.com/pin/new-product-launching-poster--303781937382168281/", "showcase;promotional_poster;launch", "B"),
    ("S028", 2, "https://www.pinterest.com/pin/digital-marketing-creative-poster-design-video--843510205250487381/", "showcase;promotional_poster", "C"),
    ("S029", 1, "https://in.pinterest.com/pin/visual-brand-identity-product-packaging-design-on-behance--373446994116339041/", "ecommerce;dtc;brand_identity", "B"),
    ("S029", 2, "https://www.pinterest.com/pin/1087549010039878901/", "ecommerce;dtc;logo", "C"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"ecommerce_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source=SRC[qid], topic_slug=TOPIC[qid], topic_mapping_status=MAP_STATUS[qid],
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin',
        notes="",
    ))

process(candidates, "ecommerce", "")
