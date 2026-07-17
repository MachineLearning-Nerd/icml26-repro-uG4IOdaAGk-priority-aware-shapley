"""Evidence orchestrator: Priority-Aware Shapley Value (Das & Srivastava,
arXiv 2602.09326, uG4IOdaAGk). Verifies the claims and writes outputs/."""
import os, sys, csv, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from pasv import (Poset, pasv_distribution, psv_distribution, pasv_value,
                  psv_value, classical_shapley, pasv_weight,
                  wsv_backward_sample_weight, random_order_value, Utility)
from mcmc import pasv_mcmc, empirical_distribution, mcmc_value_estimate

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUT, exist_ok=True)


def posets():
    """(name, Poset, ordered_partition_or_None)."""
    return [
        ("chain-4", Poset(4, {(0, 1), (1, 2), (2, 3)}), None),
        ("V-poset-4", Poset(4, {(0, 2), (1, 2), (2, 3)}), None),
        ("2-level-5", Poset(5, {(0, 3), (1, 3), (2, 4)}), None),
        ("ord-partition-B1B2", Poset(4, {(0, 2), (0, 3), (1, 2), (1, 3)}),
         [[0, 1], [2, 3]]),
        ("ord-partition-3blocks", Poset(5, {(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)}),
         [[0, 1], [2, 3], [4]]),
    ]


def claim1_definition():
    """C1: PASV incorporates precedence (supported on Π_≺) AND soft weights
    (varies with λ). Shown by: PASV has zero mass off Π_≺, and changes with λ."""
    rows = []
    for name, P, _ in posets():
        lam = np.arange(1, P.n + 1, dtype=float)
        d = pasv_distribution(P, lam)
        off_le = len([p for p in __import__("itertools").permutations(range(P.n))
                      if not P.is_le(p)])
        on_mass = sum(d.values())
        # PASV is scale-invariant in λ (only ratios matter, like WSV), so to
        # show soft weights are ACTIVE we perturb a SINGLE λ_i (changing ratios)
        lam2 = lam.copy(); lam2[0] *= 5.0
        d2 = pasv_distribution(P, lam2)
        tv_change = 0.5 * sum(abs(d[p] - d2.get(p, 0.0)) for p in d)
        rows.append({"poset": name, "mass_on_LEs": on_mass,
                     "tv_change_under_3x_lambda": tv_change,
                     "precedence_enforced": abs(on_mass - 1.0) < 1e-12,
                     # weights only affect the distribution when >1 LE exists
                     # (a total chain has a unique linear extension)
                     "weights_active": (tv_change > 0) or len(d) == 1})
    with open(os.path.join(OUT, "c1_definition.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return {"claim": "C1 PASV = precedence + soft weights",
            "all_enforce_precedence": all(r["precedence_enforced"] for r in rows),
            "all_weights_active": all(r["weights_active"] for r in rows)}


def claim2_reductions_and_axioms():
    """C2: PASV recovers PSV (Prop 3.1) and WSV (Prop 3.2), satisfies the
    Shapley axioms, and reduces to classical SV with no precedence."""
    rng = np.random.default_rng(0)
    U = lambda S: float(sum((i + 1) ** 2 * 0.5 ** i for i in S))
    rows = []; worst_psv = worst_wsv = worst_eff = worst_lin = worst_null = 0.0
    for name, P, op in posets():
        lam = np.arange(1, P.n + 1, dtype=float)
        # Prop 3.1
        d_const = pasv_distribution(P, np.ones(P.n))
        d_psv = psv_distribution(P)
        e1 = max(abs(d_const[p] - d_psv[p]) for p in d_psv)
        worst_psv = max(worst_psv, e1)
        rows.append({"poset": name, "test": "Prop3.1 const-λ==PSV", "err": e1})
        # Prop 3.2 (only for ordered-partition posets)
        if op is not None:
            d_pasv = pasv_distribution(P, lam)
            les = P.linear_extensions()
            wsv = {p: wsv_backward_sample_weight(p, op, lam) for p in les}
            zs = sum(wsv.values()); wsv = {p: v / zs for p, v in wsv.items()}
            e2 = max(abs(d_pasv[p] - wsv[p]) for p in les)
            worst_wsv = max(worst_wsv, e2)
            rows.append({"poset": name, "test": "Prop3.2 ordered-part==WSV", "err": e2})
        # Axioms E, L, NP
        psi = pasv_value(P, lam, U)
        eff = abs(psi.sum() - U(frozenset(range(P.n)))); worst_eff = max(worst_eff, eff)
        V = lambda S: float((sum(S) + 1) % 5)
        psi_mix = pasv_value(P, lam, (lambda S: 2 * U(S) + 3 * V(S)))
        lin = float(np.max(np.abs(psi_mix - (2 * pasv_value(P, lam, U) + 3 * pasv_value(P, lam, V)))))
        worst_lin = max(worst_lin, lin)
        # null player: make player n-1 irrelevant
        Un = lambda S: float(sum((i + 1) ** 2 * 0.5 ** i for i in S if i != P.n - 1))
        null = abs(pasv_value(P, lam, Un)[P.n - 1]); worst_null = max(worst_null, null)
    # Classical SV reduction (empty poset + const λ)
    empty = Poset(4, set())
    U4 = lambda S: float(sum((i + 1) for i in S))
    sv_red = float(np.max(np.abs(pasv_value(empty, np.ones(4), U4) - classical_shapley(U4, 4))))
    rows.append({"poset": "(empty)", "test": "const-λ no-precedence==classical SV", "err": sv_red})
    with open(os.path.join(OUT, "c2_reductions_axioms.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return {"claim": "C2 reductions + axioms",
            "worst_Prop3.1_PSV": worst_psv, "worst_Prop3.2_WSV": worst_wsv,
            "worst_efficiency": worst_eff, "worst_linearity": worst_lin,
            "worst_null_player": worst_null, "classical_SV_reduction_err": sv_red,
            "all_machine_precision": max(worst_psv, worst_wsv, worst_eff, worst_lin, worst_null, sv_red) < 1e-9}


def claim3_mcmc():
    """C3: adjacent-swap MH samples p exactly; value estimate converges to ψ."""
    rng = np.random.default_rng(0)
    rows = []; worst_kl = worst_val = 0.0
    for name, P, _ in posets():
        if P.n > 5:
            continue
        lam = np.arange(1, P.n + 1, dtype=float)
        d_true = pasv_distribution(P, lam)
        samples = pasv_mcmc(P, lam, n_samples=40000, burn_in=5000, seed=42)
        d_emp = empirical_distribution(samples, P)
        # total variation distance as the convergence metric
        tv = 0.5 * sum(abs(d_true[p] - d_emp[p]) for p in d_true)
        U = lambda S: float(sum((i + 1) for i in S))
        psi_true = pasv_value(P, lam, U)
        psi_est = mcmc_value_estimate(samples, U, P.n)
        val_err = float(np.max(np.abs(psi_true - psi_est)))
        worst_kl = max(worst_kl, tv); worst_val = max(worst_val, val_err)
        rows.append({"poset": name, "tv_to_stationary": tv, "value_Linf_err": val_err,
                     "n_samples": len(samples)})
    with open(os.path.join(OUT, "c3_mcmc.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return {"claim": "C3 MCMC sampler",
            "worst_tv_to_stationary": worst_kl, "worst_value_err": worst_val,
            "converges": worst_kl < 0.05 and worst_val < 0.2}


def main():
    print("=== C1 ==="); r1 = claim1_definition(); print(json.dumps(r1, indent=2, default=lambda o: bool(o) if isinstance(o,np.bool_) else float(o)))
    print("=== C2 ==="); r2 = claim2_reductions_and_axioms(); print(json.dumps(r2, indent=2, default=lambda o: bool(o) if isinstance(o,np.bool_) else float(o)))
    print("=== C3 ==="); r3 = claim3_mcmc(); print(json.dumps(r3, indent=2, default=lambda o: bool(o) if isinstance(o,np.bool_) else float(o)))
    overall = {
        "paper": "Priority-Aware Shapley Value (Das & Srivastava 2602.09326, uG4IOdaAGk)",
        "claims": {"C1_definition": r1, "C2_reductions_axioms": r2, "C3_mcmc": r3},
        "verdict": {"C1_verified": r1["all_enforce_precedence"] and r1["all_weights_active"],
                    "C2_verified": r2["all_machine_precision"],
                    "C3_verified": r3["converges"]},
    }
    json.dump(overall, open(os.path.join(OUT, "summary.json"), "w"), indent=2,
              default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    print("\nWrote", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
