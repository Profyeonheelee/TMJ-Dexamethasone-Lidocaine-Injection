suppressPackageStartupMessages({library(readxl);library(dplyr);library(ggplot2);library(geepack);library(patchwork)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat<-read_excel(resolve_data_path(),sheet="Visit_Long_191")%>%filter(Visit_Order<=7)%>%mutate(Baseline_Pain_Group_3L=factor(Baseline_Pain_Group_3L,levels=THREE_LEVELS),VisitF=factor(Visit_Order))
lab<-c("Baseline","1st FU","2nd inj","2nd FU","3rd inj","3rd FU","4th inj","4th FU");outs<-c(VAS="VAS",CMO="CMO (mm)",MMO="MMO (mm)",Pain_Location_Burden_0_6="Pain-location burden")
plots<-list();pvals<-c()
for(y in names(outs)){
 z<-dat%>%filter(!is.na(.data[[y]])); fit<-geeglm(as.formula(paste0(y," ~ Baseline_Pain_Group_3L * VisitF")),id=Study_ID,data=z,corstr="exchangeable",family=gaussian); co<-anova(fit); rn<-rownames(co); idx<-grep("Baseline_Pain_Group_3L:VisitF",rn); p<-as.numeric(co[idx,ncol(co)]); pvals[y]<-p
 s<-z%>%group_by(Baseline_Pain_Group_3L,Visit_Order)%>%summarise(mean=mean(.data[[y]]),sd=sd(.data[[y]]),n=n(),.groups="drop")%>%mutate(se=sd/sqrt(n),lo=mean-1.96*se,hi=mean+1.96*se,lo=ifelse(n>=10,lo,NA),hi=ifelse(n>=10,hi,NA))
 ptxt<-if(p<.001)"P < .001" else paste0("P = ",sub("0\\.",".",sprintf("%.3f",p)))
 plots[[y]]<-ggplot(s,aes(Visit_Order,mean,color=Baseline_Pain_Group_3L,fill=Baseline_Pain_Group_3L))+geom_ribbon(aes(ymin=lo,ymax=hi),alpha=.12,color=NA)+geom_line()+geom_point()+scale_x_continuous(breaks=0:7,labels=lab)+labs(x=NULL,y=outs[y],color=NULL,fill=NULL)+annotate("label",x=7,y=Inf,label=paste("Repeated-measures GEE\nGroup × visit interaction",ptxt,"\n95% CI shown when n ≥ 10"),hjust=1,vjust=1.2,size=2.8)+theme_classic()+theme(axis.text.x=element_text(angle=35,hjust=1),legend.position="bottom")
}
panel<-(plots[[1]]|plots[[2]])/(plots[[3]]|plots[[4]])+plot_annotation(tag_levels="A")
ggsave(file.path(output_dir(),"Figure_2.png"),panel,width=12,height=8.5,dpi=600);ggsave(file.path(output_dir(),"Figure_2.tiff"),panel,width=12,height=8.5,dpi=600,compression="lzw");print(pvals)
