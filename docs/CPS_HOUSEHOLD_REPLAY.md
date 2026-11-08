# 2026 CPS ASEC household-income replay

The Census 2026 ASEC measures calendar-year 2025 income. This replay uses the [original Census CSV archive](https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html) and compares the public-use results with the all-households row in [Census P60-289 Table 1](https://www2.census.gov/programs-surveys/demo/tables/p60/289/table1.xlsx).

| Quantity | Public-use replay | Census Table 1 |
|---|---:|---:|
| Weighted households | 137,056,386.24 | 137.1 million, rounded |
| 2025 median household money income | $87,439.85 | $87,460 |
| 90% sampling margin for the median | $1,022.33 | $1,040 |

The public-use median is $20.15 below the published estimate, a difference of 0.023%. The sampling margin is $17.67 lower. These are observed deviations between the replay and the published table. The confidence margin describes sampling uncertainty for the public-use calculation.

The household file contains 88,026 records, including 53,344 interviews. The code excludes 23 group-quarter interviews using the Census `HRHTYPE` categories 9 and 10. Each of the remaining 53,321 household keys joins to exactly one reference person and one replicate row. The reference-person weight matches the household weight, and the replicate file's full-sample weight matches within the combined rounding precision. The replay interpolates the median in $2,500 bins and repeats the calculation for each of the 160 replicate weights. It uses the Census variance factor of 4/160 and a 1.645 multiplier for the 90% margin.

The [replay receipt](../publication/results/cps_asec_2026_household_income_replay.json) includes the observed archive SHA-256. The [Census technical documentation](https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar26.pdf) and [2026 replicate-weight instructions](https://www2.census.gov/programs-surveys/cps/datasets/2026/march/2026_ASEC_Replicate_Weight_Usage_Instructions.docx) define the record types and weight joins. The archive remains with the source agency.

This benchmark establishes one weighted household income moment. The §101 credit uses tax households and current-year MAGI. Estimating its distribution requires a validated household-to-tax-unit crosswalk, appropriate income components and filing status, and a separate consumption model for the VAT burden.
