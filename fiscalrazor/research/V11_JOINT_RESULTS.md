# FiscalRazor v1.1 — source-anchored joint statutory research

**As of November 7, 2026. No official score. This is new executed code, not a claimed legislative outcome.**

## 1. What is actually computed

We add a *person → employer → tax unit → household* wage-and-consumption model with the numerical mechanics of drafted §§101–104, 106–107 and 112. The model deliberately does **not** pretend that all remaining bill sections are household tax items: §105 requires corporations; §108 requires Social Security lifetime work histories; §§109–110 require Medicare plans/claims; §111 is a discretionary budget-authority cap. All of these remain unpriced in a full reform score.

The record-level model implements the following, with all money values in **USD for a calendar tax year** and no macro or fiscal-year cash-flow claim:

1. §104 includes the amount of employer health coverage above the documented plan cap in both wages and modified AGI. It refuses unverified OASDI/HI wage classes, uncoordinated multiple insurance plans, and missing Section 125 data.
2. §102 computes the 2% surtax on revised MAGI, so healthcare inclusion can change the surtax. Its cross-effect is exactly `0.02 * (max(0,MAGI+H−T) − max(0,MAGI−T))`.
3. §103 applies the 28% itemization tax-benefit limit **only when** independently computed with/without-itemization tax liabilities are supplied; absent such liabilities, the effect is `null`, not zero.
4. §§106–107 compute combined employee and employer OASDI increments from (a) the base wage cap applied separately to each *person*, (b) current-law employer caps on *each employer*, (c) the new aggregate-per-worker high band, and (d) the extra payroll rate. Cross-employer high-band amounts sum exactly to the person's high-band wages.
5. §112 computes the HI employer/employee rate increments on wages and any 0.9% existing Additional Medicare Tax change resulting from newly taxable health coverage. Personal and employer statutory liabilities are distinct; they do not themselves establish economic incidence.
6. §101 computes proposed VAT on **input expenditure already classified under the statute** and its credit using the revised MAGI. For 2× to 3× the household poverty guideline, the credit phaseout increases the marginal income-tax/benefit withdrawal rate **by 5 percentage points** at fixed taxable consumption. This is a real structural feature of the *draft*, not a population estimate.

**Important marital distinction:** OASDI high-band thresholds apply to each wage earner; a married couple with two $150k earners is not the same payroll-tax case as a couple with one $300k earner. Likewise, splitting a worker's wages among employers does **not** change the new *high band* total, but existing employer-side base taxes can differ by employer because current law's cap is applied employer-by-employer. The code tests both properties.

### Controlled demonstration — not a real household

One wholly **synthetic** 2028 single-filer input has $498,000 MAGI, $498,000 OASDI/HI-covered wages, one employer's $17,000 plan cost, a *hypothetical* $190,000 OASDI base cap, and externally supplied pre/post itemized tax liabilities. Under the draft it produces $4,000 newly taxable healthcare, $40 surtax (entirely a healthcare interaction), $1,900 itemization limitation, $1,300 independently supplied health-related income-tax change, $32,132 combined OASDI statutory tax increment, $1,371 combined HI increment and $36 Additional Medicare Tax increment. The **$36,779 subtotal** is conditional on fabricated demonstration inputs and **is not an estimated household or federal revenue effect**.

## 2. Genuine BLS income-quintile reference data

BLS's **October 29, 2026** release gives national 2025 consumer-unit mean spending and income. Expenditure/income in the published quintiles is 209.3%, 111.6%, 87.8%, 73.0%, and 55.7%. If **exactly 50% of spending in each quintile** faced a hypothetical 5% uniform tax before rebates, the ratio of tax on mean spending to mean pretax income would be approximately 5.23%, 2.79%, 2.19%, 1.83%, and 1.39%. This is a **mechanical ratio of separately published means**, not sample-level incidence or our actual VAT base.

BLS's five rounded group counts total 137.995 million consumer units, versus the published all-unit 137.994 million. Multiplying published group counts by rounded means gives about $11,303.542 billion spending. BEA 2025 PCE is **$20,870.150 billion**, so the first is **54.1613%** of the second. These are different statistical universes. The $9.5666 trillion difference cannot be interpreted as VAT-exempt, taxable, hidden or unreported spending without a category-by-category statistical bridge. **Applying a universal scale-up to the household spending records is prohibited**.

BLS's 2025 PUMD was affected by missing October–November interviews; our BLS values come from the **published release estimates**, whose weights were specially adjusted, *not* from raw or repaired CE PUMD. The v1.0 microdata acquisition and 2025-specific correction routines are preserved but have not been executed on actual complete microdata.

## 3. SSA direct base-rate arithmetic (calendar years only)

Using the SSA 2026 Trustees' published intermediate taxable-payroll projection (VI.G1), §107's extra **employee and employer combined** OASDI rate implies the *fixed-base mechanical* increments below, excluding the new §106 high earnings band: CY2028 $24.132bn, CY2032 $145.410bn, and CY2036 $171.250bn. They are **neither 10-year federal FY cash receipts nor official joint actuarial changes**. Benefits, wage responses, additional high-band taxes, phase-in fiscalization and income-tax interactions remain unestimated.

## 4. Medicare HI high-cost stress, now with the source's rounding

CMS 2026 Trustees report Table III.B5 gives annual HI expenditures and cost rates through CY2035 rounded to $0.1 billion and 0.01 percentage point, respectively. Under the deliberately frozen projection, the drafted §112 combined extra rate of 0.75 percentage points by CY2030 prevents negative year-end reserves through CY2035 in the *intermediate* scenario but **does not** in the *high-cost* scenario. Propagating printed precision, a uniform scaling of **1.4513–1.4546×** the entire proposed extra rate schedule is needed for nonnegative high-cost **year-end** reserves in 2028–2035. This means an eventual extra combined rate of roughly **1.0885–1.0910 percentage points**, as opposed to 0.75. Even this scaled schedule does **not** establish within-year cash adequacy, the 100%-expenditure reserve standard, economic behavior, benefit utilization or 75-year HI actuarial solvency. It is not a CMS OACT reform score.

## 5. 2036 federal target remains a test, not a conclusion

The CBO 2026-02 FY2036 baseline implies a static **$1,714.022728bn** annual balance improvement to reach a 3% deficit-to-GDP target. CBO's FY2036 nominal PCE is $31,989.631bn, but its statutory taxable fraction is undetermined; applying the law's 5% VAT rate to *all* of that PCE is a theoretical exposure capacity only. Net VAT revenues cannot be inferred from a 20%-rebate percentage; the drafted household credits depend on the actual poverty-guideline distribution and income. The model does not sum SSA calendar-year liabilities, CMS calendar-year reserves, CBO fiscal-year flow benchmarks or 2025 household survey exposures.

## 6. Evidence status and exact next dependency

This release adds **published national aggregate data and tested record-level calculations**. No complete original CPS ASEC 2026, BLS CE 2025 PUMD, IRS individual tax microdata or CMS beneficiary claims were acquired in the container. JCT/SSA/CMS production microdata and policy scoring models also are not public complete downloads. The 12-provision **national FY 2027–36 score remains unestablished**. The `results/v11/v11_evidence_status.json` file and `data/v11/joint_policy_readiness.csv` make this a machine-readable constraint.

To reach national incidence, ingest and verify ASEC household/person and 160 replicate weights, income-tax PUF or legally available substitute, CE category PUMD, BEA VAT product crosswalks, and defensible CPS/CE/tax/medical data linkage, then validate published margins, taxpayer effects, and all policy interactions. Distinct household consumer units, tax filing units, wage earners, employer payroll accounts, HI/OASI/DI trust funds and federal budget accounts must not be merged by identity. A survey-level effect from weighted observation records needs uncertainty and disclosure controls. Without that, extrapolating the synthetic joint tax calculation to the nation remains forbidden.

## Sources

- [BLS October 29, 2026 Consumer Expenditures 2025, Table 3](https://www.bls.gov/news.release/archives/cesan_10292026.htm)
- [BEA 2025 annual PCE, NIPA Table 2.3.5 via FRED](https://fred.stlouisfed.org/release/tables?eid=43861&rid=53)
- [SSA 2026 Trustees Table VI.G1](https://www.ssa.gov/OACT/TR/2026/lr6g1.html)
- [CMS 2026 Trustees Report, Table III.B5](https://www.cms.gov/oact/tr/2026)
- [CBO 2026 February baseline machine-readable repository](https://github.com/US-CBO/cbo-data)

Use: `PYTHONPATH=src python scripts/run_v11.py`; `PYTHONPATH=src python -m unittest discover -s tests -q`; `(cd external/public_scoring && python -m unittest discover -s tests -q)`. All originals must be independently obtained and verified before original-byte replay claims.
