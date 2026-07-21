import csv, json, sys
from collections import Counter

OUT = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/scorer-v1.1-evaluation-2026-07-21"
BANK = "/Users/baobaoli/Desktop/visual-search-adhoc/docs/daily_report/7.16/easy-query-bank-v3/easy_query_bank_v2_2026-07-16.csv"
BASE_CSV = f"{OUT}/eval_raw/BASELINE_EASY326.csv"
CAND_CSV = f"{OUT}/eval_raw/CANDIDATE_EASY326.csv"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

bank = load(BANK)
base = load(BASE_CSV)
cand = load(CAND_CSV)
print(f"bank={len(bank)} base={len(base)} cand={len(cand)}")

def by_idx(rows):
    d = {}
    for r in rows:
        d[int(r["row_index"])] = r
    return d

bi, ci = by_idx(base), by_idx(cand)
n = len(bank)

# alignment check
mism = []
for i in range(n):
    if bi.get(i) and bi[i]["query"] != bank[i]["query"]:
        mism.append((i,"base",bi[i]["query"],bank[i]["query"]))
    if ci.get(i) and ci[i]["query"] != bank[i]["query"]:
        mism.append((i,"cand",ci[i]["query"],bank[i]["query"]))
print("alignment mismatches:", mism[:10] if mism else "NONE")

LABEL_RANK = {"FAIL":0,"UNJUDGABLE":1,"PARTIAL":2,"PASS":3}

def label(r): return r["relevance_label"]
def zero(r): return r["zero_result"] in ("True","true")
def low(r): return r["low_result"] in ("True","true")
def total(r):
    try: return int(r["total_results"])
    except: return None
def score(r):
    try: return float(r["relevance_score"])
    except: return None

def dist(rows):
    c = Counter(label(r) for r in rows)
    z = sum(1 for r in rows if zero(r))
    lo = sum(1 for r in rows if low(r))
    scs = [score(r) for r in rows if score(r) is not None]
    mean = sum(scs)/len(scs) if scs else 0
    return c, z, lo, mean

bc, bz, blo, bmean = dist(base)
cc, cz, clo, cmean = dist(cand)

print("\n=== HEADLINE ===")
for lab in ["PASS","PARTIAL","FAIL","UNJUDGABLE"]:
    print(f"{lab:12} base={bc.get(lab,0):4} cand={cc.get(lab,0):4}")
print(f"zero-result  base={bz:4} cand={cz:4}")
print(f"low-result   base={blo:4} cand={clo:4}")
print(f"mean-score   base={bmean:.2f} cand={cmean:.2f}")

# transition matrix + improved/regressed
improved=[]; regressed=[]; unchanged=0
trans = Counter()
rows_out=[]
for i in range(n):
    b=bi.get(i); c=ci.get(i)
    if not b or not c: continue
    bl, cl = label(b), label(c)
    trans[(bl,cl)] += 1
    br, cr = LABEL_RANK.get(bl,-1), LABEL_RANK.get(cl,-1)
    imp = cr>br; reg = cr<br
    if imp: improved.append((bank[i]["query"],bank[i].get("language",""),bl,cl))
    elif reg: regressed.append((bank[i]["query"],bank[i].get("language",""),bl,cl))
    else: unchanged+=1
    rows_out.append({
        "row_index":i,"query":bank[i]["query"],"language":bank[i].get("language",""),
        "category":bank[i].get("category",""),
        "base_total":total(b),"cand_total":total(c),
        "base_zero":zero(b),"cand_zero":zero(c),
        "base_low":low(b),"cand_low":low(c),
        "base_label":bl,"cand_label":cl,
        "base_score":score(b),"cand_score":score(c),
        "improved":imp,"regressed":reg,
        "base_top5":b["top5_titles"],"cand_top5":c["top5_titles"],
        "base_paths":b.get("paths_used",""),"cand_paths":c.get("paths_used",""),
        "base_rewrites":b.get("used_rewrites",""),"cand_rewrites":c.get("used_rewrites",""),
    })

print(f"\nimproved={len(improved)} regressed={len(regressed)} unchanged={unchanged}")

# write comparison CSV
cols=["row_index","query","language","category","base_total","cand_total","base_zero","cand_zero",
      "base_low","cand_low","base_label","cand_label","base_score","cand_score","improved","regressed",
      "base_paths","cand_paths","base_rewrites","cand_rewrites","base_top5","cand_top5"]
with open(f"{OUT}/FULL326_COMPARISON.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in rows_out: w.writerow(r)

print("\n=== TRANSITION MATRIX (base->cand) ===")
for (bl,cl),cnt in sorted(trans.items(), key=lambda x:-x[1]):
    tag = "IMPROVED" if LABEL_RANK.get(cl,-1)>LABEL_RANK.get(bl,-1) else ("REGRESSED" if LABEL_RANK.get(cl,-1)<LABEL_RANK.get(bl,-1) else "same")
    print(f"{bl:11} -> {cl:11} {cnt:4}  {tag}")

print("\n=== REGRESSED LIST ===")
for q,l,bl,cl in regressed: print(f"  [{l}] {q!r}: {bl}->{cl}")
print("\n=== IMPROVED LIST ===")
for q,l,bl,cl in improved: print(f"  [{l}] {q!r}: {bl}->{cl}")

# new zero-result (base non-zero, cand zero) and recovered
new_zero=[]; recovered_zero=[]
new_low=[];
for i in range(n):
    b=bi.get(i); c=ci.get(i)
    if not b or not c: continue
    if not zero(b) and zero(c): new_zero.append(bank[i]["query"])
    if zero(b) and not zero(c): recovered_zero.append(bank[i]["query"])
print("\n=== NEW ZERO-RESULT (base nonzero -> cand zero) ===", new_zero)
print("=== RECOVERED ZERO (base zero -> cand nonzero) ===", recovered_zero)

# 15-condition gate
print("\n=== GATE (candidate vs baseline) ===")
conds=[]
def cond(n,desc,ok,basis):
    conds.append((n,desc,"PASS" if ok else "FAIL",basis))
cond(1,"cand PASS >= base PASS", cc.get("PASS",0)>=bc.get("PASS",0), f"{cc.get('PASS',0)} vs {bc.get('PASS',0)}")
cond(2,"cand FAIL <= base FAIL", cc.get("FAIL",0)<=bc.get("FAIL",0), f"{cc.get('FAIL',0)} vs {bc.get('FAIL',0)}")
cond(3,"cand zero <= base zero", cz<=bz, f"{cz} vs {bz}")
cond(4,"improved >= regressed", len(improved)>=len(regressed), f"{len(improved)} vs {len(regressed)}")
cond(15,"clear net improvement", len(improved)>len(regressed) and cc.get("FAIL",0)<=bc.get("FAIL",0) and cz<=bz, f"imp {len(improved)} reg {len(regressed)}")
for n_,d,r,b in conds: print(f"#{n_} {d}: {r} ({b})")

# dump summary json
summ={"base":{"PASS":bc.get("PASS",0),"PARTIAL":bc.get("PARTIAL",0),"FAIL":bc.get("FAIL",0),"UNJUDGABLE":bc.get("UNJUDGABLE",0),"zero":bz,"low":blo,"mean":round(bmean,2)},
      "cand":{"PASS":cc.get("PASS",0),"PARTIAL":cc.get("PARTIAL",0),"FAIL":cc.get("FAIL",0),"UNJUDGABLE":cc.get("UNJUDGABLE",0),"zero":cz,"low":clo,"mean":round(cmean,2)},
      "improved":len(improved),"regressed":len(regressed),"unchanged":unchanged,
      "improved_list":improved,"regressed_list":regressed,
      "new_zero":new_zero,"recovered_zero":recovered_zero,
      "transitions":{f"{k[0]}->{k[1]}":v for k,v in trans.items()}}
with open(f"{OUT}/scripts/summary.json","w",encoding="utf-8") as f:
    json.dump(summ,f,ensure_ascii=False,indent=2)
print("\nwrote FULL326_COMPARISON.csv and summary.json")
