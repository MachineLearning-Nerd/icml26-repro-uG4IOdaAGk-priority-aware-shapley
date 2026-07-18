"""Adjacent-swap Metropolis-Hastings sampler for the PASV distribution
(Section 4 of Lee et al. 2602.09326) — Claim C3.

The state space is the set of linear extensions Π_≺.  From a current LE π we
propose swapping two ADJACENT positions (t, t+1); the swap is feasible iff it
keeps π a linear extension, i.e. ¬(π_t ≺ π_{t+1}).  Accept with the
Metropolis ratio min(1, w(π')/w(π)) using the PASV weight (eq 4).  This chain is
ergodic over Π_≺ and reversible w.r.t. PASV, so its stationary distribution is
exactly p^(≺,λ).  We verify that the empirical distribution converges to p and
that the resulting value estimate converges to ψ^PASV.
"""
from __future__ import annotations
import numpy as np
from pasv import Poset, Utility
from scalable_mcmc import LocalPASVChain


def pasv_mcmc(poset: Poset, lam: np.ndarray, n_samples: int, burn_in: int = 1000,
              seed: int = 0, thinning: int = 1):
    """Return PASV samples using Kahn init and the O(local) Lemma-4.1 ratio."""
    chain = LocalPASVChain(poset, lam, seed=seed)
    return list(chain.sample(n_samples=n_samples, burn_in=burn_in, thinning=thinning))


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
