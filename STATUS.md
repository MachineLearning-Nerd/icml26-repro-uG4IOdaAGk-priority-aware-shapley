# STATUS — Priority-Aware Shapley Value (`uG4IOdaAGk`)

**Session:** NewPaper. **Last updated:** 2026-07-17. **State:** locally complete; GitHub push pending; HF queued.

## Source
- arXiv 2602.09326 (Das & Srivastava). Clean-room from PDF.

## Evidence (locally complete)
- **C1 verified:** PASV supported on Π_≺ (precedence) + λ-dependent (soft weights).
- **C2 verified (machine precision):** Prop 3.1 const-λ→PSV (0.0); Prop 3.2
  ordered-partition→WSV (0.0); axioms E/L/NP (≤1.8e-15); classical-SV reduction (0.0).
- **C3 verified:** adjacent-swap MH → TV 0.017 to PASV; value estimate 1.3e-15.
- **21/21 pytest tests pass** (<3 s).
- Trackio complete/tagged/pinned/command-captured.

## Next
- Push GitHub `MachineLearning-Nerd/icml26-repro-uG4IOdaAGk-priority-aware-shapley`.
- Publish `DineshAI/uG4IOdaAGk` after HF quota reset; verify tags/bucket; `under_verdict`.
