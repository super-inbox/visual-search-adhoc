#!/usr/bin/env python3
"""Appends the second-pass interactive-browser-verified records for the three
thin culture-tier3 stub topics (silk-road, modernized-artifact, cultural-fusion)
flagged in DAILY_REPORT.md section 17.3 as needing a targeted follow-up pass,
the same treatment already applied to mogao-caves (S012) this session. Every
record was found via a live Pinterest search grid (interactive Chrome browser,
more specific search terms than the original batch), verified by reading the
real pin page (title/description or, where Pinterest's client-rendered pin
page had no static og:meta, via get_page_text/screenshot of the live page),
and its thumbnail captured from the live pin image render -- not fabricated.
Run once; appends to the merch checkpoint files (idempotent only if re-run
after removing the appended rows -- unlike collect_pins.process(), this does
not de-dupe on id).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "SOURCE_CANDIDATES_merch.csv")
JSONL_PATH = os.path.join(HERE, "inspirations_merch.jsonl")

FIELDNAMES = [
    "id", "query_id", "query", "query_source", "target_domain", "topic_slug",
    "title", "source_url", "source_domain", "source_type", "thumbnail_path",
    "thumbnail_status", "short_content_understanding", "style_tags",
    "collection_method", "discovered_via", "source_rank", "topic_mapping_status",
    "quality_score", "duplicate_status", "review_status", "notes",
]

NEW_ROWS = [
    dict(
        id="merch_S013_003", query_id="S013", query="Silk Road cultural merch design",
        query_source="niche_topic", target_domain="merch", topic_slug="silk-road",
        title="Samarkand T Shirt, Uzbekistan Islamic Architecture Tee, Gift Silk Road Travel Souvenir Shirt",
        source_url="https://www.pinterest.com/pin/4590786572615479424/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S013_003.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Real Etsy apparel listing ($31.83): garment-dyed cotton tee printed with a Samarkand skyline illustration and 'SAMARKAND / UZBEKISTAN' wordmark, explicitly marketed as a 'Silk Road Travel Souvenir Shirt' -- a genuine Silk Road-themed souvenir merch product, not a photo of the region itself.",
        style_tags="cultural_creative;silk_road;apparel;souvenir",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "Silk Road souvenir merchandise design" (interactive browser session, second pass with more specific search terms per DAILY_REPORT.md next-action #3)',
        source_rank="3", topic_mapping_status="mapped_stub", quality_score="B",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for silk-road (see DAILY_REPORT.md 'Still thin' / recommended next action #3); original batch's 2 records (WebSearch+curl) scored C/B and were logo/textile-photo references rather than real products.",
    ),
    dict(
        id="merch_S013_004", query_id="S013", query="Silk Road cultural merch design",
        query_source="niche_topic", target_domain="merch", topic_slug="silk-road",
        title="Xijiu Silk Road Liquor Packaging",
        source_url="https://www.pinterest.com/pin/140104238402078354/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S013_004.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Award-winning packaging design (A' Design Award, Silver, 2023) for a 'Jiang-flavor' liquor series: bottle set + display box explicitly designed around Silk Road landmarks, elements and culture with a modernized Chinese-cultural creative approach -- a genuine, high-quality Silk Road-themed product/packaging design.",
        style_tags="cultural_creative;silk_road;packaging;award_winning",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "Silk Road souvenir merchandise design" (interactive browser session, second pass)',
        source_rank="4", topic_mapping_status="mapped_stub", quality_score="A",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for silk-road; verified via live pin page description (A' Design Award listing), not fabricated.",
    ),
    dict(
        id="merch_S014_002", query_id="S014", query="modernized cultural artifact product design",
        query_source="niche_topic", target_domain="merch", topic_slug="modernized-artifact",
        title="Brutalist Roman Ruin Catch-All Bowl - Free 3D Print Model - MakerWorld",
        source_url="https://www.pinterest.com/pin/1045961082225896665/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S014_002.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Real MakerWorld 3D-print product listing: a Roman-ruin/temple-ruin architectural motif reinterpreted as a minimalist brutalist ceramic-style catch-all bowl for home decor -- a genuine 'ancient artifact modernized into a contemporary product' design, not a photo of an actual ruin.",
        style_tags="cultural_artifact;brutalist;homeware;3d_print",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "ancient artifact modern reinterpretation product design" (interactive browser session, second pass with more specific search terms per DAILY_REPORT.md next-action #3)',
        source_rank="2", topic_mapping_status="mapped_stub", quality_score="B",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for modernized-artifact (see DAILY_REPORT.md 'Still thin' / recommended next action #3); original batch had only 1 marginal C-grade record (a generic abstract art print, not clearly artifact-derived).",
    ),
    dict(
        id="merch_S014_003", query_id="S014", query="modernized cultural artifact product design",
        query_source="niche_topic", target_domain="merch", topic_slug="modernized-artifact",
        title="Amphora Vase Necklace // African Jewelry, Gold Jewelry, Afrocentric, Ancient Jewelry, Ancient Egypt, Egyptian Jewelry - Etsy",
        source_url="https://www.pinterest.com/pin/254031235227136501/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S014_003.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Real Etsy jewelry listing ($48.00, Afrohemien shop): gold-plated pendant shaped as a miniature ancient amphora vase on a 14kt gold-filled chain -- an ancient artifact form (amphora) directly modernized into a wearable product.",
        style_tags="cultural_artifact;jewelry;ancient_egypt",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "ancient artifact modern reinterpretation product design" (interactive browser session, second pass)',
        source_rank="3", topic_mapping_status="mapped_stub", quality_score="B",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for modernized-artifact; verified via live pin page description and price, not fabricated.",
    ),
    dict(
        id="merch_S015_003", query_id="S015", query="cultural fusion product design",
        query_source="niche_topic", target_domain="merch", topic_slug="cultural-fusion",
        title="Folk Kit + Bonus, an Animal Illustration by Ivanna-Ivashka | Creative Market",
        source_url="https://www.pinterest.com/pin/684969424605041707/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S015_003.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Real Creative Market graphic-asset product ($15.00): a Scandi-folk-pattern illustration kit shown applied across a full packaging/merch flatlay (tote bag, bottle labels, pouches, stickers, boxes) -- a genuine cultural-pattern-fusion asset kit for product design, matched by Pinterest's own board text 'Shop cultural fusion pattern packaging design'.",
        style_tags="cultural_fusion;packaging;pattern_kit",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "cultural fusion pattern packaging design" (interactive browser session, second pass with more specific search terms per DAILY_REPORT.md next-action #3)',
        source_rank="3", topic_mapping_status="mapped_stub", quality_score="B",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for cultural-fusion (see DAILY_REPORT.md 'Still thin' / recommended next action #3), adding a packaging-specific record alongside the original batch's 2 fashion-only records.",
    ),
    dict(
        id="merch_S015_004", query_id="S015", query="cultural fusion product design",
        query_source="niche_topic", target_domain="merch", topic_slug="cultural-fusion",
        title="Fusion, Visual Identity for Takeaway Streetfood Cafe with fusion cuisine",
        source_url="https://www.pinterest.com/pin/610167449555913969/",
        source_domain="pinterest.com", source_type="pinterest_pin",
        thumbnail_path="thumbnails/merch/S015_004.jpg", thumbnail_status="AVAILABLE",
        short_content_understanding="Real brand-identity design project (by Cara Aguavella): full logo, food-truck livery, can/box packaging and sticker system for a streetfood cafe specializing in fusion cuisine blending diverse culinary traditions -- a genuine, complete cultural-fusion brand-identity product design, not a food photo.",
        style_tags="cultural_fusion;brand_identity;packaging;food_truck",
        collection_method="ChromeBrowser+PinterestGridExtract+PageText",
        discovered_via='Pinterest search grid "east meets west fusion brand identity design" (interactive browser session, second pass)',
        source_rank="4", topic_mapping_status="mapped_stub", quality_score="A",
        duplicate_status="UNIQUE", review_status="PENDING",
        notes="Second-pass interactive-browser addendum for cultural-fusion; verified via live pin page description, not fabricated. Strongest of the second-pass cultural-fusion records -- a complete, cohesive brand-identity system rather than a single product.",
    ),
]

if __name__ == "__main__":
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        for r in NEW_ROWS:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})

    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        for r in NEW_ROWS:
            jr = dict(r)
            jr["style_tags"] = [t for t in r["style_tags"].split(";") if t]
            f.write(json.dumps(jr, ensure_ascii=False) + "\n")

    print(f"Appended {len(NEW_ROWS)} rows to {os.path.basename(CSV_PATH)} and {os.path.basename(JSONL_PATH)}")
