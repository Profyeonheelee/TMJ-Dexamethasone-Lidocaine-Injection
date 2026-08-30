# Supplementary Table S5. Early pain-presence and direction-of-change categories.
import pandas as pd
from scipy.stats import binomtest, chi2_contingency
from _common import MILD, MODSEV, bh, fmt_p, read_sheet, save_csv

base=read_sheet("Baseline_191")[["Study_ID","Pain_Present"]].rename(columns={"Pain_Present":"Baseline_Pain"})
fu=read_sheet("First_FU_191")[["Study_ID","Pain_Present"]].rename(columns={"Pain_Present":"First_FU_Pain"})
df=read_sheet("Baseline_to_FirstFU").merge(base,on="Study_ID").merge(fu,on="Study_ID")

groups=[("Overall",None),("Mild pain (VAS 0–3)",MILD),("Moderate-to-severe pain (VAS ≥4)",MODSEV)]

# Panel A: exact McNemar = exact binomial test of discordant pairs.
panel_a=[]; raw=[]
for label,val in groups:
    z=df if val is None else df[df.Baseline_Pain_Group_2L==val]
    z=z.dropna(subset=["Baseline_Pain","First_FU_Pain"])
    improved=int(((z.Baseline_Pain==1)&(z.First_FU_Pain==0)).sum())
    worsened=int(((z.Baseline_Pain==0)&(z.First_FU_Pain==1)).sum())
    disc=improved+worsened
    p=1.0 if disc==0 else binomtest(min(improved,worsened),disc,p=0.5,alternative="two-sided").pvalue
    raw.append(p)
    panel_a.append({
        "Outcome":"Pain present","Baseline pain group":label,"n":len(z),
        "Baseline n (%)":f"{int((z.Baseline_Pain==1).sum())} ({100*(z.Baseline_Pain==1).mean():.1f})",
        "First follow-up n (%)":f"{int((z.First_FU_Pain==1).sum())} ({100*(z.First_FU_Pain==1).mean():.1f})",
        "Improved n":improved,"Worsened n":worsened,"Raw_P":p,
    })
adj=bh(raw)
for r,a in zip(panel_a,adj):
    r["P value"]=fmt_p(r.pop("Raw_P"));r["FDR-adjusted P value"]=fmt_p(a)

# Panel B
panel_b=[]; tests=[]
for metric,var in [("VAS change","VAS_Response_FirstFU"),("Pain-burden change","Pain_Burden_Response_FirstFU")]:
    tab=pd.crosstab(df[var],df.Baseline_Pain_Group_2L).reindex(index=["Decreased","Maintained","Increased"],fill_value=0)
    p=chi2_contingency(tab,correction=False).pvalue
    tests.append(p)
    for label,val in groups:
        z=df if val is None else df[df.Baseline_Pain_Group_2L==val]
        counts=z[var].value_counts()
        n=len(z); dec=int(counts.get("Decreased",0)); maint=int(counts.get("Maintained",0)); inc=int(counts.get("Increased",0))
        panel_b.append({
            "Change metric":metric,"Baseline pain group":label,"n":n,
            "Decreased n (%)":f"{dec} ({100*dec/n:.1f})",
            "Maintained n (%)":f"{maint} ({100*maint/n:.1f})",
            "Increased n (%)":f"{inc} ({100*inc/n:.1f})",
            "Decreased or maintained n (%)":f"{dec+maint} ({100*(dec+maint)/n:.1f})",
            "Between-group P value":fmt_p(p) if label=="Overall" else "",
        })
adj2=bh(tests)
for i,metric in enumerate(["VAS change","Pain-burden change"]):
    for r in panel_b:
        if r["Change metric"]==metric and r["Baseline pain group"]=="Overall":
            r["FDR-adjusted P value"]=fmt_p(adj2[i])
        elif r["Change metric"]==metric:
            r["FDR-adjusted P value"]=""

save_csv(pd.DataFrame(panel_a),"Supplementary_Table_S5_Panel_A.csv")
save_csv(pd.DataFrame(panel_b),"Supplementary_Table_S5_Panel_B.csv")
print("Panel A\n",pd.DataFrame(panel_a).to_string(index=False))
print("\nPanel B\n",pd.DataFrame(panel_b).to_string(index=False))
