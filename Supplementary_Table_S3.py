# Supplementary Table S3. Outcomes according to final VAS change category.
import pandas as pd
from scipy.stats import kruskal, chi2_contingency
from _common import CHANGE_LEVELS, MODSEV, fmt_p, read_sheet, save_csv


df = read_sheet("Baseline_to_FinalFU")
g = "VAS_Response_Final"

continuous = [
    ("Baseline VAS", "Baseline_VAS", False),
    ("Final VAS", "Final_VAS", False),
    ("ΔVAS, final − baseline", "Delta_VAS_Final", False),
    ("Baseline CMO, mm", "Baseline_CMO", False),
    ("Final CMO, mm", "Final_CMO", False),
    ("ΔCMO, mm, final − baseline", "Delta_CMO_Final", True),
    ("Baseline MMO, mm", "Baseline_MMO", False),
    ("Final MMO, mm", "Final_MMO", False),
    ("ΔMMO, mm, final − baseline", "Delta_MMO_Final", True),
    ("Baseline pain-location burden score", "Baseline_Pain_Burden", False),
    ("Final pain-location burden score", "Final_Pain_Burden", False),
    ("ΔPain-location burden, final − baseline", "Delta_Pain_Burden_Final", False),
]


def msdn(s, sign=False):
    x=pd.Series(s).dropna().astype(float)
    if x.empty:return "NA"
    prefix="+" if sign and x.mean()>0 else ""
    return f"{prefix}{x.mean():.2f} ± {x.std(ddof=1):.2f} ({len(x)})"

def npct(series, predicate):
    x=pd.Series(series).dropna(); n=int(predicate(x).sum())
    return f"{n} ({100*n/len(x):.1f})"

rows=[]
# Baseline VAS first
for label,var,sign in continuous[:1]:
    groups=[df.loc[df[g]==level,var].dropna() for level in CHANGE_LEVELS]
    p=kruskal(*groups).pvalue
    rows.append({"Variable":label, **{level:msdn(df.loc[df[g]==level,var],sign) for level in CHANGE_LEVELS}, "P value":fmt_p(p)})

# Moderate-to-severe baseline pain
x=(df.Baseline_Pain_Group_2L==MODSEV)
tab=pd.crosstab(x,df[g]).reindex(columns=CHANGE_LEVELS,fill_value=0)
p=chi2_contingency(tab,correction=False).pvalue
rows.append({"Variable":"Moderate-to-severe baseline pain, n (%)", **{level:npct(x[df[g]==level],lambda s:s) for level in CHANGE_LEVELS}, "P value":fmt_p(p)})

# Final VAS / zero / delta VAS
for label,var,sign in continuous[1:3]:
    groups=[df.loc[df[g]==level,var].dropna() for level in CHANGE_LEVELS]
    p=kruskal(*groups).pvalue
    rows.append({"Variable":label, **{level:msdn(df.loc[df[g]==level,var],sign) for level in CHANGE_LEVELS}, "P value":fmt_p(p)})
    if label=="Final VAS":
        zero=df.Final_VAS_Zero
        tab=pd.crosstab(zero,df[g]).reindex(columns=CHANGE_LEVELS,fill_value=0)
        pz=chi2_contingency(tab,correction=False).pvalue
        rows.append({"Variable":"Final VAS = 0, n (%)", **{level:npct(zero[df[g]==level],lambda s:s==1) for level in CHANGE_LEVELS}, "P value":fmt_p(pz)})

for label,var,sign in continuous[3:]:
    groups=[df.loc[df[g]==level,var].dropna() for level in CHANGE_LEVELS]
    p=kruskal(*groups).pvalue
    rows.append({"Variable":label, **{level:msdn(df.loc[df[g]==level,var],sign) for level in CHANGE_LEVELS}, "P value":fmt_p(p)})

for title,var,levels in [
    ("CMO", "CMO_Response_Final", ["Increased","Maintained","Decreased"]),
    ("MMO", "MMO_Response_Final", ["Increased","Maintained","Decreased"]),
    ("Pain-location burden", "Pain_Burden_Response_Final", ["Decreased","Maintained","Increased"]),
]:
    tab=pd.crosstab(df[var],df[g]).reindex(index=levels,columns=CHANGE_LEVELS,fill_value=0)
    p=chi2_contingency(tab,correction=False).pvalue
    for i,level in enumerate(levels):
        rows.append({"Variable":f"{title} {level.lower()}, n (%)",
                     **{grp:npct(df.loc[df[g]==grp,var],lambda s,l=level:s==l) for grp in CHANGE_LEVELS},
                     "P value":fmt_p(p) if i==0 else ""})

# Pain absent at final follow-up is equivalent to Final pain presence == 0. Read directly from Final_FU_191.
final_fu=read_sheet("Final_FU_191")
merged=df[["Study_ID",g]].merge(final_fu[["Study_ID","Pain_Present"]],on="Study_ID",how="left")
tab=pd.crosstab(merged.Pain_Present,merged[g]).reindex(columns=CHANGE_LEVELS,fill_value=0)
p=chi2_contingency(tab,correction=False).pvalue
rows.append({"Variable":"Pain absent at final follow-up, n (%)",
             **{grp:npct(merged.loc[merged[g]==grp,"Pain_Present"],lambda s:s==0) for grp in CHANGE_LEVELS},
             "P value":fmt_p(p)})

table=pd.DataFrame(rows).rename(columns={"Decreased":"VAS decreased (n=102)","Maintained":"VAS maintained (n=77)","Increased":"VAS increased (n=12)"})
save_csv(table,"Supplementary_Table_S3.csv")
print(table.to_string(index=False))
