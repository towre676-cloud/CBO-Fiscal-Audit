# CPS upper-tail calibration against IRS returns

This research replay fits two moments of the 2023 IRS geographic return distribution for AGI of at least $200,000. Both fitted methods exactly reproduce 13,370,480 returns and $6.681305473 trillion of AGI nationally. The finer IRS national tabulations expose large distributional errors under either method. The calibration therefore stays in the research replay. The policy scoring and incidence models do not consume it.

## Return construction and population differences

The replay reuses the existing Census household and tax-unit extraction. A reciprocal joint spouse pair with AGI carried on one record contributes a single principal return. Filing dependents can contribute a separate modeled single return despite sharing the principal tax unit identifier. The default weight is the principal record's ASEC person weight. The household-weight diagnostic assigns the household weight to each modeled return, so a household with multiple modeled returns contributes that weight multiple times. Both joint spouses had identical person weights in every accepted joint pair in both years. The original 2023 national JSON and 306-cell state CSV regenerate byte for byte with the shared extractor.

In the 2023 upper band the person-weighted CPS count is 15.875 million, 18.73% above the geographic IRS count from the exact archived figures. The corresponding $5.602 trillion of AGI is 16.15% low. Mean AGI is $352,904 versus $499,706. Modeled joint filers account for 13.318 million returns versus 10.899 million in IRS MARS2. That 2.420 million difference accounts arithmetically for roughly 97% of the net count excess. It does not identify which survey units the IRS would classify differently. Census modeling generally treats married spouses as filing jointly and does not separately model married-separate or surviving-spouse returns. The IRS geographic table provides single, joint and head-of-household counts. The receipt keeps the remainder, which includes categories outside these columns and rounding.

Dropping all separately modeled dependents reduces the upper band by about 5,972 returns and $3.66 billion of AGI. In the under-$25,000 band it removes 6.71 million modeled returns and worsens the existing count shortfall. Substituting household weights leaves an upper-band count excess of 18.47% and an AGI shortfall of 16.39%. The $100,000–$200,000 band also has roughly 2.97 million excess modeled returns, alongside a 10.38% AGI excess. Together the six bands show that near-agreement in total counts masks offsetting composition errors. A return-level match would be needed to separate actual filing, household reconstruction, and modeled AGI crossing a band boundary.

CPS represents interviewed survey households and uses modeled filing status and AGI. The Census methods paper describes income topcoding and imputations for tax components such as capital gains. The IRS geographic table represents processed returns subject to exclusions for negative AGI, unusable ZIP/state combinations and certain address types, including foreign and military postal addresses. It also applies disclosure protection and rounds counts to tens. The national SOI Table 1.2 is a separate sample-based return tabulation with finer bands and filing statuses. Its 2023 upper band has 13.535 million returns and $6.892 trillion in AGI, 1.23% and 3.16% above the geographic targets. The replay compares each series in its own published universe. The nominal dollar cutoffs are identical across the two income years.

Sources are the [2024 CPS ASEC release](https://www.census.gov/data/datasets/2024/demo/cps/cps-asec-2024.html), [Census tax model methods](https://www.census.gov/content/dam/Census/library/working-papers/2022/demo/sehsd-wp2022-18.pdf), [2023 IRS geographic data and disclosure guide](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2023-zip-code-data-soi), [2022 IRS geographic data](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2022-zip-code-data-soi), and [IRS SOI Table 1.2 by filing status](https://www.irs.gov/statistics/soi-tax-stats-individual-statistical-tables-by-filing-status).

## Methods and state residuals

Let $x_i$ be modeled AGI, $w_i$ the person weight, $L=200{,}000$, and $(N,A)$ the IRS count and total AGI. Each method is restricted to the existing CPS upper band.

- **Count-only control.** Multiply every weight by $N/\sum_i w_i$. Conditional mean AGI stays fixed, so the 2023 fitted AGI drops to $4.719 trillion, 29.38% below the benchmark.
- **Exponential tilt.** Keep each observed AGI and multiply its weight by $\exp(\alpha+\beta(x_i-L)/10^6)$. This is the minimum relative-entropy change to normalized CPS weights subject to the mean constraint. Bisection solves for the mean and the count determines the normalization. A nontrivial fit requires the IRS mean inside positive-weight CPS support. The national 2023 tilt reduces Kish effective sample size from 4,984 to 3,093.
- **Rank-preserving stretch.** Use the count-only weight factor and multiply each return's AGI above $L$ by $(A/N-L)/(\bar x-L)$, where $\bar x$ is the original CPS weighted mean. The 2023 multiplier is 1.960. This preserves rank and broad-band membership while changing AGI. It assigns no income components to the additional AGI.

The state table contains signed relative errors for the four national variants. State WAPE is the sum of absolute state errors divided by the sum of the IRS targets. It measures geographic disagreement after pooling. Kish effective sample size is a weight concentration diagnostic and ignores the survey design. These replays have no sampling confidence intervals.

| 2023 upper band | Returns, millions | AGI, trillions | State count WAPE | State AGI WAPE |
|---|---:|---:|---:|---:|
| IRS geographic target | 13.370 | $6.681 | | |
| Original CPS | 15.875 | $5.602 | 18.84% | 19.79% |
| Count only | 13.370 | $4.719 | 7.94% | 29.62% |
| National tilt | 13.370 | $6.681 | 7.48% | 18.10% |
| National stretch | 13.370 | $6.681 | 7.94% | 13.50% |

Both local methods also fit the two margins separately in all 51 jurisdictions in 2023. Those zero residuals are imposed. In Wyoming, the state tilt puts 88.6% of fitted return weight on one record, with a Kish effective sample size of 1.26 out of 67 sampled returns. Kentucky has the largest relative state AGI miss under both national joint fits, 122.3% for tilt and 70.7% for stretch in absolute value. The exact local fits provide a stress test for support and concentration. The state CSV retains both diagnostics.

## Validation outside the fitted targets

IRS national SOI Table 1.2 was reserved for comparison. The following figures are returns in millions. The JSON also includes AGI, modeled quantiles, results by filing status, and the IRS counts and amounts of itemized deductions.

| 2023 AGI | Original CPS | National tilt | National stretch | IRS national SOI |
|---|---:|---:|---:|---:|
| $200,000–<$500,000 | 13.7870 | 9.6387 | 9.5863 | 10.9558 |
| $500,000–<$1 million | 1.5061 | 1.8797 | 2.5867 | 1.7797 |
| $1 million–<$1.5 million | 0.5169 | 1.3394 | 0.5732 | 0.3689 |
| $1.5 million–<$2 million | 0.0385 | 0.2082 | 0.3621 | 0.1473 |
| $2 million–<$5 million | 0.0269 | 0.3044 | 0.2621 | 0.2032 |
| $5 million–<$10 million | 0 | 0 | 0 | 0.0493 |
| $10 million and above | 0 | 0 | 0 | 0.0304 |

The two fits put 1.852 million and 1.197 million returns at $1 million or above, compared with 799,095 in IRS SOI. For the joint/surviving-spouse comparison alone, the estimates are 1.217 million and 866,142, versus 668,365 in SOI. The higher million-dollar counts coexist with zero fitted returns at $5 million or above. SOI reports 79,644 returns and $1.244 trillion of AGI in those two highest bands. The national geographic versus SOI scope difference cannot explain the fitted support cutoff. In the CPS tail, the original weighted median is $275,101 and the fitted medians are $318,000 for tilt and $347,204 for stretch. At the 99th percentile these values are $1.252 million, $2.212 million and $2.262 million, respectively.

The replay also applies the **frozen 2023 parameters**, including the weight normalizations, to 2022 CPS returns. The 2022 IRS geographic and SOI inputs are used for evaluation only. This is a backward transfer diagnostic on one separate income year.

| 2022 upper band | National return error | National AGI error | State count WAPE | State AGI WAPE |
|---|---:|---:|---:|---:|
| Original CPS | +7.33% | −27.28% | 10.93% | 29.10% |
| Count only | −9.60% | −38.75% | 13.19% | 39.34% |
| Frozen tilt | −8.30% | −10.77% | 11.97% | 22.91% |
| Frozen stretch | −9.60% | −12.70% | 13.19% | 18.48% |

Against 804,830 million-dollar returns in 2022 national SOI, tilt produces 1.752 million and stretch 1.034 million. Both frozen methods improve AGI fit nationally and across states on average, while worsening count error. This transfer supplies evidence about stability of the corrections and no evidence about policy response.

## What the margins identify

Geographic counts and total AGI identify mean AGI in each band. National SOI additionally identifies grouped counts, AGI and itemized totals by filing status. Those controls leave the distribution within each finer band and the links to CPS households and income components open. For example, a $200,000 floor and the 2023 geographic moments alone allow anywhere from zero to at most about 5.01 million returns with $1 million or more of AGI. The upper bound divides aggregate excess AGI above the floor by the $800,000 required per million-dollar return. This is a bound from the two geographic moments alone. The much finer national SOI estimate comes from a different statistical universe.

- **§102 surtax.** The bill thresholds depend on filing status and MAGI, which requires tax-exempt interest and foreign earned-income add-backs. Even the finer national AGI table leaves $750,000 inside a published bin. It also leaves the joint distribution of the add-backs, AGI and status unresolved for applying the thresholds. Trusts and estates are a separate population.
- **§103 itemized deductions.** National SOI provides itemizer counts and totals by fine band and status. It leaves the assignment of deduction types, affected dollars and their interactions with the surtax unresolved.
- **§106 payroll.** Return AGI combines spouses and income sources. The high payroll band requires individual covered wages, self-employment earnings, and the split between workers and employers. An AGI adjustment supplies none of those quantities.

These are independently calibrated research models of two historical margins. Mechanical statutory calculations elsewhere in the repository have their own inputs and assumptions. An official score requires CBO/JCT evaluation of the legislative package. This replay supplies no revenue, savings or household incidence estimate.

## Reproduce

Use Python 3.11 or newer and install `xlrd==2.0.1` to read the two original IRS workbooks. Download the originals into a local scratch directory under the following names. The script checks each SHA-256 before parsing. All six hashes are also recorded in the generated JSON.

| Local name | Original |
|---|---|
| `cps24.zip` | [2024 CPS ASEC CSV](https://www2.census.gov/programs-surveys/cps/datasets/2024/march/asecpub24csv.zip) |
| `cps23.zip` | [2023 CPS ASEC CSV](https://www2.census.gov/programs-surveys/cps/datasets/2023/march/asecpub23csv.zip) |
| `irs23.csv` | [2023 IRS geographic returns](https://www.irs.gov/pub/irs-soi/23zpallagi.csv) |
| `irs22.csv` | [2022 IRS geographic returns](https://www.irs.gov/pub/irs-soi/22zpallagi.csv) |
| `soi23.xls` | [2023 IRS Table 1.2](https://www.irs.gov/pub/irs-soi/23in12ms.xls) |
| `soi22.xls` | [2022 IRS Table 1.2](https://www.irs.gov/pub/irs-soi/22in12ms.xls) |

```sh
python scripts/calibrate_high_income.py /path/to/originals \
  --state-output /tmp/cps_irs_high_income_states.csv > /tmp/cps_irs_high_income.json
python -m unittest discover -s publication/tests -p 'test_high_income_calibration.py' -v
```

Compare with the [national receipt](../publication/results/cps_irs_high_income.json) and [state CSV](../publication/results/cps_irs_high_income_states.csv). Numerical regressions use tolerances for fitted moments. The original [uncalibrated national results](../publication/results/cps_irs_2023_calibration.json) and [306 state cells](../publication/results/cps_irs_2023_state_margins.csv) are separately retained.
