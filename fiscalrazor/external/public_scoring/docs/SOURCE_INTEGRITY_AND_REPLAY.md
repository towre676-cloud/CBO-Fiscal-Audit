# Public-source provenance and replay instructions

The packaged CSVs are **hand-transcribed public-table excerpts**. Their local hashes prove only internal artifact integrity, **not** an exact copy of any agency original. Original source CSV/PDF/HTML/ZIP bytes were not downloaded in this build environment. Public web references establish discoverability and what the agency displays, not complete reproducibility.

## Validate on a network-connected Windows 11 Git Bash / Python 3.11+ terminal

```bash
python -m unittest discover -s tests -q
python scripts/expansion_summary.py
python scripts/export_research_tables.py
python run.py targets
python scripts/fetch_sources.py --dry-run
python scripts/fetch_sources.py --download cbo_annual cbo_gdp cbo_revenue cbo_spending cbo_trust cbo_catalog
python run.py check-official-cbo --path downloads/cbo_annual.csv
python run.py check-official-gdp --path downloads/cbo_gdp.csv
```

Optional full original SSA HTML verification (`pip install beautifulsoup4`; public source layouts may change, in which case comparison fails closed):

```bash
python scripts/check_ssa_live.py
```

Supplementary sources linked and download-capable (not included in ZIP):

```bash
python scripts/fetch_sources.py --download ssa_2026_economy ssa_2026_noninterest ssa_2026_reserves ssa_2027_wage_base
python scripts/fetch_sources.py --download cms_2026_tables medpac_2026_exec
python scripts/fetch_sources.py --download cbo_household_2023_research cbo_household_2023_supp
# CBO publishes code for means-tested transfer underreporting in public surveys:
git clone https://github.com/US-CBO/means_tested_transfer_imputations.git
```

The downloader writes `downloads/download_manifest.json` with the original byte count, SHA-256 and source URL *if* retrieval succeeds. Keep frozen February 2026 CBO budget vintage separate from 2026 SSA/CMS Trustees CY estimates and 2025 BEA PCE observations. CBO's public transfer imputation package uses Stata and **its authors advise against using it for policy simulations**. This package only indexes it and does not run it.

## Evidence taxonomy

1. Agency source web record: independently discovered/visually verified table or methodology, manual excerpt, not a verified complete original byte copy.
2. Local arithmetic and conservation: source arithmetic reproduces from included excerpts; 53 offline tests; distinct from an independent replication of the official published software.
3. Derived actuarial measure: SSA percentage-point annual balance × its own Trustees payroll; **not** a CBO/JCT FY federal cash-flow estimate.
4. Synthetic unit tests: worked payroll interaction, household tax incidence, defense BA spendout, Treasury transfers; mechanics only, not statistical estimates.
5. Unscored reform: legal detail and validated full 10-year data missing; **NOT_ESTABLISHED** rather than a made-up zero.

`SHA256SUMS.txt` is generated for all the packaged regular files at export time and excludes itself. Download manifests use separate independent source hashes, never the package's self-hashes.

**Additional anti-fake-score gate:** `src/receipt_validation.py` requires an existing reviewed JSON record in `receipts/`, row-bound SHA-256, actual downloaded original SHA-256 and executable calculation-code SHA-256. See `docs/RECEIPT_SCHEMA.md`. No such reviewed program-and-source policy receipts are present in this archive; therefore the combined score remains blocked.
