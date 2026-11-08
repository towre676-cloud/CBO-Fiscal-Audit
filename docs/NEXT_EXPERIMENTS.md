# Independent research frontier and experiment design

These are **falsifiable tasks**, not general aspirations or claimed completions. The codebase already contains partial engines for each stage; this document defines stronger future admission criteria.

## Stage A — Full original data and reproducible account bridges

- **Completed for CBO February 2026.** All 18 original CSVs passed publisher Git blob and record-count checks. All 252 published input values matched and spending-account outlays reconciled across 11 fiscal years. See the [source replay](CBO_SOURCE_REPLAY.md).
- **CPS ASEC household benchmark completed.** The [public-use replay](CPS_HOUSEHOLD_REPLAY.md) joins all 160 replicate weights and reports its differences from Census Table 1. Extend calibration to held-out income moments and the tax-household definition required by §101.
- **BLS CE 2025 spending benchmark completed.** Original Interview and Diary archives were replayed with lapse adjustments and 44 replicate weights. Five published spending aggregates are compared in the [scoring frontier](SCORING_FRONTIER_REPLAY.md).
- **SSA/CMS trustee baseline bridge completed.** Separate OASI, DI and HI operations reconcile at published precision and annual long-run series are available through 2100.
- **IRS SOI 2023 geographic margins replayed.** Compare with same-year CPS modeled units, then extend to newer vintages as their published returns become available. Retrieve **CMS MCBS** public-use records and calibrate separately to beneficiary benchmarks. Provider-level Medicare payment estimation requires finer claims and contract information.

**Pass:** independently executed original-byte receipts, parser/weight calibration, a table of per-source deviations and negative-case tests. **Fail:** source landing pages only, hand-entered sample rows, an altered ZIP, or a publication claim based solely on source URLs.

## Stage B — Zero-policy model calibration

Build baseline household/tax-unit/medical expenditure projections under law in force in the chosen CBO vintage. Replicate published distribution totals, state and category moments, federal tax receipts, payroll coverage and Medicare expenditures **before activating any bill section**. Independently compare multiple held-out years and present sensitivity to imputation/underreporting.

**Pass:** base-year calibration error budget specified *before* tuning, matched year/law parameters and held-out validity. **Fail:** optimizing only to the desired fiscal saving.

## Stage C — Joint 12-provision analysis

Compute each provision's **first-order** revenue/outlay/fund effect and a joint full-scenario model; include exact §101 rebate rules and household taxability, payroll and employer health exclusion, statutory caps, Medicare Part A/B/D allocation, corporate tax credits/behavior and defense account spendout. Save the complete effect matrix by provision, cohort, fiscal year and budget account. Check all 66 interactions and a bounded residual for 3+ way interactions; do not assume that a missing value equals zero. Reconcile taxes and benefits at taxpayer, worker, household, provider and trust-fund levels.

**Pass:** receipt and noninterest outlay deltas + net interest + other financing reproduce the difference in debt stocks. OASI/DI/HI balances reconcile separately; household-gainer/loser shares come from genuine weighted samples. **Fail:** published option estimates added as though independent.

## Stage D — Robust, multiobjective fiscal stabilization

Evaluate the complete policy in a stochastic or interval framework spanning GDP growth, employment, interest-rate paths, mortality, medical cost growth, tax incidence and behavioral response. Distinguish **(i)** 3%-annual-deficit, **(ii)** non-rising public-debt/GDP over an entire horizon, **(iii)** OASI/DI/HI statutory solvency and full-reserve tests, and **(iv)** distributional constraints by earnings decile and vulnerable subgroup. A package may pass some constraints and fail others.

For bounded but uncertain policy effects, compute the **worst-case residual deficit** and a **Pareto frontier**, not a single unqualified saving. If uncertainty bounds are too loose, report the interval and identify the data that most reduces it (value of information). Never infer political coalition support from arithmetic or from a guessed weighted average.

## Stage E — External and professional validation

Submit a fixed, counsel-reviewed legislative specification for official-scoring consideration through an appropriate congressional route; seek nonconfidential methodological feedback from CBO, JCT, SSA OACT and CMS OACT. Obtain independent review of the code, public-data versions, uncertainty and policy assumptions. Public source-level checks do not substitute for any official estimate. A research article should make its adversarial failures and unavailable datasets explicit in the main text.

## Immediate experiments

The [scoring frontier](SCORING_FRONTIER_REPLAY.md) records the §101 tax-unit replay, BLS spending validation, and separate OASI/DI/HI baselines. For §101, the next admissions are a defensible definition of MAGI and qualifying persons for nonfilers and a legally mapped BEA/BLS consumption base. Track the uncertainty of both inputs before modeling joint distributional effects.
