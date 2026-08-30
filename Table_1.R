suppressPackageStartupMessages({library(readxl);library(dplyr)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat <- read_excel(resolve_data_path(), sheet = "Baseline_191")
cont <- c("Age","Baseline_VAS","CMO","MMO","Pain_Location_Burden_0_6")
cont_labels <- c("Age, years","Baseline VAS","CMO, mm","MMO, mm","Pain-location burden score")
cat_vars <- c("Sex","Pain_Present","Rt_Masseter","Rt_Temporalis","Rt_TMJ","Lt_Masseter","Lt_Temporalis","Lt_TMJ")
cat_labels <- c("Female sex, n (%)","Pain present, n (%)","Rt. Masseter pain, n (%)","Rt. Temporalis pain, n (%)","Rt. TMJ pain, n (%)","Lt. Masseter pain, n (%)","Lt. Temporalis pain, n (%)","Lt. TMJ pain, n (%)")

ps <- c()
for (v in cont) ps <- c(ps, wilcox.test(dat[[v]] ~ dat$Baseline_Pain_Group_2L, exact=FALSE)$p.value)
for (v in cat_vars) {
  x <- if (v == "Sex") dat[[v]] == "F" else dat[[v]]
  ps <- c(ps, categorical_p(table(x, dat$Baseline_Pain_Group_2L)))
}
adj <- p.adjust(ps, method="BH")

rows <- list(); k <- 1
cell_cont <- function(x) {x<-x[!is.na(x)]; sprintf("%.1f ± %.1f (%d)",mean(x),sd(x),length(x))}
cell_cat <- function(x,pos) {x<-x[!is.na(x)]; n<-sum(x==pos); sprintf("%d (%.1f)",n,100*n/length(x))}
for(i in seq_along(cont)){
 v<-cont[i]; rows[[length(rows)+1]]<-data.frame(Variable=cont_labels[i],Overall=cell_cont(dat[[v]]),Mild=cell_cont(dat[[v]][dat$Baseline_Pain_Group_2L==MILD]),Moderate_to_severe=cell_cont(dat[[v]][dat$Baseline_Pain_Group_2L==MODSEV]),P_value=fmt_p(ps[k]),FDR_adjusted_P_value=fmt_p(adj[k]),check.names=FALSE);k<-k+1
}
for(i in seq_along(cat_vars)){
 v<-cat_vars[i]; pos<-if(v=="Sex") "F" else 1; rows[[length(rows)+1]]<-data.frame(Variable=cat_labels[i],Overall=cell_cat(dat[[v]],pos),Mild=cell_cat(dat[[v]][dat$Baseline_Pain_Group_2L==MILD],pos),Moderate_to_severe=cell_cat(dat[[v]][dat$Baseline_Pain_Group_2L==MODSEV],pos),P_value=fmt_p(ps[k]),FDR_adjusted_P_value=fmt_p(adj[k]),check.names=FALSE);k<-k+1
}
tab <- bind_rows(data.frame(Variable="Patients, n",Overall=nrow(dat),Mild=sum(dat$Baseline_Pain_Group_2L==MILD),Moderate_to_severe=sum(dat$Baseline_Pain_Group_2L==MODSEV),P_value="",FDR_adjusted_P_value="",check.names=FALSE), bind_rows(rows))
write.csv(tab,file.path(output_dir(),"Table_1.csv"),row.names=FALSE,fileEncoding="UTF-8")
print(tab)
