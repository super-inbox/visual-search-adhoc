# Post-hoc repetition cleanup, rule v1 (spec: ../CLEANUP_RULE.md). Reference-free: reads only the prediction text.
import re

RULE_VERSION = 'v1'
MIN_COPIES = 3   # a unit must occur >= 3 times in a row
MAX_UNIT = 8     # unit length in tokens, 1..8; the smallest matching unit wins


def key(tok):
    k = re.sub(r'^\W+|\W+$', '', tok.lower())
    return k if k else tok


def cleanup(text):
    """Return (cleaned_text, collapses). collapses = [(start_token, unit_len, copies, dropped_partial_tail)].
    Unchanged input is returned as the identical string object."""
    toks = text.split()
    keys = [key(t) for t in toks]
    out, collapses, i, n = [], [], 0, len(toks)
    while i < n:
        hit = None
        for p in range(1, MAX_UNIT + 1):
            unit = keys[i:i + p]
            if len(unit) < p:
                break
            r = 1
            while keys[i + r * p:i + (r + 1) * p] == unit:
                r += 1
            if r >= MIN_COPIES:
                hit = (p, r)
                break
        if hit is None:
            out.append(toks[i]); i += 1
            continue
        p, r = hit
        out.extend(toks[i:i + p])
        j = i + r * p
        tail = keys[j:]
        partial = 0 < len(tail) < p and tail == keys[i:i + len(tail)]  # cut-off copy at the very end
        collapses.append((i, p, r, partial))
        i = n if partial else j
    if not collapses:
        return text, []
    return ' '.join(out), collapses
