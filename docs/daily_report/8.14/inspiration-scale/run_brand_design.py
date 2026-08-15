import sys
sys.path.insert(0, ".")
from collect_pins import process

QUERY_TEXT = {
    "S031": "brand color system design", "S032": "brand typography system design",
    "S033": "brand book visual identity design", "S034": "new brand launch style sheet design",
}

RAW = [
    ("S031", 1, "https://www.pinterest.com/pin/colour-palette-brandbook--568438784189215942/", "branding;color_system", "B"),
    ("S031", 2, "https://www.pinterest.com/pin/create-a-colour-palette-for-your-brand--543035667579985978/", "branding;color_system", "B"),
    ("S032", 1, "https://www.pinterest.com/pin/typography-suite-for-a-brand-identity--536209899402683974/", "branding;typography", "A"),
    ("S032", 2, "https://www.pinterest.com/pin/typography-brand-manual-by-samson-vowles--543809723765587368/", "branding;typography;manual", "B"),
    ("S033", 1, "https://in.pinterest.com/pin/557250153894219960/", "branding;visual_identity;brand_book", "A"),
    ("S033", 2, "https://www.pinterest.com/pin/21-brand-style-guide-examples-for-visual-inspiration-hello-im-an-experie-in-2022--664914332501557646/", "branding;visual_identity;style_guide", "B"),
    ("S034", 1, "https://www.pinterest.com/pin/elegant-brand-style-guide-template--1900024833478550/", "branding;style_sheet;launch", "B"),
    ("S034", 2, "https://www.pinterest.com/pin/667940188462705197/", "branding;style_sheet;guidelines", "B"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"branddesign_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source="niche_topic", topic_slug="branding", topic_mapping_status="mapped_full",
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin',
        notes="",
    ))

process(candidates, "brand_design", "")
