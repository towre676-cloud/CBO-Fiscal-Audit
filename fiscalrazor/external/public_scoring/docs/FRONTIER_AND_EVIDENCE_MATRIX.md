# Twelve-provision frontier: what public evidence we actually have

Every proposed legislative provision is **UNSCORED**. Published SSA **single-provision** examples and MedPAC payment *benchmarks* do not substitute for the joint score of a new bill.

| Reform | Best public calibration material found | Missing before score |
|---|---|---|
| VAT 5% with rebates | BEA PCE by product, BLS CE PUMD, CBO September 2026 researcher distribution files | exact tax-exclusive taxable base/exemptions, border treatment, compliance, refunds, cash timing, incidence |
| High-earner income tax surtax | 2023 IRS SOI by AGI/filing, open-source Tax-Calculator | surtax rate, thresholds, tax year, taxpayer behavior, wage/capital shifting, fiscal cash |
| Itemized deduction caps | IRS SOI detailed AGI and Schedule A, Tax-Calculator | phase-out/cap legal rules, SALT and 2025 law interaction, re-itemization, liabilities |
| Employer health tax exclusion | CMS NHE, CBO insurance subsidies, public survey wage/benefit data | exclusion limit, benefits-to-wage shifting, income/payroll tax and coverage interactions |
| Corporate rate | JCT 2026 350B→180B worked illustration, IRS corporate aggregates, CBO CapTax | exact rate, income abroad, CAMT/BEAT, credits, business behavior, dynamic model |
| OASDI >$250k | SSA published E2.5 and 2026 Trustees payroll, 2027 earnings cap | same draft text/threshold indexing, wage distribution and fiscal receipts, interactions |
| OASDI +1pt base rate | SSA E1.10 *different* ramp option, statutory cap | actual annual phaseup, high-wage rate scope, employee/employer incidence, multiple employers |
| Progressive price indexing | SSA B1.2, actuarial PIA method | cohort rule, existing-beneficiary protection, 75-year aggregate and DI/survivor response |
| Medicare Advantage | MedPAC 2026 $76B relative FFS + $11B related Part B premiums, CMS Trustees | new MA payment code, plan bids/benefits, risk scores, HI/SMI and budget classification |
| Medicare site-neutral | MedPAC fee-setting, CMS HCPCS/OPPS/ASC schedule sources | exact codes, hospital facility effect, site migration, premiums, patient access |
| Defense reductions | Official CBO spending detail by account (budget authority and outlays) | appropriations by account/FY, realistic spendout curves, terminations and offset costs |
| Medicare HI financing | Official 2026 CMS Trustees II.E1, CBO FY trust-fund projections | payroll financing law, trust-fund vs consolidated federal accounting, actuarial horizon |

## Required external acceptance passes

1. **CBO baseline original bytes**: download matched FY2026–36 February 2026 machine-readable data. SHA-256 and compare with excerpt using `run.py check-official-cbo` and `run.py check-official-gdp`; enumerate the catalog with `scripts/fetch_cbo_catalog_all.py` for the full public vintage. Never treat missing account data as zero.
2. **SSA actuarial**: preserve original 2026 HTML pages VI.G1/2/3 with digests, then live compare source rows using `scripts/check_ssa_live.py`. The optional live checker has **not** been executed on SSA originals in this offline build. Actual policy comparisons require cohorts and longitudinal actuarial assumptions.
3. **CMS**: archive full 2026 Medicare supplementary actuarial ZIP and source report, then project Part A separately from Part B/D and beneficiary premium changes. Reconcile to CBO FY Medicare accounting; do not double count Treasury transfers.
4. **JCT tax**: build/validate public IRS SOI aggregates, Tax-Calculator, PolicyEngine or analogous public model against current law, with corporate separately and annual cash fiscalization. Do not represent a simulated public sample as JCT's confidential taxpayer panel.
5. **Household**: link public CPS ASEC, BLS CE and IRS SOI distributions; calibrate national weights and total PCE to BEA; measure missing survey and imputation uncertainty. CBO's published transfer underreporting code is usable for understanding baseline adjustment but explicitly **not** a standalone policy simulator.
6. **Joint model**: implement 12 policy-year effects, nine minimum listed cross-policy effects and unenumerated simultaneous interactions, net-interest feedback, recipient/beneficiary distribution and full solvency. Until cross-checked with held-out agency examples, a total is **NOT_ESTABLISHED**.

## Files

- `docs/EXPANSION_RESULTS.md`: new source-backed numerical work, accounting, test outcomes.
- `docs/SOURCE_INTEGRITY_AND_REPLAY.md`: exact download and verification commands.
- `src/cross_account.py`: excludes internal Treasury funding/interest from public tax savings.
- `src/primary_bridges.py`: published actuarial and national accounts excerpts plus no-score audit.
- `src/distribution.py`: transparent *synthetic-only* income-decile exercise, not a national distributional claim.
- `scripts/check_ssa_live.py`: original-HTML comparator when external HTTPS available, separate from local tests.
