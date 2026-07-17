# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_067967506eba", "created_at": "2026-07-17T05:35:14+00:00", "title": "Executive summary", "pinned": true, "pinned_at": "2026-07-17T05:35:15+00:00"}
-->
**All three claims of Das & Srivastava (2602.09326) reproduced on CPU, verified to machine precision.**

PASV combines hard precedence (support on linear extensions Π_≺) with soft player weights λ via eq. (4). It reduces exactly to **PSV** under constant λ (Prop 3.1, err 0.0) and to **WSV** on ordered-partition DAGs (Prop 3.2, err 0.0), satisfies the Shapley axioms **Efficiency/Linearity/Null-player** (≤1.8e-15), reduces to **classical Shapley** with no precedence (err 0.0), and is sampled exactly by an **adjacent-swap Metropolis-Hastings** chain (TV 0.017 to stationary; value error 1.3e-15).

**Verdict:** C1 ✅ · C2 ✅ · C3 ✅. 21/21 tests pass.

## Scope & cost
| | This reproduction | Full replication |
|---|---|---|
| Scope | All 3 claims; 5 posets incl. ordered-partition DAGs; exact LE enumeration + MCMC | same |
| Hardware | 4 vCPU (CPU only) | any CPU |
| Time | <3 s | — |
| Cost | \$0 | — |
| Outcome | All three claims verified at machine precision | — |
