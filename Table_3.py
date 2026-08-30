# Table 3. Longitudinal mixed-effects models.

import warnings

import numpy as np
import pandas as pd
from scipy.stats import norm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from _common import fmt_p, read_sheet, save_csv

warnings.filterwarnings("ignore", category=UserWarning)


df = read_sheet("Visit_Long_191")
df = df.loc[df["Visit_Order"] <= 7].copy()
df["Time_30d"] = df["Days_From_Baseline"] / 30.0

time_df = (
    df.sort_values(["Study_ID", "Days_From_Baseline", "Visit_Order"])
    .drop_duplicates(["Study_ID", "Days_From_Baseline"], keep="first")
)

outcomes = [
    ("VAS", "VAS"),
    ("CMO, mm", "CMO"),
    ("MMO, mm", "MMO"),
    ("Pain-location burden score", "Pain_Location_Burden_0_6"),
]


def fit_mixedlm(formula, data):
    model = smf.mixedlm(formula, data, groups=data["Study_ID"])
    last_error = None
    for method in ["bfgs", "cg", "powell", "nm"]:
        try:
            fit = model.fit(reml=True, method=method, maxiter=10000, disp=False)
            if fit.converged:
                return fit
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"MixedLM did not converge: {last_error}")


def estimate(fit, term):
    beta = float(fit.params[term])
    se = float(fit.bse[term])
    p = float(2 * norm.sf(abs(beta / se)))
    return beta, beta - 1.96 * se, beta + 1.96 * se, p


rows = []
for label, outcome in outcomes:
    x = time_df[
        ["Study_ID", "Time_30d", "Baseline_Pain_Group_2L", outcome]
    ].dropna().copy()
    fit_time = fit_mixedlm(
        f"{outcome} ~ Time_30d + C(Baseline_Pain_Group_2L)", x
    )
    tb, tl, th, tp = estimate(fit_time, "Time_30d")

    z = df[
        ["Study_ID", "Visit_Type", "Cycle", "Baseline_Pain_Group_2L", outcome]
    ].dropna().copy()
    fit_visit = fit_mixedlm(
        f'{outcome} ~ C(Visit_Type, Treatment(reference="Injection day")) '
        "+ Cycle + C(Baseline_Pain_Group_2L)",
        z,
    )
    visit_term = next(term for term in fit_visit.params.index if "Visit_Type" in term)
    vb, vl, vh, vp = estimate(fit_visit, visit_term)

    rows.append(
        {
            "Outcome": label,
            "Elapsed-time observations, n": len(x),
            "Elapsed-time patients, n": x["Study_ID"].nunique(),
            "Time_beta": tb,
            "Time_CI_low": tl,
            "Time_CI_high": th,
            "Time_P": tp,
            "Visit-type observations, n": len(z),
            "Visit-type patients, n": z["Study_ID"].nunique(),
            "Visit_beta": vb,
            "Visit_CI_low": vl,
            "Visit_CI_high": vh,
            "Visit_P": vp,
        }
    )

numeric = pd.DataFrame(rows)
numeric["Time_FDR"] = multipletests(numeric["Time_P"], method="fdr_bh")[1]
numeric["Visit_FDR"] = multipletests(numeric["Visit_P"], method="fdr_bh")[1]

formatted = pd.DataFrame(
    {
        "Outcome": numeric["Outcome"],
        "Elapsed-time observations, n": numeric["Elapsed-time observations, n"],
        "Patients, n": numeric["Elapsed-time patients, n"],
        "Per 30-day increase, β (95% CI)": [
            f"{b:.3f} ({lo:.3f} to {hi:.3f})"
            for b, lo, hi in zip(
                numeric["Time_beta"], numeric["Time_CI_low"], numeric["Time_CI_high"]
            )
        ],
        "P value": [fmt_p(p) for p in numeric["Time_P"]],
        "FDR-adjusted P value": [fmt_p(p) for p in numeric["Time_FDR"]],
        "Visit-type observations, n": numeric["Visit-type observations, n"],
        "Visit-type patients, n": numeric["Visit-type patients, n"],
        "Follow-up vs injection-day, β (95% CI)": [
            f"{b:.3f} ({lo:.3f} to {hi:.3f})"
            for b, lo, hi in zip(
                numeric["Visit_beta"], numeric["Visit_CI_low"], numeric["Visit_CI_high"]
            )
        ],
        "Visit-type P value": [fmt_p(p) for p in numeric["Visit_P"]],
        "Visit-type FDR-adjusted P value": [fmt_p(p) for p in numeric["Visit_FDR"]],
    }
)

save_csv(numeric, "Table_3_numeric_Python.csv")
save_csv(formatted, "Table_3.csv")
print(formatted.to_string(index=False))
