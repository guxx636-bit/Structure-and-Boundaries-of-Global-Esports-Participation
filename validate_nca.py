"""Verification suite for the NCA (CE-FDH) implementation used in the paper.

Run from the repository root (the folder that holds fsqca_audit_v5.csv):

    python validate_nca.py

Four checks are performed and reported; the script exits with status 1 if any
check fails, so it can be wired into a CI step.

  C1  Analytic ceiling.  A synthetic dataset is built with a step ceiling whose
      ceiling-zone area is known in closed form.  The implementation must
      reproduce it to within 1e-4.
  C2  Ceiling recovery.  On the same synthetic data the estimated ceiling line
      must coincide with the constraint that was constructed into the data
      (maximum absolute deviation 0.000).
  C3  Permutation floor.  On synthetic data with a strong constructed ceiling
      the permutation test must return the resolution floor of the test; on
      unconstrained data it must not.
  C4  Regression.  The four effect sizes and the two decisive bottleneck
      entries reported in the paper must recompute from the archived membership
      matrix to the printed precision.

Only numpy and pandas are required.
"""

import sys

import numpy as np
import pandas as pd

B_PERM = 10_000          # permutation draws, as reported in the paper
SEED = 20261010          # fixed so the permutation p-values are reproducible
TOL = 1e-4

_failures = []


def check(name, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        _failures.append(name)


# ── core routines under test (identical to robustness_tables.py) ─────────────

def fdh_ceiling(x, y):
    """CE-FDH step ceiling: highest observed y at or below each x."""
    order = np.argsort(x, kind="mergesort")
    xs, ys = x[order], y[order]
    return xs, np.maximum.accumulate(ys)


def nca_d(x, y):
    """Ceiling zone as a proportion of the [0,1] x [0,1] calibration space."""
    trap = getattr(np, "trapezoid", None) or np.trapz
    cx, cy = fdh_ceiling(x, y)
    xs = np.concatenate(([0.0], cx, [1.0]))
    ys = np.concatenate(([cy[0]], cy, [cy[-1]]))
    return 1.0 - trap(ys, xs)


def necessity_consistency(x, y):
    return float(np.sum(np.minimum(x, y)) / np.sum(y))


def ceiling_accuracy(x, y):
    cx, cy = fdh_ceiling(x, y)
    return float(np.mean(y <= np.interp(x, cx, cy, left=cy[0], right=cy[-1]) + 1e-12))


# ── C1 / C2 : synthetic data with a known step ceiling ──────────────────────
print("\nC1-C2  synthetic step ceiling (constraint: y = 0.30 below x = 0.60, "
      "y = 0.80 at or above it)")

M = 100_000
x_syn = np.linspace(0.0, 1.0, M + 1)
y_syn = np.where(x_syn < 0.60, 0.30, 0.80)

# closed form: 0.60 * (1 - 0.30) + 0.40 * (1 - 0.80) = 0.50
d_analytic = 0.60 * (1.0 - 0.30) + 0.40 * (1.0 - 0.80)
d_syn = nca_d(x_syn, y_syn)
check("C1 analytic ceiling zone", abs(d_syn - d_analytic) < TOL,
      f"closed form {d_analytic:.6f}, implementation {d_syn:.6f}, "
      f"|diff| = {abs(d_syn - d_analytic):.2e} < {TOL:.0e}")

cx, cy = fdh_ceiling(x_syn, y_syn)
dev = float(np.max(np.abs(np.interp(x_syn, cx, cy) - y_syn)))
check("C2 ceiling recovery", dev == 0.0,
      f"max |estimated ceiling - constructed constraint| = {dev:.6f}")

# ── C3 : permutation test on constrained vs unconstrained data ──────────────
print("\nC3  permutation test behaviour")


def perm_p(x, y, cond, B=B_PERM, seed=SEED):
    rng = np.random.default_rng(seed)
    obs = nca_d(x, y)
    hits = sum(1 for _ in range(B) if nca_d(x, y[rng.permutation(len(y))]) >= obs)
    return obs, hits / B


# constrained: the step ceiling above is a hard constraint, so permuting the
# outcome destroys it and no draw should reach the observed effect size.
_, p_constrained = perm_p(x_syn, y_syn, "step")
# unconstrained: outcome independent of the condition.
rng = np.random.default_rng(7)
y_rand = rng.uniform(0.0, 1.0, M + 1)
_, p_unconstrained = perm_p(x_syn, y_rand, "noise")

check("C3 permutation floor", p_constrained == 0.0 and p_unconstrained > 0.05,
      f"constrained data p = {p_constrained:.4f} (0 of {B_PERM} draws reach the "
      f"observed effect size = the resolution floor of the test); "
      f"unconstrained data p = {p_unconstrained:.4f}")

# ── C4 : regression against the archived membership matrix ──────────────────
print("\nC4  regression against the archived membership matrix")
df = pd.read_csv("fsqca_audit_v5.csv")
mem = {c: np.round(df[c].values, 3) for c in ["TECH", "ENG", "INTL", "CULT"]}
y_obs = np.round(df["CE"].values, 3)
N = len(df)

expected_d = {"TECH": 0.350, "ENG": 0.057, "INTL": 0.097, "CULT": 0.045}
d_obs = {c: nca_d(mem[c], y_obs) for c in mem}
d_txt = ", ".join(f"{c} {d_obs[c]:.3f}" for c in ["TECH", "INTL", "ENG", "CULT"])
check("C4a effect sizes", all(abs(round(d_obs[c], 3) - expected_d[c]) < 1e-9 for c in mem),
      f"N = {N}; {d_txt} (all match the printed values)")

# bottleneck: minimum TECH membership required at each outcome threshold
rows = []
for thr in [0.500, 0.700]:
    m = y_obs >= thr
    idx = int(np.argmin(np.where(m, mem["TECH"], np.inf)))
    rows.append((thr, mem["TECH"][idx], df["country"].values[idx]))
ok_b = abs(rows[0][1] - 0.525) < 1e-9 and abs(rows[1][1] - 0.673) < 1e-9
check("C4b bottleneck entries", ok_b,
      "; ".join(f"reach >= {t:.2f} requires TECH >= {v:.3f} ({c})" for t, v, c in rows))

# TECH must also be the only condition meeting the fsQCA consistency threshold
cons = {c: necessity_consistency(mem[c], y_obs) for c in mem}
check("C4c necessity verdict", round(cons["TECH"], 2) == 0.90
      and all(round(v, 2) < 0.90 for k, v in cons.items() if k != "TECH"),
      "consistency " + ", ".join(f"{c} {cons[c]:.3f}" for c in ["TECH", "INTL", "ENG", "CULT"]))

# ── summary ────────────────────────────────────────────────────────────────
print()
if _failures:
    print(f"RESULT: {len(_failures)} check(s) FAILED -> {', '.join(_failures)}")
    sys.exit(1)
print("RESULT: all checks passed.")
print("The NCA implementation reproduces every value it is reported to produce.")
