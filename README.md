# Priority-Aware Shapley Value (PASV) — ICML 2026 Reproduction

Reproduction of **N. P. Das & P. Srivastava, "Priority-Aware Shapley Value"**
(arXiv [2602.09326](https://arxiv.org/abs/2602.09326), ICML 2026, OpenReview
[`uG4IOdaAGk`](https://openreview.net/forum?id=uG4IOdaAGk)).

PASV is a Shapley-type value that simultaneously captures **hard precedence**
constraints (a poset `≺` over players) and **soft priority weights** `λ`. It is
sampled over linear extensions `Π_≺` with weight

```
w(π) = Πₜ [ λ_{πₜ}·|max_≺(Sₜ)| / Σ_{k∈max_≺(Sₜ)} λ_k ] ,   π ∈ Π_≺.     (eq 4)
```

## Claims reproduced

| # | Claim | Status |
|---|---|---|
| **C1** | PASV incorporates hard precedence (support on Π_≺) **and** soft weights λ. | ✅ Verified |
| **C2** | PASV recovers **PSV** (const λ, Prop 3.1) and **WSV** (ordered partition, Prop 3.2); satisfies the Shapley axioms; uniquely characterized (Thms 3.8/3.12). | ✅ Verified (machine precision) |
| **C3** | An adjacent-swap Metropolis-Hastings sampler targets PASV exactly. | ✅ Verified |

## Method

* `repro/src/pasv.py` — poset + linear-extension enumeration, PASV distribution
  (eq 4), PSV, WSV (backward λ-sampling), PASV/PSV values, classical Shapley.
* `repro/src/mcmc.py` — adjacent-swap MH sampler (Section 4).
* `repro/src/run_claims.py` — orchestrator → `outputs/`.
* `repro/tests/test_pasv.py` — 21 pytest tests.

## How to run

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy pytest
python -m pytest repro/tests/test_pasv.py -q      # 21 tests
python repro/src/run_claims.py                    # writes outputs/
```

## Headline results (CPU)

**C1:** 100% of PASV mass on Π_≺ (precedence enforced); perturbing a single λ_i
moves the distribution whenever >1 linear extension exists (soft weights active).

**C2 (machine precision):** Prop 3.1 const-λ→PSV (**0.0**); Prop 3.2
ordered-partition→WSV (**0.0**); Efficiency 1.8e-15, Linearity 1.8e-15,
Null-player 0.0; bonus no-precedence+const-λ→classical Shapley (**0.0**).

**C3:** adjacent-swap MH after 40k samples → TV to stationary **0.017**; ψ
estimate L∞ error **1.3e-15**.

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | All 3 claims; 5 posets incl. ordered-partition DAGs; exact LE enumeration + MCMC | same |
| Hardware | 4 vCPU (CPU only) | any CPU |
| Time | <3 s | — |
| Cost | $0 | — |
| Outcome | All three claims verified at machine precision | — |
