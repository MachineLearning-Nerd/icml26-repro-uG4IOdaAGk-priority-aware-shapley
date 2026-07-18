# STATUS — Priority-Aware Shapley Value (`uG4IOdaAGk`)

**Session:** perfect-score campaign. **Last updated:** 2026-07-18. **State:** C3
paper-scale repair passed locally; publication and official re-verdict in progress.

GitHub: `MachineLearning-Nerd/icml26-repro-uG4IOdaAGk-priority-aware-shapley`
(previous public SHA `1ade40f`; repair SHA pending push).
HF Space: `DineshAI/uG4IOdaAGk` (repair SHA pending publish).

## Source
- arXiv 2602.09326 (Lee, Liu, Tang & Zhang). Clean-room from v2 PDF/source.

## Evidence (locally complete)
- **C1 verified:** PASV supported on Π_≺ (precedence) + λ-dependent (soft weights).
- **C2 verified (machine precision):** Prop 3.1 const-λ→PSV (0.0); Prop 3.2
  ordered-partition→WSV (0.0); axioms E/L/NP (≤1.8e-15); classical-SV reduction (0.0).
- **C3 verified at scale:** exact detailed-balance residual 3.5e-18; exact-target
  TV 0.0040 at priority ratio 1024:1; four families through n=8192; generic
  throughput ≥174k/s; batched ordered-partition MH ARE 0.0453 from N=10,000,
  517.1M scalar proposals at 6.62M/s, 73.4 MiB peak RSS.
- **Attempt ledger:** 10/11 routes pass. The global-index paper schedule is
  retained as a negative control (ARE 0.280); factorized batched adjacent-MH
  sweeps repair the measured per-block autocorrelation.
- **25/25 pytest tests pass** (6.1 s).
- Trackio full command captured; seven CSV/JSON artifacts promoted to public HF
  bucket; conclusion updated and pinned.

## Next
- Complete publish gate, push GitHub repair commit, upload rendered Space.
- Verify public SHA/tags/artifact readback and wait for official C3 re-verdict.
