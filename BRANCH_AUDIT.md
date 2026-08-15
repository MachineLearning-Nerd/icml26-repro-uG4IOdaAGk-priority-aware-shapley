# Branch audit

The original repository had one branch, `master`, at pre-normalization tip
`16ac0fb`. It is renamed to `main`; no experimental branch history existed in
this repository.

| Final branch | Former branch | Role |
| --- | --- | --- |
| `main` | `master` | Public PASV implementation, committed evidence, documentation, and final verifier |

Final remote branch set: **one branch, `main`**.

## Naming rules

- `main` is the only default/public branch.
- No legacy `master` or internal experiment prefix remains.
- Claim-specific history is represented by the producer scripts and durable
  artifacts under `outputs/`, not by undocumented branch names.

## Commit identity

All reachable commits in the final repository must use:

```text
MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
```

`verify_final.py` checks both author and committer identity across all local
refs.
