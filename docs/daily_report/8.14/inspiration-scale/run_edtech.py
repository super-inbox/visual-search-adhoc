import sys
sys.path.insert(0, ".")
from collect_pins import process

TOPIC = {"S036": "vocabulary", "S037": "dialogue", "S038": "study-sheets",
         "S039": "mind-maps", "S040": "information-card", "S041": "learning"}
MAP_STATUS = {"S036": "mapped_full", "S037": "mapped_full", "S038": "mapped_stub",
              "S039": "mapped_stub", "S040": "mapped_full", "S041": "needs_confirmation"}
QUERY_TEXT = {
    "S036": "vocabulary bilingual word poster design", "S037": "dialogue conversation practice card design",
    "S038": "study sheet infographic design", "S039": "mind map educational infographic design",
    "S040": "information card knowledge summary design", "S041": "classroom worksheet design for kids",
}

RAW = [
    ("S036", 1, "https://www.pinterest.com/pin/who-what-when-where-why-how-bilingual-spanishenglish-poster-great-for-vocabulary-or-basic-grammar-for-a--512214157604917682/", "edtech;vocabulary;bilingual;poster", "B"),
    ("S036", 2, "https://www.pinterest.com/pin/ela-bilingual-word-wall-esl-vocabulary-english-spanish-language-arts-esol--81768549490737428/", "edtech;vocabulary;bilingual;word_wall", "B"),
    ("S037", 1, "https://www.pinterest.com/pin/dialogue-task-cards-practice-writing-sentences-with-quotation-marks-3rd-4th-5th--321514860874058250/", "edtech;dialogue;task_card", "B"),
    ("S037", 2, "https://www.pinterest.com/pin/boho-conversation-cards-worksheet-templates-by-canva--836614068297278722/", "edtech;dialogue;conversation_card", "B"),
    ("S038", 1, "https://www.pinterest.com/pin/25-aesthetic-note-layouts-for-studying--291608144632687018/", "edtech;study_sheet;aesthetic;handcrafted", "B"),
    ("S038", 2, "https://in.pinterest.com/pin/aesthetic-study-notes--1087760116237673283/", "edtech;study_sheet;aesthetic", "B"),
    ("S039", 1, "https://www.pinterest.com/pin/534802524510187821/", "edtech;mind_map;infographic", "B"),
    ("S039", 2, "https://www.pinterest.com/pin/mind-map-examples-for-education-business-mind-mapping-gallery--608900812120275637/", "edtech;mind_map;education", "B"),
    ("S040", 1, "https://www.pinterest.com/pin/489203578253884040/", "edtech;information_card", "B"),
    ("S041", 1, "https://www.pinterest.com/pin/classroom-objects-worksheet-for-kids--140806230932648/", "edtech;classroom;worksheet;kids", "B"),
    ("S041", 2, "https://www.pinterest.com/pin/classroom-objects-english-esl-worksheets-for-distance-learning-and-physical-classrooms--695313629974968720/", "edtech;classroom;worksheet;kids", "B"),
]

candidates = []
for qid, seq, url, tags, q in RAW:
    candidates.append(dict(
        id=f"edtech_{qid}_{seq:03d}", query_id=qid, query=QUERY_TEXT[qid],
        query_source="niche_topic", topic_slug=TOPIC[qid], topic_mapping_status=MAP_STATUS[qid],
        pin_url=url, seq=seq, style_tags=tags, quality_score=q,
        discovered_via=f'WebSearch "{QUERY_TEXT[qid]}" site:pinterest.com/pin', notes="",
    ))
process(candidates, "edtech", "")
