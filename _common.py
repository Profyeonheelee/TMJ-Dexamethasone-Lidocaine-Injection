from __future__ import annotations

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact
from statsmodels.stats.multitest import multipletests

DATA_FILENAME = "Dexamethasone_Final_Analytic_Dataset_191.xlsx"
MILD = "Mild pain (VAS 0–3)"
MODSEV = "Moderate-to-severe pain (VAS ≥4)"
THREE_LEVELS = ["Mild pain (VAS 0–3)", "Moderate pain (VAS 4–6)", "Severe pain (VAS ≥7)"]
CHANGE_LEVELS = ["Decreased", "Maintained", "Increased"]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_data_path() -> Path:
    if len(sys.argv) > 1:
        p = Path(sys.argv[1]).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"Data file not found: {p}")

    env_path = os.getenv("TMJ_DATA")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"TMJ_DATA points to a missing file: {p}")

    candidates = [
        project_root() / "data" / DATA_FILENAME,
        Path.cwd() / DATA_FILENAME,
        Path.cwd() / "data" / DATA_FILENAME,
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(
        f"Could not find {DATA_FILENAME}. Pass the full path as the first command-line argument "
        "or set the TMJ_DATA environment variable."
    )


def output_dir() -> Path:
    out = project_root() / "outputs" / "python"
    out.mkdir(parents=True, exist_ok=True)
    return out


def read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(resolve_data_path(), sheet_name=sheet_name)


def bh(pvalues):
    pvalues = np.asarray(pvalues, dtype=float)
    return multipletests(pvalues, method="fdr_bh")[1]


def fmt_p(p: float) -> str:
    if p is None or not np.isfinite(p):
        return "NA"
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def mean_sd(x, decimals=2):
    s = pd.Series(x).dropna().astype(float)
    if s.empty:
        return np.nan, np.nan, 0
    return s.mean(), s.std(ddof=1), int(s.size)


def fmt_mean_sd_n(x, decimals=2, include_n=True, sign=False):
    m, sd, n = mean_sd(x, decimals)
    if n == 0:
        return "NA"
    sign_fmt = "+" if sign and m > 0 else ""
    txt = f"{sign_fmt}{m:.{decimals}f} ± {sd:.{decimals}f}"
    return f"{txt} ({n})" if include_n else txt


def fmt_n_pct(x):
    s = pd.Series(x).dropna()
    if s.empty:
        return "NA"
    n = int((s.astype(float) == 1).sum())
    denom = int(s.size)
    return f"{n} ({100*n/denom:.1f})"


def categorical_p_from_table(tab: pd.DataFrame) -> float:
    tab = tab.loc[(tab.sum(axis=1) > 0), (tab.sum(axis=0) > 0)]
    if tab.shape[0] < 2 or tab.shape[1] < 2:
        return np.nan
    chi = chi2_contingency(tab, correction=False)
    if tab.shape == (2, 2) and np.any(chi.expected_freq < 5):
        return fisher_exact(tab.values)[1]
    return chi.pvalue


def save_csv(df: pd.DataFrame, filename: str):
    path = output_dir() / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved: {path}")
    return path
