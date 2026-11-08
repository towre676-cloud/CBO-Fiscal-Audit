# Evidence register and claims admission

**Citation vintage:** November 7, 2026. **Research owner:** FiscalRazor, not any named public agency. **Purpose:** make the evidence boundary explicit for each publishable claim. A passed unit test is software evidence, not an official estimate or source-independent empirical validation.

| ID | Claim / topic | Evidence source | Observed scope | Admission |
|---|---|---|---|---|
| CBO-01 | FY2026–2036 budget annual receipts, spending, deficit, primary deficit, interest, debt and other financing | [CBO 2026 outlook](https://www.cbo.gov/publication/61882), [Git source](https://github.com/US-CBO/cbo-data/blob/main/data/budget/ten_year_budget/annual_fy_2026-02.csv) | 11 years, selected 21-variable excerpt in `fiscalrazor/data/verified_tables/` | **ORIGINALS_REPLAYED**; verified input cells, 11-year account bridge, and [receipt](CBO_SOURCE_REPLAY.md) |
| CBO-02 | FY2026–2036 direct fiscal-year nominal GDP | [CBO historical economic annual FY](https://github.com/US-CBO/cbo-data/blob/main/data/economic/historical_economic/annual_fy_2026-02.csv) | 11 observed fiscal-year values using direct GDP | **ORIGINALS_REPLAYED** |
| CBO-03 | FY2027–2036 nominal PCE | Same CBO FY economic source | 10 observed annual rows pinned to upstream Git SHA | **ORIGINALS_REPLAYED**; aggregate PCE only |
| MATH-01 | FY2036 annual-deficit gap $1,714.022728075B | CBO-01 & CBO-02; `publication/fiscal_accounting.py` | Exact arithmetic, fixed baseline | **REPRODUCIBLE_ALGEBRA** |
| MATH-02 | FY2036 one-year debt-ratio stability gap $1,042.80050812B | CBO-01 & CBO-02 | One-year counterfactual; FY2035 debt and GDP held fixed | **REPRODUCIBLE_ALGEBRA**; not long-run solvency |
| MATH-03 | FY2036 all-PCE 5% VAT illustration: $1,599.482B gross | CBO-03 | Assumes 100% of all CBO PCE taxed at 5% and fixed base | **STYLIZED_MECHANICAL**; neither legislative score nor legal base |
| SSA-01 | OASI Q4 2032; DI fund remains positive over 75 years; hypothetical combined OASDI Q3 2034 | [SSA 2026 Trustees](https://www.ssa.gov/oact/TR/2026/), [summary](https://www.ssa.gov/oact/trsum/) | Separate fund baselines | **OFFICIAL_BASELINE**; no joint reform score |
| SSA-02 | OASDI 75-year actuarial balance -4.42% of capped payroll | [SSA trustees' summary](https://www.ssa.gov/oact/TRSUM/) | Intermediate-case long-range projection | **OFFICIAL_BASELINE**, not 10-year annual cash |
| CMS-01 | HI Q2 2033 exhaustion and HI actuarial balance -0.56% of uncapped payroll | [Medicare trustees' report](https://www.cms.gov/oact/tr/2026), [trustees' summary](https://www.ssa.gov/oact/trsum/) | HI, separate from SMI B/D | **OFFICIAL_BASELINE**; not a modeled bill |
| JCT-01 | 21→22% corporate-rate educational estimate | [JCT March 31, 2026 methodology](https://www.jct.gov/publications/2026/revenue-estimating-process-and-microeconomic-research-2026/) | **Teaching illustration**, 350B gross, 180B after adjustments | **METHODOLOGY_EXAMPLE**; not a bill score |
| SURVEY-01 | Census 2026 CPS ASEC has replicate weights and sample records | [Census CPS ASEC 2026](https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html) | 53,321 in-universe public-use households with all 160 replicates and a benchmark comparison | **HOUSEHOLD_BASELINE_REPLAYED**; [calibration receipt](CPS_HOUSEHOLD_REPLAY.md) |
| SURVEY-02 | BLS Consumer Expenditure household spending comparisons | [BLS CEX](https://www.bls.gov/cex/pumd_data.htm) | Original Interview and Diary files, 44 replicates, five expenditure benchmarks with reported deviations | **SPENDING_BASELINE_REPLAYED** |
| LEGAL-01 | Defined twelve-provision draft | `fiscalrazor/legislation/scenario_v06.json` and legislative Markdown | Research simulation specification, with explicit effective dates | **ILLUSTRATIVE_LAW_DRAFT**; not introduced, enacted or counsel-reviewed |
| MECH-01 | Payroll/health surcharge/VAT-credit sample-record interactions | `fiscalrazor/src/fiscal_data/v11_joint.py`, tests | Supported pseudonymous record types only | **TESTED_RECORD_MECHANICS**; unweighted and not national |
| MECH-02 | §101 credit exposure on 2025 tax-unit proxies | [CPS ASEC and HHS replay](SCORING_FRONTIER_REPLAY.md) | Conditional MAGI and nonfiler scenarios | **CONDITIONAL_MICROSIMULATION** |
| TRUST-01 | Separate 2026 OASI, DI and HI ledgers | [SSA and CMS replay](SCORING_FRONTIER_REPLAY.md) | Published annual identities and series through 2100 | **TRUSTEE_BASELINES_REPLAYED** |
| IRS-01 | 2023 geographic return and AGI margins | [IRS SOI replay](SCORING_FRONTIER_REPLAY.md) | State subtotals and disclosure buckets reconciled separately | **GEOGRAPHIC_BASELINE_REPLAYED** |
| CAL-01 | 2023 modeled returns against IRS state subtotals | [Same-year calibration](CALIBRATION_AND_PROVISION_REPLAY.md) | 306 cells, residuals by income band | **UNREWEIGHTED_CALIBRATION_CHECK** |
| CAL-02 | §101 partial product and CE mapping | [BEA/BLS replay](CALIBRATION_AND_PROVISION_REPLAY.md) | Classified and mixed product spending, seven CE comparisons | **PARTIAL_PRODUCT_CLASSIFICATION** |
| CAL-03 | §§107, 108, 111, 112 source mechanics | [Provision replays](CALIBRATION_AND_PROVISION_REPLAY.md) | Isolated arithmetic and an SSA standalone comparator | **PROVISION_REPLAYED_WITH_LIMITATIONS** |
| SCORE-01 | 2027–2036 combined fiscal effect of the 12 provisions | Requires verified policy-level inputs, linked survey and tax units, appropriate feedback | **Not measured** | **NOT_ESTABLISHED** |
| SCORE-02 | OASI/DI and HI 75-year solvency *after the bill* | Requires joint SSA/CMS actuarial evaluation | **Not measured** | **NOT_ESTABLISHED** |
| SCORE-03 | Household burden by decile, age, geography and health status | Requires genuinely calibrated CPS/CE/IRS/MCBS and tested imputations | **Not measured** | **NOT_ESTABLISHED** |

## Two strict distinctions

**Source identity vs model truth.** The source archives' old `SHA256_MANIFEST_V11.txt` confirms included project-file bytes, and upstream Git blob hashes can verify official CBO file identity after downloads. Neither certifies the correctness of models or the independence of derived excerpts. The February 2026 CBO replay verified the 18 government originals and matched 252 publication input cells. The receipt records those checks.

**Different statistical units are not interchangeable.** Household units (CPS), tax return units (CBO/IRS), consumer units (BLS CE), beneficiaries (CMS), and trust-fund accounts (SSA/CMS) require statistical bridges. Published annual means and rankings do not uniquely determine their multivariate joint distribution.

## Version policy

The `fiscalrazor/` directory is the complete historical **v1.1.0** source snapshot. Its old README discusses many earlier versions. This root evidence register is the editorial reference for what this public repository currently claims. Both can be inspected and tested without overwriting historical provenance.
