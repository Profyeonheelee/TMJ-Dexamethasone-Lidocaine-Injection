# Table 2. Early paired changes from baseline to first follow-up.
import pandas as pd
from scipy.stats import wilcoxon, mannwhitneyu
from _common import MILD, MODSEV, bh, fmt_p, read_sheet, save_csv


df = read_sheet("Baseline_to_FirstFU")
gcol = "Baseline_Pain_Group_2L"

outcomes = [
    ("VAS", "Baseline_VAS", "First_FU_VAS", "Delta_VAS_FirstFU", 2),
    ("CMO, mm", "Baseline_CMO", "First_FU_CMO", "Delta_CMO_FirstFU", 2),
    ("MMO, mm", "Baseline_MMO", "First_FU_MMO", "Delta_MMO_FirstFU", 2),
    ("Pain-location burden", "Baseline_Pain_Burden", "First_FU_Pain_Burden", "Delta_Pain_Burden_FirstFU", 2),
]
groups = [("Overall", None), ("Mild pain", MILD), ("Moderate-to-severe pain", MODSEV)]

within_records = []
for outcome, bvar, fvar, dvar, dec in outcomes:
    for glabel, gvalue in groups:
        sub = df if gvalue is None else df[df[gcol] == gvalue]
        paired = sub[[bvar, fvar, dvar]].dropna(subset=[bvar, fvar])
        p = wilcoxon(paired[fvar], paired[bvar], alternative="two-sided", zero_method="wilcox").pvalue
        within_records.append({
            "Outcome": outcome,
            "Baseline pain group": glabel,
            "n": len(paired),
            "Baseline": f"{paired[bvar].mean():.{dec}f} ± {paired[bvar].std(ddof=1):.{dec}f}",
            "First follow-up": f"{paired[fvar].mean():.{dec}f} ± {paired[fvar].std(ddof=1):.{dec}f}",
            "Change": f"{paired[dvar].mean():+.{dec}f} ± {paired[dvar].std(ddof=1):.{dec}f}",
            "Raw_within_P": p,
            "Delta_var": dvar,
        })

# FDR correction across the 12 within-group tests.
within_adj = bh([x["Raw_within_P"] for x in within_records])
for rec, p_adj in zip(within_records, within_adj):
    rec["Within-group FDR P value"] = fmt_p(p_adj)

# FDR correction across the four between-group change tests.
between = {}
between_raw = []
for outcome, bvar, fvar, dvar, dec in outcomes:
    a = df.loc[df[gcol] == MILD, dvar].dropna()
    b = df.loc[df[gcol] == MODSEV, dvar].dropna()
    p = mannwhitneyu(a, b, alternative="two-sided").pvalue
    between_raw.append(p)
    between[outcome] = p
between_adj = bh(between_raw)
between_fdr = {outcomes[i][0]: between_adj[i] for i in range(len(outcomes))}

rows = []
for rec in within_records:
    is_overall = rec["Baseline pain group"] == "Overall"
    rows.append({
        "Outcome": rec["Outcome"],
        "Baseline pain group": rec["Baseline pain group"],
        "n": rec["n"],
        "Baseline": rec["Baseline"],
        "First follow-up": rec["First follow-up"],
        "Change": rec["Change"],
        "Within-group FDR P value": rec["Within-group FDR P value"],
        "Between-group FDR P value for change": "—" if is_overall else (
            fmt_p(between_fdr[rec["Outcome"]]) if rec["Baseline pain group"] == "Mild pain" else ""
        ),
    })

table = pd.DataFrame(rows)
save_csv(table, "Table_2.csv")
print(table.to_string(index=False))
