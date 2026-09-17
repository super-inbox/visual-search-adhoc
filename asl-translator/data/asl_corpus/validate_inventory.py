#!/usr/bin/env python3
"""Validate asl_corpus/inventory.json — the canonical live-status source for
the 13 private Curify ASL corpus videos.

Stdlib-only. Local, read-only: does not open any video, does not call any
model or API, does not modify any file. Run before trusting or committing
any change to inventory.json.

Usage:
    python3 asl-translator/data/asl_corpus/validate_inventory.py

Exit codes: 0 = all checks passed, 1 = one or more checks failed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INVENTORY = HERE / "inventory.json"
VIDEOS_DIR = HERE / "videos"

EXPECTED_COUNT = 13
VALID_INPUT_STATUS = {"clean", "masked", "contaminated_history", "uncertain"}
VALID_INDEPENDENCE = {"independent", "non_independent", "unknown", "not_applicable"}
VALID_HUMAN_VERIFIED = {True, False, "unknown"}
VALID_AUTHENTICITY = {"confirmed", "uncertain"}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def main() -> int:
    errors: list[str] = []

    if not INVENTORY.exists():
        print(f"FAIL: {INVENTORY} does not exist")
        return 1

    doc = json.loads(INVENTORY.read_text(encoding="utf-8"))
    videos = doc.get("videos", [])

    # ---- exactly 13 unique videos ----------------------------------------
    ids = [v.get("video_id") for v in videos]
    if len(videos) != EXPECTED_COUNT:
        fail(errors, f"expected exactly {EXPECTED_COUNT} entries, found {len(videos)}")
    if len(ids) != len(set(ids)):
        seen, dupes = set(), set()
        for i in ids:
            (dupes if i in seen else seen).add(i)
        fail(errors, f"duplicate video_id(s) in inventory.json: {sorted(dupes)}")
    if None in ids or "" in ids:
        fail(errors, "one or more entries has a missing/empty video_id")

    # ---- every entry maps to exactly one real video on disk --------------
    if VIDEOS_DIR.exists():
        disk_ids = {p.stem for p in VIDEOS_DIR.glob("*.mp4")}
        inv_ids = set(i for i in ids if i)
        missing_from_inventory = disk_ids - inv_ids
        missing_from_disk = inv_ids - disk_ids
        if missing_from_inventory:
            fail(errors, f"videos/ has files with no inventory entry: {sorted(missing_from_inventory)}")
        if missing_from_disk:
            fail(errors, f"inventory.json has entries with no matching file in videos/: {sorted(missing_from_disk)}")
    else:
        print(f"NOTE: {VIDEOS_DIR} not found — skipping disk cross-check (private video files may not be checked out here)")

    # ---- per-entry structural + semantic checks ---------------------------
    for v in videos:
        vid = v.get("video_id", "<unknown>")
        inp = v.get("input", {})
        ref = v.get("reference", {})
        pred = v.get("prediction", {})
        ev = v.get("evaluation", {})

        if inp.get("status") not in VALID_INPUT_STATUS:
            fail(errors, f"{vid}: input.status {inp.get('status')!r} not in {VALID_INPUT_STATUS}")
        if inp.get("authenticity_status") not in VALID_AUTHENTICITY:
            fail(errors, f"{vid}: input.authenticity_status {inp.get('authenticity_status')!r} not in {VALID_AUTHENTICITY}")

        if ref.get("available"):
            if ref.get("independence") not in VALID_INDEPENDENCE:
                fail(errors, f"{vid}: reference.independence {ref.get('independence')!r} not in {VALID_INDEPENDENCE}")
            if ref.get("human_verified") not in VALID_HUMAN_VERIFIED:
                fail(errors, f"{vid}: reference.human_verified {ref.get('human_verified')!r} not a valid value")

            usable = ref.get("usable_for_official_metrics")
            independent = ref.get("independence") == "independent"
            verified = ref.get("human_verified") is True

            # ---- core rule: usable_for_official_metrics=true requires BOTH
            #      independence AND human verification to actually be true ----
            if usable and not (independent and verified):
                fail(errors, (
                    f"{vid}: usable_for_official_metrics=true but provenance does not support it "
                    f"(independence={ref.get('independence')!r}, human_verified={ref.get('human_verified')!r}). "
                    f"Both must be independent/True."
                ))

            # ---- SignCaption can never be the OFFICIAL scoring reference ----
            # Checked via the explicit is_primary_source_signcaption flag, NOT
            # by string-matching "signcaption" in type/source/notes. A video can
            # legitimately have an independent human/reference gold AND a
            # SignCaption output stored only as an auxiliary comparison (e.g.
            # 155 and 1252 both mention a SignCaption candidate in their notes
            # while their PRIMARY reference is something else entirely) — that
            # must not by itself disqualify the primary reference. Only a
            # reference whose actual generating source IS SignCaption may never
            # be marked usable_for_official_metrics.
            if "is_primary_source_signcaption" not in ref:
                fail(errors, f"{vid}: reference.available=true but is_primary_source_signcaption is not set (required, explicit — do not infer it from type/source text)")
            elif ref.get("is_primary_source_signcaption") and usable:
                fail(errors, f"{vid}: primary reference source is SignCaption but usable_for_official_metrics=true — SignCaption can never be the official scoring gold, even though an independent human reference for the same video could be")

            # ---- 1320-specific: human_verified=true requires explicit
            #      provenance describing the verification, not just a claim ----
            if vid.startswith("1320_") and ref.get("human_verified") is True:
                pq = (ref.get("provenance_quality") or "").lower()
                if "pending" in pq or len(pq.strip()) < 20:
                    fail(errors, f"{vid}: human_verified=true but provenance_quality does not document an actual verification method")
        else:
            if ref.get("usable_for_official_metrics"):
                fail(errors, f"{vid}: reference.available=false but usable_for_official_metrics=true — invented status")

        if pred.get("available") and not isinstance(pred.get("configs"), list):
            fail(errors, f"{vid}: prediction.available=true but prediction.configs is not a list")

        if not ev.get("recommended_status"):
            fail(errors, f"{vid}: evaluation.recommended_status is missing")

    # ---- hard-coded canonical-status requirements (explicit, from spec) ---
    by_id = {v["video_id"]: v for v in videos if v.get("video_id")}

    def require(vid: str, path: tuple[str, ...], expected):
        node = by_id.get(vid)
        if node is None:
            fail(errors, f"REQUIRED CHECK: {vid} missing from inventory entirely")
            return
        cur = node
        for key in path:
            cur = cur.get(key, "<missing>") if isinstance(cur, dict) else "<missing>"
        if cur != expected:
            fail(errors, f"REQUIRED CHECK FAILED: {vid} {'.'.join(path)} = {cur!r}, expected {expected!r}")

    require("1252_1000016397_76.8s", ("reference", "independence"), "non_independent")
    require("1252_1000016397_76.8s", ("reference", "usable_for_official_metrics"), False)
    require("1252_1000016397_76.8s", ("evaluation", "recommended_status"), "diagnostic_only")

    require("155_demo_asl-demo-translation_26.7s", ("reference", "independence"), "unknown")
    require("155_demo_asl-demo-translation_26.7s", ("reference", "human_verified"), "unknown")
    require("155_demo_asl-demo-translation_26.7s", ("reference", "usable_for_official_metrics"), False)
    require("155_demo_asl-demo-translation_26.7s", ("evaluation", "recommended_status"), "provenance_pending")

    require("1320_1000022357_137.2s", ("input", "status"), "masked")
    require("1320_1000022357_137.2s", ("reference", "independence"), "independent")
    require("1320_1000022357_137.2s", ("reference", "human_verified"), False)
    require("1320_1000022357_137.2s", ("reference", "usable_for_official_metrics"), False)
    require("1320_1000022357_137.2s", ("evaluation", "recommended_status"), "independent_candidate_pending_human_verification")

    require("1434_screenrec_youtube_16.6s", ("reference", "usable_for_official_metrics"), False)
    require("1457_10426_28.3s", ("input", "authenticity_status"), "uncertain")

    # ---- report -------------------------------------------------------
    if errors:
        print(f"FAILED — {len(errors)} problem(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK — {len(videos)} entries, all checks passed:")
    print("  - exactly 13 unique video IDs")
    print("  - inventory matches videos/ on disk (when present)")
    print("  - no usable_for_official_metrics=true without independent+verified provenance")
    print("  - no SignCaption reference marked official gold")
    print("  - 1252 correctly marked non_independent / not usable / diagnostic_only")
    print("  - 155 correctly marked independence=unknown / not usable / provenance_pending")
    print("  - 1320 correctly marked masked / independent / not yet human_verified")
    print("  - 1434 not usable for official metrics")
    print("  - 1457 authenticity marked uncertain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
