suppressPackageStartupMessages({library(readxl);library(dplyr)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat <- read_excel(resolve_data_path(), sheet="Baseline_to_FirstFU")
outcomes <- list(
  list("VAS","Baseline_VAS","First_FU_VAS","Delta_VAS_FirstFU"),
  list("CMO, mm","Baseline_CMO","First_FU_CMO","Delta_CMO_FirstFU"),
  list("MMO, mm","Baseline_MMO","First_FU_MMO","Delta_MMO_FirstFU"),
  list("Pain-location burden","Baseline_Pain_Burden","First_FU_Pain_Burden","Delta_Pain_Burden_FirstFU")
)
groups <- list(list("Overall",NULL),list("Mild pain",MILD),list("Moderate-to-severe pain",MODSEV))
records<-list(); raw<-c()
for(o in outcomes){for(g in groups){z<-if(is.null(g[[2]]))dat else dat%>%filter(Baseline_Pain_Group_2L==g[[2]]); z<-z[complete.cases(z[,c(o[[2]],o[[3]])]),]; p<-wilcox.test(z[[o[[3]]]],z[[o[[2]]]],paired=TRUE,exact=FALSE)$p.value; raw<-c(raw,p); records[[length(records)+1]]<-list(out=o[[1]],grp=g[[1]],n=nrow(z),base=z[[o[[2]]]],fu=z[[o[[3]]]],delta=z[[o[[4]]]],p=p)}}
adj<-p.adjust(raw,"BH")
for(i in seq_along(records)) records[[i]]$fdr<-adj[i]
between_raw<-sapply(outcomes,function(o) wilcox.test(dat[[o[[4]]]][dat$Baseline_Pain_Group_2L==MILD],dat[[o[[4]]]][dat$Baseline_Pain_Group_2L==MODSEV],exact=FALSE)$p.value)
between_fdr<-p.adjust(between_raw,"BH")
rows<-list()
for(i in seq_along(records)){r<-records[[i]]; j<-match(r$out,sapply(outcomes,`[[`,1)); cell<-function(x)sprintf("%.2f ± %.2f",mean(x,na.rm=TRUE),sd(x,na.rm=TRUE)); dcell<-function(x)sprintf("%+.2f ± %.2f",mean(x,na.rm=TRUE),sd(x,na.rm=TRUE)); rows[[i]]<-data.frame(Outcome=r$out,Baseline_pain_group=r$grp,n=r$n,Baseline=cell(r$base),First_follow_up=cell(r$fu),Change=dcell(r$delta),Within_group_FDR_P_value=fmt_p(r$fdr),Between_group_FDR_P_value_for_change=if(r$grp=="Overall")"—" else if(r$grp=="Mild pain")fmt_p(between_fdr[j]) else "",check.names=FALSE)}
tab<-bind_rows(rows);write.csv(tab,file.path(output_dir(),"Table_2.csv"),row.names=FALSE,fileEncoding="UTF-8");print(tab)
