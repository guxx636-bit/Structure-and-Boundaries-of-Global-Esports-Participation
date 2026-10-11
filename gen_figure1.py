#!/usr/bin/env python3
"""Generate 3-panel Figure 1 for manuscript: CE-FDH ceiling + Y=X, annotated."""
import pandas as pd, numpy as np, matplotlib, matplotlib.pyplot as plt
matplotlib.use('Agg')
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(script_dir, "fsqca_plot_data.csv"))

# CE-FDH ceiling function
def fdh_ceiling(x, y):
    order = np.argsort(x); xs = x[order]; ys = y[order]
    n = len(xs); ceiling = np.zeros(n)
    rm = ys[0]
    for i in range(n):
        if ys[i] > rm: rm = ys[i]
        ceiling[i] = rm
    return xs, ceiling

# Compute ceilings
ce_x_t, ce_y_t = fdh_ceiling(data["TECH"].values, data["CE"].values)
ce_x_e, ce_y_e = fdh_ceiling(data["ENG"].values, data["CE"].values)
ce_x_i, ce_y_i = fdh_ceiling(data["INTL"].values, data["CE"].values)

# Regions for coloring
eu = ["South Korea","China","Japan","India","Indonesia","Vietnam","Thailand","Malaysia","Singapore"]
am = ["United States","Canada","Brazil","Mexico","Argentina"]

# Annotations
ann_all = {
    "South Korea":{"c":"#1565C0","o":(8,-12),"panel":["TECH","INTL"]},
    "China":{"c":"#C62828","o":(-12,-8),"panel":["TECH","ENG","INTL"]},
    "Brazil":{"c":"#E65100","o":(8,-8),"panel":["TECH","INTL"]},
    "Poland":{"c":"#2E7D32","o":(8,-8),"panel":["INTL"]},
    "Spain":{"c":"#4E342E","o":(8,-8),"panel":["INTL"]},
    "Japan":{"c":"#546E7A","o":(8,8),"panel":["ENG"]},
    "United Kingdom":{"c":"#6A1B9A","o":(8,0),"panel":["ENG"]},
    "Australia":{"c":"#AD1457","o":(8,-8),"panel":["ENG"]},
}

fig, axes = plt.subplots(1, 3, figsize=(21, 7))

def do_panel(ax, x, y, xcol, title, ce_x, ce_y, panel_name, d_val, cons_val):
    # Scatter by region
    for region, mask, color in [
        ("Asia", [c in eu for c in data["country"]], "#1565C0"),
        ("Americas", [c in am for c in data["country"]], "#E65100"),
        ("Europe/Oceania", [c not in eu and c not in am for c in data["country"]], "#2E7D32"),
    ]:
        xr = x[mask]; yr = y[mask]
        ax.scatter(xr, yr, s=50, c=color, alpha=0.45, ec="white", lw=0.3, zorder=2)

    # Y = X line
    ax.plot([0,1],[0,1],'--',color="#999",lw=1.2,alpha=0.6,label="Y = X (perfect necessity)",zorder=1)
    # CE-FDH ceiling line
    ax.step(ce_x, ce_y, '-', color="#D84315", lw=2.5, label="CE-FDH ceiling", zorder=3)
    # Crossover lines
    ax.axhline(0.50, color="#ccc", ls=":", lw=0.6)
    ax.axvline(0.50, color="#ccc", ls=":", lw=0.6)

    # Annotate
    for cname, cfg in ann_all.items():
        if panel_name not in cfg["panel"]: continue
        row = data[data["country"]==cname].iloc[0]
        xi, yi = row[xcol], row["CE"]
        ax.scatter([xi],[yi], s=90, c=cfg["c"], ec="white", lw=1.2, zorder=5)
        ox, oy = cfg["o"]
        ax.annotate(cname, (xi,yi), textcoords="offset points", xytext=(ox,oy),
                   fontsize=6.5, color=cfg["c"], fontweight="bold",
                   arrowprops=dict(arrowstyle="-",color=cfg["c"],lw=0.3,alpha=0.4))

    ax.set_xlabel(f"{title} fuzzy-set membership", fontsize=10)
    ax.set_ylabel("CE fuzzy-set membership", fontsize=10)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    need = f"NECESSARY (cons={cons_val:.2f}, d={d_val:.2f})" if cons_val >= 0.90 else f"NOT necessary (cons={cons_val:.2f}, d={d_val:.2f})"
    ax.set_title(f"{title} × CE\n{need}", fontsize=11, fontweight="bold")
    ax.legend(loc="lower right", fontsize=7.5, framealpha=0.7)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# Compute d for each
# NCA CE-FDH effect size: d = 1 - area under the ceiling, integrated over the FULL
# [0,1] x [0,1] unit square. The ceiling must therefore be extended leftwards from
# x=0 to the first data point and rightwards from the last data point to x=1;
# integrating only between observed points understates d (it drops the two edge
# trapezoids) and produced the wrong values in earlier versions of this figure.
def nca_d(ce_x, ce_y):
    trap = getattr(np, "trapezoid", None) or np.trapz
    xs = np.concatenate(([0.0], ce_x, [1.0]))
    ys = np.concatenate(([ce_y[0]], ce_y, [ce_y[-1]]))
    return 1.0 - trap(ys, xs)

tec_d = nca_d(ce_x_t, ce_y_t)
eng_d = nca_d(ce_x_e, ce_y_e)
intl_d = nca_d(ce_x_i, ce_y_i)
tec_c = np.sum(np.minimum(data["TECH"].values, data["CE"].values))/np.sum(data["CE"].values)
eng_c = np.sum(np.minimum(data["ENG"].values, data["CE"].values))/np.sum(data["CE"].values)
intl_c = np.sum(np.minimum(data["INTL"].values, data["CE"].values))/np.sum(data["CE"].values)

do_panel(axes[0], data["TECH"].values, data["CE"].values, "TECH",
         "A: Technological Infrastructure (TECH)", ce_x_t, ce_y_t, "TECH", tec_d, tec_c)
do_panel(axes[1], data["ENG"].values, data["CE"].values, "ENG",
         "B: English Proficiency (ENG)", ce_x_e, ce_y_e, "ENG", eng_d, eng_c)
do_panel(axes[2], data["INTL"].values, data["CE"].values, "INTL",
         "C: Esports Internationalization (INTL)", ce_x_i, ce_y_i, "INTL", intl_d, intl_c)

plt.tight_layout()
outpath = os.path.join(script_dir, "Figure_1.png")
plt.savefig(outpath, dpi=600, bbox_inches="tight", facecolor="white")
print(f"Saved: {outpath}")
# Elsevier requires figures as separate files; vector is preferred for chart/line art.
pdfpath = os.path.join(script_dir, "Figure_1.pdf")
plt.savefig(pdfpath, bbox_inches="tight", facecolor="white")
print(f"Saved: {pdfpath}")
print(f"TECH: d={tec_d:.4f}, cons={tec_c:.4f}")
print(f"ENG:  d={eng_d:.4f}, cons={eng_c:.4f}")
print(f"INTL: d={intl_d:.4f}, cons={intl_c:.4f}")
