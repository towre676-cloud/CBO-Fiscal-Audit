# FiscalRazor: substantial public-scoring expansion, 2026-11-06

**Independent research only. No official CBO/JCT score; no integrated SSA/CMS actuarial policy score; no independently calibrated ten-year package estimate.** The source table excerpts were located on public agency web pages and manually transcribed. The original complete published files have NOT been downloaded and hash-checked in the offline build container; passing the tests below means internal arithmetic is correct, not that all transcriptions were independently verified byte-for-byte.

## Concrete outputs

| Official historical/projection reference | Locally derived result and limitation |
|---|---|
| February 2026 CBO FY2036 revenue 8,300.755B, outlays 11,416.142B, nominal GDP 46,712.1423975B | Baseline signed deficit −3,115.387B; 3% GDP target deficit 1,401.36B; **baseline FY2036 improvement required ~1,714.02B**. Target, not scored savings |
| SSA Trustees 2026 VI.G3 CY2027 OASDI noninterest income 1,480B and cost 1,799B | −319B combined OASDI operating balance; separate OASI and DI rows retained. Not FY federal budget cash |
| SSA E2.5 option CY2035 2.52 points of 16,486B OASDI taxable payroll | **415.4472B** approximate annual actuarial-balance improvement, not FY receipt |
| SSA E2.5 option CY2036 2.53 points of 17,125B OASDI taxable payroll | **433.2625B** approximate annual actuarial-balance improvement; ±0.85625B from rate rounding alone. Not FY receipt |
| CMS HI Trustees 2026 Table II.E1 | CY2027 −10.5B fund change; 2032 end reserves 28.1B, depletion Q2 2033, 2033 negative reserves **hypothetical scheduled payouts** |
| MedPAC 2026 MA benchmark | ~$76B above corresponding FFS Medicare spending (57B selection + 22B coding −3B other); associated ~11B additional Part B premiums. **Neither number automatically equals recoverable federal savings** |
| BEA NIPA CY2025 PCE 20,870.150B | 5% × all PCE = **1,043.5075B**. This is *not* VAT revenue; actual tax base, credits, legal exemptions, prices, compliance, rebates and future-year volume still unscored |

Official source anchors: CBO budget https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/ten_year_budget/annual_fy_2026-02.csv and GDP https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv ; SSA https://www.ssa.gov/oact/TR/2026/lr6g1.html , https://www.ssa.gov/oact/TR/2026/lr6g2.html , https://www.ssa.gov/oact/TR/2026/lr6g3.html and option https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html ; Medicare https://www.cms.gov/oact/tr/2026 ; MedPAC https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_ExecutiveSummary_MedPAC_Report_To_Congress_SEC.pdf ; BEA/FRED https://fred.stlouisfed.org/release/tables?eid=43861&rid=53.

## Public source discoveries that materially improve reconstruction

- **CBO 2023 income distribution, published Sep 24 2026:** https://www.cbo.gov/publication/62761, with [additional researcher data](https://www.cbo.gov/system/files/2026-09/62761-additional-data-for-researchers.zip) and [supplemental XLSX](https://www.cbo.gov/system/files/2026-09/62761-supp-data.xlsx). Files are indexed but not present locally.
- **Genuine CBO Stata underreporting code:** https://github.com/US-CBO/means_tested_transfer_imputations . CBO says these imputed CPS ASEC receipt amounts target Medicaid/CHIP, SNAP, SSI and federal housing programs. **Their own README explicitly warns they are not for causal policy simulation or state-level analysis**; they may inform baseline calibration only. This code has not been run here.
- **IRS SOI public 2023 tax tables:** https://www.irs.gov/statistics/soi-tax-stats-individual-statistical-tables-by-size-of-adjusted-gross-income. Directly applicable to validating income-tax base levels and AGI strata; aggregate data cannot reproduce confidential return-level JCT interactions.
- **SSA 2027 statutory max covered wage:** $192,300, from https://www.ssa.gov/news/en/cola/factsheets/2027.html ; 2026 $184,500. Source data and 2027 high-earner payroll mechanical overlap tests included.

## Implemented accounting and computational protections

1. `src/primary_bridges.py` audits all eleven SSA economic and OASDI cash series, 2025–33 reserve stock/flow identities, 2025–35 Medicare HI flows, detailed BEA PCE hierarchy and MedPAC 57+22−3=76. Exposes **explicit original-source-byte verification = false**.
2. `src/cross_account.py` distinguishes FY consolidated public receipts and public outlays from intragovernmental transfers and fund interest. **Synthetic conservation example:** +40B payroll tax receipts, −20B provider outlays, +30B internal Treasury→HI transfer and +5B fund interest yield +60B unified primary cash improvement, not +95B; fund reserve effects differ. This is a test fixture only.
3. `src/fiscalization.py` maps user-supplied *calendar-year cash* to October–September fiscal years. Uniform monthly weight is only a timing demonstration. Its SSA rate-to-FY exercise is explicitly labeled **NOT_VALID_AS_FY_TAX_REVENUE_OR_FEDERAL_SCORE**.
4. `src/spendout.py` distributes defense BA reductions across future-year *outlays* using supplied account-specific lags. No fake default lag factors; dollar conservation and post-window residual are verified.
5. `src/payroll_interactions.py` handles the **actual 2027 $192,300 wage maximum** and a hypothetical high-wage 12.4% tax over $250,000. For one $300k W2 earner, additional high-wage tax is $6,200; a hypothetical combined +1ppt tax on the standard base is $1,923; if that extra point also applies above $250,000, interaction is **+$500** and joint increment **$8,623**. This cannot be population-scaled without actual worker wage microdata and legislation.
6. `src/distribution.py` correctly weights and ranks supplied households to quantiles and handles VAT/rebates; synthetic tests pass but `population_quality_gate` **fails closed** without actual Census CPS, BLS CE, IRS SOI, and BEA alignment. The synthetic results are **not** household effects in the US economy.
7. `scripts/export_research_tables.py` produces 33 derived SSA single-option-year actuarial equivalences and 11 CMS HI annual operation rows, with source URLs and measure labels. `scripts/expansion_summary.py` displays core calculations and unresolved gates.

## Validation status

- **56 public sources indexed** (40 retained + 16 new), source originals still require independently fetched byte hashes.
- **53 offline automated tests passed** (original 18 retained + 35 new) on transcribed data and implementation invariants.
- **120 provision-year and 90 specified interaction-year federal cash entries remain missing.** This is a minimum coverage gate, NOT proof that pairwise modeling suffices for a fully joint dynamic score.
- **All 12 proposed reforms remain UNSCORED**; the earlier $12.11 trillion claim is conditional and has not been independently established.

Run: `python -m unittest discover -s tests -q`, `python scripts/expansion_summary.py`, `python scripts/export_research_tables.py`. See `FRONTIER_AND_EVIDENCE_MATRIX.md` and `SOURCE_INTEGRITY_AND_REPLAY.md` for next validation gates.
