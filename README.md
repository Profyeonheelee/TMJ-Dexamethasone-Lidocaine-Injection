# TMJ-Dexamethasone-Lidocaine-Injection
Analysis code for a retrospective cohort study of longitudinal pain and functional outcomes after intra-articular dexamethasone–lidocaine injection in patients with TMJ arthralgia.
# TMJ Dexamethasone–Lidocaine Injection

Analysis code for the study **Longitudinal Clinical Outcomes After Intra-Articular Dexamethasone–Lidocaine Injection for Temporomandibular Joint Arthralgia**.

The repository contains parallel R and Python scripts for the main and supplementary analyses. The analytic dataset is not included because it contains clinical data subject to institutional and ethical restrictions.

## Data

The scripts use:

`Dexamethasone_Final_Analytic_Dataset_191.xlsx`

The workbook path can be supplied as the first command-line argument, set with the `TMJ_DATA` environment variable, or placed in the `data/` directory.

```bash
python Python/Table_1.py "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
Rscript R/Table_1.R "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

## Main manuscript

| File | Analysis |
| --- | --- |
| `Table_1` | Baseline characteristics according to baseline pain severity |
| `Table_2` | Baseline-to-first-follow-up paired changes |
| `Table_3` | Longitudinal mixed-effects models |
| `Table_4` | Final outcomes and direction of change |
| `Figure_1` | Overall longitudinal clinical trajectories |
| `Figure_2` | Longitudinal trajectories by three-level baseline pain severity |

## Supplementary material

| File | Analysis |
| --- | --- |
| `Supplementary_Table_S1` | Visit-wise longitudinal summary |
| `Supplementary_Table_S2` | Visit-wise outcomes by three-level baseline pain severity |
| `Supplementary_Table_S3` | Outcomes according to final VAS change category |
| `Supplementary_Table_S4` | Site-specific pain transitions |
| `Supplementary_Table_S5` | Early pain-presence and direction-of-change analyses |
| `Supplementary_Table_S6` | Baseline and early follow-up characteristics by repeat-injection status |
| `Supplementary_Figure_S1` | Early direction-of-change categories |
| `Supplementary_Figure_S2` | Visit-to-visit correlation networks |
| `Supplementary_Figure_S3` | Correlation structure of pain, mouth opening, and pain-location variables |

## Python

```bash
pip install -r Python/requirements.txt
python Python/run_all.py "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

## R

Install the packages listed in `R/R_packages.txt`, then run:

```bash
Rscript R/run_all.R "C:/path/to/Dexamethasone_Final_Analytic_Dataset_191.xlsx"
```

Output files are written to `outputs/python/` and `outputs/R/`.

## Analysis notes

Missing outcome values are not imputed. Paired analyses use patients with the required baseline and follow-up measurements, and longitudinal analyses use available outcome-specific observations.

For Table 3, the manuscript estimates were obtained with `lme4::lmer()` in R. The elapsed-time model uses actual days from baseline expressed per 30 days, with one observation per patient-day and adjustment for baseline pain severity. The visit-type model adjusts for treatment cycle and baseline pain severity. The Python script uses `statsmodels` with the same fixed- and random-effect structure; small numerical differences in mixed-model standard errors, confidence intervals, or P values may occur between software implementations.

The group-by-visit interaction tests in Figure 2 were obtained with `geepack` in R. The Python version uses the corresponding GEE structure in `statsmodels`.
