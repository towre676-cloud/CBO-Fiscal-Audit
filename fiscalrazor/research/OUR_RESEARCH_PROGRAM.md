# FiscalRazor research program beyond official scoring

The legislative draft is one **benchmark scenario**, not a final set of recommendations or a political position. The independently developed research goal is to identify *which mathematically feasible policy combinations* approach sustainable federal financing while protecting low-resource households and respecting the legal OASI, DI, HI and SMI structures. A static deficit ratio alone cannot prove long-run solvency or welfare gains.

## I. Reconciliation geometry: stock–flow duality

For each fiscal year `t`, define the unified federal balance `S_t = R_t − O_t`, the **signed** primary balance `Q_t = R_t − (O_t−I_t)`, and net interest `I_t` with `S_t = Q_t − I_t`. Debt held by the public follows `D_t = D_{t−1} − S_t + other_financing_t`. The source's other-financing adjustment must not be suppressed to make debt equal the simple sum of deficits. Separate *intragovernmental transfers* from consolidated receipts/outlays; fiscal-year shifts and trust fund accruals belong to different coordinate systems and need explicit bridge matrices.

The FY2036 February 2026 CBO baseline gives `R=8300.755B`, `O=11416.142B`, `I=2144.336B`, `Q=−971.051B`, so the deficit is `3115.387B`. At GDP `46712.1423975B`, a **3% deficit ceiling** allows `1401.364271925B`, requiring `1714.022728075B` of net annual improvement **under the frozen GDP and baseline**. If interest remained unchanged, an exact primary surplus `2144.336 − 1401.364271925 = 742.971728075B` would be required. These are deterministic identities, **not estimates of proposed reform effects**. Any macroeconomic effect changing GDP also changes the target. Complete annual target observations for 2027–2036 are in `results/v06/static_fiscal_target_2027_2036.csv`.

## II. Provision overlap calculus

Policy design is a graph, not a flat sum. Each provision owns base effects by fiscal ledger account and year; each edge represents a **measured** interaction. With 12 policies there are **66 unordered pairs** and at least nine explicitly designated high-priority interactions. Nine interactions are a **minimum regression-gate panel**, not proof the other 57 are zero. Represent the joint primary improvement as `sum_i Δ_i + sum_(i<j) Δ_ij + higher_order_remainder`, where nonzero three-way terms can exist. The remaining response is unknown, not an arbitrary −15% haircut. A simulator may instead compute the full joint scenario without the pairwise approximation, and use pairwise decompositions only as diagnostics.

Important clusters: OASDI high earnings × OASDI rate change; employer health inclusion × income tax and payroll bands; VAT × credits × wage/benefit cost-of-living; corporate rate × pass-through election × capital gains × individual surtax; MA coding × benchmark × site-neutral cost × Part B premium; Medicare HI tax × induced taxable wage from employer-health cap; defense BA × macro growth and associated receipts. Keep receipts, transfers, benefit costs and rate changes within the account they legally affect.

## III. Robust fiscal frontier, not unsupported point projections

For every FY and each policy effect, require a **source-backed credible interval** `[l_i,u_i]` for net **fiscal-year** primary-balance improvement and a source-backed bound for interest feedback. With validated bounds for all policies and interactions, the sum interval may establish *conditional* feasibility/insufficiency relative to the required gap. Absent complete bounds, return `NOT_DETERMINABLE`. An interval that spans a target cannot establish success. The module `src/fiscal_data/v06_frontier.py` implements this gate, and intentionally returns `NOT_DETERMINABLE` with the current records.

**New research objective:** map the Pareto frontier over deficit/GDP, OASI/DI reserve ratios, HI reserve ratio, bottom-decile equivalent disposable income, top-decile burden, poverty headcount, provider access, and administrative costs. Report all separately; no single arbitrary welfare scalar or fixed weight vector. Compute a robust feasibility set under economic scenario shocks before proposing optimal packages. Do not optimize what cannot be measured.

## IV. Independent mechanism identification

The *primary gap* is budget accounting; the *trust fund shortfall* is demography and statutory financing; the *household burden* is weighted tax-benefit incidence; and the *dynamic score* is behavioral and macro feedback. These are conceptually distinct models and should be independently tested against external reference outcomes before coupling them. Research tasks include:

- Infer tax-liability timing/collections from published JCT fiscalization examples; do not translate TY effects into FY effects by 75%/25% unless payment calendars and estimates support the split.
- Use SSA official single-provision runs to calibrate actuarial sensitivity **by calendar year**, keeping OASI and DI separate. Refit only on training provisions; test on independent SSA options with held-out years.
- Use CMS separate Part A, B, D and MA claims evidence to model provider care sites, program payment and premiums; validate on published historical payment rules and MedPAC outcomes before scoring reform.
- Use BEA expenditure totals to calibrate BLS Consumer Expenditure PUMD rather than interpreting total PCE as a VAT base. Use 2026 CPS ASEC design weights and the 160 actual replicate weights, with diagnostics for the 2025 CE shutdown missing-month weights. Report what fraction of the household net burden is due to tax, rebates, premiums, wage shifting, and benefit changes.
- Use CBO's public Budgetary Feedback Model for **in-domain** economic counterfactual validation; its macro sensitivity cannot produce a missing JCT legal score.
- Explore structural administrative cost (e.g., IRS compliance/registration, health-plan switching, provider access) and tax-gap collection effort as **separately sourced new proposals**, not unscored savings inserted into the fixed 12-provision law.

## V. Counterfactual research portfolio beyond these 12 provisions

The law is only one reproducible *candidate*. Our additional pursuits will test alternative policy blocks after the base mechanics are measured: (1) tax administration and compliance; (2) health-care pricing/competition and supply-side delivery; (3) fiscal multipliers and productivity of federal procurement; (4) eligibility/benefit targeting and poverty transitions; (5) housing, employment and workforce participation sensitivity; (6) debt maturity and interest-rate hedging; (7) alternative VAT zero-rating and rebate designs; (8) shock-resistant, minimum-regret portfolios. None has a projected budget saving, health outcome or distributional effect yet. Build falsifiable observational or experimental comparisons before any point claim.

## VI. Explicit stopping and failure conditions

**Fail** if baseline cannot be reproduced from original agency bytes, if a one-year SSA actuarial balance is converted to fiscal revenue without a payroll and cash timing bridge, if any benefit and trust-fund receipt are double counted, if some 12-provision effect is missing but replaced by zero, if a claimed national household estimate uses only synthetic observations, or if the policy's 2028 rules are accidentally replaced by 2026 tax law. **Pass** only for the exact tests actually run. This package's mathematically derived fiscal target and synthetic payroll/VAT examples are not scores of the national economy.
