"""P0-14 step 0: How2Sign data audit + concept vocabulary (CPU, stdlib only, no model).

Reads the three How2Sign re-aligned CSVs (tab-separated). The concept vocabulary is selected from
**train references only**. Val/test counts are computed afterwards and reported, never used to select.

Outputs (under --out):
  audit/data_audit.json             split sizes, group counts, cross-split overlap, duplicate checks
  audit/near_duplicates_test.csv    test clips whose reference is an exact / near duplicate of a train reference
  concepts/candidate_vocab_train.csv  top content-lemma families by train clip frequency (pre-filter view)
  concepts/concept_list_v1.csv      selected concepts (Tier L lexical + Tier S semantic groups) with counts
  concepts/concept_rules_v1.json    every list/threshold used, so the selection can be re-run byte-for-byte

Usage: python3 -I build_concepts.py TRAIN_CSV VAL_CSV TEST_CSV OUT_DIR
"""
import collections, csv, hashlib, json, os, re, sys

train_csv, val_csv, test_csv, out = sys.argv[1:5]

# ---------------------------------------------------------------- pre-registered selection rules
RULES = {
    "tokenizer": r"[a-z]+(?:'[a-z]+)?  after lowercasing and mapping curly quotes to '",
    "future_aux_removed": "phrases 'going to' / 'gonna' are deleted before tokenizing (English future auxiliary)",
    "tierL_min_train_clip_df": 400,          # ~1.3 % of 31k train clips; expected test positives ~30
    "tierL_max_train_clip_df_frac": 0.30,    # drop near-ubiquitous words
    "tierL_min_train_videos": 100,           # positives spread over >=100 distinct source videos
    "tierL_max_top10_video_share": 0.20,     # <=20 % of positives from the 10 most frequent videos
    "tierL_max_concepts": 40,                # cap; ranked by train clip DF
    "lemma_min_base_count": 5,
}

STOP = set("""
a about above after again against all almost also although always am among an and another any anybody anyone
anything anyway anywhere are aren't around as at away back be because been before being below between both but
by can can't cannot could couldn't did didn't do does doesn't doing don't done down during each either else enough
especially even ever every everybody everyone everything few for from further had hadn't has hasn't have haven't
having he he'd he'll he's her here here's hers herself him himself his how how's however i i'd i'll i'm i've if in
into is isn't it it'd it'll it's its itself just let let's may maybe me might mine more most much must mustn't my
myself neither never no nobody none nor not nothing now of off often on once one ones only onto or other others
otherwise our ours ourselves out over own per perhaps quite rather same shall she she'd she'll she's should
shouldn't since so some somebody someone something sometimes somewhat somewhere such than that that'll that's the
their theirs them themselves then there there's these they they'd they'll they're they've this those though through
thus to together too toward towards under until up upon us very via was wasn't we we'd we'll we're we've were weren't
what what's whatever when when's whenever where where's wherever whether which while who who's whoever whole whom
whose why why's will with within without won't would wouldn't yet you you'd you'll you're you've your yours yourself
yourselves
""".split())
# discourse markers / fillers / hedges common in How2Sign spoken-style English
DISCOURSE = set("""
actually ok okay yeah yes um uh oh hi hello hey well like really basically probably definitely certainly simply
pretty sure kind sort bit lot lots little stuff thing things way ways today now right alright guys also usually
generally obviously exactly certain particular able sure course times anymore already still again
""".split())
# light / auxiliary verbs whose English use is mostly grammatical, not lexical content
LIGHT_VERBS = set("go get make take put do have be let want need try see look come use give keep know think say tell".split())
# NOTE: 'want', 'need', 'see', 'look', 'know', 'think', 'use' are lexical ASL signs; we still exclude them from
# Tier L in v1 because in the English references they are dominated by discourse use ("you want to", "you need to",
# "you know", "I think", "let's see"), so the English token is a weak label for the signed concept.
# This choice is recorded in concept_rules_v1.json and can be reverted for a v2 list.
GENERIC = set("one two first next part different good great new many lot important start end side area also".split())
GENERIC -= {"two"}
URL_ARTIFACT = set("com www http https org net".split())  # ".com" etc. in presenter intros  # numbers are handled by the NUMBER group (Tier S)

IRREGULAR = {  # irregular inflections -> base, only for content verbs/nouns that can survive the filters
    "made": "make", "took": "take", "taken": "take", "went": "go", "gone": "go", "got": "get", "gotten": "get",
    "saw": "see", "seen": "see", "bought": "buy", "ate": "eat", "eaten": "eat", "wrote": "write", "written": "write",
    "gave": "give", "given": "give", "held": "hold", "kept": "keep", "found": "find", "felt": "feel", "built": "build",
    "children": "child", "feet": "foot", "teeth": "tooth", "women": "woman", "men": "man", "people": "people",
    "thought": "think", "brought": "bring", "taught": "teach", "caught": "catch", "fought": "fight", "sold": "sell",
    "told": "tell", "drew": "draw", "drawn": "draw", "grew": "grow", "grown": "grow", "knew": "know", "known": "know",
    "going": "go", "ran": "run", "began": "begin", "begun": "begin", "chose": "choose", "chosen": "choose", "spent": "spend",
}
NO_MERGE = set("""
news means evening wedding morning thing things ring string spring bring during nothing something anything everything
glasses series species is was has this its us bus yes always sometimes perhaps lens physics mathematics clothes
""".split())

# Tier S: small semantic groups, word lists fixed here before looking at any model output (exploratory tier)
GROUPS = {
    "NUMBER": "two three four five six seven eight nine ten eleven twelve fifteen twenty thirty forty fifty hundred "
              "thousand million dozen half percent",  # 'one' excluded: mostly pronoun ("this one")
    "COLOR": "color colors colored red blue green yellow black white orange purple pink brown gray grey",
    "FOOD_COOKING": "cook cooking cooked food recipe eat eating bake baking oven kitchen dish meal",
    "BODY_PART": "hand hands arm arms leg legs foot feet head finger fingers knee knees shoulder shoulders hip hips "
                 "body",  # 'back', 'face' excluded: dominated by non-body uses ("go back", "face it")
    "TIME_UNIT": "minute minutes hour hours seconds day days week weeks month months year years",
    # 'second' excluded from TIME_UNIT: mostly ordinal
    "WATER_LIQUID": "water oil milk juice liquid wine coffee tea",
}

# ---------------------------------------------------------------- helpers
def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))

def norm_text(s):
    s = s.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"\bgoing to\b|\bgonna\b", " ", s)

TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")

def tokens(s):
    out = []
    for t in TOK.findall(norm_text(s)):
        if t.endswith("'s"):
            t = t[:-2]
        out.append(t)
    return out

def norm_sentence(s):  # for duplicate detection: punctuation/case-insensitive
    return " ".join(TOK.findall(s.lower().replace("’", "'")))

def signer_proxy(video_name):  # "<ytid>-<k>-rgb_front" -> "k"  (UNVERIFIED proxy; see DATA_AUDIT.md)
    return video_name.rsplit("-rgb_front", 1)[0].rsplit("-", 1)[-1]

splits = {"train": load(train_csv), "val": load(val_csv), "test": load(test_csv)}
sha = {k: hashlib.sha256(open(p, "rb").read()).hexdigest() for k, p in
       [("train", train_csv), ("val", val_csv), ("test", test_csv)]}

# ---------------------------------------------------------------- lemma families from TRAIN only
train_counts = collections.Counter(t for r in splits["train"] for t in tokens(r["SENTENCE"]))

def base_of(w):
    if w in IRREGULAR:
        return IRREGULAR[w]
    if w in NO_MERGE or len(w) <= 3:
        return w
    cands = []
    if w.endswith("ies"): cands.append(w[:-3] + "y")
    if w.endswith("es"): cands.append(w[:-2])
    if w.endswith("s") and not w.endswith("ss"): cands.append(w[:-1])
    if w.endswith("ing"):
        cands += [w[:-3], w[:-3] + "e"]
        if len(w) > 5 and w[-4] == w[-5]: cands.append(w[:-4])
    if w.endswith("ed"):
        cands += [w[:-2], w[:-1]]
        if w.endswith("ied"): cands.append(w[:-3] + "y")
        if len(w) > 4 and w[-3] == w[-4]: cands.append(w[:-3])
    for c in cands:
        if len(c) >= 3 and train_counts.get(c, 0) >= RULES["lemma_min_base_count"]:
            return c
    return w

LEMMA = {w: base_of(w) for w in train_counts}

def lemmas(s):
    return {LEMMA.get(t, base_of(t)) for t in tokens(s)}

EXCLUDE = STOP | DISCOURSE | LIGHT_VERBS | GENERIC | URL_ARTIFACT

# ---------------------------------------------------------------- per-clip annotations
for name, rows in splits.items():
    for r in rows:
        r["_lem"] = lemmas(r["SENTENCE"])
        r["_tok"] = set(tokens(r["SENTENCE"]))
        r["_nw"] = len(tokens(r["SENTENCE"]))
        try:
            r["_dur"] = float(r["END_REALIGNED"]) - float(r["START_REALIGNED"])
        except ValueError:
            r["_dur"] = None

# ---------------------------------------------------------------- candidate vocabulary (train)
train = splits["train"]
N = len(train)
df = collections.Counter(l for r in train for l in r["_lem"])
vids_by = collections.defaultdict(collections.Counter)
forms_by = collections.defaultdict(collections.Counter)
for r in train:
    for l in r["_lem"]:
        vids_by[l][r["VIDEO_ID"]] += 1
for w, c in train_counts.items():
    forms_by[LEMMA[w]][w] += c

def stats(l):
    v = vids_by[l]
    top10 = sum(c for _, c in v.most_common(10))
    return {"train_clip_df": df[l], "train_frac": df[l] / N, "train_videos": len(v),
            "top10_video_share": top10 / max(df[l], 1)}

cand_rows = []
for l, c in df.most_common():
    if len(cand_rows) >= 300:
        break
    if c < 100:
        break
    reason = ("stopword" if l in STOP else "discourse" if l in DISCOURSE else "light_verb" if l in LIGHT_VERBS
              else "generic" if l in GENERIC else "url_artifact" if l in URL_ARTIFACT else "number_word" if l in GROUPS["NUMBER"].split()
              else "too_short" if len(l) <= 2 else "")
    s = stats(l)
    if not reason:
        if s["train_frac"] > RULES["tierL_max_train_clip_df_frac"]: reason = "too_frequent"
        elif s["train_videos"] < RULES["tierL_min_train_videos"]: reason = "few_videos"
        elif s["top10_video_share"] > RULES["tierL_max_top10_video_share"]: reason = "video_concentrated"
        elif c < RULES["tierL_min_train_clip_df"]: reason = "below_min_df"
    cand_rows.append({"lemma": l, **s, "forms": " ".join(f for f, _ in forms_by[l].most_common(6)),
                      "excluded_reason": reason or "eligible"})

eligible = [r for r in cand_rows if r["excluded_reason"] == "eligible"][: RULES["tierL_max_concepts"]]

# ---------------------------------------------------------------- concept definitions
concepts = []
for r in eligible:
    forms = sorted(w for w in train_counts if LEMMA[w] == r["lemma"])
    concepts.append({"concept": r["lemma"].upper(), "tier": "L", "match": "lemma", "key": r["lemma"],
                     "forms": forms})
for g, words in GROUPS.items():
    concepts.append({"concept": g, "tier": "S", "match": "token_any", "key": g, "forms": sorted(set(words.split()))})

def positive(r, c):
    return (c["key"] in r["_lem"]) if c["match"] == "lemma" else bool(r["_tok"] & set(c["forms"]))

def split_stats(rows, c):
    pos = [r for r in rows if positive(r, c)]
    neg = [r for r in rows if not positive(r, c)]
    mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
    return {"n_pos": len(pos), "n_neg": len(neg), "videos_pos": len({r["VIDEO_ID"] for r in pos}),
            "mean_words_pos": mean([r["_nw"] for r in pos]), "mean_words_neg": mean([r["_nw"] for r in neg])}

concept_rows = []
for c in concepts:
    row = {"concept": c["concept"], "tier": c["tier"], "match": c["match"], "forms": " ".join(c["forms"])}
    for s in ("train", "val", "test"):
        st = split_stats(splits[s], c)
        row.update({f"{s}_pos": st["n_pos"], f"{s}_pos_videos": st["videos_pos"]})
        if s == "train":
            row["train_prevalence"] = round(st["n_pos"] / len(splits[s]), 4)
            row["train_len_ratio_pos_neg"] = round(st["mean_words_pos"] / st["mean_words_neg"], 3)
    concept_rows.append(row)

# ---------------------------------------------------------------- leakage / duplicate audit
def groups(rows, key):
    return {key(r) for r in rows}

vid = lambda r: r["VIDEO_ID"]
sp = lambda r: signer_proxy(r["VIDEO_NAME"])
overlap = {}
for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
    overlap[f"{a}-{b}"] = {
        "video_id_overlap": len(groups(splits[a], vid) & groups(splits[b], vid)),
        "sentence_name_overlap": len(groups(splits[a], lambda r: r["SENTENCE_NAME"]) &
                                     groups(splits[b], lambda r: r["SENTENCE_NAME"])),
        "signer_proxy_overlap": sorted(groups(splits[a], sp) & groups(splits[b], sp), key=lambda x: int(x) if x.isdigit() else 0),
    }

train_norm = collections.Counter(norm_sentence(r["SENTENCE"]) for r in train)
train_sent_by_norm = collections.defaultdict(list)
for r in train:
    train_sent_by_norm[norm_sentence(r["SENTENCE"])].append(r["SENTENCE_NAME"])

# near-duplicate: share >= 50 % of the test sentence's word 4-grams with one train sentence (sentences >= 6 words)
def grams(ws, n=4):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}

gram_index = collections.defaultdict(set)
train_grams = []
for i, r in enumerate(train):
    g = grams(norm_sentence(r["SENTENCE"]).split())
    train_grams.append(g)
    for x in g:
        gram_index[x].add(i)

near_rows = []
for s in ("test", "val"):
    for r in splits[s]:
        ns = norm_sentence(r["SENTENCE"])
        ws = ns.split()
        kind, best, match = "", 0.0, ""
        if ns in train_norm:
            kind, best, match = "exact", 1.0, train_sent_by_norm[ns][0]
        elif len(ws) >= 6:
            g = grams(ws)
            hits = collections.Counter(j for x in g for j in gram_index.get(x, ()))
            if hits:
                j, h = hits.most_common(1)[0]
                if h / len(g) >= 0.5:
                    kind, best, match = "near", h / len(g), train[j]["SENTENCE_NAME"]
        if kind:
            near_rows.append({"split": s, "sentence_name": r["SENTENCE_NAME"], "kind": kind,
                              "overlap": round(best, 3), "n_words": len(ws), "train_match": match,
                              "sentence": r["SENTENCE"]})

within_train_dup = sum(c - 1 for c in train_norm.values() if c > 1)

def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return xs[int(q * (len(xs) - 1))] if xs else None

audit = {
    "csv_sha256": sha,
    "splits": {s: {"rows": len(rows), "video_ids": len(groups(rows, vid)),
                   "video_names": len(groups(rows, lambda r: r["VIDEO_NAME"])),
                   "signer_proxy_values": dict(collections.Counter(sp(r) for r in rows).most_common()),
                   "words_median": pct([r["_nw"] for r in rows], 0.5),
                   "duration_s_median": pct([r["_dur"] for r in rows], 0.5),
                   "duration_s_p95": pct([r["_dur"] for r in rows], 0.95)}
               for s, rows in splits.items()},
    "cross_split_overlap": overlap,
    "duplicates": {
        "train_within_exact_duplicate_rows": within_train_dup,
        "test_exact_dup_of_train": sum(1 for r in near_rows if r["split"] == "test" and r["kind"] == "exact"),
        "test_near_dup_of_train": sum(1 for r in near_rows if r["split"] == "test" and r["kind"] == "near"),
        "val_exact_dup_of_train": sum(1 for r in near_rows if r["split"] == "val" and r["kind"] == "exact"),
        "val_near_dup_of_train": sum(1 for r in near_rows if r["split"] == "val" and r["kind"] == "near"),
        "near_dup_rule": "test/val sentence (>=6 words) shares >=50% of its word 4-grams with a single train sentence",
    },
    "concepts": {"tierL_selected": len(eligible), "tierS_groups": len(GROUPS)},
}

# ---------------------------------------------------------------- write
os.makedirs(os.path.join(out, "audit"), exist_ok=True)
os.makedirs(os.path.join(out, "concepts"), exist_ok=True)

def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

json.dump(audit, open(os.path.join(out, "audit", "data_audit.json"), "w"), indent=1)
write_csv(os.path.join(out, "audit", "near_duplicates_test.csv"), near_rows)
write_csv(os.path.join(out, "concepts", "candidate_vocab_train.csv"), cand_rows)
write_csv(os.path.join(out, "concepts", "concept_list_v1.csv"), concept_rows)
json.dump({"rules": RULES, "stopwords": sorted(STOP), "discourse": sorted(DISCOURSE),
           "light_verbs": sorted(LIGHT_VERBS), "generic": sorted(GENERIC), "url_artifact": sorted(URL_ARTIFACT), "irregular": IRREGULAR,
           "no_merge": sorted(NO_MERGE), "groups": {k: sorted(set(v.split())) for k, v in GROUPS.items()},
           "csv_sha256": sha},
          open(os.path.join(out, "concepts", "concept_rules_v1.json"), "w"), indent=1)
print(json.dumps(audit["splits"], indent=1))
print(json.dumps(audit["cross_split_overlap"], indent=1))
print(json.dumps(audit["duplicates"], indent=1))
print("Tier L selected:", [c["concept"] for c in concepts if c["tier"] == "L"])
