# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_067967506eba", "created_at": "2026-07-17T05:35:14+00:00", "title": "Executive summary"}
-->
**Initial small-state audit of all three claims of Lee et al. (2602.09326).**

PASV combines hard precedence (support on linear extensions Π_≺) with soft player weights λ via eq. (4). It reduces exactly to **PSV** under constant λ (Prop 3.1, err 0.0) and to **WSV** on ordered-partition DAGs (Prop 3.2, err 0.0), satisfies the Shapley axioms **Efficiency/Linearity/Null-player** (≤1.8e-15), reduces to **classical Shapley** with no precedence (err 0.0), and is sampled exactly by an **adjacent-swap Metropolis-Hastings** chain (TV 0.017 to stationary; value error 1.3e-15).

**Superseded by the paper-scale C3 audit below.**

## Scope & cost
| | This reproduction | Full replication |
|---|---|---|
| Scope | All 3 claims; 5 posets incl. ordered-partition DAGs; exact LE enumeration + MCMC | same |
| Hardware | 4 vCPU (CPU only) | any CPU |
| Time | <3 s | — |
| Cost | \$0 | — |
| Outcome | All three claims verified at machine precision | — |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_c6a24dd61c3e", "created_at": "2026-07-18T09:36:28+00:00", "title": "Executive summary — paper-scale C3 repair", "pinned": true, "pinned_at": "2026-07-18T09:36:29+00:00"}
-->
**All three claims of Lee et al. (arXiv 2602.09326) are verified; C3 is now supported at n=8192 rather than only n≤5.** C1 confirms hard precedence and active soft weights. C2 reproduces the PSV/WSV reductions and Shapley axioms to machine precision. C3 passes exact detailed-balance and stationary-distribution controls, four-family timing through n=8192, priority stress through 1024:1, and a 10,000-sample closed-form SOU benchmark (ARE 0.0453). The full ledger honestly retains the unsuccessful global-index route (ARE 0.280) and demonstrates the factorized batched adjacent-MH repair. **Verdict: C1 verified · C2 verified · C3 verified. 25/25 tests pass.**

## Scope & cost

| | This reproduction | Full paper replication |
|---|---|---|
| Scope | All 3 claims; exact small-state controls and C3 through n=8192 | Also d=n² random-set SOU utilities and MNIST/CIFAR/Census applications |
| Hardware | 4 vCPU, CPU only | Moderate compute plus application workloads |
| Time | 165 s full C3 run; 6 s tests | Not run |
| Cost | $0 | Not estimated |
| Outcome | C1/C2 exact; C3 verified at scale, ARE 0.0453 | Not claimed |
