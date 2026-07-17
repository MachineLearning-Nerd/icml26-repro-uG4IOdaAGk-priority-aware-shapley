"""Adjacent-swap Metropolis-Hastings sampler for the PASV distribution
(Section 4 of Das & Srivastava 2602.09326) — Claim C3.

The state space is the set of linear extensions Π_≺.  From a current LE π we
propose swapping two ADJACENT positions (t, t+1); the swap is feasible iff it
keeps π a linear extension, i.e. ¬(π_t ≺ π_{t+1}).  Accept with the
Metropolis ratio min(1, w(π')/w(π)) using the PASV weight (eq 4).  This chain is
ergodic over Π_≺ and reversible w.r.t. PASV, so its stationary distribution is
exactly p^(≺,λ).  We verify that the empirical distribution converges to p and
that the resulting value estimate converges to ψ^PASV.
"""
from __future__ import annotations
from typing import Dict, Tuple, List
import numpy as np
from pasv import Poset, pasv_weight, random_order_value, Utility


def _is_le_after_swap(poset: Poset, perm, t):
    """Is swapping positions t,t+1 still a linear extension? Only the adjacency
    π_t ≺ π_{t+1} can be violated by an adjacent swap."""
    a, b = perm[t], perm[t + 1]
    return b not in poset.succ[a]   # not (a ≺ b)


def pasv_mcmc(poset: Poset, lam: np.ndarray, n_samples: int, burn_in: int = 1000,
              seed: int = 0):
    """Return a list of sampled linear extensions (thin=1 after burn-in)."""
    rng = np.random.default_rng(seed)
    perm = list(next(iter(poset.linear_extensions())))   # any LE to start
    w = pasv_weight(poset, tuple(perm), lam)
    n = poset.n
    samples: List[Tuple[int, ...]] = []
    total = burn_in + n_samples
    for step in range(total):
        t = rng.integers(0, n - 1)
        if _is_le_after_swap(poset, perm, t):
            perm[t], perm[t + 1] = perm[t + 1], perm[t]
            w_new = pasv_weight(poset, tuple(perm), lam)
            if rng.random() < w_new / w:
                w = w_new
            else:
                perm[t], perm[t + 1] = perm[t + 1], perm[t]   # reject -> revert
        if step >= burn_in:
            samples.append(tuple(perm))
    return samples


def empirical_distribution(samples, poset):
    les = poset.linear_extensions()
    counts = {p: 0 for p in les}
    for s in samples:
        counts[s] += 1
    tot = sum(counts.values())
    return {p: c / tot for p, c in counts.items()}


def mcmc_value_estimate(samples, U: Utility, n: int) -> np.ndarray:
    """Monte Carlo estimate of ψ from MCMC samples (averages marginal contribs)."""
    acc = np.zeros(n)
    for perm in samples:
        for i in range(n):
            k = perm.index(i)
            S = frozenset(perm[:k])
            acc[i] += (U(S | {i}) - U(S))
    return acc / len(samples)
