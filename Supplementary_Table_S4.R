suppressPackageStartupMessages({library(readxl);library(dplyr)})
source(file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])), "_common.R"))
dat<-read_excel(resolve_data_path(),sheet="Pain_Site_Transitions")
sites<-c("Rt. Masseter","Rt. Temporalis","Rt. TMJ","Lt. Masseter","Lt. Temporalis","Lt. TMJ");trs<-c("Resolved (1→0)","Persistent (1→1)","Newly developed (0→1)","Absent throughout (0→0)")
rows<-list();for(s in sites){for(g in CHANGE_LEVELS){z<-dat%>%filter(Pain_Site==s,VAS_Response_Final==g);r<-data.frame(Pain_site=s,Final_VAS_change=g,n=n_distinct(z$Study_ID),check.names=FALSE);for(tr in trs){n<-sum(z$Transition==tr);r[[tr]]<-sprintf("%d (%.1f)",n,100*n/nrow(z))};rows[[length(rows)+1]]<-r}}
tab<-bind_rows(rows);write.csv(tab,file.path(output_dir(),"Supplementary_Table_S4.csv"),row.names=FALSE,fileEncoding="UTF-8");print(tab)
