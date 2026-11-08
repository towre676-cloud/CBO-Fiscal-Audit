# FiscalRazor · 2026-11-06 reconciliation of two sessions

**Status:** evidence-anchored integration of compatible public results into working source code.
The other session's `RESEARCH_STATUS.md`, `SOURCE_REGISTER.md`, and `SCORING_ARCHITECTURE.md`
were read from the Library. Its ZIP file was located, but its internal source files
were not inspectable in this container; do not describe this as independent code replay.

## Confirmed additions

1. **Direct CBO GDP denominator:** FY2036 nominal GDP $46,712.1423975bn, as
   published in Feb 2026 CBO fiscal-year historical-economic CSV. Prior v0.2
   derived GDP from the rounded public-debt/GDP ratio. This correction changes
   the static gap from ~$1,714.01794bn to exactly $1,714.022728075bn.
   Full source Git blob SHA-1 `e0799d7972696a65823e5d90cf36486d21903520`.
   Direct excerpt file: `data/verified_tables/cbo_gdp_fy2026_2036_official.csv`.
2. **SSA single-provision benchmarks** 2026–2036 (calendar-year effects,
   percentage points of current-law OASDI taxable payroll): E2.5 (12.4% tax above
   $250k starting 2027, no benefit credit), E1.10 (0.1pp annual rate increase
   2028–37), B1.2 (30th-percentile PIA price index from new eligibles in 2033).
   2036 effects: +2.53pp, +0.86pp, +0.01pp; **DO NOT SUM** as a combined bill.
   An anchored CY2035 E2.5 calculation 16,486bn * 2.52/100 = 415.4472bn is
   a single provision's actuarial-balance calculation, NOT a FY federal deficit score.
3. **JCT illustrative tax calculation:** Official published *example*, not an
   official score: rate 21→22% mechanical +350bn, nine adjustments -170bn,
   illustrative 10-year net +180bn. This is a source-backed teaching-case
   regression test. Do not infer an elasticity, apply a multiplier to another
   tax proposal, or count it as a reform's scored revenue.

## Comparative engineering

- Original data foundation v0.2: 46 catalog entries (not 46 acquired files),
  20 CBO Git identities, 231 budget values, 11 SSA IV.B1 yearly baseline rows,
  household 160-replicate variance machinery, source-status and hash gates.
- Other public scoring reconstruction: 40 public resource URLs, 7 CBO aggregate
  budget series and 11 direct GDP rows, 33 SSA option values, JCT worked example,
  extensive architecture for fiscalization, VAT incidence, OASI/DI/HI, budget
  authority to outlay conversion, and interaction ownership.
- v0.3 source code adds the direct GDP, SSA options and JCT demo to the v0.2
  test suite. Other session's independent code is **not** attested as merged.

## Hard research gaps and gates

- **No legislation specified.** VAT legal base and rebates, payroll provisions,
  tax-exclusion caps, MA payment changes, budget authority schedules, employer
  incidence, and grandfathering are essential to a scored policy.
- **No official joint fiscal score** for precisely specified bill text and law
  vintage, and no combined SSA OASI/DI or CMS Medicare HI actuary report.
- **No microdata-reproduced household impacts.** CPS/CE/IRS independent tax-benefit
  simulation, statistically coherent weighting and validation still unperformed.
- **No Medicare behavioral reform scored.** CMS 2026 Trustees ZIP and MedPAC
  clinical payment detail must be ingested, and Part A trust cash cannot be
  equated with Part B/D unified-budget savings.
- **No independent full-source byte ingestion.** Selected copies and published
  values are checked, large raw archives are still listed NOT_ACQUIRED.
- **No fiscalization or interaction engine** robust enough to score a joint bill.
  Missing provisions and interactions must never be silently entered as zero.

## Official links (specific frozen vintages)

- https://github.com/US-CBO/cbo-data/blob/main/data/economic/historical_economic/annual_fy_2026-02.csv
- https://github.com/US-CBO/cbo-data/blob/main/data/budget/ten_year_budget/annual_fy_2026-02.csv
- https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html
- https://www.ssa.gov/OACT/solvency/provisions/tables/table_run201.html
- https://www.ssa.gov/OACT/solvency/provisions/tables/table_run153.html
- https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html
- https://www.jct.gov/getattachment/c9ab0cfe-71ce-4912-b0c2-75c9a569ead8/Revenue-Estimating-Process-And-Microeconomic-Research-2026.pdf

**Next gate:** specify bill text then run independently validated current-law
budget, cohort actuarial, corporate/individual/VAT, and household models. Only
agency-issued scores may be labeled official.
