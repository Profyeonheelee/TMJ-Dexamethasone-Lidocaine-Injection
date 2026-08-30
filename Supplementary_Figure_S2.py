# Supplementary Figure S2. Visit-to-visit Spearman correlation networks.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from _common import output_dir, read_sheet


df=read_sheet("Correlation_Input_Wide")
visit_labels=["Baseline","1st FU","2nd inj","2nd FU","3rd inj","3rd FU","4th inj","4th FU"]
sets={
    "VAS":["VAS_Baseline","VAS_1st_FU","VAS_2nd_inj","VAS_2nd_FU","VAS_3rd_inj","VAS_3rd_FU","VAS_4th_inj","VAS_4th_FU"],
    "CMO":["CMO_Baseline","CMO_1st_FU","CMO_2nd_inj","CMO_2nd_FU","CMO_3rd_inj","CMO_3rd_FU","CMO_4th_inj","CMO_4th_FU"],
    "MMO":["MMO_Baseline","MMO_1st_FU","MMO_2nd_inj","MMO_2nd_FU","MMO_3rd_inj","MMO_3rd_FU","MMO_4th_inj","MMO_4th_FU"],
    "Pain-location burden":["Pain_Burden_Baseline","Pain_Burden_1st_FU","Pain_Burden_2nd_inj","Pain_Burden_2nd_FU","Pain_Burden_3rd_inj","Pain_Burden_3rd_FU","Pain_Burden_4th_inj","Pain_Burden_4th_FU"],
}

fig,axes=plt.subplots(2,2,figsize=(10,8))
norm=Normalize(vmin=0,vmax=1); cmap=plt.cm.Oranges
for ax,(title,cols),panel in zip(axes.flat,sets.items(),["A","B","C","D"]):
    corr=df[cols].corr(method="spearman",min_periods=3)
    G=nx.Graph(); G.add_nodes_from(range(8))
    for i in range(8):
        for j in range(i+1,8):
            r=corr.iloc[i,j]
            if np.isfinite(r) and r>0:
                G.add_edge(i,j,weight=float(r))
    pos=nx.circular_layout(G)
    nx.draw_networkx_nodes(G,pos,ax=ax,node_size=850,node_color="white",edgecolors="0.4")
    nx.draw_networkx_labels(G,pos,ax=ax,labels={i:visit_labels[i] for i in range(8)},font_size=7)
    for u,v,d in G.edges(data=True):
        r=d["weight"]
        nx.draw_networkx_edges(G,pos,edgelist=[(u,v)],ax=ax,width=0.5+3.5*r,edge_color=[cmap(norm(r))])
    ax.set_title(title,fontweight="bold");ax.axis("off")
    ax.text(-0.06,1.02,panel,transform=ax.transAxes,fontweight="bold",fontsize=14)
sm=ScalarMappable(norm=norm,cmap=cmap);sm.set_array([])
fig.colorbar(sm,ax=axes.ravel().tolist(),fraction=.02,pad=.02,label="Spearman ρ")
fig.tight_layout(rect=(0,0,0.95,1))
out=output_dir()/"Supplementary_Figure_S2.png"
fig.savefig(out,dpi=600,bbox_inches="tight")
fig.savefig(output_dir()/"Supplementary_Figure_S2.tiff",dpi=600,bbox_inches="tight")
print(f"Saved: {out}")
