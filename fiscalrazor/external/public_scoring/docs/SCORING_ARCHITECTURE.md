# Reverse-engineered score-system architecture and technical implementation specification

This is an **independent research specification**, not a representation of agencies' unpublished internal architectures. It is deliberately designed to let official public models and calibration targets reject incorrect claims.

## 0. Make a fixed legal specification

Define effective dates, fiscalization, rate/base parameters, transitional rules, affected cohorts, exceptions, benefit grandfathering, implementation appropriation, tax-filing treatment, and scope for every provision in `data/provisions.json`. For Congress's estimates, language matters: "5% VAT" does not specify the taxable base, invoice-credit/refund rules, exports, government spending, medical care, housing imputation, education, food, small-business exemptions, or credit eligibility. Similarly "cap the employer health exclusion" does not specify the cap trajectory, and "cut defense 10%" does not specify annual *budget authority* vs annual *outlays*. Do not create an official-like point estimate from policy slogans.

## 1. Synchronize baseline vintages and time accounting

Use CBO's February 2026 FY2026–2036 baseline in billions of nominal dollars. Freeze this vintage. Never splice it directly to a 2025 federal baseline, a newer 2026 tax-law forecast, a CMS **CY** trust-fund estimate, or a long-run NHE series without reconciliation. Distinguish `FY` (Oct previous CY–Sep current CY) from `CY`. Some budget lines are net of offsetting receipts; use CBO's definition per table. If a source changes, create a new versioned baseline and re-run every provision.

Let baseline receipts be `R0[y]`, outlays `O0[y]`, net interest `I0[y]`, primary deficit `P0[y]` (signed). Define signed deficit `D0[y] = R0[y] − O0[y] = P0[y] − I0[y]`. In FY2036 this gives `8,300.755 − 11,416.142 = −3,115.387`, with `P0 = −971.051`, `I0 = 2,144.336`, all billions of nominal dollars.

Directly use the matched 2026-02 CBO FY economic series `gdp` as the denominator; **do not derive nominal GDP from rounded debt/GDP percentages**. The published FY2036 GDP is $46,712.1423975B. A 3% GDP *annual FY2036 deficit* target is $1,401.36B; improvement needed against the baseline is $1,714.02B **before modeled policy feedback**. This is a required target, **not** validated package savings. Federal debt is a stock, annual deficit a flow; do not mix or sum stocks and flows.

## 2. Reconstruct the JCT tax-legislative engine

Public approximation: a reproducible microsimulation using survey PUFs and/or Tax-Calculator, projected from the 2022 tax return year to FY2026–2036 using official population/income factors. Every record `i` carries household/tax-unit weight `w[i,y]`, baseline tax liability `T0[i,y]`, policy tax liability `T1[i,y]`, benefit credits/rebates `B0/B1`, behavior/income shifting `x0/x1`, and federal tax interactions. Each estimate:

`ΔTaxLiability_CY[y] = Σ_i w[i,y] · [T1(i,y;x1) − T0(i,y;x0)]`.

**Tax liability is not fiscal-year receipts**. Convert using explicit tax payment patterns (withholding, estimated quarterly payments, annual settlement, deferral, corporate fiscal years), not a blanket factor. The JCT March 2026 paper calls this fiscalization, and explicitly notes FY2036 has Oct–Dec 2035 and Jan–Sep 2036.

Build these distinct subengines: individual income and payroll, corporate including CAMT/BEAT and credits, international business and transfer pricing, estate/gift, excise/VAT. Add taxpayer decisions (itemizing vs standard deduction; business entity, savings/portfolio choices, taxable income elasticities, realization responses, compensation timing, avoidance and compliance). Cross-tax responses matter, e.g. corporate rate increase changes shareholder taxes and employee wages.

**Calibration experiment:** JCT's illustrative ten-year corporate rate 21→22% gives `350 −110 −7 −2 −11 −20 −7 −1 −6 −6 = 180` billion. Reproducing that sum verifies only arithmetic; it does NOT validate a 21→22% model or imply that a 2ppt, 4ppt, or different-year reform generates linearly scaled net revenue. It exposes interaction categories and flags any simplistic tax-rate × corporate-profits calculation as inadequate.

Conventional score holds aggregate GNP fixed (while individuals move income, change timing, sectors etc). Run economy-wide feedback independently, then jointly resolve rather than applying a universal "behavior haircut."

## 3. VAT module: national accounts → invoice VAT → household distribution

Define `C_taxable[y] = Σ_k eligible_fraction[k,y] × PCE[k,y]`, after reclassifying imputed spending and in-scope consumption and considering nonresident/visitor, government and cross-border treatment. Estimate `Gross VAT = τ · C_taxable` for a tax-exclusive rate or `τ/(1+τ) · tax-inclusive-consumption` for tax-inclusive spend (these are different bases). Then model compliance, exemptions, intermediate input credits, sector/consumer responses, retailer transition, imported purchases and export zero rating. Separately model refundable household rebates/credits by size/income and delivery: `Net federal fiscal VAT effect = recorded gross collections − refunded credits − administration and other impacts`. Use BLS Consumer Expenditure Survey PUMD for distribution, with special corrections for missing 2025 interviews; calibrate aggregates to BEA PCE and households to Census/IRS. Holding existing tariffs, state sales taxes, Medicare payments, price levels or Social Security tax receipts fixed may create inconsistent overlaps.

## 4. SSA: cohort actuarial projection, not 10-year tax spreadsheet

Government published model flow:
`Population[a,s,y]` → mortality/fertility/migration → covered employment and wages → taxable payroll + wage distribution → contribution/benefit base → AIME and PIA benefit rules → retiree/survivor/disability incidence → beneficiary benefits and program costs → OASI and DI trust-fund balances, income/cost rates, actuarial balance.

SSA 2026 provision benchmarks included in `ssa_2026_option_benchmarks.csv` are real **single-provision model outputs**; E2.5 for CY2036 improves the annual balance by **2.53 percentage points of current-law OASDI taxable payroll**. E1.10 improves it by **0.86 points** (but this is NOT the same ramp as our policy), and B1.2 by **0.01 points** (newly eligible 2033; strong benefits from this change occur later). Do not sum to 3.40%: the combined model must be rerun because OASDI tax base, high earners' tax responses, claim decisions, and benefit provisions interact. Indexation causes cohort lag; no large near-term savings may be assumed from a long-run solvency figure.

For each scenario report: annual OASI income/outgo/balance, DI income/outgo/balance, reserves and interest, actuarial balance 75 years, 75th-year annual balance, required tax rate and year of trust fund depletion. Combined OASDI can be shown analytically **but separate legal fund balances must remain visible**. Calendar-year cash projections must be reconciled to federal FY receipts/outlays with cash timing. Payroll tax changes can affect other federal income tax receipts because of shifted compensation, payroll tax deductibility and coverage.

## 5. CMS Medicare: beneficiaries × services × unit costs, separately for HI and SMI

Project enrollment by age/disability/dual status, private-plan vs FFS selection, covered services and utilization, provider unit reimbursement, technological and drug trends, plan risk scores and bids, premium/other income and federal matching payments. For Part A HI track dedicated payroll tax, reserves, interest, and provider payments; for Part B and Part D SMI track premiums plus general revenue financing (and statutory special charges) separately. A cut in Part B gross benefit outlays may partly reduce beneficiary premiums and therefore the **net unified budget effect**; this is not an HI trust-fund savings dollar.

Medicare Advantage reforms must model risk coding intensity and 2026 V28 risk-model transition, benchmarks, quality bonuses, plan bids, rebates, beneficiary enrollment and provider payment spillovers. Site-neutral reforms require a procedure/site-level dataset, provider mix, patient migration, geographic wages and negotiated sector responses. Derive cost and quality distribution as well as federal savings. CBO may incorporate medical coverage spillovers, MA beneficiary behavior and payroll income shifts not separately visible in a Trustees report. Independently compare against CMS' 2026 expanded tables and MedPAC March 2026 payment analysis, then reconcile to matched CBO FY Medicare budget lines.

## 6. Discretionary spending (defense) is an outlay *pipeline*

Use detailed CBO spending by TIN: `budget_authority[account,y]` does not equal `outlays[account,y]`. A $100B appropriation reduction produces outlay reductions over several years dependent on contract duration, procurement, salaries, previous-year unspent obligations and new appropriations. Estimate spendout weights `s[account, k]` calibrated to historical CBO estimates and account type:

`ΔOutlay[account,y] = Σ_{t<=y} s[account,y−t] · ΔBudgetAuthority[account,t]`.

Account for procurement termination, military pensions, transitions and other mandatory spillovers. Never treat a $100B cut in BA as a $100B cash deficit reduction immediately.

## 7. Interactions and budget integration

A noninterest federal **signed** budget score for FY y is

`ΔPrimaryBalance[y] = ΔReceipts[y] − ΔNoninterestOutlays[y]`,

where changes include every provision, rebates, mandatory spending and implementation. A positive number improves the primary balance. `ΔNetInterest[y]` is estimated by CBO's simplified debt-service tool only *within its range* or by a separately calibrated dynamic model and verified term structure. Then

`ΔTotalBalance[y] = ΔPrimaryBalance[y] − ΔNetInterest[y]`.

Define provision/account-year **ownership** and explicit interaction edges. Obvious pairings include VAT and its rebate; OASDI base rate and earnings above $250k; corporate rate and personal capital gains/dividends; employer exclusion cap and other income taxes; MA and site neutrality; MA and HI financing. Each effect appears **once** at the correct federal accounting line and FY. Policy estimates may need a single joint simulation, not independent scores with an arbitrary overlap factor. Annual totals, outlay/net receipts, trust funds and debt-stock changes must reconcile with accounting identities.

CBO's public debt-service calculator can return comparisons using inputs within its prescribed input range; public BFM allows sensitivity to alternate economic inputs. They cannot magically provide the official score for a multi-trillion-dollar package. Label any larger extrapolation clearly as an independent, unvalidated scenario and quantify uncertainty, not as a CBO result.

## 8. Distribution and welfare (parallel mandatory score)

Produce annual distribution by (a) household equivalized disposable income decile; (b) tax filing unit income; (c) age/cohort; (d) disability and health use; (e) homeownership/geography; (f) business ownership; and (g) year. For each unit, model tax, rebate, net consumption price increase, employer pass-through, benefit changes, medical premiums and cost sharing. Sample weights, poverty definitions and family adjustments vary; report them. Bridge CPS+CE+SOI by statistically coherent imputation and compare group totals to each source. Report means, medians, percentiles, net gainers/losers, effective average burden and uncertainty. A progressive rebate does not automatically establish a progressive net VAT package.

## 9. Validation must precede claims

First zero-policy baseline matches official 2026 CBO exactly (11-year CSV, not rounded prose). Then scenario-level tax calculator baseline to IRS SOI; JCT public individual precedent cases; SSA three option-year benchmark curves and 75-year targets; CMS annual Part A/B/D cash and beneficiaries; CBO account outlays and debt rate sensitivities. Run external held-out policy examples, match without retuning, and report failure residuals and confidence intervals. Only after this should the engine estimate package deltas. An exact end-to-end official score remains the agencies' prerogative.
