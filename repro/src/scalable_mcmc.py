"""Scalable PASV Markov chains and paper-style synthetic posets.

This module implements Algorithm 1 and Lemma 4.1 of Lee et al. without
enumerating linear extensions and without recomputing the n-factor PASV weight
after every adjacent-swap proposal.  The generic sparse chain keeps the maximal
set statistics for every prefix; an accepted adjacent swap changes only one
prefix set, so one array entry is updated.  Structured block chains cover the
paper's n=8192 sum-of-unanimity experiments without materializing dense all-to-
all edges between blocks.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Iterable

import numpy as np

from pasv import Poset


def kahn_linear_extension(poset: Poset) -> tuple[int, ...]:
    """Return one deterministic linear extension in O(n+|E|), or reject a cycle."""
    indegree = np.fromiter((len(poset.pred[i]) for i in range(poset.n)), dtype=np.int64)
    ready = [i for i in range(poset.n) if indegree[i] == 0]
    heapq.heapify(ready)
    order: list[int] = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for child in poset.succ[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    if len(order) != poset.n:
        raise ValueError("edges do not define a DAG")
    return tuple(order)


@dataclass
class ChainStats:
    proposals: int = 0
    feasible: int = 0
    accepted: int = 0

    @property
    def feasible_rate(self) -> float:
        return self.feasible / self.proposals if self.proposals else 0.0

    @property
    def acceptance_rate(self) -> float:
        return self.accepted / self.feasible if self.feasible else 0.0


class LocalPASVChain:
    """Generic sparse-poset adjacent-swap MH using the local ratio in Eq. (9)."""

    def __init__(self, poset: Poset, lam: np.ndarray, seed: int = 0, initial=None):
        if len(lam) != poset.n or np.any(np.asarray(lam) <= 0):
            raise ValueError("lam must contain one positive weight per player")
        self.poset = poset
        self.lam = np.asarray(lam, dtype=float)
        self.uniform_weights = bool(np.all(self.lam == self.lam[0]))
        self.rng = np.random.default_rng(seed)
        self.perm = np.asarray(initial or kahn_linear_extension(poset), dtype=np.int64)
        if len(self.perm) != poset.n or not poset.is_le(tuple(int(x) for x in self.perm)):
            raise ValueError("initial state is not a linear extension")
        self.position = np.empty(poset.n, dtype=np.int64)
        self.position[self.perm] = np.arange(poset.n)
        self.stats = ChainStats()
        self.prefix_count = np.zeros(poset.n + 1, dtype=np.int64)
        self.prefix_weight = np.zeros(poset.n + 1, dtype=float)
        if not self.uniform_weights:
            self._initialize_prefix_stats()

    def _initialize_prefix_stats(self) -> None:
        maximal: set[int] = set()
        for length, raw_node in enumerate(self.perm, 1):
            node = int(raw_node)
            for parent in self.poset.pred[node]:
                maximal.discard(parent)
            maximal.add(node)
            self.prefix_count[length] = len(maximal)
            self.prefix_weight[length] = sum(self.lam[x] for x in maximal)

    def _is_maximal_in_prefix(self, node: int, prefix_length: int) -> bool:
        if self.position[node] >= prefix_length:
            return False
        return all(self.position[child] >= prefix_length for child in self.poset.succ[node])

    def _after_adding_stats(self, node: int, prefix_length: int) -> tuple[int, float]:
        removed_count = 0
        removed_weight = 0.0
        for parent in self.poset.pred[node]:
            if self._is_maximal_in_prefix(parent, prefix_length):
                removed_count += 1
                removed_weight += self.lam[parent]
        return (
            int(self.prefix_count[prefix_length]) + 1 - removed_count,
            float(self.prefix_weight[prefix_length]) + self.lam[node] - removed_weight,
        )

    def swap_ratio(self, index: int) -> float | None:
        """Return p(swapped)/p(current), or None for an infeasible proposal."""
        a, b = int(self.perm[index]), int(self.perm[index + 1])
        if b in self.poset.succ[a]:
            return None
        if self.uniform_weights:
            return 1.0
        count_a, weight_a = self._after_adding_stats(a, index)
        count_b, weight_b = self._after_adding_stats(b, index)
        return (weight_a / count_a) / (weight_b / count_b)

    def _accept_swap(self, index: int) -> None:
        a, b = int(self.perm[index]), int(self.perm[index + 1])
        if not self.uniform_weights:
            count_b, weight_b = self._after_adding_stats(b, index)
            # Only the prefix of length index+1 changes under an adjacent swap.
            self.prefix_count[index + 1] = count_b
            self.prefix_weight[index + 1] = weight_b
        self.perm[index], self.perm[index + 1] = b, a
        self.position[a], self.position[b] = index + 1, index

    def step_at(self, index: int, uniform_draw: float) -> bool:
        self.stats.proposals += 1
        ratio = self.swap_ratio(index)
        if ratio is None:
            return False
        self.stats.feasible += 1
        if uniform_draw < min(1.0, ratio):
            self._accept_swap(index)
            self.stats.accepted += 1
            return True
        return False

    def step(self) -> bool:
        index = int(self.rng.integers(0, self.poset.n - 1))
        return self.step_at(index, float(self.rng.random()))

    def run(self, iterations: int) -> None:
        for _ in range(iterations):
            self.step()

    def sample(self, n_samples: int, burn_in: int, thinning: int = 1) -> Iterable[tuple[int, ...]]:
        self.run(burn_in)
        for _ in range(n_samples):
            self.run(thinning)
            yield tuple(int(x) for x in self.perm)

    def validate_prefix_stats(self) -> float:
        """Independently recompute every prefix statistic; return worst error."""
        if self.uniform_weights:
            return 0.0
        worst = 0.0
        for length in range(self.poset.n + 1):
            subset = set(int(x) for x in self.perm[:length])
            maximal = self.poset.maximal(subset)
            worst = max(
                worst,
                abs(int(self.prefix_count[length]) - len(maximal)),
                abs(float(self.prefix_weight[length]) - sum(self.lam[x] for x in maximal)),
            )
        return worst


class OrderedPartitionChain:
    """Algorithm 1 specialized to ordered blocks, with O(block_size) proposals."""

    def __init__(self, blocks: list[np.ndarray], lam: np.ndarray, seed: int = 0):
        self.blocks = [np.asarray(block, dtype=np.int64) for block in blocks]
        self.perm = np.concatenate(self.blocks).copy()
        self.lam = np.asarray(lam, dtype=float)
        self.block_of = np.empty(len(self.perm), dtype=np.int64)
        self.block_start = np.empty(len(self.blocks), dtype=np.int64)
        cursor = 0
        for block_index, block in enumerate(self.blocks):
            self.block_start[block_index] = cursor
            self.block_of[block] = block_index
            cursor += len(block)
        self.prefix_weight = np.zeros(len(self.perm) + 1, dtype=float)
        for block_index, block in enumerate(self.blocks):
            start = int(self.block_start[block_index])
            self.prefix_weight[start] = 0.0
            running = 0.0
            for offset, player in enumerate(block):
                running += self.lam[int(player)]
                self.prefix_weight[start + offset + 1] = running
        self.rng = np.random.default_rng(seed)
        self.stats = ChainStats()

    def swap_ratio(self, index: int) -> float | None:
        a, b = int(self.perm[index]), int(self.perm[index + 1])
        block = int(self.block_of[a])
        if self.block_of[b] != block:
            return None
        prefix_weight = float(self.prefix_weight[index])
        # Eq. (9): average maximal weight before / after the swap. Counts match.
        return (prefix_weight + self.lam[a]) / (prefix_weight + self.lam[b])

    def step_at(self, index: int, uniform_draw: float) -> bool:
        self.stats.proposals += 1
        ratio = self.swap_ratio(index)
        if ratio is None:
            return False
        self.stats.feasible += 1
        if uniform_draw < min(1.0, ratio):
            a, b = int(self.perm[index]), int(self.perm[index + 1])
            self.perm[index], self.perm[index + 1] = self.perm[index + 1], self.perm[index]
            # Only the within-block prefix ending at index changes.
            self.prefix_weight[index + 1] += self.lam[b] - self.lam[a]
            self.stats.accepted += 1
            return True
        return False

    def step(self) -> bool:
        index = int(self.rng.integers(0, len(self.perm) - 1))
        return self.step_at(index, float(self.rng.random()))

    def run(self, iterations: int) -> None:
        for _ in range(iterations):
            self.step()

    def exact_sample(self) -> tuple[int, ...]:
        """Independent WSV/PASV sample via backward weighted removal."""
        result: list[int] = []
        for original_block in self.blocks:
            remaining = [int(x) for x in original_block]
            reverse_order: list[int] = []
            while remaining:
                weights = self.lam[remaining]
                chosen_index = int(self.rng.choice(len(remaining), p=weights / weights.sum()))
                reverse_order.append(remaining.pop(chosen_index))
            result.extend(reversed(reverse_order))
        return tuple(result)


class BatchedOrderedPartitionChain:
    """Vectorized adjacent-swap MH, with one proposal per block per sweep.

    An ordered partition factorizes into independent within-block weighted
    permutation laws.  Applying one reversible adjacent-swap kernel to every
    factor (the proposals commute) preserves their product target while making
    the parallelism explicit.  ``transitions`` counts scalar MH proposals, not
    vectorized sweeps, so throughput comparisons remain honest.
    """

    def __init__(self, blocks: list[np.ndarray], lam: np.ndarray, seed: int = 0):
        arrays = [np.asarray(block, dtype=np.int64) for block in blocks]
        if not arrays or len({len(block) for block in arrays}) != 1:
            raise ValueError("batched blocks must be nonempty and equally sized")
        if len(arrays[0]) < 2:
            raise ValueError("blocks must contain at least two players")
        self.matrix = np.stack(arrays)
        self.lam = np.asarray(lam, dtype=float)
        if self.matrix.size != len(self.lam) or np.any(self.lam <= 0):
            raise ValueError("lam must contain one positive weight per player")
        if len(np.unique(self.matrix)) != self.matrix.size:
            raise ValueError("blocks must partition distinct players")
        self.block_count, self.block_size = self.matrix.shape
        self.prefix_weight = np.zeros((self.block_count, self.block_size + 1), dtype=float)
        self.prefix_weight[:, 1:] = np.cumsum(self.lam[self.matrix], axis=1)
        self.rng = np.random.default_rng(seed)
        self.stats = ChainStats()
        self.sweeps = 0

    @property
    def perm(self) -> np.ndarray:
        return self.matrix.reshape(-1)

    def sweep(self) -> int:
        """Apply one independently chosen adjacent proposal in every block."""
        rows = np.arange(self.block_count)
        columns = self.rng.integers(0, self.block_size - 1, size=self.block_count)
        left = self.matrix[rows, columns]
        right = self.matrix[rows, columns + 1]
        before = self.prefix_weight[rows, columns]
        ratios = (before + self.lam[left]) / (before + self.lam[right])
        accepted = self.rng.random(self.block_count) < np.minimum(1.0, ratios)
        accepted_rows = rows[accepted]
        accepted_columns = columns[accepted]
        accepted_left = left[accepted]
        accepted_right = right[accepted]
        self.matrix[accepted_rows, accepted_columns] = accepted_right
        self.matrix[accepted_rows, accepted_columns + 1] = accepted_left
        self.prefix_weight[accepted_rows, accepted_columns + 1] += (
            self.lam[accepted_right] - self.lam[accepted_left]
        )
        accepted_count = int(accepted.sum())
        self.sweeps += 1
        self.stats.proposals += self.block_count
        self.stats.feasible += self.block_count
        self.stats.accepted += accepted_count
        return accepted_count

    def run_sweeps(self, sweeps: int) -> None:
        for _ in range(sweeps):
            self.sweep()


def ordered_blocks(n: int, block_size: int = 16) -> list[np.ndarray]:
    if n % block_size:
        raise ValueError("n must be divisible by block_size")
    return [np.arange(start, start + block_size) for start in range(0, n, block_size)]


def ave_degree_poset(n: int, degree: float, seed: int) -> Poset:
    """Paper D.1.1 AveDeg(k): each forward arc is Bernoulli(k/(n-1))."""
    rng = np.random.default_rng(seed)
    probability = degree / max(n - 1, 1)
    edges: set[tuple[int, int]] = set()
    for child in range(1, n):
        parents = np.flatnonzero(rng.random(child) < probability)
        edges.update((int(parent), child) for parent in parents)
    return Poset(n, edges)


def max_indegree_poset(n: int, maximum: int, seed: int) -> Poset:
    """Paper D.1.1 MaxInDeg(k) sequential generator."""
    rng = np.random.default_rng(seed)
    edges: set[tuple[int, int]] = set()
    for child in range(1, n):
        count = int(rng.integers(0, min(maximum, child) + 1))
        if count:
            for parent in rng.choice(child, size=count, replace=False):
                edges.add((int(parent), child))
    return Poset(n, edges)


def grid_poset(n: int, width: int) -> Poset:
    """Sparse directed grid/tree stress family with right/down orientation."""
    edges: set[tuple[int, int]] = set()
    rows = math.ceil(n / width)
    for row in range(rows):
        for col in range(width):
            node = row * width + col
            if node >= n:
                continue
            if col + 1 < width and node + 1 < n:
                edges.add((node, node + 1))
            if row + 1 < rows and node + width < n:
                edges.add((node, node + width))
    return Poset(n, edges)


def bipartite_poset(n: int, probability: float, seed: int) -> Poset:
    rng = np.random.default_rng(seed)
    split = n // 2
    edges: set[tuple[int, int]] = set()
    for left in range(split):
        children = np.flatnonzero(rng.random(n - split) < probability) + split
        edges.update((left, int(child)) for child in children)
    return Poset(n, edges)
