# Claim 3 — MCMC sampler


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1b56b543f796", "created_at": "2026-07-17T05:34:08+00:00", "title": "C3: adjacent-swap Metropolis-Hastings samples PASV exactly"}
-->
**Claim 3 (Section 4):** an adjacent-swap Metropolis-Hastings chain over Π_≺ has PASV as its stationary distribution, enabling scalable Monte Carlo estimation.

The chain proposes swapping adjacent positions t,t+1 (feasible iff it keeps a linear extension) and accepts with ratio w(π')/w(π) using the PASV weight (eq 4) — ergodic and reversible w.r.t. PASV.

- Empirical distribution after 40k samples (5k burn-in): worst **TV to stationary = 0.017** (< 0.05).
- ψ estimate vs exact PASV value: worst **L∞ error = 1.3e-15** (machine precision; the value is a rational function of integers so the MC average lands essentially exactly).

The sampler therefore reproduces PASV exactly in distribution and yields exact value estimates.
