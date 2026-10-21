"""P0-19 Stage 0 decision as a lookup on the P0-16 reference implementation (verdict_policy.verdict).

verdict_policy only accepts the words SUPPORTED / PARTIAL / NOT SUPPORTED / VOID. For Stage 0 they are read as:
  SUPPORTED     -> GO        (Stage 0 passes; this is NOT a P0-19 verdict, only permission to plan Stage 1)
  NOT SUPPORTED -> NO-GO     (P0-19 stops at Stage 0; development NOT SUPPORTED; H19 stays sealed)
  VOID          -> VOID      (a sanity gate failed; nothing interpreted)
No PARTIAL is defined.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p019_common import P016  # noqa: E402

sys.path.insert(0, os.path.join(P016, "scripts"))
from verdict_policy import verdict  # noqa: E402

GATES = ["G1_reproduction", "G2_determinism", "G3_no_holdout", "G4_input_integrity", "G5_label_reproduction"]
CRITERIA = ["C1_k4", "C2_k4", "C3_k4", "C1_k8", "C2_k8", "C3_k8"]
RULES = [
    ("SUPPORTED", {"C1_k4": True, "C2_k4": True, "C3_k4": True}),
    ("SUPPORTED", {"C1_k8": True, "C2_k8": True, "C3_k8": True}),
]
STAGE0_WORD = {"SUPPORTED": "GO", "NOT SUPPORTED": "NO-GO", "VOID": "VOID"}


def stage0_decision(gates, criteria):
    v = verdict(gates, criteria, RULES)
    out = {"policy_verdict": v, "stage0": STAGE0_WORD[v], "selected_k": None}
    if v == "SUPPORTED":
        out["selected_k"] = 4 if all(criteria[f"C{i}_k4"] for i in (1, 2, 3)) else 8
    return out
