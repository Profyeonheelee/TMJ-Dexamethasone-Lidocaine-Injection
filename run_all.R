# Run all R analyses.

args <- commandArgs(trailingOnly = TRUE)
script_arg <- commandArgs(trailingOnly = FALSE)
file_arg <- sub("^--file=", "", script_arg[grepl("^--file=", script_arg)])
here <- if (length(file_arg)) dirname(normalizePath(file_arg[1])) else getwd()
data_arg <- if (length(args)) args[1] else ""

scripts <- c(
  "Table_1.R",
  "Table_2.R",
  "Table_3.R",
  "Table_4.R",
  "Figure_1.R",
  "Figure_2.R",
  "Supplementary_Table_S1.R",
  "Supplementary_Table_S2.R",
  "Supplementary_Table_S3.R",
  "Supplementary_Table_S4.R",
  "Supplementary_Table_S5.R",
  "Supplementary_Table_S6.R",
  "Supplementary_Figure_S1.R",
  "Supplementary_Figure_S2.R",
  "Supplementary_Figure_S3.R"
)

for (script in scripts) {
  cat("\n===", script, "===\n")
  cmd <- c(file.path(here, script), if (nzchar(data_arg)) data_arg)
  status <- system2("Rscript", cmd)
  if (status != 0) stop(paste("Failed:", script))
}
