# FiscalRazor cross-session technical reconciliation — 2026-11-06

## Evidence and scope

Audited two actual ZIP files, not summaries: (A) `FiscalRazor_Federal_Actuarial_v0.4.0_2026-11-06.zip` (78 entries; independent test suite 101) and (B) `FiscalRazor_Public_Scoring_Expansion_2026-11-06.zip` (49 entries; independent test suite 53). Each original test suite was executed on clean extraction. They cover different code structures and include some conceptually overlapping test cases. The independently authored B package is preserved unmodified at `external/public_scoring/`. The v0.5 cross-artifact checks are executable in `src/fiscal_data/reconcile_public.py`, which rejects conflicts rather than choosing a preferred number silently.

## Primary source table alignment

| Common subject | Source A | Source B | Cross-artifact status |
|---|---|---|---|
| Direct CBO February 2026 FY GDP | 11 FY levels | 11 FY levels | 11/11 equal as decimal numbers |
| CBO FY budget baseline | 21 fields × 11 years | Seven shared fields × 11 years | 77/77 common field-year values identical |
| SSA annual single options E2.5 / E1.10 / B1.2 | 3 × 11 indexed as columns | 3 × 11 rows | 33/33 option-year values equal |
| CMS HI annual accounts | 11 years, seven fields | 11 years, nine fields | 55/55 shared numeric field-year comparisons equal; actuarial statuses agree |

**Total 176 matched field-year comparisons.** This establishes agreement between **two secondary excerpts**, not complete independently acquired raw source bytes. Matching manually transcribed excerpts does not prove the original government dataset was acquired or the tax/actuarial production model replicated.

FY2036 CBO baseline signed deficit −3,115.387 billion; direct GDP 46,712.1423975 billion. A 3%-of-GDP annual deficit target is 1,401.364271925 billion and the **static baseline deficit improvement required is 1,714.022728075 billion**. Neither model supplies a validated policy package that achieves it.

## New official benchmark discoveries admitted from package B

1. **SSA cohort and trust fund bridge.** `ssa_trustees_2026_economic_cy.csv`, `ssa_trustees_2026_oasdi_noninterest_cy.csv`, and `ssa_trustees_2026_oasdi_reserves_cy.csv` add separate OASI, DI, combined OASDI noninterest income/cost and reserve projections. Published single-provision rate changes translate to an estimated CY2035 $415.4472 billion and CY2036 $433.2625 billion actuarial annual-balance dollar *equivalences* for option E2.5, not FY unified-budget revenues. Percentage rates are rounded to two decimals, so a precision interval exists. Calendar-year benefits and FICA tax flows cannot be inserted directly into fiscal-year CBO results. The OASI fund is legally separate from DI; OASI is projected to exhaust reserves Q4 2032, while a hypothetical *combined* OASDI would exhaust Q3 2034. See https://www.ssa.gov/oact/trsum/ and https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html.
2. **SSA 2027 wage cap.** SSA's statutory 2027 Social Security taxable wage maximum is $192,300 (2026 $184,500). This can anchor synthetic single-worker tax tests, but is not a substitute for weighted tax-record income microdata. https://www.ssa.gov/cola/factsheets/2027.html.
3. **MedPAC Medicare Advantage reference.** MedPAC's March 2026 projected **$76 billion** in MA payments above estimated comparable fee-for-service expenditures (components −3 base, +57 favorable selection, +22 risk coding) and a related $11 billion of Part B premium impact. Neither is automatically recoverable statutory savings; reform requires plan/bid/risk/coding response and HI/SMI mapping. https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch12_MedPAC_Report_To_Congress_SEC.pdf.
4. **BEA consumption.** BEA's 2025 PCE total $20,870.150 billion (2025, historical national accounts) is verified by BEA/FRED and internal category aggregation. Mechanical `0.05 × PCE = $1,043.5075 billion` **does not measure** net VAT revenue, because actual statutory tax base, imputed consumption, exemptions, refunds, avoidance, price changes and household offsets are unspecified. https://fred.stlouisfed.org/series/PCECA.
5. **Applied accounting tools.** B adds account-external vs intragovernmental-transfer conservation, fiscalization of specified actual CY cashflows to FY, defense budget-authority spendout lags, an OASDI wage-cap interaction fixture, a synthetic-only VAT/rebate distribution test, and an evidence receipt gate. These are retained as separately executable modules; they are not recalibrated or described as real policy scores.

## Capabilities retained from A, not replaced

A has the broader CBO 21-indicator baseline, 11 CMS HI rows **plus 33 CMS Part B/D/SMI account-year rows**, the HI funding-floor derivations, a detailed 2025 Consumer Expenditure missing-month weighting diagnostic, CPS 2026 replicate-weight and field preflight checks, 51 registered source entries, and 101 test cases. They remain operative. The $32.94444 billion/year HI year-end-floor is a *frozen-reserve arithmetic example*, not an official 75-year solvency estimate. The 75-year HI actuarial deficit uses the *uncapped* HI tax base; the 75-year OASDI deficit uses *capped* OASDI taxable payroll.

## Data registry collision

A lists 51 sources; B lists 56 entries. The bare sum 107 is **not a distinct dataset count**. After simple host/path normalization, the two catalogs yield 93 endpoint paths, some of which are alternative landing pages and downloads for the *same* scientific source. In B, 56 entries correspond to 54 normalized endpoint paths; the union is for navigation, not a claim of 93 validated datasets. All original large government source archives remain **unacquired** in the archived work. The GitHub government repository source blob identifiers and web-source readings give metadata or excerpt confidence, not a full original data replay.

## What remains unsolved

1. Enacted-law, effective-date, itemization/SALT, VAT invoice, payroll threshold and benefit-indexing parameters for **one coherent 12-provision draft law**.
2. Federal FY2027–2036 **ten-year unified score**, cross-tax interactions, receipts vs accrued liabilities, defense authorization→outlays, and CBO-consistent interest response.
3. OASI / DI **75-year joint actuarial** effects with reserves and scenario demographic/benefit interactions, not summing single options.
4. Medicare **HI and SMI** annual reserve/premium/outlay responses to actual legal reforms, not a static +$32.94B funding-floor example.
5. Real CPS/CE/IRS/BEA-linked household microsimulation, calibrated national samples and 160-replicate sampling uncertainty, with additional uncertainty for imputation/behavior.
6. Original-byte acquisition and hash checking of the source releases and authentic CBO/JCT/SSA/CMS comparisons. Full restricted production JCT tax-return data and agency models are not in the public domain.

**Research status:** no authorized or agency-issued combined score, no valid inferred reform savings. The $12.11 trillion figure is *not* an established result. A public research approximation cannot be labeled an official CBO/JCT/SSA/CMS score.

## Reproduction command

Run from this directory on Python 3.11+:

```bash
python scripts/replay_all_v05.py
```

This runs A + cross tests, runs B's original tests separately, reconciles 176 common data cells, and emits `results/v05_reconciliation.json` with explicit data and official-score status. The archive includes source manifests of both packages, but source hash verification is not a substitute for an agency original-byte download and upstream content integrity check.
