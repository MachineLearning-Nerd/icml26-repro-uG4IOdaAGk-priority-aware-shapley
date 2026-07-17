"""Formal pytest suite: Priority-Aware Shapley Value (Das & Srivastava 2602.09326).
Run: pytest -q repro/tests"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pytest
from pasv import (Poset, pasv_distribution, psv_distribution, pasv_value,
                  psv_value, classical_shapley, wsv_backward_sample_weight)
from mcmc import pasv_mcmc, empirical_distribution, mcmc_value_estimate

POSETS = [
    ("chain", Poset(4, {(0, 1), (1, 2), (2, 3)}), None),
    ("V", Poset(4, {(0, 2), (1, 2), (2, 3)}), None),
    ("2level", Poset(5, {(0, 3), (1, 3), (2, 4)}), None),
    ("op2", Poset(4, {(0, 2), (0, 3), (1, 2), (1, 3)}), [[0, 1], [2, 3]]),
    ("op3", Poset(5, {(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)}),
     [[0, 1], [2, 3], [4]]),
]


# -- C1: precedence enforced + soft weights active --
def test_c1_precedence_enforced():
    for _, P, _ in POSETS:
        d = pasv_distribution(P, np.arange(1, P.n + 1, dtype=float))
        assert abs(sum(d.values()) - 1.0) < 1e-12
        for perm in d:
            assert P.is_le(perm)


def test_c1_weights_active_when_multi_le():
    P = Poset(4, {(0, 2), (1, 2), (2, 3)})       # >1 LE
    d = pasv_distribution(P, np.array([1.0, 2.0, 3.0, 4.0]))
    lam2 = np.array([5.0, 2.0, 3.0, 4.0])
    d2 = pasv_distribution(P, lam2)
    assert 0.5 * sum(abs(d[p] - d2[p]) for p in d) > 0.01


# -- C2 / Prop 3.1: const λ -> PSV --
@pytest.mark.parametrize("name,P,op", POSETS)
def test_c2_prop31_psv(name, P, op):
    d = pasv_distribution(P, np.ones(P.n))
    psv = psv_distribution(P)
    assert max(abs(d[p] - psv[p]) for p in psv) < 1e-12


# -- C2 / Prop 3.2: ordered partition -> WSV --
@pytest.mark.parametrize("name,P,op", [(n, P, op) for n, P, op in POSETS if op])
def test_c2_prop32_wsv(name, P, op):
    lam = np.arange(1, P.n + 1, dtype=float)
    d = pasv_distribution(P, lam)
    les = P.linear_extensions()
    wsv = {p: wsv_backward_sample_weight(p, op, lam) for p in les}
    zs = sum(wsv.values()); wsv = {p: v / zs for p, v in wsv.items()}
    assert max(abs(d[p] - wsv[p]) for p in les) < 1e-9


# -- C2: Shapley axioms E, L, NP --
@pytest.mark.parametrize("name,P,op", POSETS)
def test_c2_axioms(name, P, op):
    lam = np.arange(1, P.n + 1, dtype=float)
    U = lambda S: float(sum((i + 1) ** 2 * 0.5 ** i for i in S))
    psi = pasv_value(P, lam, U)
    assert abs(psi.sum() - U(frozenset(range(P.n)))) < 1e-9            # Efficiency
    V = lambda S: float((sum(S) + 1) % 5)
    psi_mix = pasv_value(P, lam, (lambda S: 2 * U(S) + 3 * V(S)))
    assert np.max(np.abs(psi_mix - (2 * pasv_value(P, lam, U) + 3 * pasv_value(P, lam, V)))) < 1e-9  # Linearity
    Un = lambda S: float(sum((i + 1) ** 2 * 0.5 ** i for i in S if i != P.n - 1))
    assert abs(pasv_value(P, lam, Un)[P.n - 1]) < 1e-9                # Null player


# -- C2: no precedence + const λ -> classical Shapley --
def test_c2_classical_sv():
    empty = Poset(4, set())
    U = lambda S: float(sum((i + 1) for i in S))
    assert np.max(np.abs(pasv_value(empty, np.ones(4), U) - classical_shapley(U, 4))) < 1e-12


# -- C3: MCMC converges to p and estimates ψ --
@pytest.mark.parametrize("name,P,op", [(n, P, op) for n, P, op in POSETS if P.n <= 5])
def test_c3_mcmc(name, P, op):
    lam = np.arange(1, P.n + 1, dtype=float)
    d_true = pasv_distribution(P, lam)
    samples = pasv_mcmc(P, lam, n_samples=30000, burn_in=5000, seed=7)
    d_emp = empirical_distribution(samples, P)
    tv = 0.5 * sum(abs(d_true[p] - d_emp[p]) for p in d_true)
    assert tv < 0.06
    U = lambda S: float(sum((i + 1) for i in S))
    psi_est = mcmc_value_estimate(samples, U, P.n)
    assert np.max(np.abs(psi_est - pasv_value(P, lam, U))) < 0.25


# -- Negative control: PASV is NOT uniform when λ non-constant & >1 LE --------
def test_negative_nonuniform_not_psv():
    P = Poset(4, {(0, 2), (1, 2), (2, 3)})
    d = pasv_distribution(P, np.array([1.0, 5.0, 1.0, 1.0]))
    psv = psv_distribution(P)
    assert max(abs(d[p] - psv[p]) for p in psv) > 0.01
