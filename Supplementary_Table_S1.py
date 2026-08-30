# Supplementary Table S1. Visit-wise longitudinal summary.
import pandas as pd
from _common import read_sheet, save_csv


df = read_sheet("Visit_Long_191")
df = df[df.Visit_Order <= 7].copy()
visit_map = {
    0: "Baseline / 1st injection",
    1: "1st follow-up",
    2: "2nd injection",
    3: "2nd follow-up",
    4: "3rd injection",
    5: "3rd follow-up",
    6: "4th injection",
    7: "4th follow-up",
}


def msdn(s, dec=2):
    x = pd.Series(s).dropna().astype(float)
    if x.empty:
        return "NA"
    return f"{x.mean():.{dec}f} ± {x.std(ddof=1):.{dec}f} ({len(x)})"

rows = []
for vo in range(8):
    z = df[df.Visit_Order == vo]
    pain = z.Pain_Present.dropna()
    pain_cell = f"{int((pain == 1).sum())} ({100*(pain == 1).mean():.1f})" if len(pain) else "NA"
    rows.append({
        "Visit": visit_map[vo],
        "Total n": len(z),
        "Mean days from baseline": msdn(z.Days_From_Baseline, 1).split(" (")[0],
        "VAS": msdn(z.VAS, 2),
        "CMO, mm": msdn(z.CMO, 2),
        "MMO, mm": msdn(z.MMO, 2),
        "Pain present, n (%)": pain_cell,
        "Pain-location burden score": msdn(z.Pain_Location_Burden_0_6, 2),
    })

table = pd.DataFrame(rows)
save_csv(table, "Supplementary_Table_S1.csv")
print(table.to_string(index=False))
