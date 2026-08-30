# Table 4. Final clinical outcomes and direction of change.
import pandas as pd
from scipy.stats import mannwhitneyu, chi2_contingency
from _common import MILD, MODSEV, bh, categorical_p_from_table, fmt_p, read_sheet, save_csv


df = read_sheet("Baseline_to_FinalFU")
gcol = "Baseline_Pain_Group_2L"


def mean_sd_n(s, dec=2, sign=False):
    x = pd.Series(s).dropna().astype(float)
    if x.empty:
        return "NA"
    prefix = "+" if sign and x.mean() > 0 else ""
    return f"{prefix}{x.mean():.{dec}f} ± {x.std(ddof=1):.{dec}f} ({len(x)})"


def n_pct_bool(s):
    x = pd.Series(s).dropna()
    n = int((x.astype(float) == 1).sum())
    return f"{n} ({100*n/len(x):.1f})"


def n_pct_level(s, level):
    x = pd.Series(s).dropna()
    n = int((x == level).sum())
    return f"{n} ({100*n/len(x):.1f})"

continuous = [
    ("Final VAS", "Final_VAS", False),
    ("ΔVAS, final − baseline", "Delta_VAS_Final", False),
    ("Final CMO, mm", "Final_CMO", False),
    ("ΔCMO, mm, final − baseline", "Delta_CMO_Final", True),
    ("Final MMO, mm", "Final_MMO", False),
    ("ΔMMO, mm, final − baseline", "Delta_MMO_Final", True),
    ("Final pain-location burden score", "Final_Pain_Burden", False),
    ("ΔPain-location burden, final − baseline", "Delta_Pain_Burden_Final", False),
]

# The manuscript applies BH across 11 inferential comparisons in Table 4.
raw_tests = []
test_keys = []
for label, var, sign in continuous:
    a = df.loc[df[gcol] == MILD, var].dropna()
    b = df.loc[df[gcol] == MODSEV, var].dropna()
    raw_tests.append(mannwhitneyu(a, b, alternative="two-sided").pvalue)
    test_keys.append(label)

# Final VAS = 0
raw_tests.append(categorical_p_from_table(pd.crosstab(df["Final_VAS_Zero"], df[gcol])))
test_keys.append("Final VAS = 0, n (%)")

# Directional category distributions: chi-square omnibus test.
for key, var in [("VAS change distribution", "VAS_Response_Final"),
                 ("Pain-location burden change distribution", "Pain_Burden_Response_Final")]:
    raw_tests.append(chi2_contingency(pd.crosstab(df[var], df[gcol]), correction=False).pvalue)
    test_keys.append(key)

adj = bh(raw_tests)
pmap = {k: (p, a) for k,p,a in zip(test_keys, raw_tests, adj)}

rows = [{
    "Outcome": "Patients with available final follow-up, n",
    "Overall": str(len(df)),
    "Mild pain (VAS 0–3)": str((df[gcol] == MILD).sum()),
    "Moderate-to-severe pain (VAS ≥4)": str((df[gcol] == MODSEV).sum()),
    "P value": "", "FDR-adjusted P value": "",
}]

# Keep manuscript row order.
def add_cont(label, var, sign=False):
    p,a = pmap[label]
    rows.append({
        "Outcome": label,
        "Overall": mean_sd_n(df[var], sign=sign),
        "Mild pain (VAS 0–3)": mean_sd_n(df.loc[df[gcol] == MILD, var], sign=sign),
        "Moderate-to-severe pain (VAS ≥4)": mean_sd_n(df.loc[df[gcol] == MODSEV, var], sign=sign),
        "P value": fmt_p(p), "FDR-adjusted P value": fmt_p(a),
    })

add_cont("Final VAS", "Final_VAS")
p,a = pmap["Final VAS = 0, n (%)"]
rows.append({
    "Outcome": "Final VAS = 0, n (%)",
    "Overall": n_pct_bool(df.Final_VAS_Zero),
    "Mild pain (VAS 0–3)": n_pct_bool(df.loc[df[gcol] == MILD, "Final_VAS_Zero"]),
    "Moderate-to-severe pain (VAS ≥4)": n_pct_bool(df.loc[df[gcol] == MODSEV, "Final_VAS_Zero"]),
    "P value": fmt_p(p), "FDR-adjusted P value": fmt_p(a),
})

p,a = pmap["VAS change distribution"]
for j,level in enumerate(["Decreased","Maintained","Increased"]):
    rows.append({
        "Outcome": f"VAS {level.lower()} from baseline, n (%)",
        "Overall": n_pct_level(df.VAS_Response_Final, level),
        "Mild pain (VAS 0–3)": n_pct_level(df.loc[df[gcol] == MILD, "VAS_Response_Final"], level),
        "Moderate-to-severe pain (VAS ≥4)": n_pct_level(df.loc[df[gcol] == MODSEV, "VAS_Response_Final"], level),
        "P value": fmt_p(p) if j == 0 else "",
        "FDR-adjusted P value": fmt_p(a) if j == 0 else "",
    })

add_cont("ΔVAS, final − baseline", "Delta_VAS_Final")
add_cont("Final CMO, mm", "Final_CMO")
add_cont("ΔCMO, mm, final − baseline", "Delta_CMO_Final", True)
add_cont("Final MMO, mm", "Final_MMO")
add_cont("ΔMMO, mm, final − baseline", "Delta_MMO_Final", True)
add_cont("Final pain-location burden score", "Final_Pain_Burden")
add_cont("ΔPain-location burden, final − baseline", "Delta_Pain_Burden_Final")

p,a = pmap["Pain-location burden change distribution"]
for j,level in enumerate(["Decreased","Maintained","Increased"]):
    rows.append({
        "Outcome": f"Pain-location burden {level.lower()}, n (%)",
        "Overall": n_pct_level(df.Pain_Burden_Response_Final, level),
        "Mild pain (VAS 0–3)": n_pct_level(df.loc[df[gcol] == MILD, "Pain_Burden_Response_Final"], level),
        "Moderate-to-severe pain (VAS ≥4)": n_pct_level(df.loc[df[gcol] == MODSEV, "Pain_Burden_Response_Final"], level),
        "P value": fmt_p(p) if j == 0 else "",
        "FDR-adjusted P value": fmt_p(a) if j == 0 else "",
    })

table = pd.DataFrame(rows)
save_csv(table, "Table_4.csv")
print(table.to_string(index=False))
