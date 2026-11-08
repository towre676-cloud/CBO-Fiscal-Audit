# CMS Medicare Trustees — source-reproduced first pass

**Report**: 2026 Medicare Trustees Report (June 9, 2026): https://www.cms.gov/oact/tr/2026. The local datasets transcribe Table II.E1 (page 28 of report, physical PDF page index 33) and Table II.F1 (page 35, PDF index 40). CMS publishes amounts to one decimal billion USD. The source's 2025 figures are actual; later figures are Trustees intermediate-case forecasts. The locally held table transcripts are not the complete original CMS supplementary ZIP. Run `python scripts/analyze_medicare_2026.py` to reproduce every calculation.

## Source check and independent arithmetic

CY2025 Medicare HI outlays **$444.2B** plus Part B **$584.3B** and Part D **$181.5B** equals **$1,210.0B** gross trust-fund outlays. CY2035 HI **$877.3B**, Part B **$1,319.1B**, Part D **$346.7B** equals **$2,543.1B** gross. Ratio **2.1017355** across 10 years. This is calendar-year gross Medicare trust-fund spending, NOT the same quantity as CBO FY Medicare outlays in the unified federal budget.

Table II.E1 HI assets are **$261.9B** at end of 2026, **$28.1B** at end of 2032, and a hypothetical **−$56.9B** at end of 2033. CMS projects reserve depletion in the **second quarter of 2033**. The reported negative balances in 2033–2035 denote continuation of scheduled costs after depletion for actuarial comparison; they do **not** assert legal authority to borrow from HI once the fund is exhausted. At end of 2035 this hypothetical deficit reaches **−$296.5B**.

## Bounded algebraic target — no unscored legislation

Define an additional uniform end-year HI income increment `q` each year in 2027–2035, with no policy feedback, reserve interest recalculation or change in outlays. For each year `y`, hypothetical year-end assets equal `A0[y] + (y−2026)q`. Requiring the figure to remain nonnegative throughout this published horizon implies

`q >= max(0, max_y{-A0[y]/(y−2026)}) = $296.5B/9 = $32.944444...B/year`, with the **2035 year-end requirement binding**. This is a floor for an artificially fixed baseline under end-year testing, NOT a payroll-tax score, debt saving, 75-year solvency result, or guaranteed intra-year sufficiency. It is not an adequate contingency reserve. Results may differ with quarterly payment timing and interest.

The Trustees' recommended contingency reserve is assets at the **beginning** of a year of at least that year's expenditures. For beginning of 2035 alone, adding uniform income in 2027–2034 would require at least `(877.3 − (−168.5))/8 = $130.725B/year` under the same fixed-path assumption. That does not meet the recommendation in *every prior year*: in 2027 the ratio is only 50% without upfront funding. A beginning-of-2027 full-reserve condition would require an immediate additional `524.9−261.9=$263B` in assets before expenditures. None of these financing floors is a federal budget saving.

The Trustees themselves estimate the **75-year HI actuarial deficit of 0.56% of HI taxable payroll** for 2026–2100 (and an income-rate equivalent of **0.65%** if change waits until depletion in 2033). These are official *source-baseline actuarial measures* from printed page 69, and use uncapped Medicare HI taxable payroll, **not** the capped OASDI payroll base. They are distinct from the $32.94B nine-year algebraic lower bound. The Trustees' rates include present-value funding and a target end-of-period trust-fund reserve, so they cannot be inferred from simple yearly sums.

## Vital CBO reconciliation still required

CBO's FY2035 **net Medicare mandatory outlays** are **$2,154.893B**. The CY2035 CMS **gross** HI+SMI expenditure is **$2,543.1B**. The numeric difference, **$388.207B**, is a *non-comparability diagnostic*, not unexplained savings and not an error established in either source. Reconciling it requires the legal fund/account mapping, premiums and offsetting receipts, fiscalization, total versus government contributions, MA Part A/B split, and other methodological items. **It must never be added to a federal deficit score**.

## Next actual source files

- CMS 2026 expanded supplementary ZIP: https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip
- 2026 Trustees main report: https://www.cms.gov/oact/tr/2026
- CMS 2026 fiscal-year historical/projected appendix V.H; confirm vs the unified CBO program definition before cross-agency reconciliation.
