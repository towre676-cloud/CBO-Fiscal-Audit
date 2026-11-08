# Executed evidence and outstanding scoring boundaries — November 6, 2026

## Completed reproducible checks

- **CBO:** FY2026–2036, 21 selected budget series (231 cells), plus 11 directly published GDP levels; internal budget-accounting identities checked. The original full machine-readable CBO files are *not distributed* in this archive. A source fetcher, original Git blob identities and source cross-checks are provided for later end-to-end acquisition.
- **SSA:** Eleven calendar years of public OASI/DI rates and three public individually scored annual OASDI option series (33 option-year values). These are *not* an additive combined package score, nor fiscal-year federal cash impacts.
- **JCT:** The published 2026 ten-line corporate-rate *teaching example*, $350B mechanical and $180B post-adjustment, reproduced only as an illustrated calculation. It is not an estimate for FiscalRazor's proposed legislation.
- **Medicare:** Eleven calendar-year Table II.E1 HI rows and 33 account-year Table II.F1 Part B, D and total SMI rows, from the 2026 CMS Trustees public PDF, transcribed and checked against published stock/flow and account-additivity identities. Calendar-year gross Medicare trust-fund outlays grow from $1,210.0B in 2025 to $2,543.1B in 2035; these figures are not interchangeable with CBO fiscal-year net budget figures.
- **Research-only HI arithmetic:** Under frozen CMS HI cashflows, year-end nonnegative reserves through CY2035 require at least $32.944444...B per year added in 2027–2035. This is neither an official government policy score nor an adequate reserve/long-range solvency proof. The published 75-year HI actuarial deficit is 0.56% of *uncapped HI* taxable payroll, not OASDI's capped taxable payroll.
- **Household readiness:** Explicit 2026 Census CPS ASEC CSV source-member/record-count verification, only executable after acquiring the original ZIP; official BLS corrections for the missing-month 2025 CE PUMD data; fail-closed 160-replicate household variance calculations require actual survey replicate weights and model provenance.

## Not executed, not inferred

1. Original large IRS SOI, Census CPS ASEC, BLS CE PUMD, CMS expanded supplementary ZIP, and complete CBO/SSA bulk tables: **zero full raw release archives acquired in this container**. URLs and source identities do not count as ingested datasets.
2. Household taxes, consumptions, geographic impacts, distributional quantiles, beneficiary effects or weighted national outputs: **no actual reform incidence scores**.
3. Full combined OASI/DI 75-year policy projections, separate HI/SMI modified reserve paths and cross-program interactions: **not computed**.
4. A JCT-style multi-tax-unit and corporate policy estimate, a year-specific federal FY cash/interest score, a combined CBO/JCT score, or any official agency score: **not available**.
5. An enacted or draft legislative package that specifies all effective dates, bases, exemptions, rate pathways, administrative budgets, transition rules and cohort effects: **not fully specified**. No numeric joint package estimate is admitted until it is.

## Critical definition reconciliation

- `CY` is a calendar year; `FY` runs from October of the previous calendar year through September. Tax liabilities are not cash receipts, and defense budget authority is not budget outlays.
- Medicare `HI` (Part A) is legally distinct from `SMI` (Parts B and D). A B/D savings estimate cannot be credited to the HI trust fund without a statutory and accounting bridge.
- CBO's FY Medicare net mandatory outlays and CMS's CY HI+SMI gross trust-fund expenditures cannot be subtracted to infer savings or error; the $388.207B numeric difference in 2035 is an explicit **noncomparability diagnostic**.
- A finite 2026–2035 HI cash shortfall and a 75-year present-value actuarial deficit are distinct financial criteria. Both must be tested in any genuine reform.
- Statistical replicate weights capture sampling variance, not tax-model parameter uncertainty, imputation variability or economy-wide feedback.

## Reproduce

Run with Python >=3.11, from the project root:

```bash
export PYTHONPATH=src
python scripts/verify_package.py
python scripts/analyze_medicare_2026.py
python scripts/check_everything.py
python scripts/fetch_sources.py --inventory
```

For a source-download-enabled Windows machine, follow `README.md` to fetch the authentic ZIPs/files with SHA-256 receipts, inspect exact source fields, and only then produce distributional results or an independent score.
