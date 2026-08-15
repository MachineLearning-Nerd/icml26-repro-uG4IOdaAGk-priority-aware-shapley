# Status — `icml26-priority-aware-shapley`

**Last updated:** 2026-08-15

**Repository:** <https://github.com/MachineLearning-Nerd/icml26-priority-aware-shapley>

**Role:** independent ICML 2026 reproduction and evidence audit

## Current verdicts

| Claim | Result | Evidence boundary |
| --- | --- | --- |
| C1 — PASV definition | **VERIFIED** | Five controlled posets: all mass is on feasible linear extensions and non-constant `λ` changes multi-extension distributions |
| C2 — reductions and axioms | **VERIFIED** | PSV, WSV, classical-Shapley reductions and axioms; worst recorded error `1.7763568394002505e-15` |
| C3 — MCMC and scalability | **VERIFIED** | Routes 1–9 and 11 pass; route 10 remains a documented negative control; scale reaches `n=8192` |

The original repository name was
`icml26-repro-uG4IOdaAGk-priority-aware-shapley`. The final branch and identity
mapping is documented in [`BRANCH_AUDIT.md`](BRANCH_AUDIT.md).

This repository is not the authors' official code and does not imply author
endorsement. Application-level MNIST/CIFAR10/Census results are outside the
committed reproduction scope.
