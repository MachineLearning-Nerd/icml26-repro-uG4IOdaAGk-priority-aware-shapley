# Claim 1 — Definition


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_81856e1813bb", "created_at": "2026-07-17T05:34:06+00:00", "title": "C1: PASV = hard precedence + soft priority weights"}
-->
**Claim 1:** PASV is a random-order value supported on the **linear extensions** Π_≺ (hard precedence) whose distribution depends on player-specific **soft weights λ**.

Verified on 5 posets (chain, V, 2-level, two ordered-partition DAGs):
- **Precedence enforced:** 100% of PASV mass lies on Π_≺ (0 mass on order-violating permutations) in every case.
- **Soft weights active:** changing a single λ_i (which changes the weight *ratios*) changes the distribution (TV > 0) whenever >1 linear extension exists. (PASV is scale-invariant in λ — only ratios matter, as with WSV.)
