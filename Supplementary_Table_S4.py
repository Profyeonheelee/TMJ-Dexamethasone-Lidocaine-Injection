# Supplementary Table S4. Site-specific pain transitions by final VAS change category.
import pandas as pd
from _common import CHANGE_LEVELS, read_sheet, save_csv


df = read_sheet("Pain_Site_Transitions")
site_order = ["Rt. Masseter", "Rt. Temporalis", "Rt. TMJ", "Lt. Masseter", "Lt. Temporalis", "Lt. TMJ"]
transition_order = ["Resolved (1→0)", "Persistent (1→1)", "Newly developed (0→1)", "Absent throughout (0→0)"]

rows=[]
for site in site_order:
    for grp in CHANGE_LEVELS:
        z=df[(df.Pain_Site==site)&(df.VAS_Response_Final==grp)]
        row={"Pain site":site,"Final VAS change":grp,"n":z.Study_ID.nunique()}
        for tr in transition_order:
            n=int((z.Transition==tr).sum())
            row[tr]=f"{n} ({100*n/len(z):.1f})" if len(z) else "NA"
        rows.append(row)

table=pd.DataFrame(rows)
save_csv(table,"Supplementary_Table_S4.csv")
print(table.to_string(index=False))
