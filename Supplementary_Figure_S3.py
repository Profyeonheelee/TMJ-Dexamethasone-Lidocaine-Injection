# Supplementary Figure S3. Cross-domain Spearman correlation structure.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from _common import output_dir, read_sheet

vars_raw=["VAS","CMO","MMO","Pain_Present","Pain_Location_Burden_0_6","Rt_Masseter","Rt_Temporalis","Rt_TMJ","Lt_Masseter","Lt_Temporalis","Lt_TMJ","Age","Female"]
labels={"VAS":"VAS","CMO":"CMO","MMO":"MMO","Pain_Present":"Pain\npresence","Pain_Location_Burden_0_6":"Pain-location\nburden","Rt_Masseter":"Rt.\nMasseter","Rt_Temporalis":"Rt.\nTemporalis","Rt_TMJ":"Rt. TMJ","Lt_Masseter":"Lt.\nMasseter","Lt_Temporalis":"Lt.\nTemporalis","Lt_TMJ":"Lt. TMJ","Age":"Age","Female":"Female"}

def prep(sheet):
    d=read_sheet(sheet).copy();d["Female"]=d.Sex.eq("F").astype(float)
    return d[vars_raw].apply(pd.to_numeric,errors="coerce")
base=prep("Baseline_191");first=prep("First_FU_191");final=prep("Final_FU_191")

def corr(d): return d.corr(method="spearman",min_periods=3)
cb,cf,cl=corr(base),corr(first),corr(final)

fig=plt.figure(figsize=(13,9))
gs=fig.add_gridspec(2,2,wspace=.25,hspace=.30)
axA=fig.add_subplot(gs[0,0]); axB=fig.add_subplot(gs[0,1]); axC=fig.add_subplot(gs[1,0]); axD=fig.add_subplot(gs[1,1])

# Panel A: selected major baseline associations (|rho| >= 0.15) for a readable network.
G=nx.Graph();G.add_nodes_from(vars_raw)
for i in range(len(vars_raw)):
    for j in range(i+1,len(vars_raw)):
        r=cb.iloc[i,j]
        if np.isfinite(r) and abs(r)>=0.15:
            G.add_edge(vars_raw[i],vars_raw[j],weight=float(r))
pos=nx.spring_layout(G,seed=8,k=0.65)
nx.draw_networkx_nodes(G,pos,ax=axA,node_size=950,node_color="white",edgecolors="0.35")
nx.draw_networkx_labels(G,pos,ax=axA,labels=labels,font_size=7)
for u,v,d in G.edges(data=True):
    r=d["weight"]; color="#B22222" if r>=0 else "#1F4E79"
    nx.draw_networkx_edges(G,pos,edgelist=[(u,v)],ax=axA,width=.5+3*abs(r),edge_color=color,alpha=.75)
axA.set_title("A",loc="left",fontweight="bold",fontsize=14);axA.axis("off")

# Heatmaps B-D.
def heat(ax,c,title,panel):
    im=ax.imshow(c.to_numpy(),vmin=-1,vmax=1,cmap="RdBu_r")
    ax.set_xticks(range(len(vars_raw)),[labels[v].replace("\n"," ") for v in vars_raw],rotation=55,ha="right",fontsize=6)
    ax.set_yticks(range(len(vars_raw)),[labels[v].replace("\n"," ") for v in vars_raw],fontsize=6)
    for i in range(len(vars_raw)):
        for j in range(len(vars_raw)):
            val=c.iloc[i,j]
            if np.isfinite(val):
                ax.text(j,i,f"{val:.2f}",ha="center",va="center",fontsize=4.5)
    ax.set_title(f"{panel}   {title}",loc="left",fontweight="bold")
    return im
im=heat(axB,cb,"Baseline","B");heat(axC,cf,"1st follow-up","C");heat(axD,cl,"Final follow-up","D")
fig.colorbar(im,ax=[axB,axC,axD],fraction=.018,pad=.02,label="Spearman ρ")
out=output_dir()/"Supplementary_Figure_S3.png"
fig.savefig(out,dpi=600,bbox_inches="tight")
fig.savefig(output_dir()/"Supplementary_Figure_S3.tiff",dpi=600,bbox_inches="tight")
print(f"Saved: {out}")
