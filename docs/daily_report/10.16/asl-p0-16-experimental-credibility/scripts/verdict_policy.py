"""P0-16 reference implementation of SANITY_GATE_POLICY.md (for reuse by P0-18 / P0-19 scoring code).

    from verdict_policy import verdict, null_gate, truth_table, assert_plan_matches_code

verdict(gates, criteria, rules):
  gates     {name: bool | None}   sanity gates; None (not computable) counts as FAIL
  criteria  {name: bool}          pre-registered criteria
  rules     ordered list of (VERDICT, {criterion: required bool}); VERDICT in {"SUPPORTED", "PARTIAL"}
            PARTIAL may appear only if the plan defines it. No other verdict words are accepted.
  -> "VOID" if any gate fails; else the first rule whose requirements all hold; else "NOT SUPPORTED".
"""
import itertools, statistics

VERDICTS = ("SUPPORTED", "PARTIAL", "NOT SUPPORTED", "VOID")


def verdict(gates, criteria, rules):
    if not gates:
        raise ValueError("a plan must define at least one sanity gate")
    for v, req in rules:
        if v not in ("SUPPORTED", "PARTIAL"):
            raise ValueError(f"rule verdict must be SUPPORTED or PARTIAL, got {v!r}")
        missing = set(req) - set(criteria)
        if missing:
            raise ValueError(f"rule refers to undefined criteria {sorted(missing)}")
    if not all(g is True for g in gates.values()):
        return "VOID"
    for v, req in rules:
        if all(criteria[c] is want for c, want in req.items()):
            return v
    return "NOT SUPPORTED"


def null_gate(values, band, min_seeds=20, stat="median"):
    """PASS iff the median (or mean) of >= min_seeds null-control values lies in the inclusive band. Unrounded."""
    if values is None or len(values) < min_seeds:
        return False
    s = statistics.median(values) if stat == "median" else statistics.fmean(values)
    return band[0] <= s <= band[1]


def truth_table(gate_names, criterion_names, rules):
    """Every (gates, criteria) combination -> verdict, as {(gate bools, criterion bools): verdict}."""
    out = {}
    for gb in itertools.product([True, False], repeat=len(gate_names)):
        for cb in itertools.product([True, False], repeat=len(criterion_names)):
            out[(gb, cb)] = verdict(dict(zip(gate_names, gb)), dict(zip(criterion_names, cb)), rules)
    return out


def assert_plan_matches_code(plan_table, gate_names, criterion_names, rules):
    """plan_table: the plan's verdict table written out independently as {(gate bools, criterion bools): verdict}.
    Must cover every combination and agree with verdict(). Raise on any difference (freeze is then not allowed)."""
    code = truth_table(gate_names, criterion_names, rules)
    if set(plan_table) != set(code):
        raise AssertionError("plan table does not cover exactly every gate x criterion combination")
    diff = {k: (plan_table[k], code[k]) for k in code if plan_table[k] != code[k]}
    if diff:
        raise AssertionError(f"plan and code disagree on {len(diff)} combinations, e.g. {next(iter(diff.items()))}")
    return len(code)
