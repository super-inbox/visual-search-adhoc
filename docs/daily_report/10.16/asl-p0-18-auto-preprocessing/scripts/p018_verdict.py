"""P0-18 verdict: criteria evaluation + the P0-16 reference verdict() lookup (SANITY_GATE_POLICY.md).

The verdict table (EXPERIMENT_PLAN.md §8) is encoded ONLY as RULES below and evaluated by P0-16's verdict_policy.verdict:
  any gate FAIL -> VOID
  P1 & P2 & P3 & P4 & P5 -> SUPPORTED
  P1 & P3 & P4 & P5 & not P2 -> PARTIAL   (improves over the old pipeline but recovers less of the oracle gap than the
                                           pre-registered fraction)
  otherwise -> NOT SUPPORTED
"""
import os, sys

P016 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "asl-p0-16-experimental-credibility", "scripts")
sys.path.insert(0, P016)
from verdict_policy import verdict, assert_plan_matches_code  # noqa: E402

GATES = ["G1_env_reproduction", "G2_decode_determinism", "G3_integrity"]
CRITERIA = ["P1", "P2", "P3", "P4", "P5"]
RULES = [("SUPPORTED", {"P1": True, "P2": True, "P3": True, "P4": True, "P5": True}),
         ("PARTIAL", {"P1": True, "P2": False, "P3": True, "P4": True, "P5": True})]


def criteria(res, th):
    """res: computed H18 quantities for the primary arm (res["primary_arm"]); th: frozen thresholds (config). Returns {P1..P5: bool} and the values used."""
    d = res["delta_B_minus_A"]; rec = res["gap_recovery"]
    c = {
        "P1": d["bleu4"]["delta"] >= th["P1_min_delta_bleu4"] and d["bleu4"]["ci95"][0] > 0,
        "P2": (rec["gap_bleu4"] >= th["P2_min_gap_bleu4"] and rec["recovery_bleu4"] is not None
               and rec["recovery_bleu4"] >= th["P2_min_recovery"]),
        "P3": res["failure_rate"] <= th["P3_max_failure_rate"],
        "P4": res["runtime"]["preproc_s_per_clip"] <= th["P4_max_preproc_s_per_clip"],
        "P5": (th["P5_len_ratio"][0] <= res["point"][res["primary_arm"]]["len_ratio"] <= th["P5_len_ratio"][1]
               and d["wer"]["ci95"][1] <= th["P5_max_wer_increase_ci_upper"]),
    }
    return {k: bool(v) for k, v in c.items()}


def decide(gates, crit):
    assert set(gates) == set(GATES) and set(crit) == set(CRITERIA)
    return verdict(gates, crit, RULES)
