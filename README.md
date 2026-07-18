# Priority-Aware Shapley Value (PASV) — ICML 2026 Reproduction

Reproduction of **Kiljae Lee, Ziqi Liu, Weijing Tang & Yuan Zhang,
"Priority-Aware Shapley Value"**
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
| **C3** | An adjacent-swap Metropolis-Hastings sampler targets PASV exactly and enables scalable Monte Carlo estimation. | ✅ Verified at n=8192 |

## Method

* `repro/src/pasv.py` — poset + linear-extension enumeration, PASV distribution
  (eq 4), PSV, WSV (backward λ-sampling), PASV/PSV values, classical Shapley.
* `repro/src/mcmc.py` — generic adjacent-swap MH sampler (Section 4), with
  non-enumerating Kahn initialization and Lemma 4.1 local ratios.
* `repro/src/scalable_mcmc.py` — sparse-poset and vectorized ordered-partition
  kernels; no factorial enumeration or dense n² edge materialization.
* `repro/src/run_c3_scalability.py` — eleven-route correctness, convergence,
  timing, memory, and accuracy audit through the paper's maximum n=8192.
* `repro/tests/test_pasv.py` — 25 pytest tests.

## How to run

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy pytest
python -m pytest repro/tests/test_pasv.py -q      # 25 tests
python repro/src/run_claims.py                    # writes outputs/
python repro/src/run_c3_scalability.py --output-dir outputs  # ~3 min CPU
```

## Headline results (CPU)

**C1:** 100% of PASV mass on Π_≺ (precedence enforced); perturbing a single λ_i
moves the distribution whenever >1 linear extension exists (soft weights active).

**C2 (machine precision):** Prop 3.1 const-λ→PSV (**0.0**); Prop 3.2
ordered-partition→WSV (**0.0**); Efficiency 1.8e-15, Linearity 1.8e-15,
Null-player 0.0; bonus no-precedence+const-λ→classical Shapley (**0.0**).

**C3 correctness:** an exact finite transition-matrix check gives detailed
balance residual **3.5e-18**; 200k samples on an enumerated target with a
1024:1 priority range give TV **0.0040**. Local acceptance ratios agree with
the full PASV product to **1.1e-15**.

**C3 scale:** 15 sparse-poset configurations across four families reach
**n=8192** without enumerating linear extensions; the worst measured scalar
throughput is **216k transitions/s**. At n=8192 and priority ratios through
1024:1, throughput remains at least **175k/s**. A factorized adjacent-MH kernel
for 512 ordered blocks processes **517.1M** scalar proposals at **6.65M/s** and
estimates a closed-form sum-of-unanimity value with ARE **0.0453** from 10,000
retained samples; peak RSS is **73.4 MiB** in the captured run.

The audit retains a negative route: the paper's global-uniform proposal with
burn-in 100,000 and thinning 1,000 has ARE **0.280** on this controlled utility
because each block moves only about twice between retained states. Batched
commuting within-block proposals preserve the same product target and resolve
that measured autocorrelation bottleneck.

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | All 3 claims; exact small-poset checks plus 4 families and ordered partitions through n=8192 | Paper also uses d=n² random-set SOU utilities and application datasets |
| Hardware | 4 vCPU (CPU only) | any CPU |
| Time | ~3 min full C3 audit; 6 s tests | — |
| Cost | $0 | — |
| Outcome | C1/C2 verified; C3 correctness and scalability verified | — |
