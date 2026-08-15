# Claim-to-evidence map

Each claim below names the code that produces its evidence, the committed
artifacts that record the result, and the boundary of what the result does
not establish.

## Evidence flow

```text
arXiv v2 text snapshot
        ↓
mathematical implementation + controlled posets
        ↓
claim runner → CSV/JSON artifacts
        ↓
pytest invariants + negative controls
        ↓
scalability acceptance rule and final verifier
```

## Claim 1 — PASV definition

**Paper contract.** PASV should support only precedence-feasible linear
extensions while allowing contributor-specific positive weights `λ` to alter
the distribution whenever the poset has more than one feasible extension.

**Producer and checks.**

- Implementation: `repro/src/pasv.py`
- Producer: `repro/src/run_claims.py`, function `claim1_definition()`
- Focused tests: `test_c1_precedence_enforced()` and
  `test_c1_weights_active_when_multi_le()` in `repro/tests/test_pasv.py`
- Artifact: `outputs/c1_definition.csv`

**Observed result.** Five controlled posets have total mass `1.0` on their
linear extensions. A single-weight perturbation changes the distribution on
every multi-extension case; the chain case is correctly unchanged because it
has only one feasible order. Result: **VERIFIED** for this finite definition
contract.

## Claim 2 — reductions and axioms

**Paper contract.** Constant weights should recover precedence-only Shapley
value (PSV); ordered-partition precedence with the corresponding weights
should recover weighted Shapley value (WSV); and PASV should satisfy efficiency,
linearity, and the null-player axiom. With no precedence and constant weights,
it should reduce to classical Shapley value.

**Producer and checks.**

- Implementation: `repro/src/pasv.py`
- Producer: `repro/src/run_claims.py`, function
  `claim2_reductions_and_axioms()`
- Focused tests: `test_c2_prop31_psv()`, `test_c2_prop32_wsv()`,
  `test_c2_axioms()`, and `test_c2_classical_sv()`
- Artifact: `outputs/c2_reductions_axioms.csv`

**Observed result.** The committed eight-row check records zero error for both
special-case reductions and the classical reduction. The worst efficiency or
linearity error is `1.7763568394002505e-15`; the null-player error is zero.
Result: **VERIFIED** to machine precision on the registered finite controls.

## Claim 3 — adjacent-swap MCMC and scalability

**Paper contract.** The adjacent-swap Metropolis–Hastings chain should target
the PASV distribution, support accurate Monte Carlo value estimates, and scale
without factorial linear-extension enumeration.

### Small-poset correctness route

- Generic chain: `repro/src/mcmc.py`
- Producer: `repro/src/run_claims.py`, function `claim3_mcmc()`
- Focused tests: `test_c3_mcmc()` and the negative non-uniformity control
- Artifact: `outputs/c3_mcmc.csv`

Five small posets use 40,000 retained samples each. The worst total-variation
distance to the exact stationary distribution is `0.01638159340659339`, and
the worst value-estimation infinity-norm error is
`1.3322676295501878e-15`.

### Large-scale 11-route audit

- Scalable kernels: `repro/src/scalable_mcmc.py`
- Producer: `repro/src/run_c3_scalability.py`
- Focused tests: Kahn initialization, local ratios, prefix statistics,
  ordered-partition invariants, and batched-sweep behavior
- Artifacts: `outputs/c3_scalability_attempts.json`,
  `outputs/c3_family_scaling.csv`, `outputs/c3_priority_skew.csv`,
  `outputs/c3_sou_convergence.csv`, and
  `outputs/c3_batched_sou_convergence.csv`

The registered acceptance rule requires routes 1–9 and route 11 to pass; route
10 is a retained negative control. The committed audit records:

| Route group | Evidence | Result |
| --- | --- | --- |
| 1–4 | Kahn initialization at `n=8192`; 7,085 local-ratio comparisons; 10,000 prefix-state checks; 1,940 ordered-partition comparisons | **PASS** |
| 5–6 | 26-state exact transition-matrix detailed balance residual `3.4694460492507815e-18`; 200,000-sample exact-target TV `0.004043521214755388` at priority ratio 1024 | **PASS** |
| 7 | 15 configurations across four synthetic families, maximum `n=8192`, minimum throughput `222,501.63` transitions/s | **PASS** |
| 8 | Six `n=8192` priority-skew settings through ratio `1024:1`, minimum throughput `174,756.74` transitions/s | **PASS** |
| 9 | Independent exact backward sampler, 5,000 samples at `n=128`, ARE `0.052913156209120966` | **PASS** |
| 10 | Global-index paper schedule, `n=8192`, 512 blocks, ARE `0.2800655365314504` | **RETAINED NEGATIVE CONTROL** |
| 11 | Factorized batched adjacent-MH, 10,000 samples, 517,120,000 scalar proposals, ARE `0.045301974145854476`, 6,620,418 proposals/s | **PASS** |

The factorized route does not change the target distribution: its local
ordered-partition ratios are checked against the dense target and its block
invariants are tested. It addresses the measured autocorrelation bottleneck
of route 10. Overall result: **VERIFIED** under the explicit acceptance rule,
not by suppressing the failed route.

## Reproduction boundary

The paper's application experiments on MNIST/CIFAR10 data valuation and
Census Income feature attribution are not included in the committed audit.
The verified C3 scope is the exact mathematical/synthetic sampler and
scalability contract described above.
