suppressPackageStartupMessages({library(readxl);library(dplyr);library(tidyr);library(ggplot2);library(lme4);library(patchwork)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat<-read_excel(resolve_data_path(),sheet="Visit_Long_191")%>%filter(Visit_Order<=7)
lab<-c("Baseline","1st FU","2nd inj","2nd FU","3rd inj","3rd FU","4th inj","4th FU")
outcomes<-c(VAS="VAS",CMO="CMO (mm)",MMO="MMO (mm)",Pain_Location_Burden_0_6="Pain-location burden")
titles<-c(VAS="VAS trajectory",CMO="CMO trajectory",MMO="MMO trajectory",Pain_Location_Burden_0_6="Pain-location burden trajectory")
plots<-list();pvals<-c()
for(y in names(outcomes)){
 z<-dat%>%filter(!is.na(.data[[y]])); full<-lmer(as.formula(paste0(y," ~ factor(Visit_Order) + (1|Study_ID)")),z,REML=FALSE);null<-lmer(as.formula(paste0(y," ~ 1 + (1|Study_ID)")),z,REML=FALSE);p<-anova(null,full)$`Pr(>Chisq)`[2];pvals[y]<-p
 s<-z%>%group_by(Visit_Order)%>%summarise(mean=mean(.data[[y]]),sd=sd(.data[[y]]),n=n(),.groups="drop")%>%mutate(se=sd/sqrt(n),lo=mean-1.96*se,hi=mean+1.96*se)
 ptxt<-if(p<.001)"P < .001" else paste0("P = ",sub("0\\.",".",sprintf("%.3f",p)))
 plots[[y]]<-ggplot(s,aes(Visit_Order,mean))+geom_ribbon(aes(ymin=lo,ymax=hi),alpha=.18)+geom_line()+geom_point()+scale_x_continuous(breaks=0:7,labels=lab)+labs(title=titles[y],x=NULL,y=outcomes[y])+annotate("label",x=7,y=Inf,label=paste("Linear mixed-effects model\nVisit effect",ptxt),hjust=1,vjust=1.2,size=3)+theme_classic()+theme(axis.text.x=element_text(angle=35,hjust=1))
}
panel<-(plots[[1]]|plots[[2]])/(plots[[3]]|plots[[4]])+plot_annotation(tag_levels="A")
ggsave(file.path(output_dir(),"Figure_1.png"),panel,width=11,height=8.5,dpi=600);ggsave(file.path(output_dir(),"Figure_1.tiff"),panel,width=11,height=8.5,dpi=600,compression="lzw");print(pvals)
