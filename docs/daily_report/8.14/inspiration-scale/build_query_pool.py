#!/usr/bin/env python3
"""Builds query_pool.csv, selected_queries.csv, query_coverage.csv for the
8.14 inspiration-scale batch from researched A1 (exploration.jsonl) and A2
(curify-frontend topic registry) source data. A3 is blocked (see
user_queries_input_schema.csv) so it contributes zero rows this round.

Source data below was gathered by direct inspection of:
  - agentic-adhoc/visual-intent-routing/benchmarks/vir_v2/data/candidates/exploration.jsonl
  - curify-frontend/messages/en/topics.json (185 declared topics)
  - curify-frontend/lib/taxonomy.json (tier1-tier4 vocabulary)
Every row's source_reference cites the exact file/key it was derived from.
Not a live scraper -- a deterministic builder over a fixed, cited dataset.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Prior pilot's 10 queries (docs/daily_report/8.8 + 8.12), for overlap comparison.
OLD_PILOT_QUERIES = {
    "figure": "merch", "sticker": "merch", "logo": "brand_design",
    "business card": "brand_design", "coffee package": "packaging",
    "gift box": "packaging", "product photo": "ecommerce",
    "influencer post": "ecommerce", "flashcard": "edtech", "certificate": "edtech",
}

# columns: id, query, normalized_query, query_source, target_domain,
# secondary_domain, source_reference, existing_topic_slug, topic_mapping_status,
# existing_pilot_overlap, priority, priority_reason, notes
ROWS = [
    # --- A1: exploration_jsonl (4 usable clusters out of 10; one representative
    # query per cluster -- the other 2 of 3 lines per cluster are zh/mixed
    # near-duplicates of the same intent, not distinct design intents) ---
    dict(query="Explore three visual directions for a calm home-fragrance launch centered on an aroma diffuser.",
         normalized_query="home fragrance diffuser launch campaign visuals",
         query_source="exploration_jsonl", target_domain="ecommerce", secondary_domain="brand_design",
         source_reference="exploration.jsonl id=004,014,024 cluster=home-fragrance-launch (EN line id=014)",
         existing_topic_slug="ecommerce;showcase", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium",
         priority_reason="Real benchmark query, clear ecommerce product-launch intent; moderate confidence per A1 audit (synthetic template-routing prompt, not organic search).",
         notes="A1 cluster home-fragrance-launch; zh/mixed variants (004,024) are translations of the same intent, not separate queries."),
    dict(query="Explore three visual directions for a Marvel character world focused on personalities and relationship dynamics.",
         normalized_query="Marvel character poster merch design",
         query_source="exploration_jsonl", target_domain="merch", secondary_domain="",
         source_reference="exploration.jsonl id=005,015,025 cluster=marvel-personality-world (EN line id=015)",
         existing_topic_slug="merch;character-ip;fan-art", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium",
         priority_reason="Fandom/character-merch intent maps to merch + character-ip/fan-art, both thin (stub) Curify topics -- helps fill a topic gap, not just a query gap.",
         notes="A1 cluster marvel-personality-world."),
    dict(query="Explore three visual directions for a beginner-friendly campaign for learning English homophones and confusing words.",
         normalized_query="English homophones flashcard learning design",
         query_source="exploration_jsonl", target_domain="edtech", secondary_domain="",
         source_reference="exploration.jsonl id=006,016,026 cluster=homophone-learning-campaign (EN line id=016)",
         existing_topic_slug="language;vocabulary;flashcards", topic_mapping_status="mapped_full",
         existing_pilot_overlap="close_variation",
         priority="medium",
         priority_reason="Clean edtech match (vocabulary/flashcards), but overlaps old pilot's 'flashcard' query in spirit -- kept for the specific homophone/confusable-words angle, which the old pilot never covered.",
         notes="A1 cluster homophone-learning-campaign."),
    dict(query="Explore three visual directions for a Chiikawa-themed cozy reading space and lifestyle idea.",
         normalized_query="Chiikawa character lifestyle merch design",
         query_source="exploration_jsonl", target_domain="merch", secondary_domain="",
         source_reference="exploration.jsonl id=010,020,030 cluster=chiikawa-reading-space (EN line id=020)",
         existing_topic_slug="merch;character-ip;fan-art", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium",
         priority_reason="Same character-merch/topic-gap logic as marvel-personality-world; different IP (Chiikawa vs Marvel) so genuinely distinct visual direction.",
         notes="A1 cluster chiikawa-reading-space."),

    # --- A2: niche_topic (derived from curify-frontend messages/en/topics.json + lib/taxonomy.json) ---
    # merch
    dict(query="IP character merch flatlay design", normalized_query="IP character merch flatlay design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="topics.json#topics.merch (description: 'IP-themed flatlay mockups')",
         existing_topic_slug="merch", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high",
         priority_reason="Direct description match on the fully-authored 'merch' topic page.", notes=""),
    dict(query="sticker sheet print on demand design", normalized_query="sticker sheet POD design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="topics.json#topics.merch keywords=['sticker design','print on demand','POD','DTG']",
         existing_topic_slug="merch;stickers", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="close_variation", priority="low",
         priority_reason="Close variation of old pilot query 'sticker' -- kept in reserve only.", notes=""),
    dict(query="character sprite sheet merch design", normalized_query="character sprite sheet merch design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="topics.json#topics.merch (description: 'character sprite sheets')",
         existing_topic_slug="merch;character-ip", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="Distinct sub-intent of merch (sprite sheet vs flatlay), thin topic (character-ip) benefits from more examples.", notes=""),
    dict(query="brand mascot character design", normalized_query="brand mascot character design",
         query_source="niche_topic", target_domain="merch", secondary_domain="brand_design",
         source_reference="taxonomy.json#tier3.character=mascots; topics.json#topics.mascots (stub)",
         existing_topic_slug="mascots", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="mascots is a declared but stub (no title/description) topic -- zero authored content today, high gap-fill value.", notes=""),
    dict(query="fan art character IP poster design", normalized_query="fan art character IP poster design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.character=fan-art; topics.json#topics.fan-art (stub)",
         existing_topic_slug="fan-art", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium", priority_reason="Stub topic, same gap-fill logic as mascots.", notes=""),
    dict(query="original IP character design for merch", normalized_query="original IP character merch design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.character=original-ip; topics.json#topics.original-ip (stub)",
         existing_topic_slug="original-ip", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium", priority_reason="Stub topic; distinct from fan-art/character-ip (original IP creation vs existing-fandom content).", notes=""),
    dict(query="Dunhuang mural inspired museum merch design", normalized_query="Dunhuang museum merch design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.culture=dunhuang; tier4.cultures=['Dunhuang']; topics.json#topics.dunhuang (stub)",
         existing_topic_slug="dunhuang", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="Directly matches task brief's 'museum merch / cultural creative products' example; stub topic with zero authored examples today.", notes=""),
    dict(query="Mogao Caves art museum souvenir design", normalized_query="Mogao Caves museum souvenir design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.culture=mogao-caves; topics.json#topics.mogao-caves (stub)",
         existing_topic_slug="mogao-caves", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="Same cultural-merch/museum-souvenir gap-fill category as Dunhuang, distinct subject.", notes=""),
    dict(query="Silk Road cultural artifact merch design", normalized_query="Silk Road cultural merch design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.culture=silk-road; topics.json#topics.silk-road (stub)",
         existing_topic_slug="silk-road", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium", priority_reason="Same cultural-merch gap-fill category; broader/less iconic subject than Dunhuang/Mogao so slightly lower priority.", notes=""),
    dict(query="modernized cultural artifact product design", normalized_query="modernized cultural artifact product design",
         query_source="niche_topic", target_domain="merch", secondary_domain="",
         source_reference="taxonomy.json#tier3.culture=modernized-artifact; topics.json#topics.modernized-artifact (stub)",
         existing_topic_slug="modernized-artifact", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="medium", priority_reason="Stub topic; conceptually the 'contemporary reinterpretation' angle of cultural merch.", notes=""),
    dict(query="cultural fusion product design", normalized_query="cultural fusion product design",
         query_source="niche_topic", target_domain="merch", secondary_domain="brand_design",
         source_reference="taxonomy.json#tier3.culture=cultural-fusion; topics.json#topics.cultural-fusion (stub)",
         existing_topic_slug="cultural-fusion", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="low", priority_reason="Broadest/vaguest of the culture-tier3 stub topics; kept but lower confidence of a crisp visual direction.", notes=""),

    # packaging
    dict(query="food packaging label design", normalized_query="food packaging label design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=food-packaging (undeclared in topics.json, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="partial_overlap", priority="high",
         priority_reason="food-packaging is real taxonomy vocab with no dedicated page; broader than old pilot's 'coffee package' (one product) so still net-new coverage.", notes=""),
    dict(query="beverage packaging bottle design", normalized_query="beverage packaging bottle design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=beverage-packaging (undeclared, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="partial_overlap", priority="high", priority_reason="Bottle/cup packaging explicitly named in task brief's packaging domain examples.", notes=""),
    dict(query="cosmetic packaging design", normalized_query="cosmetic packaging design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=cosmetic-packaging (undeclared, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="high", priority_reason="No cosmetics coverage at all in old pilot; explicit taxonomy vocab.", notes=""),
    dict(query="electronics packaging design", normalized_query="electronics packaging design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=electronics-packaging (undeclared, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="medium", priority_reason="No electronics coverage in old pilot; genuinely new product category.", notes=""),
    dict(query="luxury packaging design", normalized_query="luxury packaging design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="brand_design",
         source_reference="taxonomy.json#tier3.product=luxury-packaging (undeclared, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="high", priority_reason="Distinct style tier (luxury) missing from old pilot entirely -- good style-diversity gap-fill.", notes=""),
    dict(query="gift box packaging design", normalized_query="gift box packaging design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=gift-packaging (undeclared, parent=packaging)",
         existing_topic_slug="packaging", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="close_variation", priority="low",
         priority_reason="Close variation of old pilot query 'gift box' -- reserved, not selected.", notes=""),
    dict(query="unboxing experience packaging design", normalized_query="unboxing experience packaging design",
         query_source="niche_topic", target_domain="packaging", secondary_domain="ecommerce",
         source_reference="topics.json#topics.packaging keywords=['unboxing']",
         existing_topic_slug="packaging", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium", priority_reason="Unboxing-moment framing is a distinct visual/content direction not covered by product-type packaging queries above.", notes=""),

    # ecommerce
    dict(query="ecommerce hero banner design", normalized_query="ecommerce hero banner design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="topics.json#topics.ecommerce keywords=['hero-banner']; taxonomy.json#tier3.product=hero-banner",
         existing_topic_slug="ecommerce", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Direct keyword match on fully-authored ecommerce topic.", notes=""),
    dict(query="product lifestyle shot ecommerce design", normalized_query="product lifestyle shot ecommerce design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=lifestyle-shot (undeclared, parent=ecommerce)",
         existing_topic_slug="ecommerce", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="high", priority_reason="Lifestyle-shot is a distinct visual treatment from studio/flat-lay product photos.", notes=""),
    dict(query="product flat lay ecommerce photography", normalized_query="product flat lay ecommerce photography",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="topics.json#topics.ecommerce keywords=['flat-lay']; taxonomy.json#tier3.product=flat-lay",
         existing_topic_slug="ecommerce", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Direct keyword match, distinct composition style from hero-banner.", notes=""),
    dict(query="product detail image ecommerce design", normalized_query="product detail image ecommerce design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="topics.json#topics.ecommerce keywords=['detail-image']",
         existing_topic_slug="ecommerce", topic_mapping_status="mapped_full",
         existing_pilot_overlap="partial_overlap", priority="low",
         priority_reason="Overlaps old pilot's 'product photo' in spirit (both close-up product photography) -- reserved.", notes=""),
    dict(query="product launch mood board design", normalized_query="product launch mood board design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="brand_design",
         source_reference="topics.json#topics.showcase keywords=['mood-board','launch']; taxonomy.json#tier3.product=mood-board",
         existing_topic_slug="showcase", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium", priority_reason="Mood-board framing bridges ecommerce launch content and brand_design direction-setting.", notes=""),
    dict(query="product lineup promotional poster design", normalized_query="product lineup promotional poster design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=product-lineup,promotional-poster (undeclared, parent=showcase)",
         existing_topic_slug="showcase", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="medium", priority_reason="Multi-product campaign composition, distinct from single-product ecommerce queries above.", notes=""),
    dict(query="DTC product campaign visual design", normalized_query="DTC product campaign visual design",
         query_source="niche_topic", target_domain="ecommerce", secondary_domain="",
         source_reference="topics.json#topics.ecommerce keywords=['dtc','shopify']",
         existing_topic_slug="ecommerce", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium", priority_reason="DTC/Shopify brand-campaign angle, distinct from generic marketplace product photography.", notes=""),

    # brand_design
    dict(query="logo application brand identity design", normalized_query="logo application brand identity design",
         query_source="niche_topic", target_domain="brand_design", secondary_domain="",
         source_reference="taxonomy.json#tier3.product=logo-application (undeclared, parent=branding)",
         existing_topic_slug="branding", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="close_variation", priority="low",
         priority_reason="Close variation of old pilot query 'logo' -- reserved.", notes=""),
    dict(query="brand color system design", normalized_query="brand color system design",
         query_source="niche_topic", target_domain="brand_design", secondary_domain="",
         source_reference="topics.json#topics.branding keywords=['color-system']",
         existing_topic_slug="branding", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Color-system is a distinct brand-design artifact from logo work, direct keyword match, no old-pilot coverage.", notes=""),
    dict(query="brand typography system design", normalized_query="brand typography system design",
         query_source="niche_topic", target_domain="brand_design", secondary_domain="",
         source_reference="topics.json#topics.branding keywords=['typography']",
         existing_topic_slug="branding", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Typography system is a distinct brand-design artifact, direct keyword match.", notes=""),
    dict(query="brand book visual identity design", normalized_query="brand book visual identity design",
         query_source="niche_topic", target_domain="brand_design", secondary_domain="",
         source_reference="topics.json#topics.branding keywords=['brand-book','visual-identity']",
         existing_topic_slug="branding", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Multi-page identity-system artifact, distinct from single-asset logo/color/type queries.", notes=""),
    dict(query="new brand launch style sheet design", normalized_query="new brand launch style sheet design",
         query_source="niche_topic", target_domain="brand_design", secondary_domain="",
         source_reference="topics.json#topics.branding description ('for new brands and rebrands')",
         existing_topic_slug="branding", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium", priority_reason="Launch/rebrand framing distinct from static identity-artifact queries above.", notes=""),

    # edtech
    dict(query="flashcard visual design for learning", normalized_query="flashcard visual design for learning",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.flashcards (stub); taxonomy.json#tier2.learning=flashcards",
         existing_topic_slug="flashcards", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="close_variation", priority="low",
         priority_reason="Close variation of old pilot query 'flashcard' -- reserved.", notes=""),
    dict(query="vocabulary bilingual word poster design", normalized_query="vocabulary bilingual word poster design",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.vocabulary (full page, description: 'bilingual word posters')",
         existing_topic_slug="vocabulary", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Direct description match on a fully-authored topic.", notes=""),
    dict(query="dialogue conversation practice card design", normalized_query="dialogue conversation practice card design",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.dialogue (full page, description: 'conversation practice cards')",
         existing_topic_slug="dialogue", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="high", priority_reason="Direct description match on a fully-authored topic, distinct format from vocabulary posters.", notes=""),
    dict(query="study sheet infographic design", normalized_query="study sheet infographic design",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.study-sheets (stub); taxonomy.json#tier3.design=study-sheets",
         existing_topic_slug="study-sheets", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="Stub topic, zero authored content today -- high gap-fill value.", notes=""),
    dict(query="mind map educational infographic design", normalized_query="mind map educational infographic design",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.mind-maps (stub); taxonomy.json#tier3.design=mind-maps",
         existing_topic_slug="mind-maps", topic_mapping_status="mapped_stub",
         existing_pilot_overlap="none", priority="high", priority_reason="Stub topic, distinct visual form (node/branch diagram) from linear study sheets.", notes=""),
    dict(query="information card knowledge summary design", normalized_query="information card knowledge summary design",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="topics.json#topics.information-card (full page, displayName 'Info Cards')",
         existing_topic_slug="information-card", topic_mapping_status="mapped_full",
         existing_pilot_overlap="none", priority="medium", priority_reason="Fully-authored topic; adjacent to study-sheets/mind-maps but a distinct single-fact-card format.", notes=""),
    dict(query="classroom worksheet design for kids", normalized_query="classroom worksheet design for kids",
         query_source="niche_topic", target_domain="edtech", secondary_domain="",
         source_reference="taxonomy.json#tier4.school=['Classroom Objects','School Subjects','Stationery and Supplies']",
         existing_topic_slug="learning", topic_mapping_status="needs_confirmation",
         existing_pilot_overlap="none", priority="medium", priority_reason="School/classroom vocabulary bucket has no dedicated topic page; worksheet framing untested in old pilot (which had flashcard/certificate only).", notes=""),
]

FIELDNAMES = [
    "id", "query", "normalized_query", "query_source", "target_domain",
    "secondary_domain", "source_reference", "existing_topic_slug",
    "topic_mapping_status", "priority", "priority_reason",
    "existing_pilot_overlap", "selection_status", "notes",
]


def build():
    for i, r in enumerate(ROWS, start=1):
        r["id"] = f"S{i:03d}"
        nq = r["normalized_query"].strip().lower()
        r["selection_status"] = "reserve" if r["existing_pilot_overlap"] == "close_variation" else "selected"
        if nq in OLD_PILOT_QUERIES:
            r["existing_pilot_overlap"] = "exact_duplicate"
            r["selection_status"] = "rejected"

    pool_path = os.path.join(HERE, "query_pool.csv")
    with open(pool_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in ROWS:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})

    selected = [r for r in ROWS if r["selection_status"] == "selected"]
    sel_path = os.path.join(HERE, "selected_queries.csv")
    with open(sel_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in selected:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})

    # coverage
    domains = ["merch", "packaging", "ecommerce", "edtech", "brand_design"]
    cov_path = os.path.join(HERE, "query_coverage.csv")
    with open(cov_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target_domain", "pool_count", "selected_count", "reserve_count",
                    "a1_count", "a2_count", "a3_count", "mapped_full_count",
                    "mapped_stub_count", "needs_confirmation_count", "old_pilot_overlap_count"])
        for d in domains:
            rows_d = [r for r in ROWS if r["target_domain"] == d]
            w.writerow([
                d,
                len(rows_d),
                len([r for r in rows_d if r["selection_status"] == "selected"]),
                len([r for r in rows_d if r["selection_status"] == "reserve"]),
                len([r for r in rows_d if r["query_source"] == "exploration_jsonl"]),
                len([r for r in rows_d if r["query_source"] == "niche_topic"]),
                len([r for r in rows_d if r["query_source"] == "user_query"]),
                len([r for r in rows_d if r["topic_mapping_status"] == "mapped_full"]),
                len([r for r in rows_d if r["topic_mapping_status"] == "mapped_stub"]),
                len([r for r in rows_d if r["topic_mapping_status"] == "needs_confirmation"]),
                len([r for r in rows_d if r["existing_pilot_overlap"] in ("close_variation", "partial_overlap", "exact_duplicate")]),
            ])

    print(f"pool={len(ROWS)} selected={len(selected)} reserve={len(ROWS)-len(selected)}")
    for d in domains:
        n = len([r for r in ROWS if r["target_domain"] == d and r["selection_status"] == "selected"])
        print(f"  {d}: {n} selected")


if __name__ == "__main__":
    build()
