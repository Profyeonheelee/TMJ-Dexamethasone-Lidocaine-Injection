suppressPackageStartupMessages({library(readxl);library(dplyr)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat<-read_excel(resolve_data_path(),sheet="Visit_Long_191")%>%filter(Visit_Order<=7)
vl<-c("Baseline / 1st injection","1st follow-up","2nd injection","2nd follow-up","3rd injection","3rd follow-up","4th injection","4th follow-up")
cell<-function(x){x<-x[!is.na(x)];if(!length(x))"NA" else sprintf("%.2f ± %.2f (%d)",mean(x),sd(x),length(x))}
rows<-lapply(0:7,function(v){z<-dat%>%filter(Visit_Order==v);pp<-z$Pain_Present[!is.na(z$Pain_Present)];data.frame(Visit=vl[v+1],Total_n=nrow(z),Mean_days_from_baseline=sprintf("%.1f ± %.1f",mean(z$Days_From_Baseline),sd(z$Days_From_Baseline)),VAS=cell(z$VAS),CMO_mm=cell(z$CMO),MMO_mm=cell(z$MMO),Pain_present_n_pct=sprintf("%d (%.1f)",sum(pp==1),100*mean(pp==1)),Pain_location_burden_score=cell(z$Pain_Location_Burden_0_6),check.names=FALSE)})
tab<-bind_rows(rows);write.csv(tab,file.path(output_dir(),"Supplementary_Table_S1.csv"),row.names=FALSE,fileEncoding="UTF-8");print(tab)
