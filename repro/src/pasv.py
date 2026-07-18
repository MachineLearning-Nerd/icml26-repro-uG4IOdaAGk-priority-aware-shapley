"""Priority-Aware Shapley Value (PASV) and its predecessors, from
"Priority-Aware Shapley Value" (Lee et al., arXiv 2602.09326, uG4IOdaAGk).

A poset ([n], ≺) encodes hard precedence (i ≺ j => i before j in any order).
A linear extension (LE) π is a permutation respecting ≺; Π_≺ is their set.

Distributions over Π_≺:
  PSV   (Faigle-Kern):      uniform over Π_≺.
  WSV   (Kalai-Samet):      λ-weighted, defined on ordered-partition DAGs.
  PASV  (this paper, eq 4): general posets, λ-weighted, with the crucial
        |max_≺(S_t)| factor so that const-λ recovers PSV (Prop 3.1) and
        ordered-partition recovers WSV (Prop 3.2).

PASV weight of an LE π  (eq 4):
    w(π) = Π_{t=1..n}  λ_{π_t} · |max_≺(S_t)| / Σ_{k ∈ max_≺(S_t)} λ_k ,
with S_t = {π_1,...,π_t} and max_≺(S) = {i ∈ S : ¬∃ j ∈ S, i ≺ j}.
"""
from __future__ import annotations
from typing import Callable, Dict, List, Set, Tuple
from itertools import permutations
import numpy as np

Utility = Callable[frozenset, float]


class Poset:
    def __init__(self, n: int, edges: Set[Tuple[int, int]]):
        """edges: set of (i,j) meaning i ≺ j (i must precede j)."""
        self.n = n
        self.succ: Dict[int, Set[int]] = {i: set() for i in range(n)}   # i -> {j : i≺j}
        self.pred: Dict[int, Set[int]] = {i: set() for i in range(n)}
        for (i, j) in edges:
            self.succ[i].add(j)
            self.pred[j].add(i)

    def is_le(self, perm: Tuple[int, ...]) -> bool:
        pos = {p: t for t, p in enumerate(perm)}
        return all(pos[i] < pos[j] for (i, j) in self.edges_list())

    def edges_list(self):
        return [(i, j) for i in range(self.n) for j in self.succ[i]]

    def linear_extensions(self) -> List[Tuple[int, ...]]:
        return [p for p in permutations(range(self.n)) if self.is_le(p)]

    def maximal(self, S) -> Set[int]:
        """max_≺(S) = {i ∈ S : no j ∈ S with i ≺ j}."""
        Sset = set(S)
        return {i for i in Sset if not (self.succ[i] & Sset)}


def pasv_weight(poset: Poset, perm: Tuple[int, ...], lam: np.ndarray) -> float:
    """Eq. (4) unnormalized weight of a linear extension."""
    w = 1.0
    for t in range(1, poset.n + 1):
        S_t = set(perm[:t])
        mx = poset.maximal(S_t)
        denom = sum(lam[k] for k in mx)
        w *= lam[perm[t - 1]] * len(mx) / denom
    return w


def pasv_distribution(poset: Poset, lam: np.ndarray) -> Dict[Tuple[int, ...], float]:
    les = poset.linear_extensions()
    ws = np.array([pasv_weight(poset, p, lam) for p in les])
    ws = ws / ws.sum()
    return {p: float(w) for p, w in zip(les, ws)}


def psv_distribution(poset: Poset) -> Dict[Tuple[int, ...], float]:
    les = poset.linear_extensions()
    return {p: 1.0 / len(les) for p in les}


def wsv_backward_sample_weight(perm, ordered_partition, lam):
    """WSV via the described backward λ-sampling on an ordered-partition DAG.
    Returns the probability of `perm` under that sampling process."""
    blocks = ordered_partition  # list of lists, order = precedence B1≺B2≺...
    n = len(perm)
    # build position map
    pos = {p: t for t, p in enumerate(perm)}
    prob = 1.0
    remaining = list(range(n))
    for t in range(n - 1, -1, -1):                       # place perm[t] last..first
        # candidates = block whose all members still unplaced & it's the last nonempty block
        # equivalently the maximal (latest) block with remaining members
        cand = None
        for b in reversed(blocks):
            mem = [x for x in b if x in remaining]
            if mem:
                cand = mem
                break
        s = sum(lam[x] for x in cand)
        prob *= lam[perm[t]] / s
        remaining.remove(perm[t])
    return prob


def random_order_value(dist: Dict[Tuple[int, ...], float], U: Utility, i: int) -> float:
    """ψ_i = E_{π~dist}[ U(S_{pos(i)-1} ∪ {i}) − U(S_{pos(i)-1}) ]."""
    val = 0.0
    for perm, p in dist.items():
        k = perm.index(i)
        S = frozenset(perm[:k])
        val += p * (U(S | {i}) - U(S))
    return val


def pasv_value(poset: Poset, lam: np.ndarray, U: Utility) -> np.ndarray:
    dist = pasv_distribution(poset, lam)
    return np.array([random_order_value(dist, U, i) for i in range(poset.n)])


def psv_value(poset: Poset, U: Utility) -> np.ndarray:
    dist = psv_distribution(poset)
    return np.array([random_order_value(dist, U, i) for i in range(poset.n)])


def classical_shapley(U: Utility, n: int) -> np.ndarray:
    """Classical Shapley value (uniform over all permutations)."""
    from math import factorial
    phi = np.zeros(n)
    for perm in permutations(range(n)):
        for i in range(n):
            k = perm.index(i)
            S = frozenset(perm[:k])
            phi[i] += (U(S | {i}) - U(S)) / factorial(n)
    return phi
