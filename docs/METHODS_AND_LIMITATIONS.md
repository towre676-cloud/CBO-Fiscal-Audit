# Methodology and limits: what constitutes a federal fiscal proof?

## The object to be estimated

A policy score is a **causal difference between two consistently specified law-and-economy scenarios**. Official current-law baseline figures are not that difference. A public-source independent score needs explicit projections for revenues, outlays and financing effects *with and without the proposed legal changes*, using compatible demographic, macroeconomic and fiscal assumptions. Separate CBO, SSA, and CMS reports have different units, periods, and legal accounting boundaries.

### 1. Budget identity and interest

Write the annual signed unified-budget surplus as \(S_t=R_t-O_t\), where \(R\) is receipts and \(O\) total outlays, including \(I\) net interest. Define primary surplus \(P_t=S_t+I_t\). A positive annual deficit is \(F_t=-S_t\). Changes satisfy

\[
\Delta S_t=\Delta R_t-\Delta O_t,\quad
\Delta P_t=\Delta R_t-\Delta(O_t-I_t).
\]

Public debt changes by \(B_t-B_{t-1}=F_t+A_t\), where \(A_t\) collects non-deficit financing adjustments. **Do not assume \(A_t=0\)**, add interest savings twice, or divide federal fiscal-year payments by the wrong calendar-year GDP denominator. Using CBO's exact FY GDP is preferable to inverting a rounded debt ratio.

For policy analysis the fixed-rate assumption \(\Delta I_t=r\sum_{s<t}\Delta F_s\) is at best a stylized sensitivity. Interest rate, borrowing maturity, portfolio rollover, timing and macro feedback must be simulated/estimated and separately validated for a large change. The public debt-service calculator and CBO Budgetary Feedback Model have documented scopes, not unlimited applicability.

### 2. Legislative and cash timing

Each bill section needs legal incidence, definition of taxable base/covered service, effective date, administrative appropriation, phase-in, grandfathering, avoidance rules and cross-references. Corporate tax liability for calendar-tax-year \(t\) may be remitted in fiscal year \(t\), \(t+1\) and beyond. Defense budget authority changes do not yield identical-year outlay savings; account-level spendout curves are needed. A Medicare Part B outlay change can alter Part B premiums and general-fund transfers without equal change in the HI trust-fund balance.

### 3. Trust-fund actuarial adequacy

For OASI, DI and HI, one-year liquidity, reserve exhaustion dates, 75-year actuarial balance and terminal-year deficits are **different questions**. OASI and DI are separate by law. Their trustees' combined OASDI analytical display does not itself combine reserves legally. The OASDI percent-of-taxable-payroll denominator uses the Social Security earnings cap; HI taxable payroll is uncapped. Convert neither to general receipts without actual taxable payroll and tax-collection timing. The report must state whether deficits assume scheduled or payable benefits after depletion.

### 4. JCT-style taxes: identities vs behavioral scores

A tax rate multiplied by an income/expenditure base yields at most an explicit **mechanical counterfactual**. A conventional revenue estimate includes behavioral and accounting responses, credits, tax interactions, capital gains, deduction switching, corporate entity and financing choices, international profit shifting, income realization timing and fiscalization. In its March 2026 methodology paper JCT uses a corporate tax illustration to show why mechanical changes differ from adjusted figures. That illustration is **not** a production scoring function available for transplantation.

### 5. Consumer tax and household distribution

BLS consumer expenditures measure survey consumer units, BEA PCE measures national accounts, IRS covers tax returns, and Census covers households/people. The different aggregates cannot be forced together by multiplying each household's spending by a scalar. Decompose sector coverage, tax exemption/zero-rating/input credits, measurement gap, imputed flows, nonhousehold items, statutory taxable base and category-specific pass-through. Validate household credit take-up and nonfiler access separately. Calculate design-based standard errors from actual Census 160 replicate weights, then add separate model/parameter uncertainty; survey variance alone is not total uncertainty.

### 6. Non-additive interaction structure

Twelve provisions imply \({12 \choose 2}=66\) pairwise interactions. A finite list of selected pairs is not a proof that the other 57 vanish. A formally identified package interaction decomposition requires an **explicit joint model**, and can include higher-order effects. Shared payroll, medical spending and income effects belong to exactly one unified-budget account and (when relevant) one trust-fund account. Avoid treating a transfer between federal funds as additional unified-budget income.

## Three levels of publication-readiness

1. **Source-backed descriptive:** a published agency projection and its provenance; source audit and units explicit. *Presently available for selected excerpts.*
2. **Independently reproducible mechanical:** pure arithmetic, algebraic inequalities and supported sample records, with source fixtures and adversarial tests. *Available in this repository.*
3. **National causal joint reform score:** harmonized law, real tax/benefit/cost samples, independently validated zero-policy baseline, explicit interactions and fiscal timing, uncertainty and independent held-out checks; separately compare agency-issued results if obtained. *Not yet established.*

No amount of green unit tests for levels 1–2 upgrades an unsupported level-3 claim.
