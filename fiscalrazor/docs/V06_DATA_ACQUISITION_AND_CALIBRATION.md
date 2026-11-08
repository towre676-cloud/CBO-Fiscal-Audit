# Full public-data acquisition and calibration specification

## Current machine-verified acquisition status

The operating container lacks outbound network DNS/access. A direct request to the official CBO machine-readable GitHub CSV failed with a connection error. The current v0.6 release therefore **preserves the selected 2026 sources and their metadata** and **does not claim any complete original public source archives have been acquired**. Run `python scripts/source_gate_v06.py` to regenerate the exact acquisition statuses; `NOT_ACQUIRED` is a hard block, not a green-check state. Some public files require large downloads, and agency confidential files are not downloadable.

## Priority source gates in strict order

| Stage | Source | Canonical data/endpoint | Required validation and use |
|---|---|---|---|
| 1 | CBO 2026-02 10-year FY baseline | https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/ten_year_budget/annual_fy_2026-02.csv | Git blob SHA-1 matching known upstream; all 21×11 selected cells; revenue−outlays, interest/primary identity and debt/other financing |
| 1 | CBO 2026-02 direct FY nominal GDP | https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv | Git blob SHA; 11 direct FY GDP values; target ≤3% GDP exact denominator |
| 1 | CBO revenue, spending by account, trusts | https://github.com/US-CBO/cbo-data | Every detailed account and budget function; millions vs billions; no mixing BA and outlays; OASI/DI/HI bridge |
| 1 | CBO published 2026-02 macroeconomic years + demographics | https://github.com/US-CBO/cbo-data | Calendar/FY mapping, population, wage bases, labor forecast; source version fixed |
| 2 | SSA 2026 Trustees entire single-year workbook | https://www.ssa.gov/oact/TR/2026/ | OASI/DI operations and full calendar-year 2026–2100; validate published income/cost/reserve curves |
| 2 | CMS 2026 Medicare expanded tables ZIP | https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip | HI Part A operations, SMI B/D, beneficiaries, financing and supplementary scenario; validate published totals |
| 3 | Census 2026 CPS ASEC CSV incl. replicate weights | https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asecpub26csv.zip | 2026 public file indexed; 133 MB; validate record counts, field layouts, 160 official replicates, nonfilers and low incomes |
| 3 | Census 2026 separate ASEC replicate weights | https://www2.census.gov/programs-surveys/cps/datasets/2026/march/CPS_ASEC_ASCII_REPWGT_2026.ZIP | 65 MB; construct linked household/person replicas and validate published household distribution reference tables |
| 3 | BLS CE interview/diary PUMD and methodology | https://www.bls.gov/cex/pumd_data.htm | Survey weight calibration; **2025 October–November missing** and 2025 PUMD lacks published reweights, so prefer clean 2024 benchmark or explicitly correct missing data |
| 3 | BEA detailed PCE by product | https://www.bea.gov/data/consumer-spending/main | National expenditure category shares, zero-rate/exempt counterfactual and bridge to CE PUMD; total PCE is not taxable VAT base |
| 3 | IRS SOI public tables, disclosure-limited tax PUF | https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-returns | Income tax distribution, earnings, itemization, corporate receipts; restricted return correlations unavailable; no pretend exact JCT sample |
| 3 | CBO household distribution research ZIP | https://www.cbo.gov/publication/62761 | Independently reproduce household distribution targets before applying reform; identify data years and sample definitions |
| 4 | MedPAC and CMS service-level claims | https://www.medpac.gov/ ; https://data.cms.gov/ | MA coding, bids, FFS comparison, premiums and site-neutral claim conversion; preserve geography and patient mix |
| 4 | JCT methods, published examples | https://www.jct.gov/operations/revenue-estimating/ | Fiscalization, corporate rate behavioral effects and cross-tax effects; teaching example **not official score** |

## On a connected Windows 11 / Git Bash computer

Use Python 3.11+ for **FiscalRazor's own stdlib modules**. For external Tax-Calculator, the **October 30, 2026 release 6.9.0** dropped Python 3.12 and earlier support and removed its previous `AGI surtax` built-in parameters. A separate Python 3.13+ environment should be used for current Tax-Calculator, and our 2% MAGI surtax must be coded as an independent supplementary calculation—not assumed to be implemented by a missing built-in parameter. This is an explicit model-integration dependency.

```
python scripts/acquire_priority_v06.py --list
python scripts/acquire_priority_v06.py --group cbo_core --max-mb 200
python scripts/acquire_priority_v06.py --group actuarial --max-mb 300
python scripts/acquire_priority_v06.py --group household --max-mb 300
python scripts/source_gate_v06.py
python scripts/run_v06.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

The existing `acquisition.py` rejects HTML masquerading as data, incorrect file magic for ZIP/XLSX/PDF/GZIP, unexpected Git blob hashes, missing receipts, path traversal, zero bytes and download size overruns. The current package does not include the CMS and Census originals, or official scoring software under confidentiality restrictions. Preserve every acquired byte, its source URL and SHA-256 receipt, the agency release/vintage, file-format schema, observed field list and transformation script.

## Model and release gates

1. `RAW_BYTES`: all files used in a component downloaded; cryptographic identity and source license established.
2. `BASELINE_REPRODUCTION`: exact agency reference tables recomputed **from the original bytes** with provenance trace to source rows/records; tolerance and units declared.
3. `MODEL_CALIBRATION`: tax, actuarial, medical and household models reproduce known reference estimates on training periods.
4. `HELD_OUT_VALIDATION`: source-hidden held-out provisions/years reproduce within pre-registered numerical tolerances, without parameter retuning.
5. `LEGISLATION_SCORE`: full 12-provision panel with 120 provision-year and 90 designated interaction-year receipts; missing interactions not silently zero.
6. `JOINT_SENSITIVITY`: conditional robustness under interest, GDP, wages, health and coverage responses; OASI, DI, HI, SMI reserve and expenditure separately reconciled.
7. `OFFICIAL_CERTIFICATION`: only actual CBO/JCT/SSA/CMS issued scored results may be attributed to those agencies; public research and reverse engineering cannot create that designation.

At present, **gates 1–7 have not been satisfied for the complete 12-provision reform**. Several synthetic unit calculations and officially published baseline excerpts pass their own narrower tests.

## References checked November 2026

- Census files and sizes: https://www2.census.gov/programs-surveys/cps/datasets/2026/march/
- BLS 2025 2-month gap and PUMD adjustment omission: https://www.bls.gov/cex/ce-pumd-2025-shutdown-impact.htm
- CMS 2026 Trustees' full ZIP: https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds
- Tax-Calculator 6.9.0 release and removed AGI surtax: https://taxcalc.pslmodels.org/about/releases/
- 2026 CBO open-source budgetary feedback: https://github.com/US-CBO/budgetary-feedback-model
