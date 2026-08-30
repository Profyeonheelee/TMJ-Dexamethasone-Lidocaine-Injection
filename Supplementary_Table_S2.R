suppressPackageStartupMessages({library(readxl);library(dplyr)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat<-read_excel(resolve_data_path(),sheet="Visit_Long_191")%>%filter(Visit_Order<=7)
vl<-c("Baseline / 1st injection day","1st follow-up after 1st injection","2nd injection day","2nd follow-up","3rd injection day","3rd follow-up","4th injection day","4th follow-up")
outs<-c(VAS="VAS",CMO="CMO, mm",MMO="MMO, mm",Pain_Location_Burden_0_6="Pain-location burden score")
cell<-function(x){x<-x[!is.na(x)];if(!length(x))return("NA");if(length(x)==1)return(sprintf("%.2f (1)",x));sprintf("%.2f ± %.2f (%d)",mean(x),sd(x),length(x))}
rows<-list();for(y in names(outs)){for(v in 0:7){r<-data.frame(Outcome=outs[y],Visit=vl[v+1],check.names=FALSE);for(g in THREE_LEVELS)r[[g]]<-cell(dat[[y]][dat$Visit_Order==v & dat$Baseline_Pain_Group_3L==g]);rows[[length(rows)+1]]<-r}}
tab<-bind_rows(rows);write.csv(tab,file.path(output_dir(),"Supplementary_Table_S2.csv"),row.names=FALSE,fileEncoding="UTF-8");print(tab)
