# Illustrative Federal Fiscal and Social Insurance Reform Act of 2027

**Research draft, v0.6.0, November 6, 2026. NOT introduced, enacted, formally scored, or reviewed by legislative counsel.**

## Interpretive conventions

This is a **complete operational parameter specification for independent simulation**, not a verbatim replacement for the U.S. Code. Where a new statutory provision must be created, Congress's Office of Legislative Counsel would determine the final section numbering, coordination amendments, definitions and effective-date text. The formulas, rates, populations, deadlines and exclusions below constitute the one locked research scenario; no authority has endorsed the choices. All references to current law mean the federal statutes in force **as of November 6, 2026**, with statutory revisions through October 2026 verified individually where indicated. The 2025 reconciliation law (P.L. 119-21), especially the changes to 26 U.S.C. §§68 and 164, is incorporated into the **baseline** rather than falsely counted as a new saving.

Unless otherwise specified, `year` for taxes is the calendar tax year; defense caps are fiscal years beginning October 1; Medicare plan payments use contract calendar years; Social Security benefits use the year in which the worker first becomes eligible. Dollar thresholds specified for 2028 are nominal USD. Round annual future thresholds to the nearest $100 except where $1,000 is expressly specified. Published CPI-U, SSA average wage index (AWI), HHS poverty guidelines, and annual statutory contribution-and-benefit base numbers are **required external inputs**, never extrapolated from memory.

> **Critical consequence:** No provision's budget cost or saving is included until a matched federal fiscal-year estimate exists. An effect on OASI, DI, HI or SMI balances is not separately added to the unified budget if the associated federal tax receipt or outlay was already counted. Interest is a separate feedback module.

### Section 101 — Federal destination-based value-added tax and refundable household credit

Effective on taxable supplies delivered on or after **January 1, 2029**, impose a tax-exclusive **5.00% destination-based invoice-credit VAT** on a registered seller's sales of otherwise taxable goods and services to persons in the United States. Tax business-to-business supplies with recovery of input tax shown by valid invoices; tax imports into the United States at the corresponding destination rate; zero-rate exports and permit input-credit refunds on exported supplies. Registration is required for persons with more than **$100,000 of annual domestic taxable turnover** (same rate for voluntarily registered smaller sellers). File quarterly returns, remit net output tax less verified input tax, and permit negative periods to be refunded after anti-fraud review.

Zero-rate unprepared food meeting the federal SNAP food definition, prescription medicines, and exports. Exempt without input-credit entitlement: residential rents (including imputed owner-occupied housing), actual clinical care, tuition at accredited institutions, the implicit margin on financial intermediation, and nonmarket government services. All remaining destination consumer spending is taxable unless specifically zero-rated or exempt in the law. Distinguish zero-rating from exemption in modeling; they have different treatment of intermediate inputs and potentially different prices.

Create a **refundable federal VAT credit** for each resident tax household, payable even with zero income-tax liability, based on its current-year MAGI, number of qualifying persons under household rules, and the official HHS poverty guideline `P_y(size, location)`. Define the credit as `0.05 × P × clamp((3P − MAGI)/P, 0, 1)`; full credit applies at MAGI up to 200% of guideline, declines linearly to zero at 300%. A resident may claim by return or Treasury nonfiler/direct-benefit procedures; advances are reconciled against current-year MAGI. This is a **chosen credit formula**, not a fixed 20% earmark from hypothetical collections. Neither gross VAT nor credit is scored using total unadjusted BEA PCE.

Administered by Treasury/IRS in consultation with Census, BEA and BLS. New chapter to be assigned by legislative counsel. Statutory base reconstruction and survey incidence modeling must precede any federal revenue estimate.

### Section 102 — High-income individual surtax

For taxable years beginning **January 1, 2028**, impose an additional federal tax equal to **2.00%** of the excess of modified adjusted gross income (MAGI) over the applicable threshold: single **$500,000**, married filing jointly or qualifying surviving spouse **$1,000,000**, head of household **$750,000**, married filing separately **$500,000**. For non-grantor trusts and estates, use a $500,000 threshold. Define MAGI as AGI plus federal tax-exempt interest under 26 U.S.C. §103 and foreign earned-income exclusions under §911; this add-back is for determining the surcharge base, not an amendment to general AGI. The trust rule must account for grantor-trust look-through to prevent duplicated income.

Index thresholds after 2028 by CPI-U relative to the 2028 index and round to $100. The surtax is separate from the current-law Medicare additional tax, net investment income tax, and existing brackets. Source and cash timing: income tax liability is accrued on a calendar-year basis and converted to fiscal-year receipts using collection and settlement timing—not a 1:1 calendar/fiscal assumption.

### Section 103 — Maximum 28% federal income-tax benefit of itemized deductions for high-income taxpayers

For tax years beginning **2028**, after applying the existing statutory limitations to charitable, medical, mortgage, SALT and other itemized deductions (including **26 U.S.C. §§68 and 164 under P.L. 119-21**), calculate the positive income-tax liability reduction from the residual allowed deduction `D`: `T_without − T_with`. If MAGI exceeds **$300,000 single / MFS; $450,000 head of household; $600,000 MFJ or qualifying surviving spouse**, increase tax liability by `max(0, T_without − T_with − 0.28D)`. Index thresholds after 2028 by CPI-U.

The hypothetical counterfactual `T_without` means tax recomputed under the same law and taxpayer facts **but with itemized deductions set to zero**, preserving all existing tax interactions. The cap is an additional taxpayer-level adjustment after current-law §68; do **not** count a P.L. 119-21 reduction as new revenue. It does not remove the availability of the standard deduction. New IRC §68A to be assigned on counsel review.

### Section 104 — Cap employer health-plan tax exclusion

For tax years and wages paid after **December 31, 2027**, cap the combined exclusion for employer-paid health coverage and pretax employee salary reductions for that coverage at annual 2028 values of **$13,000 self-only** or **$31,000 family**. Employee coverage changes during a year are prorated by calendar month. Include `max(0, employer_allocated_plan_cost − applicable_cap)` in taxable income and, in conjunction with corresponding amendments to **26 U.S.C. §§3121 and 3306**, in covered wage measures for FICA and FUTA; coordinate employee salary-reduction amounts through §125 without taxing the same premium twice.

For self-insured arrangements, use the employer's substantiated per-employee actuarial cost. Cost is the allocable employer plan cost **excluding separately purchased after-tax employee premiums**. Index cap amounts after 2028 using CPI-U; there is no implicit age, region or collective-bargaining grandfathering. Health-plan switching, wages, payroll effects, effective tax value, and employee cost shifting are **unscored**; they must be explicitly simulated.

### Section 105 — Corporate income-tax rate

For corporate taxable years beginning on or after **January 1, 2028**, replace **21%** with **22%** in 26 U.S.C. §11(b), retaining all other corporate tax-law rules unless expressly amended, including §55 corporate AMT, BEAT/international provisions, general business credits, loss carryforwards and entity classification. Do not prorate a corporation's tax rate for a taxable year already underway. Treasury shall publish withholding/estimated payment changes. A mechanical 1% of taxable income is **not** a JCT revenue score because of interactions and behavioral responses.

### Section 106 — Additional OASDI tax above $250,000, without new benefit credit

For wages earned after **December 31, 2027**, impose an additional **6.2% employee and 6.2% employer tax** on annual OASDI-covered wages **above** the high earnings threshold `H_y`, while preserving tax on covered wages at or below the normal Social Security contribution-and-benefit base `B_y`. For 2028 `H_2028 = max(B_2028, $250,000)`. For years 2029 onward, `H_y = max(B_y, nearest_$1,000[$250,000 × AWI_(y−2)/AWI_2026])`. The coverage set is `[0, B_y] ∪ (H_y, ∞)`; it cannot overlap. Apply equivalent 12.4% SECA provisions for the high band and relevant wage/self-employment aggregate coordination.

The additional earnings are **not used to increase AIME, PIA or any other credited benefit formula**. Amend 26 U.S.C. §§3101, 3111, 1401 and 3121 plus the Social Security Act earnings-record and benefit computation provisions. For multiple employers and concurrent self-employment, form aggregate annual covered compensation `W = sum(employer wages) + net covered SE earnings`. The **new high band** `max(0,W−H_y)` is allocated among each W-2 employer and self-employment component **pro rata to that component's fraction of W**. Each W-2 employer owes the 6.2% employer share on its allocated high-band amount, the employee owes the 6.2% employee share on all W-2 allocations, and the self-employed worker owes 12.4% on the allocated SE portion; the allocations sum to the aggregate band exactly. IRS/SSA determine allocations after W-2/SE filings and notify employers; employer additional high-band payments are due by **March 15** of the following calendar year, subject to published administrative extensions. Normal base-band employer FICA remains per-employer as under current law. The aggregate high-band amount must be invariant to splitting compensation among multiple employers, and a tax unit may not claim two high-band exclusions merely because it has two employers. Withholding for an unknowable cross-employer high band is not required before IRS reconciliation. Legislative counsel must reconcile confidentiality, multiple-employer notification, income allocation timing and SECA deductions with existing statutory rules. **Keep OASI and DI trust-fund allocations separate** under the then-applicable statutory proportions.

### Section 107 — Five-step rise in combined OASDI contribution rate

On all covered OASDI wages, **including the above-threshold band created by §106**, raise the employee rate above 6.2% and the employer rate above 6.2% by **0.10 percentage points each in 2028**, **0.20 each in 2029**, **0.30 each in 2030**, **0.40 each in 2031**, and **0.50 each from 2032 onward**. The combined 2032 increase is **1.00 percentage point**. Apply the combined increase to the self-employment OASDI rate under §1401(a).

**Mandatory decomposition:** For earnings above the newly taxable threshold, the interaction between §106 and §107 is the phased additional rate multiplied by the high-band earnings. Do not count those earnings twice. Separate OASI, DI, and unified-budget attribution is required.

### Section 108 — Progressive price index of new OASDI benefits

For workers **newly eligible beginning in calendar year 2033**, implement SSA's publicly described **B1.2 (30th percentile) progressive-price-indexing formula** for PIA under **42 U.S.C. §415**. Create a new bend point at the 30th percentile of the newly retired workers' AIME distribution, preserve the **current-law initial PIA** for AIME at or below that point, and adjust the higher bend factors so that the initial PIA at the taxable-maximum wage rises by the CPI rather than the national average wage index. Preserve continuity at all bend points; neither prior eligibility nor prior benefits are retrospectively reduced. Current-law post-eligibility COLAs continue to apply.

The precise B1.2 official table is a calibration target, not a score for the *other* reforms. AIME distributions, cohort rules, survivor/DI treatment and administrative disability determinations require SSA actuary inputs. Do not book immediate retirement-benefit savings before the affected cohort qualifies.

### Section 109 — Medicare Advantage risk coding and county benchmarks

For **contract years beginning January 1, 2029**, amend 42 U.S.C. §1395w–23 to require the MA coding-pattern downward adjustment to be **at least 8.5%**, or the Secretary's empirically documented coding differential if higher; maintain the otherwise applicable risk adjustment and normalization rules, avoiding a second adjustment on the same coding difference. Set the county MA **pre-quality-bonus benchmark** at no more than **105% of the comparable standardized FFS per-beneficiary amount**. Do not amend the current-law quality-bonus formula except through the benchmark ceiling. Identify effects on MA bids, premiums, plan rebates, enrollment, coding, benefit packages and Parts A/B separately. No part of a MedPAC excess-payment estimate is presumed to be recoverable without a joint payment simulation.

### Section 110 — Medicare site-neutral clinic visit payments

For hospital outpatient claims on or after **January 1, 2029**, cap combined Medicare facility and professional payment for non-emergency office/clinic visits at the **same locality-specific physician fee schedule nonfacility amount** for the clinically equivalent service. The initial code set is **G0463 and CPT 99202–99205 and 99211–99215**, at on-campus and off-campus hospital outpatient departments. Exclude emergency department encounters, critical-access hospitals, federally qualified health centers and rural health clinics. Reduce the hospital facility component first, subject to a zero floor; prohibit balance billing to beneficiaries for the disallowed amount.

Phase in **50% of the payment difference in CY2029**, and **100% for CY2030 and later**. Require a publicly documented claims-level service/code crosswalk and pre/post utilization monitoring. Medicaid, provider access, geographic wage indexes, volume shifts, Part B premium offsets, and provider behavior are not invented or assumed away. Coordinate with 42 U.S.C. §§1395l, 1395ww and CMS billing authority.

### Section 111 — Multi-year defense discretionary budget-authority caps

Beginning in **FY2028**, impose the following nominal ceilings for **base discretionary defense budget authority (function 050)** in billions of dollars, rather than promising an immediate cut in outlays: FY2028 **897.179**, FY2029 **918.853**, FY2030 **940.253**, FY2031 **962.510**, FY2032 **984.957**, FY2033 **1,007.580**, FY2034 **1,031.073**, FY2035 **1,054.897**, FY2036 **1,079.686**. These are policy choices equal to 95% of the specified **CBO February 2026 base-defense BA projection**, rounded to the nearest $0.001 billion. They do **not** supersede the actual enacted appropriations in any fiscal year.

Apply 2 U.S.C. §901 enforcement, with emergency/supplemental defense spending included absent an expressly recorded national emergency or formal war waiver; the exception must be published separately. Account-level obligation rates, termination costs, prior-year outlays, compensation and procurement spendout must translate budget authority changes to **fiscal outlays**; budget authority reductions cannot be booked instantly as deficit reductions.

### Section 112 — Dedicated uncapped Medicare Hospital Insurance financing

For wages and self-employment income earned after **December 31, 2027**, add an uncapped HI payroll tax of **0.125 percentage points on both employee and employer in 2028**, **0.25 points each in 2029**, and **0.375 points each in 2030 and thereafter**, a combined increase reaching **0.75 percentage points**. The corresponding SECA HI additional rate is **0.25, 0.50 and 0.75 percentage points**. Existing 0.9% additional Medicare tax remains unchanged. Amend 26 U.S.C. §§3101(b), 3111(b), 1401(b), and the HI trust-fund allocation provisions. Deposit the new collections **only in HI**, not in Supplementary Medical Insurance (B/D) or the OASDI funds.

The statute does not designate this as a reduction in Medicare benefit expenditure. SSA and CMS must calculate separate HI solvency and budget projections; a receipt deposited in HI must not be counted again as a general-fund transfer.

## Coordinating sections: reporting, funding, simulation and audit

**Sec. 201. Administrators.** IRS/Treasury administer titles 101–107 and 112; SSA OACT and commissioner administer titles 106–108 and OASI/DI allocations; CMS OACT and CMS administer 109–112; OMB and DoD administer §111. Government Accountability Office shall review implementation controls. Each agency retains its lawful data confidentiality.

**Sec. 202. Accounting.** Publish annual FY2027–2036 effects separately by unified-budget receipts, noninterest outlays, net interest, OASI and DI trust-fund cash, HI, SMI Part B, SMI Part D, and other financing changes. Reconcile calendar-year and fiscal-year receipts using tax deposit/cash timing. Do not count intragovernmental transfers twice. Publish effects of payroll tax deductions and employer health inclusion on income taxes and other federal revenue.

**Sec. 203. Estimates.** Request a **joint current-law CBO/JCT budget score, SSA OACT 75-year actuarial score, CMS OACT HI/SMI actuarial evaluation**, and external independent full-survey household incidence, including uncertainty, before describing the package as fiscally stabilizing. Agency estimates retain their official independent status; this research document does not confer official approval.

**Sec. 204. Modernization and error correction.** Fiscalization, source and version SHA hashes, effect ownership and designated policy interactions are mandatory in the research implementation. The Office of Legislative Counsel must reconcile all cross-references, section numbering, interpretation of multiyear agency appropriations, and administrative effective dates before any bill is introduced.

## Scoring blockers explicitly recorded

The specification makes **12 proposed mechanisms mathematically explicit**, but it is **not yet counsel-ready legislative text**: VAT exemptions and zero-rate categories require definitions by statutory cross-reference, health-benefit §125 and FICA provisions require withholding rules, Social Security benefit indexing requires actuary-determined PIA factors, and the Medicare service/coding crosswalk must be validated. Social Security, CMS, JCT and CBO must score the *same* precise text and baseline, including cross-effects and cash-fiscal timing. Neither the research draft nor any sample household arithmetic is an official or published estimate of its savings.

## Contemporaneous primary references

- Title 26 §11: https://uscode.house.gov/us/usc/119-121/t26/s11/
- Title 26 §§3101, 3111, 1401: https://uscode.house.gov/us/usc/119-124/t26/s3101/ ; https://uscode.house.gov/us/usc/119-124/t26/s3111/ ; https://uscode.house.gov/us/usc/119-124/t26/s1401/
- Title 26 §§68, 106: https://uscode.house.gov/us/usc/119-121/t26/s68/ ; https://uscode.house.gov/us/usc/119-121/t26/s106/
- Social Security primary insurance amount, Title 42 §415: https://uscode.house.gov/us/usc/119-120/t42/s415/
- Medicare Advantage payments, Title 42 §1395w-23: https://uscode.house.gov/us/usc/119-121/t42/s1395w-23/
- Discretionary budget enforcement, Title 2 §901: https://uscode.house.gov/us/usc/119-121/t2/s901/
- SSA 2026 B1.2 provision description: https://www.ssa.gov/OACT/solvency/provisions/tables/table_run153.html
- CRS on 2025 SALT law: https://www.everycrsreport.com/reports/RL32781.html
- CBO official machine-readable February 2026 baseline: https://github.com/US-CBO/cbo-data
