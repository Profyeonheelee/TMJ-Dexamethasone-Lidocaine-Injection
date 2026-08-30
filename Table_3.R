# Table 3. Longitudinal mixed-effects models.

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
  library(lme4)
})

source(file.path(
  dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])),
  "_common.R"
))

dat <- read_excel(resolve_data_path(), sheet = "Visit_Long_191") %>%
  filter(Visit_Order <= 7) %>%
  mutate(
    Study_ID = factor(Study_ID),
    Visit_Type = factor(Visit_Type, levels = c("Injection day", "Follow-up")),
    Baseline_Pain_Group_2L = factor(Baseline_Pain_Group_2L, levels = c(MILD, MODSEV)),
    Time_30d = Days_From_Baseline / 30
  )

# One record per patient-day for the elapsed-time model.
same_day_qc <- dat %>%
  count(Study_ID, Days_From_Baseline, name = "n_records") %>%
  filter(n_records > 1)

write.csv(
  same_day_qc,
  file.path(output_dir(), "Table_3_same_day_QC.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)

dat_time <- dat %>%
  arrange(Study_ID, Days_From_Baseline, Visit_Order) %>%
  group_by(Study_ID, Days_From_Baseline) %>%
  slice(1) %>%
  ungroup()

outcomes <- c("VAS", "CMO", "MMO", "Pain_Location_Burden_0_6")
labels <- c(
  VAS = "VAS",
  CMO = "CMO, mm",
  MMO = "MMO, mm",
  Pain_Location_Burden_0_6 = "Pain-location burden score"
)

fit_elapsed <- function(outcome) {
  fit <- lmer(
    as.formula(paste0(
      outcome,
      " ~ Time_30d + Baseline_Pain_Group_2L + (1 | Study_ID)"
    )),
    data = dat_time,
    REML = TRUE,
    na.action = na.omit
  )

  co <- summary(fit)$coefficients
  beta <- co["Time_30d", "Estimate"]
  se <- co["Time_30d", "Std. Error"]
  mf <- model.frame(fit)

  data.frame(
    Outcome = outcome,
    Observations = nobs(fit),
    Patients = n_distinct(mf$Study_ID),
    Beta = beta,
    CI_low = beta - 1.96 * se,
    CI_high = beta + 1.96 * se,
    P = 2 * pnorm(abs(beta / se), lower.tail = FALSE),
    Singular = isSingular(fit, tol = 1e-4),
    stringsAsFactors = FALSE
  )
}

fit_visit <- function(outcome) {
  fit <- lmer(
    as.formula(paste0(
      outcome,
      " ~ Visit_Type + Cycle + Baseline_Pain_Group_2L + (1 | Study_ID)"
    )),
    data = dat,
    REML = TRUE,
    na.action = na.omit
  )

  co <- summary(fit)$coefficients
  term <- "Visit_TypeFollow-up"
  beta <- co[term, "Estimate"]
  se <- co[term, "Std. Error"]
  mf <- model.frame(fit)

  data.frame(
    Outcome = outcome,
    Observations = nobs(fit),
    Patients = n_distinct(mf$Study_ID),
    Beta = beta,
    CI_low = beta - 1.96 * se,
    CI_high = beta + 1.96 * se,
    P = 2 * pnorm(abs(beta / se), lower.tail = FALSE),
    Singular = isSingular(fit, tol = 1e-4),
    stringsAsFactors = FALSE
  )
}

elapsed <- bind_rows(lapply(outcomes, fit_elapsed)) %>%
  mutate(FDR = p.adjust(P, method = "BH"))

visit <- bind_rows(lapply(outcomes, fit_visit)) %>%
  mutate(FDR = p.adjust(P, method = "BH"))

numeric_table <- left_join(
  elapsed,
  visit,
  by = "Outcome",
  suffix = c("_Time", "_Visit")
)

numeric_table$Outcome <- unname(labels[numeric_table$Outcome])

fmt_ci <- function(beta, low, high) {
  sprintf("%.3f (%.3f to %.3f)", beta, low, high)
}

table3 <- numeric_table %>%
  transmute(
    Outcome,
    `Elapsed-time observations, n` = Observations_Time,
    `Patients, n` = Patients_Time,
    `Per 30-day increase, β (95% CI)` = fmt_ci(Beta_Time, CI_low_Time, CI_high_Time),
    `P value` = sapply(P_Time, fmt_p),
    `FDR-adjusted P value` = sapply(FDR_Time, fmt_p),
    `Visit-type observations, n` = Observations_Visit,
    `Visit-type patients, n` = Patients_Visit,
    `Follow-up vs injection-day, β (95% CI)` = fmt_ci(Beta_Visit, CI_low_Visit, CI_high_Visit),
    `Visit-type P value` = sapply(P_Visit, fmt_p),
    `Visit-type FDR-adjusted P value` = sapply(FDR_Visit, fmt_p)
  )

write.csv(
  numeric_table,
  file.path(output_dir(), "Table_3_numeric_R.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
write.csv(
  table3,
  file.path(output_dir(), "Table_3.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)

print(table3)
