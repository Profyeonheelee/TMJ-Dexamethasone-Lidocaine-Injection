from pathlib import Path
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact
from statsmodels.stats.multitest import multipletests


DATA_FILE = "Dexamethasone_Final_Analytic_Dataset_191.xlsx"

MILD = "Mild pain (VAS 0–3)"
MODSEV = "Moderate-to-severe pain (VAS ≥4)"
THREE_LEVELS = [
    "Mild pain (VAS 0–3)",
    "Moderate pain (VAS 4–6)",
    "Severe pain (VAS ≥7)",
]
CHANGE_LEVELS = ["Decreased", "Maintained", "Increased"]


def project_root() -> Path:
    return Path(__file__).resolve().parent


def resolve_data_path() -> Path:
    candidates = []

    if len(sys.argv) > 1 and sys.argv[1].strip():
        candidates.append(Path(sys.argv[1]).expanduser())

    env_path = os.getenv("TMJ_DATA", "").strip()
    if env_path:
        candidates.append(Path(env_path).expanduser())

    root = project_root()
    candidates.extend([
        root / "data" / DATA_FILE,
        root / DATA_FILE,
    ])

    for path in candidates:
        if path.is_file():
            return path.resolve()

    checked = "\n".join(f"  - {p}" for p in candidates)
    raise FileNotFoundError(
        f"Could not locate {DATA_FILE}. Checked:\n{checked}\n"
        "Supply the workbook path as the first command-line argument, "
        "set TMJ_DATA, or place the workbook in the data/ directory."
    )


def output_dir() -> Path:
    out = project_root() / "outputs" / "python"
    out.mkdir(parents=True, exist_ok=True)
    return out


def read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(resolve_data_path(), sheet_name=sheet_name)


def save_csv(df: pd.DataFrame, filename: str) -> Path:
    path = output_dir() / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def bh(p_values):
    p = np.asarray(p_values, dtype=float)
    return multipletests(p, method="fdr_bh")[1]


def fmt_p(p) -> str:
    if p is None or not np.isfinite(float(p)):
        return "NA"
    p = float(p)
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def categorical_p_from_table(table) -> float:
    arr = np.asarray(table, dtype=float)
    if arr.ndim != 2 or min(arr.shape) < 2:
        return np.nan

    chi2, p_chi, _, expected = chi2_contingency(arr, correction=False)

    if arr.shape == (2, 2) and np.any(expected < 5):
        return float(fisher_exact(arr, alternative="two-sided").pvalue)

    return float(p_chi)
