DATA_FILE <- "Dexamethasone_Final_Analytic_Dataset_191.xlsx"

MILD <- "Mild pain (VAS 0–3)"
MODSEV <- "Moderate-to-severe pain (VAS ≥4)"
THREE_LEVELS <- c(
  "Mild pain (VAS 0–3)",
  "Moderate pain (VAS 4–6)",
  "Severe pain (VAS ≥7)"
)
CHANGE_LEVELS <- c("Decreased", "Maintained", "Increased")

project_root <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- args[grepl("^--file=", args)]

  if (length(file_arg)) {
    script_path <- sub("^--file=", "", file_arg[1])
    return(dirname(normalizePath(script_path, mustWork = FALSE)))
  }

  normalizePath(getwd(), mustWork = FALSE)
}

resolve_data_path <- function() {
  candidates <- character(0)

  trailing <- commandArgs(trailingOnly = TRUE)
  if (length(trailing) && nzchar(trailing[1])) {
    candidates <- c(candidates, path.expand(trailing[1]))
  }

  env_path <- Sys.getenv("TMJ_DATA", unset = "")
  if (nzchar(env_path)) {
    candidates <- c(candidates, path.expand(env_path))
  }

  root <- project_root()
  candidates <- c(
    candidates,
    file.path(root, "data", DATA_FILE),
    file.path(root, DATA_FILE)
  )

  for (path in candidates) {
    if (file.exists(path)) {
      return(normalizePath(path, mustWork = TRUE))
    }
  }

  stop(
    paste0(
      "Could not locate ", DATA_FILE, ".\nChecked:\n  - ",
      paste(candidates, collapse = "\n  - "),
      "\nSupply the workbook path as the first command-line argument, ",
      "set TMJ_DATA, or place the workbook in the data/ directory."
    ),
    call. = FALSE
  )
}

output_dir <- function() {
  out <- file.path(project_root(), "outputs", "R")
  dir.create(out, recursive = TRUE, showWarnings = FALSE)
  out
}

fmt_p <- function(p) {
  if (length(p) == 0 || is.na(p)) return("NA")
  if (p < 0.001) return("<0.001")
  sprintf("%.3f", p)
}

categorical_p <- function(tab) {
  tab <- as.matrix(tab)

  if (length(dim(tab)) != 2 || any(dim(tab) < 2)) {
    return(NA_real_)
  }

  chi <- suppressWarnings(chisq.test(tab, correct = FALSE))

  if (all(dim(tab) == c(2, 2)) && any(chi$expected < 5)) {
    return(fisher.test(tab)$p.value)
  }

  chi$p.value
}
