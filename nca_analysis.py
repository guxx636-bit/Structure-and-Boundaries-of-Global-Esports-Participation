#!/usr/bin/env python3
"""
NCA (Necessary Condition Analysis) — CR-FDH ceiling line
For TECH and ENG as necessary conditions for high CE.

Method: Ceiling Regression on Free Disposal Hull (CR-FDH)
  - Sort X ascending, find ceiling Y for each X bin
  - Effect size d = area above ceiling line / total area
  - Bottleneck table: min X needed to reach each Y level
"""
import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(script_dir, "fsqca_plot_data.csv"))

# ── CR-FDH ceiling line ────────────────────────────────────────────────
def cr_fdh(x, y):
    """Ceiling Regression on Free Disposal Hull.
    Returns: ceiling_y for each x, and effect size d."""
    order = np.argsort(x)
    xs = x[order]
    ys = y[order]

    # FDH ceiling: for each point, ceiling = max Y among points with X ≤ current X
    n = len(xs)
    ceiling = np.zeros(n)
    running_max = ys[0]
    for i in range(n):
        if ys[i] > running_max:
            running_max = ys[i]
        ceiling[i] = running_max

    # Effect size d = (area without condition - area with condition) / area without condition
    # Simplified: 1 - (area under ceiling / total area)
    # Area under ceiling via trapezoidal rule
    area_ceiling = 0.0
    for i in range(n - 1):
        area_ceiling += (ceiling[i] + ceiling[i+1]) * (xs[i+1] - xs[i]) / 2.0
    # Add area from x=0 to first point
    area_ceiling += ceiling[0] * xs[0]
    # Add area from last point to x=1
    area_ceiling += ceiling[-1] * (1.0 - xs[-1])

    total_area = 1.0  # 0-1 × 0-1 square
    d = 1.0 - area_ceiling / total_area
    d = max(0.0, d)  # d should be non-negative

    # Ceiling accuracy: proportion of points below ceiling
    accuracy = np.mean(ys <= ceiling)

    return {
        "ceiling_x": xs,
        "ceiling_y": ceiling,
        "d": d,
        "accuracy": accuracy,
        "n_empty": int(np.sum(ys > ceiling)),
    }

# ── Bottleneck table ───────────────────────────────────────────────────
def bottleneck_table(x, y, levels=np.arange(0.0, 1.05, 0.1)):
    """For each Y level, what is the minimum X needed to reach it?
    This is the inverse of the ceiling: given Y, what X is required?"""
    tbl = []
    for lvl in levels:
        # Cases that achieve at least this Y level
        mask = y >= lvl
        if np.sum(mask) == 0:
            min_x = "-"
        else:
            min_x = np.min(x[mask])
        tbl.append({"Y_level": lvl, "min_X": min_x, "n_cases": int(np.sum(mask))})
    return pd.DataFrame(tbl)

# ── Run NCA for TECH and ENG ──────────────────────────────────────────
print("=" * 70)
print("NCA (Necessary Condition Analysis) — CR-FDH")
print("=" * 70)

for cond, label in [("TECH", "Technological Infrastructure"), ("ENG", "English Proficiency")]:
    x = data[cond].values
    y = data["CE"].values

    result = cr_fdh(x, y)
    print(f"\n── {cond}: {label} ──")
    print(f"  Effect size d = {result['d']:.4f}")
    print(f"  Ceiling accuracy = {result['accuracy']:.4f}")
    print(f"  Points above ceiling = {result['n_empty']}")
    print(f"  Interpretation:")
    if result['d'] >= 0.3:
        print(f"    d = {result['d']:.3f} ≥ 0.3 → LARGE effect (strong necessary condition)")
    elif result['d'] >= 0.1:
        print(f"    d = {result['d']:.3f} ≥ 0.1 → MEDIUM effect (moderate necessary condition)")
    else:
        print(f"    d = {result['d']:.3f} < 0.1 → SMALL effect (weak or absent necessary condition)")

    # Bottleneck table
    print(f"\n  Bottleneck table:")
    bt = bottleneck_table(x, y)
    for _, row in bt.iterrows():
        minx_fmt = f"{row['min_X']:.4f}" if isinstance(row['min_X'], float) else row['min_X']
        print(f"    CE ≥ {row['Y_level']:.1f}: min {cond} = {minx_fmt} ({row['n_cases']} cases)")

# ── Compare: fsQCA necessity vs NCA ────────────────────────────────────
print(f"\n{'=' * 70}")
print(f"COMPARISON: fsQCA necessity consistency vs. NCA effect size")
print(f"{'=' * 70}")
print(f"{'Condition':<10} {'fsQCA cons':>12} {'fsQCA verdict':>18} {'NCA d':>8} {'NCA effect':>15} {'Verdict':>15}")
print("-" * 80)

for cond, label in [("TECH", "Technological Infra."), ("ENG", "English Proficiency"),
                     ("INTL", "Internationalization"), ("CULT", "Cultural Openness")]:
    cons = np.sum(np.minimum(data[cond].values, data["CE"].values)) / np.sum(data["CE"].values)
    r = cr_fdh(data[cond].values, data["CE"].values)
    fsqca_v = "NECESSARY" if cons >= 0.90 else ("borderline" if cons >= 0.80 else "not necessary")
    nca_v = "LARGE" if r['d'] >= 0.3 else ("MEDIUM" if r['d'] >= 0.1 else "SMALL")
    if cons >= 0.90 and r['d'] >= 0.1:
        verdict = "ROBUST necessary"
    elif cons >= 0.90:
        verdict = "WEAKLY necessary"
    elif r['d'] >= 0.1:
        verdict = "NCA-necessary only"
    else:
        verdict = "not necessary"
    print(f"{label:<18} {cons:>12.4f} {fsqca_v:>18} {r['d']:>8.4f} {nca_v:>15} {verdict:>18}")

# ── Ceiling line coordinates for plotting ──────────────────────────────
for cond in ["TECH", "ENG"]:
    r = cr_fdh(data[cond].values, data["CE"].values)
    out = pd.DataFrame({"ceiling_x": r["ceiling_x"], "ceiling_y": r["ceiling_y"], "d": r["d"]})
    out.to_csv(os.path.join(script_dir, f"nca_ceiling_{cond}.csv"), index=False)

print(f"\n✓ NCA complete. Ceiling coordinates saved.")
print(f"\n── IMPLICATIONS FOR MANUSCRIPT ──")
tec_r = cr_fdh(data["TECH"].values, data["CE"].values)
eng_r = cr_fdh(data["ENG"].values, data["CE"].values)
print(f"  TECH: fsQCA=0.90, NCA d={tec_r['d']:.3f} ({'LARGE' if tec_r['d']>=0.3 else 'MEDIUM'})")
print(f"  → Use Goertz (2023) terminology: 'almost necessary' if d ≥ 0.15")
print(f"  ENG: fsQCA=0.77, NCA d={eng_r['d']:.3f} ({'LARGE' if eng_r['d']>=0.3 else 'MEDIUM'})")
print(f"  → Not necessary by either standard")
