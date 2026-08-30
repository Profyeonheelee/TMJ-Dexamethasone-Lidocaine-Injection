DATA_FILENAME <- "Dexamethasone_Final_Analytic_Dataset_191.xlsx"
MILD <- "Mild pain (VAS 0–3)"
MODSEV <- "Moderate-to-severe pain (VAS ≥4)"
THREE_LEVELS <- c("Mild pain (VAS 0–3)", "Moderate pain (VAS 4–6)", "Severe pain (VAS ≥7)")
CHANGE_LEVELS <- c("Decreased", "Maintained", "Increased")

project_root <- function() {
  normalizePath(file.path(dirname(sys.frame(1)$ofile %||% getwd()), ".."), mustWork = FALSE)
}
`%||%` <- function(x, y) if (is.null(x)) y else x

resolve_data_path <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) >= 1 && file.exists(args[1])) return(normalizePath(args[1]))
  env <- Sys.getenv("TMJ_DATA", unset = "")
  if (nzchar(env) && file.exists(env)) return(normalizePath(env))

  script_arg <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", script_arg[grepl("^--file=", script_arg)])
  script_dir <- if (length(file_arg)) dirname(normalizePath(file_arg[1])) else getwd()
  root <- normalizePath(file.path(script_dir, ".."), mustWork = FALSE)
  candidates <- c(
    file.path(root, "data", DATA_FILENAME),
    file.path(getwd(), DATA_FILENAME),
    file.path(getwd(), "data", DATA_FILENAME)
  )
  hit <- candidates[file.exists(candidates)]
  if (!length(hit)) stop("Data file not found. Pass the xlsx path as the first argument or set TMJ_DATA.")
  normalizePath(hit[1])
}

output_dir <- function() {
  script_arg <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", script_arg[grepl("^--file=", script_arg)])
  script_dir <- if (length(file_arg)) dirname(normalizePath(file_arg[1])) else getwd()
  out <- file.path(normalizePath(file.path(script_dir, ".."), mustWork = FALSE), "outputs", "R")
  dir.create(out, recursive = TRUE, showWarnings = FALSE)
  out
}

fmt_p <- function(p) {
  if (is.na(p)) return("NA")
  if (p < 0.001) "<0.001" else sprintf("%.3f", p)
}

mean_sd_n <- function(x, digits = 2, sign = FALSE) {
  x <- x[!is.na(x)]
  if (!length(x)) return("NA")
  m <- mean(x); s <- sd(x)
  prefix <- if (sign && m > 0) "+" else ""
  sprintf(paste0("%s%.", digits, "f ± %.", digits, "f (%d)"), prefix, m, s, length(x))
}

n_pct <- function(x) {
  x <- x[!is.na(x)]
  if (!length(x)) return("NA")
  n <- sum(as.numeric(x) == 1)
  sprintf("%d (%.1f)", n, 100*n/length(x))
}

categorical_p <- function(tab) {
  tab <- as.matrix(tab)
  tab <- tab[rowSums(tab) > 0, colSums(tab) > 0, drop = FALSE]
  if (nrow(tab) < 2 || ncol(tab) < 2) return(NA_real_)
  chi <- suppressWarnings(chisq.test(tab, correct = FALSE))
  if (all(dim(tab) == c(2,2)) && any(chi$expected < 5)) fisher.test(tab)$p.value else chi$p.value
}
