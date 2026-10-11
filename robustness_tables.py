#!/usr/bin/env python3
"""
robustness_tables.py — reproduces every robustness table reported in the paper.

Input   : fsqca_audit_v5.csv   (one row per country; raw composites AND primary
                               calibrated membership, as exported by fsqca_v5_verified.py)
Output  : printed tables (no files written)

Reproduced here:
  Table 9  / A2.1   NCA bottleneck table
  Table A2.2        NCA permutation test (Dul et al., 2020), B = 10,000, seed 20261010
  Table 5  / A3.1   truth table, dual consistency (cons_full vs cons_core)
  Table A4.1        sufficient rows at alternative consistency thresholds
  Table 10 / A4.3.1 TECH necessity consistency as a function of Brazil's membership
  Table 12 / A4.2.1 multiplicative shifts of the external anchors
  Table A4.2.2      sample-percentile anchors

Deterministic except for the permutation test, whose seed is fixed below.

Run:  python3 robustness_tables.py
"""
import os
import numpy as np
import pandas as pd

SEED = 20261010          # fixed so the permutation p-values are reproducible
B_PERM = 10_000          # permutation draws (Dul et al., 2020 recommend >= 10,000)
PRECISION = 3            # membership is analysed at the precision printed in A1

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "fsqca_audit_v5.csv"))
N = len(df)
CONDS = ["TECH", "ENG", "INTL", "CULT"]
PRETTY = {"TECH": "Technological infrastructure", "ENG": "English proficiency",
          "INTL": "Internationalization", "CULT": "Cultural openness"}

# ── Convention: analyse the membership matrix at the precision it is printed ──
# Appendix A1 reports membership to three decimals, so all statistics here are
# computed on that three-decimal matrix. This is what makes every number in the
# main text and the appendix reproducible from the appendix alone. The only
# value that moves materially between the rounded and unrounded matrices is
# INTL's NCA effect size (0.097 rounded vs 0.096 unrounded); that difference is
# disclosed in the note to Table A2.2. Raw composites are never rounded, so the
# anchor-robustness tables, which recalibrate from raw values, are unaffected.
_RAW_COLS = ["intl_raw", "ce_raw", "cult_raw", "tech_raw", "eng_raw"]
MEMBERSHIP = df.copy()
for _c in CONDS + ["CE"]:
    MEMBERSHIP[_c] = MEMBERSHIP[_c].round(PRECISION)
FULL = df          # unrounded, kept only for the disclosure above

# Primary external anchors, as in manuscript Table 2. TECH anchors are expressed
# on the raw TECH composite (0-1); ENG anchors are EF EPI points; the others are
# on their own 0-1 raw composites.
ANCHORS = {
    "INTL": (0.35, 0.15, 0.06),
    "CE":   (0.55, 0.42, 0.32),
    "CULT": (0.65, 0.48, 0.35),
    "TECH": (0.85, 0.60, 0.35),
    "ENG":  (610.0, 500.0, 450.0),
}
RAW = {"INTL": "intl_raw", "CE": "ce_raw", "CULT": "cult_raw",
       "TECH": "tech_raw", "ENG": "eng_raw"}


def calibrate(series, full_in, cross, full_out):
    """Direct log-odds calibration; membership = 0.95/0.50/0.05 at the three anchors."""
    series = np.asarray(series, dtype=float)
    out = np.zeros(len(series))
    for i, v in enumerate(series):
        if v >= cross:
            slope = np.log(19) / max(full_in - cross, 1e-12)
        else:
            slope = np.log(19) / max(cross - full_out, 1e-12)
        out[i] = 1.0 / (1.0 + np.exp(-slope * (v - cross)))
    return np.clip(out, 0.001, 0.999)


def fdh_ceiling(x, y):
    """CR-FDH ceiling: running maximum of y when cases are ordered by x."""
    order = np.argsort(x, kind="mergesort")
    xs, ys = x[order], y[order]
    ceil, run = np.zeros(len(xs)), ys[0]
    for i in range(len(xs)):
        run = max(run, ys[i])
        ceil[i] = run
    return xs, ceil


def nca_d(x, y):
    """Effect size d = 1 - area under the ceiling, integrated over the whole [0,1]^2 square."""
    trap = getattr(np, "trapezoid", None) or np.trapz
    cx, cy = fdh_ceiling(x, y)
    xs = np.concatenate(([0.0], cx, [1.0]))
    ys = np.concatenate(([cy[0]], cy, [cy[-1]]))
    return 1.0 - trap(ys, xs)


def necessity_consistency(cond_membership, ce_membership):
    """fsQCA necessity consistency = sum(min(X, Y)) / sum(Y)."""
    return np.sum(np.minimum(cond_membership, ce_membership)) / np.sum(ce_membership)


def truth_rows(membership, ce, drop=()):
    """16-row truth table with standard and core consistency."""
    keep = ~membership["country"].isin(drop)
    m, y = membership[keep].reset_index(drop=True), ce[keep]
    rows = []
    for i in range(16):
        bits = {"INTL": (i >> 0) & 1, "CULT": (i >> 1) & 1,
                "TECH": (i >> 2) & 1, "ENG": (i >> 3) & 1}
        memb = np.ones(len(m))
        for c, h in bits.items():
            memb = np.minimum(memb, m[c] if h else 1 - m[c])
        tot = memb.sum()
        cons_full = np.sum(np.minimum(memb, y)) / tot if tot > 0 else 0.0
        core = memb > 0.5
        n_core = int(core.sum())
        cons_core = (np.sum(np.minimum(memb[core], y[core])) / memb[core].sum()
                     if n_core else 0.0)
        label = "".join(c if bits[c] else c.lower() for c in ["INTL", "CULT", "TECH", "ENG"])
        rows.append(dict(label=label, n_core=n_core, cons_full=cons_full,
                         cons_core=cons_core, delta=cons_full - cons_core, tot=tot))
    return rows


print("=" * 78)
print(f"robustness_tables.py | input fsqca_audit_v5.csv | N = {N} | permutation B = {B_PERM}, seed = {SEED}")
print("=" * 78)

ce = MEMBERSHIP["CE"].values
membership = MEMBERSHIP[["country"] + CONDS]

# ── 0. Primary-specification necessities and effect sizes ─────────────────
print("\n[0] Primary specification")
print(f"    {'condition':>10} {'cons':>9} {'d':>9}    {'cons':>9} {'d':>9}")
print(f"    {'':>10} {'(A1 matrix)':>9} {'(A1 matrix)':>9}    {'(unrounded)':>9} {'(unrounded)':>9}")
for c in CONDS:
    con_r = necessity_consistency(MEMBERSHIP[c].values, ce)
    d_r = nca_d(MEMBERSHIP[c].values, ce)
    con_f = necessity_consistency(FULL[c].values, FULL["CE"].values)
    d_f = nca_d(FULL[c].values, FULL["CE"].values)
    print(f"    {c:>10} {con_r:>9.4f} {d_r:>9.4f}    {con_f:>9.4f} {d_f:>9.4f}")

# ── 1. Table 9 / A2.1 : NCA bottleneck table ─────────────────────────────
print("\n[1] Table 9 / A2.1  NCA bottleneck table (minimum TECH for a given CE level)")
print(f"    {'CE threshold':>13} {'cases':>6} {'min TECH':>9}  binding case")
levels = [0.999, 0.95, 0.90, 0.80, 0.70, 0.60, 0.50, 0.30, 0.00]
for lv in levels:
    m = ce >= lv
    idx = np.argmin(np.where(m, MEMBERSHIP["TECH"].values, np.inf))
    print(f"    {lv:>13.3f} {int(m.sum()):>6d} {MEMBERSHIP['TECH'].values[idx]:>9.3f}  {MEMBERSHIP['country'].values[idx]}")

# ── 2. Table A2.2 : permutation test ─────────────────────────────────────
print(f"\n[2] Table A2.2  permutation test (B = {B_PERM}, seed = {SEED}, one-sided)")
rng = np.random.default_rng(SEED)
perms = [rng.permutation(N) for _ in range(B_PERM)]
print(f"    {'condition':>10} {'d':>8} {'p':>8}   significant at .05 / .01")
for c in CONDS:
    x = MEMBERSHIP[c].values
    obs = nca_d(x, ce)
    hits = sum(1 for p in perms if nca_d(x, ce[p]) >= obs)
    pval = hits / B_PERM
    print(f"    {c:>10} {obs:>8.3f} {pval:>8.3f}   "
          f"{'yes' if pval < .05 else 'no':>3} / {'yes' if pval < .01 else 'no':>3}"
          f"   ({hits}/{B_PERM})")

# ── 3. Table 5 / A3.1 : truth table with dual consistency ────────────────
print("\n[3] Table 5 / A3.1  truth table, dual consistency")
rows = truth_rows(membership, ce)
rows.sort(key=lambda r: -r["cons_full"])
print(f"    {'row':>5} {'Ncore':>5} {'cons(full)':>10} {'cons(core)':>10} {'delta':>8}")
for r in rows:
    cc = f"{r['cons_core']:.3f}" if r["n_core"] else "  -  "
    dd = f"{r['delta']:+.3f}" if r["n_core"] else "  -  "
    print(f"    {r['label']:>5} {r['n_core']:>5d} {r['cons_full']:>10.3f} {cc:>10} {dd:>8}")

# ── 4. Table A4.1 : consistency-threshold sensitivity ────────────────────
print("\n[4] Table A4.1  sufficient rows at alternative consistency thresholds")
for ct in [0.90, 0.85, 0.80, 0.75]:
    sel = [r for r in rows if r["n_core"] >= 1 and r["cons_full"] >= ct]
    labels = ", ".join(f"{r['label']} ({r['cons_full']:.3f})" for r in sel) or "none"
    print(f"    threshold {ct:.2f}: {len(sel)} row(s) -> {labels}")

# ── 5. Table 10 / A4.3.1 : boundary sensitivity (Brazil) ─────────────────
print("\n[5] Table 10 / A4.3.1  TECH necessity consistency vs Brazil's TECH membership")
tech = MEMBERSHIP["TECH"].values.copy()
bi = int(np.where(MEMBERSHIP["country"].values == "Brazil")[0][0])
print(f"    {'Brazil TECH':>12} {'consistency':>12}  >= 0.90?")
for bv in [0.600, 0.525, 0.510, 0.500, 0.490, 0.480, 0.470, 0.460, 0.450, 0.400]:
    t = tech.copy()
    t[bi] = bv
    c = necessity_consistency(t, ce)
    print(f"    {bv:>12.3f} {c:>12.4f}  {'yes' if c >= 0.90 else 'no'}")
t = np.delete(tech, bi)
c = np.sum(np.minimum(t, np.delete(ce, bi))) / np.sum(np.delete(ce, bi))
print(f"    {'dropped (n=23)':>12} {c:>12.4f}  {'yes' if c >= 0.90 else 'no'}")
print(f"    (observed Brazil TECH = {tech[bi]:.4f})")

# ── 6. Table 12 / A4.2.1 : multiplicative anchor shifts ──────────────────
# The shift is applied to the anchors of ALL conditions simultaneously, the
# outcome included: full membership and crossover are moved up by s, full
# non-membership down by s, preserving the substantive ordering of the anchors.
# Recalibrating the outcome as well is what makes the comparison a genuine
# re-specification of the whole measurement model rather than a change of one
# condition against a fixed yardstick.
print("\n[6] Table 12 / A4.2.1  multiplicative shifts of the external anchors (all conditions)")
print(f"    {'shift':>8} {'TECH cross':>11} {'consistency':>12} {'d':>8}  violations")
for s in [0.00, 0.05, 0.10, 0.15]:
    alt = {c: calibrate(df[RAW[c]], ANCHORS[c][0] * (1 + s),
                        ANCHORS[c][1] * (1 + s), ANCHORS[c][2] * (1 - s))
           for c in ["CE"] + CONDS}
    cons = necessity_consistency(alt["TECH"], alt["CE"])
    viol = [(df["country"].values[i], alt["TECH"][i]) for i in range(N)
            if alt["TECH"][i] < 0.5 <= alt["CE"][i]]
    vtxt = f"{len(viol)} " + ", ".join(f"{c} ({v:.3f})" for c, v in viol) if viol else "0"
    print(f"    {s * 100:>7.0f}% {ANCHORS['TECH'][1] * (1 + s):>11.2f} {cons:>12.4f} "
          f"{nca_d(alt['TECH'], alt['CE']):>8.3f}  {vtxt}")

# ── 7. Table A4.2.2 : sample-percentile anchors ──────────────────────────
print("\n[7] Table A4.2.2  sample-percentile anchors (95th / 50th / 5th)")
alt = {}
for c in ["CE"] + CONDS:
    lo, mid, hi = df[RAW[c]].quantile(0.05), df[RAW[c]].quantile(0.50), df[RAW[c]].quantile(0.95)
    alt[c] = calibrate(df[RAW[c]], hi, mid, lo)
    print(f"    {c:5s} anchors {hi:.3f} / {mid:.3f} / {lo:.3f}")
print(f"    {'condition':>10} {'cons(percentile)':>17} {'cons(primary)':>14}")
for c in CONDS:
    print(f"    {c:>10} {necessity_consistency(alt[c], alt['CE']):>17.3f} "
          f"{necessity_consistency(df[c].values, ce):>14.3f}")
viol = [(df["country"].values[i], alt["TECH"][i], alt["CE"][i]) for i in range(N)
        if alt["TECH"][i] < 0.5 <= alt["CE"][i]]
print(f"    TECH ceiling violations under percentile anchors: {len(viol)}")
for c, t, y in viol:
    print(f"        {c:<14} TECH = {t:.3f}, reach = {y:.3f}")
print(f"    TECH d under percentile anchors = {nca_d(alt['TECH'], alt['CE']):.3f}")
print("\ndone.")
