"""Plan-code verdict consistency test for P0-18 (required before FREEZE by P0-16 SANITY_GATE_POLICY §3).

The plan's verdict table (EXPERIMENT_PLAN.md §8) is written out here independently, over all 2^3 gate x 2^5 criterion
combinations (256), and compared with p018_verdict.decide(). Run: python3 -I test_p018_verdict.py
"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p018_verdict import GATES, CRITERIA, RULES, decide, assert_plan_matches_code  # noqa: E402

plan = {}
for gb in itertools.product([True, False], repeat=len(GATES)):
    for cb in itertools.product([True, False], repeat=len(CRITERIA)):
        P1, P2, P3, P4, P5 = cb
        if not all(gb):
            v = "VOID"
        elif P1 and P2 and P3 and P4 and P5:
            v = "SUPPORTED"
        elif P1 and P3 and P4 and P5 and not P2:
            v = "PARTIAL"
        else:
            v = "NOT SUPPORTED"
        plan[(gb, cb)] = v
n = assert_plan_matches_code(plan, GATES, CRITERIA, RULES)
for (gb, cb), v in plan.items():
    assert decide(dict(zip(GATES, gb)), dict(zip(CRITERIA, cb))) == v
assert sum(v == "PARTIAL" for v in plan.values()) == 1 and sum(v == "SUPPORTED" for v in plan.values()) == 1
print(f"P0-18 plan-code verdict test: {n} combinations match (1 SUPPORTED, 1 PARTIAL, "
      f"{sum(v == 'VOID' for v in plan.values())} VOID, {sum(v == 'NOT SUPPORTED' for v in plan.values())} NOT SUPPORTED)")
