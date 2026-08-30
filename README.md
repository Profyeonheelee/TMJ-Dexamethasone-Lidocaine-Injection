# TMJ Dexamethasone–Lidocaine Injection

[svg](https://github.com/Profyeonheelee/TMJ-Dexamethasone-Lidocaine-Injection/tree/main#tmj-dexamethasonelidocaine-injection)

Analysis code for the study **Longitudinal Clinical Outcomes After Intra-Articular Dexamethasone–Lidocaine Injection for Temporomandibular Joint Arthralgia**.

The repository contains parallel R and Python scripts for the main and supplementary analyses. The analytic dataset is not included because it contains clinical data subject to institutional and ethical restrictions. Analyses are provided in both R and Python where applicable. **The R implementation was used for the primary mixed-effects models reported in the manuscript.**

## Data

The scripts use:

`Dexamethasone_Final_Analytic_Dataset_191.xlsx`

The workbook path can be supplied as the first command-line argument, set with the `TMJ_DATA` environment variable, or placed in the `data/` directory.

```bash
python Table_1.py "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
Rscript Table_1.R "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

## Main manuscript

| File | Analysis |
| --- | --- |
| `Table_1.R` / `Table_1.py` | Baseline characteristics according to baseline pain severity |
| `Table_2.R` / `Table_2.py` | Baseline-to-first-follow-up paired changes |
| `Table_3.R` / `Table_3.py` | Longitudinal mixed-effects models |
| `Table_4.R` / `Table_4.py` | Final outcomes and direction of change |
| `Figure_1.R` / `Figure_1.py` | Overall longitudinal clinical trajectories |
| `Figure_2.R` / `Figure_2.py` | Longitudinal trajectories by three-level baseline pain severity |

## Supplementary material

| File | Analysis |
| --- | --- |
| `Supplementary_Table_S1.R` / `Supplementary_Table_S1.py` | Visit-wise longitudinal summary |
| `Supplementary_Table_S2.R` / `Supplementary_Table_S2.py` | Visit-wise outcomes by three-level baseline pain severity |
| `Supplementary_Table_S3.R` / `Supplementary_Table_S3.py` | Outcomes according to final VAS change category |
| `Supplementary_Table_S4.R` / `Supplementary_Table_S4.py` | Site-specific pain transitions |
| `Supplementary_Table_S5.R` / `Supplementary_Table_S5.py` | Early pain-presence and direction-of-change analyses |
| `Supplementary_Table_S6.R` / `Supplementary_Table_S6.py` | Baseline and early follow-up characteristics by repeat-injection status |
| `Supplementary_Figure_S1.R` / `Supplementary_Figure_S1.py` | Early direction-of-change categories |
| `Supplementary_Figure_S2.R` / `Supplementary_Figure_S2.py` | Visit-to-visit correlation networks |
| `Supplementary_Figure_S3.R` / `Supplementary_Figure_S3.py` | Correlation structure of pain, mouth opening, and pain-location variables |

## Python

The Python scripts are stored directly in the repository root.

Main packages used include `pandas`, `NumPy`, `SciPy`, `statsmodels`, `matplotlib`, and `NetworkX`.

Run an individual analysis from the repository directory, for example:

```bash
python Table_1.py "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

## R

The R scripts are also stored directly in the repository root.

Main packages used include `readxl`, `dplyr`, `lme4`, and `geepack`.

Run an individual analysis from the repository directory, for example:

```bash
Rscript Table_1.R "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

## Analysis notes

Missing outcome values are not imputed. Paired analyses use patients with the required baseline and follow-up measurements, and longitudinal analyses use available outcome-specific observations.

For Table 3, the manuscript estimates were obtained with `lme4::lmer()` in R. The elapsed-time model uses actual days from baseline expressed per 30 days, with one observation per patient-day and adjustment for baseline pain severity. The visit-type model adjusts for treatment cycle and baseline pain severity. The Python script uses `statsmodels` with the same fixed- and random-effect structure; small numerical differences in mixed-model standard errors, confidence intervals, or P values may occur between software implementations.

The group-by-visit interaction tests in Figure 2 were obtained with `geepack` in R. The Python version uses the corresponding GEE structure in `statsmodels`.
