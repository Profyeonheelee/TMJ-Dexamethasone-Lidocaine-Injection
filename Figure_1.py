# Figure 1. Overall longitudinal trajectories of clinical outcomes.
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2
import statsmodels.formula.api as smf
from _common import output_dir, read_sheet

warnings.filterwarnings("ignore")

df = read_sheet("Visit_Long_191")
df = df[df.Visit_Order <= 7].copy()
visit_order = list(range(8))
visit_labels = ["Baseline", "1st FU", "2nd inj", "2nd FU", "3rd inj", "3rd FU", "4th inj", "4th FU"]

outcomes = [
    ("VAS", "VAS", "VAS trajectory"),
    ("CMO", "CMO (mm)", "CMO trajectory"),
    ("MMO", "MMO (mm)", "MMO trajectory"),
    ("Pain_Location_Burden_0_6", "Pain-location burden", "Pain-location burden trajectory"),
]


def omnibus_visit_p(y):
    x = df[["Study_ID", "Visit_Order", y]].dropna().copy()
    full = smf.mixedlm(f"{y} ~ C(Visit_Order)", x, groups=x.Study_ID).fit(reml=False, method="bfgs", maxiter=10000, disp=False)
    null = smf.mixedlm(f"{y} ~ 1", x, groups=x.Study_ID).fit(reml=False, method="bfgs", maxiter=10000, disp=False)
    lr = 2 * (full.llf - null.llf)
    df_diff = full.df_modelwc - null.df_modelwc
    return chi2.sf(lr, df_diff)

fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
for ax, (y, ylabel, title), panel in zip(axes.flat, outcomes, ["A", "B", "C", "D"]):
    s = (df.groupby("Visit_Order")[y]
           .agg(["mean", "std", "count"])
           .reindex(visit_order))
    se = s["std"] / np.sqrt(s["count"])
    lo, hi = s["mean"] - 1.96 * se, s["mean"] + 1.96 * se
    ax.plot(visit_order, s["mean"], marker="o", linewidth=1.8)
    ax.fill_between(visit_order, lo, hi, alpha=0.20)
    ax.set_xticks(visit_order, visit_labels, rotation=35, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.text(-0.12, 1.04, panel, transform=ax.transAxes, fontsize=15, fontweight="bold")
    p = omnibus_visit_p(y)
    ptxt = "P < .001" if p < .001 else f"P = {p:.3f}".replace("0.", ".")
    ax.text(0.98, 0.95, f"Linear mixed-effects model\nVisit effect {ptxt}", transform=ax.transAxes,
            ha="right", va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="0.8"))
    ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
out = output_dir() / "Figure_1.png"
fig.savefig(out, dpi=600, bbox_inches="tight")
fig.savefig(output_dir() / "Figure_1.tiff", dpi=600, bbox_inches="tight")
print(f"Saved: {out}")
print({y: omnibus_visit_p(y) for y,_,_ in outcomes})
