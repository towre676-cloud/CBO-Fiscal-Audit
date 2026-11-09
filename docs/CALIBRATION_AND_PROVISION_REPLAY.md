# Same-year tax calibration, VAT spending classification, and provision replay

This pass uses income-year 2023 for the Census–IRS tax comparison, calendar-year 2025 for the BEA–BLS spending comparison, and the published 2026 trustee and February CBO vintages for provision mechanics. The separate time bases are recorded in each receipt.

## 1. Census tax units against 2023 IRS filings

The 2024 CPS ASEC tax model supplies 2023 filing status, modeled AGI and unit identifiers. Principal modeled returns use the principal person's weight, with reciprocal spouse validation for a joint return. A separately modeled single return by a dependent enters the filing comparison separately. The replay includes positive AGI and compares 306 state-by-income-band cells with IRS geographic state subtotals. The IRS release excludes some addresses and applies disclosure controls, so its state subtotal universe differs from the full IRS filing population. The alternative using household weights is retained as a diagnostic. Neither set of weights was adjusted to fit the IRS controls.

| 2023 AGI band | CPS modeled returns, millions | IRS returns, millions | CPS AGI relative to IRS |
|---|---:|---:|---:|
| $1 to under $25,000 | 34.75 | 40.39 | −17.11% |
| $25,000 to under $50,000 | 34.66 | 35.88 | −5.54% |
| $50,000 to under $75,000 | 25.02 | 24.11 | +2.39% |
| $75,000 to under $100,000 | 15.94 | 15.65 | +1.04% |
| $100,000 to under $200,000 | 30.46 | 27.49 | +10.38% |
| $200,000 or above | 15.88 | 13.37 | −16.15% |
| **Total** | **156.70** | **156.88** | **−5.24%** |

The $200,000-or-above band has 18.74% more modeled returns but 16.15% less total AGI than the IRS margin. This failure blocks the use of the uncalibrated CPS upper tail for the surtax, itemized deductions, or the OASDI high band. Reweighting to counts alone would leave the conditional mean within each band unchanged. A matched return-and-income calibration and a held-out validation year are separate admissions. The [national receipt](../publication/results/cps_irs_2023_calibration.json) and [306-cell comparison](../publication/results/cps_irs_2023_state_margins.csv) preserve the discrepancies. Sources: [2024 CPS ASEC](https://www.census.gov/data/datasets/2024/demo/cps/cps-asec-2024.html) and [2023 IRS geographic data](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2023-zip-code-data-soi).

The [upper-tail calibration follow-up](HIGH_INCOME_TAX_CALIBRATION.md) matches both 2023 geographic moments and tests the adjustments against finer IRS national bands and a frozen 2022 transfer. It records the remaining gaps before provision scoring.

## 2. BEA product classification and BLS comparison

The November 3, 2026 BEA flat-file archive supplies Table 2.4.5U in current dollars. The replay checks that goods and services reconcile to PCE and rejects any assignment of both an ancestor and its descendant. For 2025, PCE is $20.870 trillion. Removing the two published net geographic adjustment lines yields a $20.817 trillion expenditure proxy before those adjustments. This arithmetic helps keep resident-versus-destination bookkeeping explicit. The actual VAT destination test requires transaction and supplier information.

| 2025 category under the product mapping | Trillions of dollars |
|---|---:|
| Classified as exempt | 4.097 |
| Classified as zero-rated | 0.776 |
| Classified as standard-rated | 1.594 |
| Unclassified or mixed | 14.350 |

Treating every unclassified dollar as excluded or standard-rated yields a **$1.594T–$15.944T classification interval within this expenditure proxy**. A static 5% multiplication gives $79.68B–$797.21B before the refundable credit. The endpoints describe this product mapping. Invoice credits, embedded tax in exempt sectors, the registration threshold, behavior, and purchases outside the proxy can change collections. Stationary tenant rent stays in the mixed balance because the annual series includes landlord durables. Tuition, most food and much of clinical care require a more granular treatment. Explicit private transaction categories and statutory definitions must drive later refinements.

Seven BLS categories are replayed from the original 2025 Interview and Diary archives and paired with conceptually related BEA series. Examples include $373.60 in annual household prescription spending per CE consumer unit alongside $593.52B in economy-wide PCE prescription spending, and $2,503.72 in CE gasoline and other fuel spending alongside $376.65B in BEA gasoline and other motor fuel. The first pair demonstrates how payer scope matters. The alcohol pair also differs in its treatment of away-from-home purchases. These pairs provide scope checks for a future bridge. Each estimate retains its original units and denominator. See the [line-level receipt](../publication/results/bea_bls_vat_spending_base.json), [BEA table](https://apps.bea.gov/iTable/?categories=underlying&isuri=1&nipa_table_list=2017&reqid=19&step=3), and [BLS expenditure hierarchy](https://www.bls.gov/cex/pumd_doc.htm).

## 3. Four provision replays

| Section | Evidence established | Remaining step |
|---|---|---|
| §107 OASDI rate rise | Multiplying the draft rates by SSA current-law taxable payroll gives a $171.25B gross base-band effect in CY2036. | Add the §106 high-band interaction and estimate earnings response, income-tax offsets, timing, and separate OASI/DI attribution. |
| §108 progressive price indexing | SSA's standalone B1.2 comparator improves the 75-year actuarial balance by **1.70 percentage points** of taxable payroll. The remaining balance is **−2.72%**, and combined depletion remains in **2034** in the SSA comparator. | Apply the joint policy to insured cohorts and value separate OASI and DI outcomes. |
| §111 defense authority cap | The nine draft ceilings match 95% of the pinned CBO base-defense authority, rounded as specified. The cumulative difference is **$467.211B** of authority. Two illustrative lag schedules give **$394.24B** and **$441.77B** of gross FY2028–2036 cash differences. | Replace the chosen lag schedules with obligation, spendout, waiver, and termination-cost evidence at the account level. |
| §112 HI financing | The statutory increments on CMS taxable payroll yield **$160.82B** gross in CY2036. Adding 0.75 percentage points to the published HI income-minus-cost rate yields a nonnegative rate in all **71** years from 2030 through 2100. The narrowest margin is **0.04 percentage points** in 2042. | Recompute quarterly cash, reserves, behavioral and income-tax offsets, and cross-provision effects. Annual rate coverage alone leaves the reserve path unresolved. |

These results are recorded in the [provision receipt](../publication/results/provision_107_108_111_112.json). The §107 and §112 calculations freeze each agency payroll base and preserve calendar-year attribution. The §108 result is the published SSA estimate for B1.2 alone. The §111 cash examples use chosen cohort weights with unit total and no offsets. Sources: [SSA payroll projections](https://www.ssa.gov/oact/tr/2026/lr6g1.html), [SSA B1.2](https://www.ssa.gov/OACT/solvency/provisions/tables/table_run153.html), [CMS trustee tables](https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds), and [CBO February 2026 source replay](CBO_SOURCE_REPLAY.md).

## 4. Remaining provision-level gates

| Section | Next evidence admission |
|---|---|
| §101 VAT and credit | Validate same-year tax-unit and income calibration before projection. Fix the legal MAGI, residency and nonfiler rules. Resolve mixed BEA and UCC categories using transaction and payer evidence, then test alternative household spending matches. |
| §§102–103 surtax and deductions | Reconcile the upper tail to IRS return, filing-status and deduction distributions. Run the same returns through both provisions to estimate the interaction. |
| §104 employer health exclusion | Join credible premium, coverage-tier and compensation distributions. Separate income tax, OASDI and HI effects, including the high band. |
| §105 corporate rate | Build an affected taxable corporate base by fiscal year, accounting for credits, losses, foreign income, timing and behavioral response. |
| §106 OASDI high band | Obtain covered individual earnings, self-employment and employer allocations with credible top-tail support. Apply the indexed threshold and model the subsequent collection lag. |
| §§107–108 OASDI rate and benefits | Jointly run §§106–108 on a common earnings and cohort baseline. Reconcile payroll cash and benefit changes separately to OASI and DI. |
| §§109–110 Medicare Advantage and site-neutral payments | Calibrate contract/county benchmarks, risk scores, service codes and payment systems. Use beneficiary or claims evidence to assign overlapping services to HI and SMI accounts. |
| §111 defense caps | Validate the cohort spendout profile using account-level obligations, actual outlays and waiver scenarios. |
| §112 HI financing | Model quarterly deposits and reserves, plus the HI/SMI assignment of §§109–110. |

The package model still needs all 66 pairwise interactions and higher-order effects, fiscal-year cash and debt reconciliation, a matched household incidence distribution, and joint post-reform actuarial projections. Official scoring requires an agreed bill and evaluation by the responsible agencies.
