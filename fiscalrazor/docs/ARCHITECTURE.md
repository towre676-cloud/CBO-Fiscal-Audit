# Federal Fiscal Data Foundation — architecture and scientific contracts

## Four independent evidence streams

**Budget (CBO/Treasury)**: ten-year CBO baseline fiscal-year time series; actual Treasury monthly and annual cash accounting; budget-account level CBO spending; revenue detail; historical and long-term budget; BLS/BEA macroeconomic denominators. Each vintage is immutable. Calendar-year economic variables never silently join fiscal-year accounting.

**Tax (JCT/IRS/Treasury)**: legal baseline dated to actual federal law, JCT budget scores, Treasury tax expenditures, IRS SOI aggregates, Policy Simulation Library tax model. Aggregate scoring is not the simple sum of independent option scores. The tax-unit population differs from the Census household population; join and weight crosswalk mandatory.

**Actuarial (SSA/CMS)**: 2026 Trustees data, OASI, DI, HI, SMI separate. The OASDI combined table is illustrative, not statutory consolidation. SSA OASDI payroll and Medicare HI payroll are distinct denominators. Reproduce both annual reserve trajectories and the 75-year valuation under a *single legislative package* before any solvency claim.

**Household (Census/CBO/IRS/health services)**: 2026 ASEC, person/household/family records, public-use replicate weights and survey universes; older CBO 2023 household distribution including transfer adjustments; IRS SOI aggregates; CMS utilization. This enables descriptive pre-tax household distributions on actual observations. Reform incidence needs a reproducible tax-benefit model and model-generated household-level before/after liabilities/benefits plus population and price assumptions, not mere Census income.

## Units and accounting invariants

- Monetary CBO snapshot values: billions of current dollars, FY, `proj_deficit_total` is NEGATIVE for a deficit; reports display positive deficit magnitude.
- Deficit = outlays − receipts = primary deficit + net interest. Mandatory + discretionary + interest = total outlays. Social Security/Medicare/Medicaid are subcomponents of mandatory spending and never added again.
- Public debt changes by deficit **plus other financing**; source supplies a distinct financing residual. Debt cannot be modeled from deficits alone.
- CBO GDP ratio derives from rounded share; report as *implied* and never pretend it is independently measured exact GDP.
- SSA percent taxable payroll is a flow rate; cannot add to nominal CBO dollar figures without actual wage-base series, time-frequency translation and tax law.
- Medicare HI payroll is uncapped and not the OASDI capped wage base; percentages cannot be combined.
- An actuarial present-value deficit and an annual budget shortfall are different objects. A reform needs separate reconciliations.

## Version reconciliation

February 2026 CBO full ten-year baseline is the retained financial anchor, with the exact upstream CBO Git blob SHA pinned. FY2026 final actuals and CBO August tariff changes remain separately dated events. The August 2026 $0.9 trillion tariff-related ten-year deficit revision includes $0.2 trillion interest. Without the revised annual profile, no year-by-year distribution is made. A full new CBO current-law baseline as of November 6, 2026 was not located in this investigation.

## Official score admission

A combined CBO/JCT budget score is an agency product, requiring a precise bill, current legal baseline, behavioral/macro assumptions and ten annual fiscal effects. SSA and CMS actuarial scores require separate projection models beyond public annual results. The repository records these requirements and blocks automatic assertions of agency certification. Independent estimates are allowed when fully reproduced and explicitly labeled nonofficial; none are invented to fill an incomplete record.
