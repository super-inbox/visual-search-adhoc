"""Tests that verdict_policy.py implements SANITY_GATE_POLICY.md. Run: python3 -I test_verdict_policy.py"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verdict_policy import verdict, null_gate, truth_table, assert_plan_matches_code  # noqa: E402

n = 0
def check(cond, msg):
    global n
    assert cond, msg
    n += 1

# --- policy §2: any gate FAIL (or None) -> VOID, whatever the criteria
G, C = ["N1", "N2"], ["P1", "P2", "P3"]
RULES_WITH_PARTIAL = [("SUPPORTED", {"P1": True, "P2": True, "P3": True}),
                      ("PARTIAL", {"P1": True, "P2": True, "P3": False})]
for cb in itertools.product([True, False], repeat=3):
    crit = dict(zip(C, cb))
    for gates in ({"N1": False, "N2": True}, {"N1": True, "N2": False}, {"N1": None, "N2": True}):
        check(verdict(gates, crit, RULES_WITH_PARTIAL) == "VOID", f"gate failure must be VOID {gates} {crit}")

# --- policy §2: PARTIAL only where the plan defines it
tt = truth_table(G, C, RULES_WITH_PARTIAL)
check(sum(v == "PARTIAL" for v in tt.values()) == 1, "exactly one PARTIAL combination when the plan defines one")
RULES_NO_PARTIAL = [("SUPPORTED", {"P1": True, "P2": True, "P3": True})]
check("PARTIAL" not in truth_table(G, C, RULES_NO_PARTIAL).values(), "PARTIAL must never appear if undefined")
check(set(truth_table(G, C, RULES_NO_PARTIAL).values()) == {"SUPPORTED", "NOT SUPPORTED", "VOID"}, "verdict set")

# --- policy §3: the plan's independently written table must match the code on every combination
plan = {}
for gb in itertools.product([True, False], repeat=2):
    for cb in itertools.product([True, False], repeat=3):
        p1, p2, p3 = cb
        plan[(gb, cb)] = ("VOID" if not all(gb) else "SUPPORTED" if p1 and p2 and p3 else
                          "PARTIAL" if p1 and p2 else "NOT SUPPORTED")
check(assert_plan_matches_code(plan, G, C, RULES_WITH_PARTIAL) == 32, "32 combinations checked")
wrong = dict(plan); wrong[((False, True), (True, True, True))] = "PARTIAL"     # the P0-14 pattern: gate fails, PARTIAL
try:
    assert_plan_matches_code(wrong, G, C, RULES_WITH_PARTIAL); check(False, "mismatch not detected")
except AssertionError as e:
    check("disagree" in str(e), "plan-code mismatch is detected")

# --- historical P0-14 pattern under the new policy: C1-C6 pass, S1 fails -> VOID (recorded verdict unchanged)
p014 = verdict({"S1": False}, {f"C{i}": True for i in range(1, 7)},
               [("SUPPORTED", {f"C{i}": True for i in range(1, 7)})])
check(p014 == "VOID", "P0-14 pattern is VOID under P0-16 policy")
# --- P0-15 pattern: N1, N2 pass, P1 fails (abstain), P2 passes, P3 fails -> NOT SUPPORTED (matches the record)
check(verdict({"N1": True, "N2": True}, {"P1": False, "P2": True, "P3": False}, RULES_WITH_PARTIAL) == "NOT SUPPORTED",
      "P0-15 pattern is NOT SUPPORTED")

# --- invalid rules are rejected
for bad in ([("STRONG SUPPORT", {"P1": True})], [("SUPPORTED", {"P9": True})]):
    try:
        verdict({"N1": True}, {"P1": True}, bad); check(False, "bad rule accepted")
    except ValueError:
        check(True, "")
try:
    verdict({}, {"P1": True}, RULES_NO_PARTIAL[:0]); check(False, "no gate accepted")
except ValueError:
    check(True, "")

# --- policy §4: null gates need >= 20 seeds, inclusive band, unrounded statistic
check(not null_gate([0.5] * 19, (0.45, 0.55)), "fewer than 20 seeds fails")
check(null_gate([0.5] * 20, (0.45, 0.55)), "20 seeds at chance passes")
check(null_gate([0.55] * 20, (0.45, 0.55)), "boundary is inclusive")
check(not null_gate([0.53017] * 20, (0.47, 0.53)), "unrounded 0.53017 is outside [0.47, 0.53]")
check(not null_gate(None, (0.45, 0.55)), "missing values fail")
print(f"verdict policy tests: {n} checks passed")
