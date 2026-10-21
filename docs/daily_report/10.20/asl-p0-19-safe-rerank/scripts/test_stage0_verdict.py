"""Plan-code consistency test for the Stage 0 decision (P0-16 SANITY_GATE_POLICY section 3).

The plan table below is written out independently of stage0_verdict.RULES, from EXPERIMENT_PLAN.md section 4:
  any gate FAIL                                  -> VOID
  else (C1_k4 and C2_k4 and C3_k4) or (C1_k8 and C2_k8 and C3_k8) -> SUPPORTED (read: GO)
  else                                           -> NOT SUPPORTED (read: NO-GO)
Usage: python -I test_stage0_verdict.py   (prints the number of combinations checked; exit 0 = pass)
"""
import itertools, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage0_verdict import CRITERIA, GATES, RULES, stage0_decision  # noqa: E402
from verdict_policy import assert_plan_matches_code  # noqa: E402  (path set by stage0_verdict)

plan = {}
for gb in itertools.product([True, False], repeat=len(GATES)):
    for cb in itertools.product([True, False], repeat=len(CRITERIA)):
        c = dict(zip(CRITERIA, cb))
        if not all(gb):
            v = "VOID"
        elif (c["C1_k4"] and c["C2_k4"] and c["C3_k4"]) or (c["C1_k8"] and c["C2_k8"] and c["C3_k8"]):
            v = "SUPPORTED"
        else:
            v = "NOT SUPPORTED"
        plan[(gb, cb)] = v
n = assert_plan_matches_code(plan, GATES, CRITERIA, RULES)

# selected k: smallest passing k
T = dict.fromkeys(GATES, True)
both = dict.fromkeys(CRITERIA, True)
only8 = {**both, "C2_k4": False}
assert stage0_decision(T, both) == {"policy_verdict": "SUPPORTED", "stage0": "GO", "selected_k": 4}
assert stage0_decision(T, only8)["selected_k"] == 8
assert stage0_decision(T, {**both, "C3_k4": False, "C1_k8": False})["stage0"] == "NO-GO"
assert stage0_decision({**T, "G2_determinism": None}, both)["stage0"] == "VOID"      # not computable = FAIL
print(f"stage0 plan-code test PASS: {n} combinations (5 gates x 6 criteria) + 4 selected-k / VOID checks")
