# Public evidence inventory — Federal scoring ecosystem, November 6, 2026

There are 40 individually indexed resources with stable URLs and roles in `data/public_source_registry.json`. `web_verified` means the public resource's landing page or data format was inspected via a web reader, **not that its full content has been ingested or every result re-run**. This distinction is deliberate. Nothing in this bundle certifies a score issued by the Congressional Budget Office, Joint Committee on Taxation, Social Security's Office of the Chief Actuary, or CMS's Office of the Actuary.

## CBO: current-law baseline, rules, accounts and interest

**First canonical source:** [CBO 2026 budget and economic outlook](https://www.cbo.gov/publication/61882), 2026–2036, February 11, 2026. **Machine-readable source:** [official `US-CBO/cbo-data` repository](https://github.com/US-CBO/cbo-data), indexed by [catalog.json](https://raw.githubusercontent.com/US-CBO/cbo-data/main/catalog.json). Exact February 2026 FY data:

- [10-year budget aggregates](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/ten_year_budget/annual_fy_2026-02.csv); amount **billions of nominal dollars**; source for our transcribed excerpt.
- [Revenue details](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/revenue_detail/annual_fy_2026-02.csv); nominal billions, revenue components by variable and year.
- [Spending detail](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/spending_detail/annual_fy_2026-02.csv); one row per fiscal-year/account, `tin`, `agency`, `bureau`, `function_code`, `budget_authority`, `outlays`; amount **millions**, not billions.
- [Trust fund projection](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/trust_fund/annual_fy_2026-02.csv); OASI, DI, HI, funding streams, and stock vs cash flows; amount billions.
- [Published budget data index](https://www.cbo.gov/data/budget-economic-data); earlier baselines, historical, demography, economic, detailed social programs, debt.

**Genuinely executable CBO code:** [Budgetary Feedback Model (BFM)](https://github.com/US-CBO/budgetary-feedback-model). It is a small-deviation macroeconomic-to-budget calculator; it does not change the tax-law sensitivities when tax legislation changes. It is therefore **not** a VAT/corporate/individual score engine. Additional tools: [CapTax](https://github.com/US-CBO/captax) (effective capital tax rates, not revenue score), [rules-of-thumb model](https://github.com/US-CBO/rules-of-thumb-model), and [input-output price model](https://github.com/US-CBO/IO-price-model).

**Debt service:** [CBO's 2026–2036 public debt-service calculator](https://www.cbo.gov/publication/61912) takes annual changes in noninterest spending and receipts, and returns approximate interest feedback. Its public interface limits individual revenue/outlay changes to under **$1 trillion per year**. The calculator does **not** change interest rates as a response to the policy and its results are expressly not official. It is a better comparison case than assigning an assumed flat 4% rate. A $1.7 trillion annual policy change may exceed the safe input range, so do **not** extend its forecasts without independent verification.

CBO separately publishes [October 26, 2026 NIPA-adjusted projections](https://www.cbo.gov/publication/62876) derived from the February 2026 baseline. These are translated into national accounts; they **must not be added** to budget cash receipts/outlays.

- [CBO February 2026 fiscal-year economic dataset](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv) publishes nominal GDP directly: `FY2036,gdp,46712.1423975`, billions of dollars. The matched FY2026–2036 GDP series is manually transcribed to `data/cbo_2026_02_fy_nominal_gdp_excerpt.csv`; cross-check against the full official CSV with `python run.py check-official-gdp --path downloads/cbo_gdp.csv`.

## JCT: production design and what can be reverse-engineered

- [JCT: official revenue-estimating methods](https://www.jct.gov/operations/revenue-estimating/) describes the tax legislative score mandate, FY ten-year point estimates, and individual, corporate, international, estate and gift submodels. Production IRS SOI tax-return microdata are confidential.
- **Most informative recent source:** [JCT, *Revenue Estimating Process and Microeconomic Research*, March 31, 2026](https://www.jct.gov/publications/2026/revenue-estimating-process-and-microeconomic-research-2026/), and [the 19-page PDF](https://www.jct.gov/getattachment/c9ab0cfe-71ce-4912-b0c2-75c9a569ead8/Revenue-Estimating-Process-And-Microeconomic-Research-2026.pdf). It describes 2026 microsimulation model structure, option/optimizer behavior, avoidance timing, profit shifting and accounting treatment. Its ten-year 21%→22% corporate-rate example has $350 billion mechanical gross and $180 billion *illustrative* net. `data/jct_2026_corporate_illustration.csv` preserves all ten documented line items without silently generalizing them.
- [JCT 2023 Individual Tax Model description, JCX-48-23](https://www.jct.gov/publications/2023/jcx-48-23/) documents a much more extensive individual tax calculation approach than a simple mean-income tax-rate model.

JCT's March 2026 document specifies a representative sample of more than **400,000 actual 2022 individual returns representing around 200 million filing units**, linked to other administrative and survey information, and around **65,000 corporate returns representing 1.5 million-plus companies**, with 120,000+ foreign subsidiaries. Those source samples are NOT public downloads. Access to IRS returns is restricted by law; public IRS tables cannot fully reconstruct cross-variable tax-return correlations or entity behavior. Not all Member-requested estimates are published: JCT confirms requests are confidential unless released by the requesting Member.

**Conventional vs dynamic:** A conventional JCT score holds aggregate GNP fixed while reflecting within-economy behavioral and timing responses. A dynamic package score requires another modeling stage, coordinated with CBO. Tax incidence across households differs from the statutory payer.

## SSA Office of the Chief Actuary: actuarial scoring

- [2026 OASDI Trustees Report portal](https://www.ssa.gov/oact/TR/2026/) publishes supplemental single-year tables and long-range and short-range methodology.
- [June 2026 long-range model documentation (PDF)](https://www.ssa.gov/oact/TR/2026/2026_LR_Model_Documentation.pdf) documents demography → labor markets → covered wages/earnings → taxable payroll → benefits → reserves; public equations and component relationships, but not full production source code.
- [Annual program-specific assumptions and methods](https://www.ssa.gov/OACT/TR/2026/V_C_prog.html) define PIA, covered wages, taxable earnings, payroll, and beneficiary models.
- [Solvency provision index](https://www.ssa.gov/oact/solvency/provisions/summary.html) and the detailed 2026 individual proposal tables:
  - [E2.5: apply 12.4% OASDI tax on wages above $250,000 starting 2027 with no benefit credit](https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html).
  - [E1.10: increase OASDI rate 0.1 percentage points/year during 2028–2037](https://www.ssa.gov/OACT/solvency/provisions/tables/table_run201.html).
  - [B1.2: progressive price-indexing above 30th percentile starting with new beneficiaries in 2033](https://www.ssa.gov/OACT/solvency/provisions/tables/table_run153.html).

**Important:** SSA's actuarial effects in the provided tables are **percentage points of current-law taxable payroll** on a **calendar-year** basis. The cash or unified-budget consequences require separately modeled taxable payroll, tax receipt timing, benefit payment timing, federal tax interactions, and debt interest. Simply dividing by 100 and claiming FY budget savings fails. Nor can independently scored options be added after combining high-earner taxes, rate rises, and benefit indexing: they interact.

**High-quality official calibration anchor:** The intermediate-case 2035 **current-law taxable payroll is $16.486 trillion**, as stated in [SSA's 2026 short-range actuarial narrative](https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html). It is *not* the 2036 payroll base and must not be used to convert E2.5's 2036 percent estimate into dollars. See the single-year official tables for matching years.

## CMS/MedPAC: Medicare components

- [2026 Medicare Trustees Report](https://www.cms.gov/oact/tr/2026) is an annual actuarial baseline with HI (hospital insurance, Part A) and SMI (Part B and Part D) **separate**; the 10-year actuarial forecast in this report is 2026–2035 **calendar years**, not FY2026–2036.
- [CMS trustees' downloadable annual/supplementary tables](https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds), including [2026 expanded ZIP](https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip). The ZIP binary was not ingested here.
- [CMS National Health Expenditure projections](https://www.cms.gov/data-research/statistics-trends-and-reports/national-health-expenditure-data/projected) have a different population/systemwide accounting perspective from the Medicare Trust Funds. Their current published horizon is 2034, so FY2035 and FY2036 require an explicit extension if used.
- [MedPAC March 2026 policy report](https://www.medpac.gov/document/march-2026-report-to-the-congress-medicare-payment-policy/) contains Medicare Advantage payment, coding intensity, risk adjustment and delivery details. The March report estimates **$22B** in Medicare Advantage coding-intensity related payments in **2026**, not an achievable savings score for a new reform: rate changes, risk-score model transition, plan bids and program responses matter.

An HI trust-fund solvency gain is not necessarily the same as a lower *unified* federal budget deficit. For MA and site neutrality, capture Part A/Part B allocation, premium offsets, Medicaid spillovers, cost sharing, induced utilization, coding, payments to hospitals and related tax effects.

## Household and business microdata needed for an independent public model

- **IRS:** [SOI individual tax returns](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-returns) and [SOI form-field dictionaries](https://www.irs.gov/statistics/soi-tax-stats-program-documentation-data-items-by-forms-and-schedules).
- **Census:** [2026 CPS ASEC public-use data](https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html), demographic and income distribution with replicate/survey weights.
- **BLS:** [Consumer Expenditure Survey Public Use Microdata](https://www.bls.gov/cex/pumd_data.htm), expenditures and demographics for VAT incidence. **2025 PUMD has missing Oct–Nov collection data caused by the federal government funding lapse**. BLS says its published 2025 weights were specially adjusted but these weights are not incorporated into PUMD; handle [the explicit methodology warning](https://www.bls.gov/cex/ce-pumd-2025-shutdown-impact.htm), rather than treating 2025 microdata naively.
- **BEA:** [official PCE detail](https://www.bea.gov/data/consumer-spending/main) and [PCE by product table](https://apps.bea.gov/iTable/?categories=underlying&isuri=1&nipa_table_list=2017&reqid=19&step=3), for the VAT base and aggregate reconciliation. Total PCE includes components that may be excluded or imputed; it is NOT a turnkey VAT base.
- **Open-source policy calculators:** [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator) and [PolicyEngine US](https://www.policyengine.org/us/model). Their versions and data may differ from JCT present-law assumptions, but their code provides a realistic independent microsimulation starting point.

## What is NOT obtainable as ordinary unrestricted public knowledge

1. The **exact confidential sampled tax-return microdata** powering JCT models, including matched returns for large corporations and subsidiaries. IRS disclosure constraints apply.
2. **Complete production JCT internal model source**, elasticity choices for every proposal, analyst deliberations, and unpublished individual Member score requests.
3. The **full executable production SSA and CMS actuarial systems** with all proprietary internal files, fine-grained administrative records and assumptions encoded in code. Their published model *documentation* is extensive and publicly exploitable, but does not make them fully reproducible bit-for-bit.
4. A single official combined multi-agency score **before precise draft legislative text and formal agency work**. A bundle of independent public-model runs does not confer official status.

For public methodological questions CBO gives `communications@cbo.gov`. JCT has a Member-request route and public documentation; a Member can request a formal tax estimate and decide whether to release it. For SSA OACT see their site; for Medicare OACT see CMS trustees' reports. Request missing **nonconfidential** information only; do not mislabel access to protected returns as possible through an ordinary public-record request.
