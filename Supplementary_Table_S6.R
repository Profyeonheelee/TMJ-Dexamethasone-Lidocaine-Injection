# Supplementary Table S6. Repeat-injection comparison.

suppressPackageStartupMessages({
  library(readxl)
  library(dplyr)
})

source(file.path(
  dirname(sub("^--file=", "", commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))][1])),
  "_common.R"
))

dat <- read_excel(resolve_data_path(), sheet = "Visit_Long_191")

repeat_status <- dat %>%
  group_by(Study_ID) %>%
  summarise(
    Repeat_Injection = any(
      Visit_Type == "Injection day" & Cycle >= 2,
      na.rm = TRUE
    ),
    .groups = "drop"
  ) %>%
  mutate(
    Repeat_Group = ifelse(
      Repeat_Injection,
      "Repeat injection",
      "No repeat injection"
    ),
    Repeat_Group = factor(
      Repeat_Group,
      levels = c("No repeat injection", "Repeat injection")
    )
  )

baseline <- dat %>%
  filter(Visit_Order == 0) %>%
  arrange(Study_ID) %>%
  distinct(Study_ID, .keep_all = TRUE) %>%
  transmute(
    Study_ID,
    Sex,
    Age,
    Baseline_VAS = VAS,
    Baseline_CMO = CMO,
    Baseline_MMO = MMO,
    Baseline_Pain_Burden = Pain_Location_Burden_0_6
  )

first_fu <- dat %>%
  filter(Visit_Order == 1) %>%
  arrange(Study_ID) %>%
  distinct(Study_ID, .keep_all = TRUE) %>%
  transmute(
    Study_ID,
    FirstFU_Days = Days_From_Baseline,
    FirstFU_VAS = VAS,
    FirstFU_CMO = CMO,
    FirstFU_MMO = MMO,
    FirstFU_Pain_Burden = Pain_Location_Burden_0_6
  )

pt <- baseline %>%
  left_join(first_fu, by = "Study_ID") %>%
  left_join(repeat_status, by = "Study_ID") %>%
  mutate(
    Delta_VAS = FirstFU_VAS - Baseline_VAS,
    Delta_CMO = FirstFU_CMO - Baseline_CMO,
    Delta_MMO = FirstFU_MMO - Baseline_MMO,
    Delta_Pain_Burden = FirstFU_Pain_Burden - Baseline_Pain_Burden,
    Female = Sex == "F"
  )

qc <- pt %>%
  summarise(
    Patients = n(),
    No_repeat_injection = sum(!Repeat_Injection, na.rm = TRUE),
    Repeat_injection = sum(Repeat_Injection, na.rm = TRUE),
    Missing_first_followup = sum(is.na(FirstFU_Days))
  )

write.csv(
  qc,
  file.path(output_dir(), "Supplementary_Table_S6_QC.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)

mean_sd_n <- function(x) {
  x <- x[!is.na(x)]
  if (!length(x)) return("NA")
  sprintf("%.2f ± %.2f (%d)", mean(x), sd(x), length(x))
}

n_pct <- function(x) {
  x <- x[!is.na(x)]
  if (!length(x)) return("NA")
  sprintf("%d (%.1f%%)", sum(x), 100 * mean(x))
}

wilcox_p <- function(var) {
  keep <- !is.na(pt[[var]]) & !is.na(pt$Repeat_Group)
  suppressWarnings(
    wilcox.test(pt[[var]][keep] ~ pt$Repeat_Group[keep], exact = FALSE)$p.value
  )
}

categorical_p_s6 <- function(var) {
  tab <- table(pt[[var]], pt$Repeat_Group, useNA = "no")
  chi <- suppressWarnings(chisq.test(tab))
  if (any(chi$expected < 5)) fisher.test(tab)$p.value else chi$p.value
}

variables <- c(
  Age = "Age, years",
  FirstFU_Days = "Time to first follow-up, days",
  Baseline_VAS = "Baseline VAS",
  FirstFU_VAS = "First-follow-up VAS",
  Delta_VAS = "ΔVAS, first follow-up − baseline",
  Baseline_Pain_Burden = "Baseline pain-location burden",
  FirstFU_Pain_Burden = "First-follow-up pain-location burden",
  Delta_Pain_Burden = "ΔPain-location burden",
  Baseline_CMO = "Baseline CMO, mm",
  FirstFU_CMO = "First-follow-up CMO, mm",
  Delta_CMO = "ΔCMO, mm",
  Baseline_MMO = "Baseline MMO, mm",
  FirstFU_MMO = "First-follow-up MMO, mm",
  Delta_MMO = "ΔMMO, mm"
)

groups <- levels(pt$Repeat_Group)

continuous_rows <- lapply(names(variables), function(var) {
  data.frame(
    Variable = unname(variables[var]),
    `No repeat injection` = mean_sd_n(pt[[var]][pt$Repeat_Group == groups[1]]),
    `Repeat injection` = mean_sd_n(pt[[var]][pt$Repeat_Group == groups[2]]),
    `P value` = fmt_p(wilcox_p(var)),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
}) %>% bind_rows()

female_row <- data.frame(
  Variable = "Female, n (%)",
  `No repeat injection` = n_pct(pt$Female[pt$Repeat_Group == groups[1]]),
  `Repeat injection` = n_pct(pt$Female[pt$Repeat_Group == groups[2]]),
  `P value` = fmt_p(categorical_p_s6("Female")),
  check.names = FALSE,
  stringsAsFactors = FALSE
)

patient_row <- data.frame(
  Variable = "Patients, n",
  `No repeat injection` = as.character(sum(pt$Repeat_Group == groups[1], na.rm = TRUE)),
  `Repeat injection` = as.character(sum(pt$Repeat_Group == groups[2], na.rm = TRUE)),
  `P value` = "",
  check.names = FALSE,
  stringsAsFactors = FALSE
)

order <- c(
  "Age, years",
  "Time to first follow-up, days",
  "Baseline VAS",
  "First-follow-up VAS",
  "ΔVAS, first follow-up − baseline",
  "Baseline pain-location burden",
  "First-follow-up pain-location burden",
  "ΔPain-location burden",
  "Baseline CMO, mm",
  "First-follow-up CMO, mm",
  "ΔCMO, mm",
  "Baseline MMO, mm",
  "First-follow-up MMO, mm",
  "ΔMMO, mm"
)

get_row <- function(label) continuous_rows %>% filter(Variable == label)

table_s6 <- bind_rows(
  patient_row,
  get_row("Age, years"),
  female_row,
  get_row("Time to first follow-up, days"),
  lapply(order[3:length(order)], get_row) %>% bind_rows()
)

write.csv(
  table_s6,
  file.path(output_dir(), "Supplementary_Table_S6.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)

print(qc)
print(table_s6)
