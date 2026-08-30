# Supplementary Figure S1. Early direction-of-change categories by baseline pain severity.
import pandas as pd
import matplotlib.pyplot as plt
from _common import THREE_LEVELS, CHANGE_LEVELS, output_dir, read_sheet


df=read_sheet("Baseline_to_FirstFU")
group_order=["Overall",*THREE_LEVELS]
labels={
    "Overall":"Overall (n=191)",
    THREE_LEVELS[0]:"Mild pain (VAS 0–3, n=126)",
    THREE_LEVELS[1]:"Moderate pain (VAS 4–6, n=54)",
    THREE_LEVELS[2]:"Severe pain (VAS ≥7, n=11)",
}
colors={"Decreased":"#4CAF50","Maintained":"#F4C542","Increased":"#E85C50"}


def make_counts(var):
    rows=[]
    for grp in group_order:
        z=df if grp=="Overall" else df[df.Baseline_Pain_Group_3L==grp]
        n=len(z)
        counts=z[var].value_counts()
        for ch in CHANGE_LEVELS:
            c=int(counts.get(ch,0)); rows.append((grp,ch,c,100*c/n if n else 0))
    return pd.DataFrame(rows,columns=["Group","Change","n","Percent"])

fig,axes=plt.subplots(2,1,figsize=(9,7.5),sharex=True)
for ax,var,title,panel in [
    (axes[0],"VAS_Response_FirstFU","VAS change category by baseline pain group","A"),
    (axes[1],"Pain_Burden_Response_FirstFU","Pain-burden change category by baseline pain group","B"),
]:
    dat=make_counts(var)
    y=list(range(len(group_order)))
    left=[0]*len(group_order)
    # Stack order used in the figure.
    for ch in ["Increased","Maintained","Decreased"]:
        vals=[]
        for grp in group_order:
            vals.append(float(dat[(dat.Group==grp)&(dat.Change==ch)].Percent.iloc[0]))
        bars=ax.barh(y,vals,left=left,height=.55,label=ch,color=colors[ch])
        for i,(bar,v) in enumerate(zip(bars,vals)):
            if v>=3:
                ax.text(left[i]+v/2,bar.get_y()+bar.get_height()/2,f"{v:.1f}%",ha="center",va="center",fontsize=8)
        left=[a+b for a,b in zip(left,vals)]
    ax.set_yticks(y,[labels[g] for g in group_order])
    ax.invert_yaxis(); ax.set_xlim(0,100); ax.set_title(title); ax.set_xlabel("Percentage (%)")
    ax.text(-0.11,1.03,panel,transform=ax.transAxes,fontweight="bold",fontsize=14)
    ax.spines[["top","right"]].set_visible(False)
handles,lab=axes[0].get_legend_handles_labels()
fig.legend(handles,lab,loc="lower center",ncol=3,title="Direction of change",frameon=False)
fig.tight_layout(rect=(0,0.07,1,1))
out=output_dir()/"Supplementary_Figure_S1.png"
fig.savefig(out,dpi=600,bbox_inches="tight")
fig.savefig(output_dir()/"Supplementary_Figure_S1.tiff",dpi=600,bbox_inches="tight")
print(f"Saved: {out}")
