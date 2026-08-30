# Figure 2. Longitudinal trajectories according to three-level baseline pain severity.
import warnings
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _common import THREE_LEVELS, output_dir, read_sheet

warnings.filterwarnings("ignore")

df = read_sheet("Visit_Long_191")
df = df[df.Visit_Order <= 7].copy()
visit_order = list(range(8))
visit_labels = ["Baseline", "1st FU", "2nd inj", "2nd FU", "3rd inj", "3rd FU", "4th inj", "4th FU"]

outcomes = [
    ("VAS", "VAS", "VAS trajectory by baseline pain group"),
    ("CMO", "CMO (mm)", "CMO trajectory by baseline pain group"),
    ("MMO", "MMO (mm)", "MMO trajectory by baseline pain group"),
    ("Pain_Location_Burden_0_6", "Pain-location burden", "Pain-location burden by baseline pain group"),
]

labels = {THREE_LEVELS[0]: "Mild pain", THREE_LEVELS[1]: "Moderate pain", THREE_LEVELS[2]: "Severe pain"}
colors = {THREE_LEVELS[0]: "#3B6EA8", THREE_LEVELS[1]: "#D99A21", THREE_LEVELS[2]: "#B64A4A"}


def interaction_p(y):
    x = df[["Study_ID", "Visit_Order", "Baseline_Pain_Group_3L", y]].dropna().copy()
    fit = smf.gee(
        f"{y} ~ C(Baseline_Pain_Group_3L) * C(Visit_Order)",
        groups="Study_ID", data=x,
        cov_struct=sm.cov_struct.Exchangeable(),
        family=sm.families.Gaussian(),
    ).fit()
    wt = fit.wald_test_terms(skip_single=False, scalar=True).table
    return float(wt.loc["C(Baseline_Pain_Group_3L):C(Visit_Order)", "pvalue"])

fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
for ax, (y, ylabel, title), panel in zip(axes.flat, outcomes, ["A", "B", "C", "D"]):
    for grp in THREE_LEVELS:
        sub = df[df.Baseline_Pain_Group_3L == grp]
        s = sub.groupby("Visit_Order")[y].agg(["mean", "std", "count"]).reindex(visit_order)
        ax.plot(visit_order, s["mean"], marker="o", linewidth=1.7, label=labels[grp], color=colors[grp])
        stable = s["count"] >= 10
        se = s["std"] / np.sqrt(s["count"])
        lo, hi = s["mean"] - 1.96*se, s["mean"] + 1.96*se
        ax.fill_between(visit_order, lo, hi, where=stable.to_numpy(), interpolate=False,
                        alpha=0.15, color=colors[grp])
    ax.set_xticks(visit_order, visit_labels, rotation=35, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.text(-0.12, 1.04, panel, transform=ax.transAxes, fontsize=15, fontweight="bold")
    p = interaction_p(y)
    ptxt = "P < .001" if p < .001 else f"P = {p:.3f}".replace("0.", ".")
    ax.text(0.98, 0.95, f"Repeated-measures GEE\nGroup × visit interaction {ptxt}\n95% CI shown when n ≥ 10",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.8, edgecolor="0.8"))
    ax.spines[["top", "right"]].set_visible(False)

handles, leglabels = axes[0,0].get_legend_handles_labels()
fig.legend(handles, leglabels, loc="lower center", ncol=3, frameon=False)
fig.tight_layout(rect=(0,0.05,1,1))
out = output_dir() / "Figure_2.png"
fig.savefig(out, dpi=600, bbox_inches="tight")
fig.savefig(output_dir() / "Figure_2.tiff", dpi=600, bbox_inches="tight")
print(f"Saved: {out}")
print({y: interaction_p(y) for y,_,_ in outcomes})
