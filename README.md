# icml26-priority-aware-shapley

Independent ICML 2026 reproduction and evidence audit for
[*Priority-Aware Shapley Value*](https://arxiv.org/abs/2602.09326).

Paper authors: Kiljae Lee, Ziqi Liu, Weijing Tang, and Yuan Zhang.

This repository is a clean-room reproduction and audit. It is not the
authors' official implementation and does not claim an affiliation with the
authors. The paper record and version used here are [arXiv
2602.09326v2](https://arxiv.org/abs/2602.09326), revised 14 June 2026.

## What the paper does

Priority-Aware Shapley Value (PASV) extends permutation-based Shapley values
to settings where contributors have both:

- hard precedence constraints, represented by a poset and its feasible linear
  extensions; and
- soft, contributor-specific priority weights `λ` that bias feasible orders.

The paper shows reductions to precedence-only Shapley value (PSV) and
weight-based Shapley value (WSV), gives an axiomatic characterization, and
develops an adjacent-swap Metropolis–Hastings sampler for scalable Monte Carlo
estimation.

## Scientific status

| Claim | Contract tested | Result | Evidence |
| --- | --- | --- | --- |
| C1 — PASV definition | Precedence support and non-constant priority weights | **VERIFIED** | [C1 evidence](CLAIM_EVIDENCE.md#claim-1--pasv-definition) |
| C2 — reductions and axioms | PSV/WSV reductions, classical reduction, efficiency, linearity, null player | **VERIFIED** to machine precision | [C2 evidence](CLAIM_EVIDENCE.md#claim-2--reductions-and-axioms) |
| C3 — adjacent-swap MCMC and scale | Correctness controls plus accepted scalability routes through `n=8192` | **VERIFIED** under the registered acceptance rule | [C3 evidence](CLAIM_EVIDENCE.md#claim-3--adjacent-swap-mcmc-and-scalability) |

C3 retains one failed route as a negative control: the paper-style global-index
schedule has high autocorrelation on the controlled 512-block utility. The
factorized batched adjacent-MH route preserves the same target and passes the
registered accuracy threshold. The failed route is reported, not hidden.

## How the claims are produced

The reproduction is driven by small, inspectable Python functions and durable
CSV/JSON artifacts:

1. `repro/src/pasv.py` defines posets, feasible linear extensions, PASV/PSV,
   WSV, and utility values.
2. `repro/src/mcmc.py` implements the generic adjacent-swap MH chain and
   empirical value estimator.
3. `repro/src/scalable_mcmc.py` implements Kahn initialization, sparse-poset
   local ratios, prefix statistics, and the factorized ordered-partition
   chain.
4. `repro/src/run_claims.py` produces C1/C2 and the small-poset C3 artifacts.
5. `repro/src/run_c3_scalability.py` runs the 11-route C3 audit, including
   exact transition-matrix checks, priority-skew stress, timing/memory
   scaling, and the retained negative control.
6. `repro/tests/test_pasv.py` checks mathematical identities, negative
   controls, local-ratio invariants, and the scalable chain.

The complete producer-to-artifact map is in
[`CLAIM_EVIDENCE.md`](CLAIM_EVIDENCE.md). Paper and output provenance is in
[`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md).

## Reproduce

Create the small locked environment used by the original reproduction:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install numpy pytest
```

Run the focused tests:

```bash
python -m pytest repro/tests/test_pasv.py -q
```

Regenerate the claim summary and the full C3 scalability audit:

```bash
python repro/src/run_claims.py
python repro/src/run_c3_scalability.py --output-dir outputs
```

The full C3 audit is CPU-only and takes about three minutes on the recorded
four-vCPU run. `verify_final.py` checks the published artifacts and focused
tests without rerunning that longer audit:

```bash
python verify_final.py
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `repro/src/pasv.py` | PASV, PSV, WSV, classical Shapley, and poset utilities |
| `repro/src/mcmc.py` | Generic adjacent-swap Metropolis–Hastings sampler |
| `repro/src/scalable_mcmc.py` | Sparse and factorized scalable kernels |
| `repro/src/run_claims.py` | C1/C2/small-C3 evidence producer |
| `repro/src/run_c3_scalability.py` | 11-route large-scale C3 audit |
| `repro/tests/test_pasv.py` | Focused formal tests |
| `outputs/` | Committed CSV/JSON evidence and summary |
| `docs/paper.txt` | Local text snapshot of arXiv v2 |
| `CLAIM_EVIDENCE.md` | Claim-to-code-to-artifact map |
| `SOURCE_MANIFEST.md` | Paper, environment, and output provenance |
| `BRANCH_AUDIT.md` | Branch normalization record |
| `CITATION.cff` | Citation metadata |
| `verify_final.py` | Fail-closed final-state verifier |

## Scope and limitations

The committed audit covers exact small-poset identities, MCMC convergence
controls, four synthetic poset families, priority ratios through 1024:1, and
ordered partitions through `n=8192`. The paper's application experiments on
MNIST/CIFAR10 data valuation and Census Income feature attribution are not
claimed as reproduced here. The global-index route is intentionally retained
as a negative result; the accepted C3 verdict depends on the factorized
ordered-partition kernel and its explicit target-preservation checks.

## Citation and thanks

Please cite the paper when using this repository. See
[`CITATION.cff`](CITATION.cff) and the BibTeX entry in
[`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md).

Thank you to Kiljae Lee, Ziqi Liu, Weijing Tang, and Yuan Zhang for the paper,
the clear mathematical specification, and the problem framing that made this
independent clean-room reproduction possible. Reporting the failed sampling
route alongside the repaired route is part of that reproducibility record.

Maintained by [MachineLearning-Nerd](https://github.com/MachineLearning-Nerd).
