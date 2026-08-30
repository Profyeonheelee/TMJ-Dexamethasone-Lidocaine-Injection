# Table 1. Baseline characteristics according to baseline pain severity.
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from _common import MILD, MODSEV, bh, categorical_p_from_table, fmt_p, read_sheet, save_csv


df = read_sheet("Baseline_191")
group_col = "Baseline_Pain_Group_2L"

continuous = [
    ("Age, years", "Age", 1),
    ("Baseline VAS", "Baseline_VAS", 1),
    ("CMO, mm", "CMO", 1),
    ("MMO, mm", "MMO", 1),
    ("Pain-location burden score", "Pain_Location_Burden_0_6", 1),
]
categorical = [
    ("Female sex, n (%)", "Sex", "F"),
    ("Pain present, n (%)", "Pain_Present", 1),
    ("Rt. Masseter pain, n (%)", "Rt_Masseter", 1),
    ("Rt. Temporalis pain, n (%)", "Rt_Temporalis", 1),
    ("Rt. TMJ pain, n (%)", "Rt_TMJ", 1),
    ("Lt. Masseter pain, n (%)", "Lt_Masseter", 1),
    ("Lt. Temporalis pain, n (%)", "Lt_Temporalis", 1),
    ("Lt. TMJ pain, n (%)", "Lt_TMJ", 1),
]


def cont_cell(s):
    x = pd.Series(s).dropna().astype(float)
    return f"{x.mean():.1f} ± {x.std(ddof=1):.1f} ({len(x)})"


def cat_cell(s, positive):
    s = pd.Series(s).dropna()
    n = int((s == positive).sum())
    return f"{n} ({100*n/len(s):.1f})"

rows = []
raw_p = []
meta = []

for label, var, _ in continuous:
    a = df.loc[df[group_col] == MILD, var].dropna()
    b = df.loc[df[group_col] == MODSEV, var].dropna()
    p = mannwhitneyu(a, b, alternative="two-sided").pvalue
    raw_p.append(p)
    meta.append(("continuous", label, var, None))

for label, var, positive in categorical:
    x = (df[var] == positive) if var == "Sex" else df[var]
    tab = pd.crosstab(x, df[group_col])
    p = categorical_p_from_table(tab)
    raw_p.append(p)
    meta.append(("categorical", label, var, positive))

adj = bh(raw_p)

for i, (kind, label, var, positive) in enumerate(meta):
    if kind == "continuous":
        overall = cont_cell(df[var])
        mild = cont_cell(df.loc[df[group_col] == MILD, var])
        modsev = cont_cell(df.loc[df[group_col] == MODSEV, var])
    else:
        overall = cat_cell(df[var], positive)
        mild = cat_cell(df.loc[df[group_col] == MILD, var], positive)
        modsev = cat_cell(df.loc[df[group_col] == MODSEV, var], positive)
    rows.append({
        "Variable": label,
        "Overall": overall,
        "Mild pain (VAS 0–3)": mild,
        "Moderate-to-severe pain (VAS ≥4)": modsev,
        "P value": fmt_p(raw_p[i]),
        "FDR-adjusted P value": fmt_p(adj[i]),
    })

patients = pd.DataFrame([{
    "Variable": "Patients, n",
    "Overall": str(len(df)),
    "Mild pain (VAS 0–3)": str((df[group_col] == MILD).sum()),
    "Moderate-to-severe pain (VAS ≥4)": str((df[group_col] == MODSEV).sum()),
    "P value": "",
    "FDR-adjusted P value": "",
}])

table = pd.concat([patients, pd.DataFrame(rows)], ignore_index=True)
save_csv(table, "Table_1.csv")
print(table.to_string(index=False))
