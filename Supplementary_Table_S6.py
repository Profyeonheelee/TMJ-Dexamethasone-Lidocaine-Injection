# Supplementary Table S6. Repeat-injection comparison.

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu

from _common import fmt_p, read_sheet, save_csv


dat = read_sheet("Visit_Long_191")

repeat_status = (
    dat.assign(
        repeat_flag=dat["Visit_Type"].eq("Injection day") & dat["Cycle"].ge(2)
    )
    .groupby("Study_ID")["repeat_flag"]
    .any()
    .rename("Repeat_Injection")
    .reset_index()
)

baseline = (
    dat.loc[dat["Visit_Order"] == 0]
    .sort_values("Study_ID")
    .drop_duplicates("Study_ID")
    [["Study_ID", "Sex", "Age", "VAS", "CMO", "MMO", "Pain_Location_Burden_0_6"]]
    .rename(
        columns={
            "VAS": "Baseline_VAS",
            "CMO": "Baseline_CMO",
            "MMO": "Baseline_MMO",
            "Pain_Location_Burden_0_6": "Baseline_Pain_Burden",
        }
    )
)

first_fu = (
    dat.loc[dat["Visit_Order"] == 1]
    .sort_values("Study_ID")
    .drop_duplicates("Study_ID")
    [["Study_ID", "Days_From_Baseline", "VAS", "CMO", "MMO", "Pain_Location_Burden_0_6"]]
    .rename(
        columns={
            "Days_From_Baseline": "FirstFU_Days",
            "VAS": "FirstFU_VAS",
            "CMO": "FirstFU_CMO",
            "MMO": "FirstFU_MMO",
            "Pain_Location_Burden_0_6": "FirstFU_Pain_Burden",
        }
    )
)

pt = baseline.merge(first_fu, on="Study_ID", how="left").merge(
    repeat_status, on="Study_ID", how="left"
)
pt["Repeat_Group"] = np.where(
    pt["Repeat_Injection"], "Repeat injection", "No repeat injection"
)
pt["Female"] = pt["Sex"].eq("F")
pt["Delta_VAS"] = pt["FirstFU_VAS"] - pt["Baseline_VAS"]
pt["Delta_CMO"] = pt["FirstFU_CMO"] - pt["Baseline_CMO"]
pt["Delta_MMO"] = pt["FirstFU_MMO"] - pt["Baseline_MMO"]
pt["Delta_Pain_Burden"] = (
    pt["FirstFU_Pain_Burden"] - pt["Baseline_Pain_Burden"]
)


def mean_sd_n(values):
    x = pd.Series(values).dropna().astype(float)
    if x.empty:
        return "NA"
    return f"{x.mean():.2f} ± {x.std(ddof=1):.2f} ({len(x)})"


def n_pct(values):
    x = pd.Series(values).dropna().astype(bool)
    if x.empty:
        return "NA"
    n = int(x.sum())
    return f"{n} ({100 * n / len(x):.1f}%)"


def continuous_p(var):
    a = pt.loc[~pt["Repeat_Injection"], var].dropna()
    b = pt.loc[pt["Repeat_Injection"], var].dropna()
    return mannwhitneyu(a, b, alternative="two-sided").pvalue


def categorical_p(var):
    tab = pd.crosstab(pt[var], pt["Repeat_Group"])
    chi = chi2_contingency(tab, correction=True)
    if np.any(chi.expected_freq < 5):
        return fisher_exact(tab.to_numpy())[1]
    return chi.pvalue


variables = [
    ("Age, years", "Age"),
    ("Time to first follow-up, days", "FirstFU_Days"),
    ("Baseline VAS", "Baseline_VAS"),
    ("First-follow-up VAS", "FirstFU_VAS"),
    ("ΔVAS, first follow-up − baseline", "Delta_VAS"),
    ("Baseline pain-location burden", "Baseline_Pain_Burden"),
    ("First-follow-up pain-location burden", "FirstFU_Pain_Burden"),
    ("ΔPain-location burden", "Delta_Pain_Burden"),
    ("Baseline CMO, mm", "Baseline_CMO"),
    ("First-follow-up CMO, mm", "FirstFU_CMO"),
    ("ΔCMO, mm", "Delta_CMO"),
    ("Baseline MMO, mm", "Baseline_MMO"),
    ("First-follow-up MMO, mm", "FirstFU_MMO"),
    ("ΔMMO, mm", "Delta_MMO"),
]

no_repeat = ~pt["Repeat_Injection"]
repeat = pt["Repeat_Injection"]

continuous_rows = {}
for label, var in variables:
    continuous_rows[label] = {
        "Variable": label,
        "No repeat injection": mean_sd_n(pt.loc[no_repeat, var]),
        "Repeat injection": mean_sd_n(pt.loc[repeat, var]),
        "P value": fmt_p(continuous_p(var)),
    }

rows = [
    {
        "Variable": "Patients, n",
        "No repeat injection": str(int(no_repeat.sum())),
        "Repeat injection": str(int(repeat.sum())),
        "P value": "",
    },
    continuous_rows["Age, years"],
    {
        "Variable": "Female, n (%)",
        "No repeat injection": n_pct(pt.loc[no_repeat, "Female"]),
        "Repeat injection": n_pct(pt.loc[repeat, "Female"]),
        "P value": fmt_p(categorical_p("Female")),
    },
    continuous_rows["Time to first follow-up, days"],
]

for label, _ in variables[2:]:
    rows.append(continuous_rows[label])

table = pd.DataFrame(rows)
save_csv(table, "Supplementary_Table_S6.csv")
print(table.to_string(index=False))
