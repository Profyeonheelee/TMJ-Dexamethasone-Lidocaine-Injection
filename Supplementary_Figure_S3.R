suppressPackageStartupMessages({library(readxl);library(igraph)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
vars<-c("VAS","CMO","MMO","Pain_Present","Pain_Location_Burden_0_6","Rt_Masseter","Rt_Temporalis","Rt_TMJ","Lt_Masseter","Lt_Temporalis","Lt_TMJ","Age","Female")
labs<-c("VAS","CMO","MMO","Pain presence","Pain-location burden","Rt. Masseter","Rt. Temporalis","Rt. TMJ","Lt. Masseter","Lt. Temporalis","Lt. TMJ","Age","Female")
prep<-function(sheet){d<-read_excel(resolve_data_path(),sheet=sheet);d$Female<-as.numeric(d$Sex=="F");as.data.frame(lapply(d[,vars],as.numeric))}
B<-prep("Baseline_191");F<-prep("First_FU_191");L<-prep("Final_FU_191");corx<-function(x)cor(x,use="pairwise.complete.obs",method="spearman");CB<-corx(B);CF<-corx(F);CL<-corx(L)
cols<-colorRampPalette(c("navy","white","red"))(201)
plot_heat<-function(C,title){image(1:ncol(C),1:nrow(C),t(C[nrow(C):1,]),zlim=c(-1,1),col=cols,axes=FALSE,main=title);axis(1,1:ncol(C),labs,las=2,cex.axis=.45);axis(2,1:nrow(C),rev(labs),las=2,cex.axis=.45);for(i in 1:nrow(C))for(j in 1:ncol(C))text(j,nrow(C)-i+1,sprintf("%.2f",C[i,j]),cex=.32)}
plot_net<-function(C){A<-C;diag(A)<-0;A[abs(A)<.15]<-0;g<-graph_from_adjacency_matrix(A,mode="undirected",weighted=TRUE,diag=FALSE);E(g)$color<-ifelse(E(g)$weight>=0,"firebrick","#1F4E79");E(g)$width<-.5+4*abs(E(g)$weight);V(g)$label<-labs;V(g)$size<-23;V(g)$color<-"white";V(g)$frame.color<-"grey40";plot(g,layout=layout_with_fr(g),vertex.label.cex=.55,main="A   Baseline selected associations")}
png(file.path(output_dir(),"Supplementary_Figure_S3.png"),width=3600,height=2600,res=300);par(mfrow=c(2,2),mar=c(5,5,3,2));plot_net(CB);plot_heat(CB,"B   Baseline");plot_heat(CF,"C   1st follow-up");plot_heat(CL,"D   Final follow-up");dev.off()
tiff(file.path(output_dir(),"Supplementary_Figure_S3.tiff"),width=12,height=9,units="in",res=600,compression="lzw");par(mfrow=c(2,2),mar=c(5,5,3,2));plot_net(CB);plot_heat(CB,"B   Baseline");plot_heat(CF,"C   1st follow-up");plot_heat(CL,"D   Final follow-up");dev.off()
