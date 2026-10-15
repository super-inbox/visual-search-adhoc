# Post-hoc repetition cleanup: frozen rule (v1)

Written and frozen **before** any metric was computed on cleaned output. Implementation: `scripts/cleanup_rule.py`
(`RULE_VERSION = 'v1'`). Its sha256 is recorded in `metrics/rule_freeze.json` by the dry run, and the metric run refuses to
start if the file has changed since.

## Rule

The rule sees only the prediction text. It never reads the reference, clip metadata or scores, so it can run in a product.

1. **Tokens.** Split the prediction on whitespace. Each token gets a match key: lowercase, with leading and trailing
   non-alphanumeric characters stripped (so `D,` `d` `D.` share the key `d`). A token that is only punctuation keeps
   itself as its key.
2. **Tandem repeat.** Scan the tokens left to right. At position *i*, look for the **smallest** unit length
   *p* ∈ {1, …, 8} for which the unit `keys[i:i+p]` occurs **at least 3 times in a row** starting at *i*
   (*r* ≥ 3 consecutive copies).
3. **Collapse.** If found, keep the **first** copy with its original tokens and drop copies 2…*r*.
   - If what follows the run is a **partial copy** (a proper prefix of the unit) **and it is the end of the output**,
     drop it too. This is the cut-off tail of a loop.
   - Continue scanning right after the kept copy. If no unit matches at *i*, move to *i* + 1.
4. **Output.**
   - If nothing was collapsed, return the original string **unchanged, byte for byte**.
   - Otherwise join the kept tokens with single spaces. No punctuation is added and nothing is reordered.

## Why these choices (fixed in advance)

- **≥ 3 consecutive copies**: ordinary English rarely repeats a phrase three times in a row, but does repeat twice
  ("very very", "a D, a D"). Two copies are never touched.
- **Consecutive (tandem) only**: a phrase that recurs non-adjacently ("we're going to … we're going to") is a legitimate
  pattern and also occurs in references. The rule leaves it alone. This also means it will **miss** loops whose copies
  are not adjacent or that vary slightly, and that is accepted.
- **p ≤ 8**: covers word and short-phrase loops; longer cycles are rare and riskier to collapse.
- **Keep the first copy**: the first copy is the model's actual content. Only the redundant copies are removed.
- **No terminal punctuation added**: adding a period would game the truncation metric without changing content.

## Guards checked before any metric (dry run)

- **G1, legitimate repetitions:** apply the rule to all 128 **references**. It must change **none**.
- **G2, change set:** apply the rule to the 128 A_official predictions and list every changed clip, whether it is one of
  the 18 taxonomy `repetition_loop` clips, and the before / after text. Requirement: no non-loop clip changes.

  "Loop clip" uses the taxonomy definition (`error_taxonomy_annotations.jsonl`, A_official
  `primary_error_type == repetition_loop`: a repeated 3-gram not present in the reference, with rep-3-gram ratio
  ≥ 0.15). That definition reads the reference, so it is used only for **evaluation subsets**, never by the rule.

  A changed clip outside the 18 is a G2 violation. It is reported, not silently fixed. Revising the rule after a
  violation would make it v2, documented here, and decided before metrics are seen.
- The originals are never modified. `A_official.txt` is sha256-checked before and after the run.

## Decision rule for "useful improvement" (fixed in advance)

On the 18 loop clips, compared with the original A_official output, Stage 1 is **useful** only if all of these hold:

1. the loop rate (taxonomy definition) falls by at least half;
2. corpus WER falls, with a paired-bootstrap 95 % CI entirely below 0;
3. corpus chrF does not get worse: point estimate Δ ≥ −0.5;
4. every non-loop clip is byte-identical, so the full-set change comes only from the loop clips.

Full-128 BLEU-4 is reported, with the decision not depending on it. A loop removal on 18 clips can only move corpus
BLEU-4 slightly, since BLEU-4 is precision-based and the loop copies are mostly already counted as clipped n-grams.

If the rule is **not useful**, the GPU decode-time repetition constraint is not implemented. The result is reported
first.
