# Source and provenance manifest

This repository distinguishes the paper source, the independent clean-room
implementation, and the generated evidence artifacts.

## Paper

| Field | Value |
| --- | --- |
| Title | *Priority-Aware Shapley Value* |
| Authors | Kiljae Lee; Ziqi Liu; Weijing Tang; Yuan Zhang |
| Current version | arXiv `2602.09326v2`, revised 14 June 2026 |
| Paper | [arXiv abstract and metadata](https://arxiv.org/abs/2602.09326) |
| ICML/OpenReview record | [OpenReview `uG4IOdaAGk`](https://openreview.net/forum?id=uG4IOdaAGk) |
| Local source snapshot | `docs/paper.txt` |
| Local snapshot SHA-256 | `86523b554e1020748cb6f3fa197ec4cf201f70ddb022e801ce91cce8fee90c05` |
| Local snapshot size | 116,866 bytes |

The local snapshot begins with the v2 author list and date. The arXiv record
is the authoritative citation source; the GitHub description that preceded
this audit contained an incorrect author attribution and has been corrected in
the repository metadata.

## Implementation boundary

The code under `repro/src/` is an independent clean-room implementation from
the paper specification and local text snapshot. No official author code is
claimed or bundled. The public implementation surface is organized as:

| Component | Source |
| --- | --- |
| PASV/PSV/WSV definitions | `repro/src/pasv.py` |
| Generic adjacent-swap MH | `repro/src/mcmc.py` |
| Sparse and factorized scalable chains | `repro/src/scalable_mcmc.py` |
| C1/C2/small-C3 producer | `repro/src/run_claims.py` |
| Large C3 audit | `repro/src/run_c3_scalability.py` |
| Formal focused tests | `repro/tests/test_pasv.py` |

## Evidence artifacts

The following committed outputs are the evidence consumed by
`verify_final.py`:

| Artifact | SHA-256 |
| --- | --- |
| `outputs/summary.json` | `f6b98c368b4410f2ef4f8bcbef3a79bfc6ad3d812047485e9e7fc7f85ed60870` |
| `outputs/c1_definition.csv` | `24a6cc261bb51122487fc09013c56b08d96e4add708169ff67b0a5cc4fa761f8` |
| `outputs/c2_reductions_axioms.csv` | `6cf27c6abce0cf71d6540b81323a9fbfc81fe4cc33bd8813566b085e98e41698` |
| `outputs/c3_mcmc.csv` | `5685cc4927cea0cb3d066c3e904753faa3fab35b34bae9e9b37e39a61363c1f0` |
| `outputs/c3_scalability_attempts.json` | `436d75b9b6dcbd42a6954f476c8fe2ca6968e16cc4812231e3575049b15736e0` |
| `outputs/c3_family_scaling.csv` | `d4e9fe71d361c9a1918170a7bbdd734daea63047381b7794c2f2d5bceac13e56` |
| `outputs/c3_priority_skew.csv` | `865dc2cf245fe8e0cd4396e6bae43a3820dcb64d4e4e00d5250064f4307c2da9` |
| `outputs/c3_sou_convergence.csv` | `62a9d1ed3eff81b649d2e8dd99b3051b8ce8183915906920522ab1bf6af15bcc` |
| `outputs/c3_batched_sou_convergence.csv` | `983f184b5881bce7e6caded746c46b09d13c8ecdc7a5a8e4adfd17a2e3acfea2` |

The recorded full C3 run used Python 3.12.13, NumPy 2.5.1, four logical CPU
cores, and no GPU. The focused tests and the large audit are CPU-only.

## Paper citation

```bibtex
@article{lee2026priority,
  title         = {Priority-Aware Shapley Value},
  author        = {Lee, Kiljae and Liu, Ziqi and Tang, Weijing and Zhang, Yuan},
  journal       = {arXiv preprint arXiv:2602.09326},
  year          = {2026},
  doi           = {10.48550/arXiv.2602.09326},
  url           = {https://arxiv.org/abs/2602.09326}
}
```

## Attribution and thanks

MachineLearning-Nerd maintains this repository as an independent reproduction
and evidence audit. Thank you to Kiljae Lee, Ziqi Liu, Weijing Tang, and Yuan
Zhang for publishing a precise PASV definition, its reductions and axioms, and
the sampler/scalability ideas that made a clean-room audit possible.
