# Supplementary Table S2. Visit-wise outcomes by three-level baseline pain severity.
import pandas as pd
from _common import THREE_LEVELS, read_sheet, save_csv


df = read_sheet("Visit_Long_191")
df = df[df.Visit_Order <= 7].copy()
visit_labels = {
    0: "Baseline / 1st injection day", 1: "1st follow-up after 1st injection",
    2: "2nd injection day", 3: "2nd follow-up", 4: "3rd injection day",
    5: "3rd follow-up", 6: "4th injection day", 7: "4th follow-up",
}
outcomes = [("VAS","VAS"),("CMO, mm","CMO"),("MMO, mm","MMO"),("Pain-location burden score","Pain_Location_Burden_0_6")]


def cell(s):
    x = pd.Series(s).dropna().astype(float)
    if x.empty:
        return "NA"
    if len(x) == 1:
        return f"{x.iloc[0]:.2f} (1)"
    return f"{x.mean():.2f} ± {x.std(ddof=1):.2f} ({len(x)})"

rows=[]
for out_label, var in outcomes:
    for vo in range(8):
        row={"Outcome":out_label,"Visit":visit_labels[vo]}
        for grp in THREE_LEVELS:
            row[grp]=cell(df.loc[(df.Visit_Order==vo)&(df.Baseline_Pain_Group_3L==grp),var])
        rows.append(row)

table=pd.DataFrame(rows)
save_csv(table,"Supplementary_Table_S2.csv")
print(table.to_string(index=False))
