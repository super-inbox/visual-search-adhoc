"""Reference-free, deterministic coverage-plus-motion sampler. No application imports."""
import math
import numpy as np


def uniform(n, budget):
    if n < 0 or budget < 0:
        raise ValueError('negative size/budget')
    k = min(n, budget)
    return np.linspace(0, n-1, k).round().astype(int).tolist() if k else []


def coverage_motion(energy, budget=256):
    e = np.asarray(energy, dtype=float)
    if e.ndim != 1 or not np.isfinite(e).all() or (e < 0).any():
        raise ValueError('energy must be a finite nonnegative vector')
    n = len(e); k = min(n, budget)
    if budget < 0:
        raise ValueError('negative budget')
    if k == 0 or n <= k or k < 4 or e.max() <= 1e-12:
        return uniform(n, budget)
    # Clipping reduces the influence of a single camera/compression spike.
    weights = np.minimum(e, np.quantile(e, .95))
    if weights.sum() <= 1e-12:
        return uniform(n, budget)
    selected = set(uniform(n, math.ceil(k / 2)))
    remaining = np.array([i for i in range(n) if i not in selected])
    w = weights[remaining]
    if w.sum() > 0:
        cum = np.cumsum(w)
        q = (np.arange(k-len(selected)) + .5) / (k-len(selected)) * cum[-1]
        selected.update(remaining[np.searchsorted(cum,q)].tolist())
    # Quantiles can collide: spread remaining points by largest distance to any
    # retained frame, rather than filling from the beginning of the clip.
    while len(selected) < k:
        chosen = np.array(sorted(selected))
        distance = np.min(np.abs(np.arange(n)[:,None]-chosen[None,:]),axis=1)
        selected.add(int(np.argmax(distance)))
    return sorted(selected)
