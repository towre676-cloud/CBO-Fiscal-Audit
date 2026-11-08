# FiscalRazor v0.8.0 — Real Public-Source Ingestion and Independent Research

**Release evidence status: NO complete original government source archives acquired in this isolated container.**

The code actually attempted four different original-source downloads (CBO, Census, CMS, IRS). Each failed with `Temporary failure in name resolution` because outbound access to the government and GitHub download hosts is unavailable in the container. These failed attempts are retained under `results/v08/source_download_attempt.json` and `download_attempt_stderr.txt`. This is **not** a successful data acquisition, national household estimate, or joint official CBO/JCT/SSA/CMS score. The package supplies tested ingestion software and source-excerpt baseline arithmetic now, not fabricated raw datasets.

## Immediate outputs from this run

1. `results/v08/fiscal_objectives_2027_2036.csv`: all 10 actual published February-2026-CBO baseline FY arithmetic comparisons of the 3% deficit target against the one-year no-rising-debt/GDP target. These are **unscored policy objectives**, not effects of a reform.
2. `results/v08/cbo_18_original_receipts_required.csv`: 18 SHA-1 Git blob source pins and expected record counts totaling 97,459 official CBO rows. Complete originals must be downloaded locally to pass the original-byte verification gate.
3. `results/v08/twelve_provision_source_gates.json`: source-availability and model-admission status for all 12 legally defined provisions (all unscored).
4. `results/v08/raw_cbo_replay.json`, `public_microdata_replay.json`, and `verification_receipt_v08.json`: explicit failures/blocked states where genuine local original source files are absent.
5. `src/fiscal_data/primary_ingest_v08.py`: original-source HTTPS acquisition, atomic transfers, original raw Git-SHA verification for CBO and HTTPS provenance receipts plus ZIP/CSV format tests for the other agencies; separate household and IRS aggregate processing. An external ZIP with no publisher checksum is never called cryptographically publisher-pinned.
6. `src/fiscal_data/research_v08.py`: independent ten-year fiscal arithmetic, per-provision raw-input requirements, and a mathematical interval test requiring **all 66 pairwise interactions**, explicit higher-order residual and debt-service bounds. It rejects missing values rather than substituting zeros.

## Run with real internet access

From the extracted repository root on Windows 11 PowerShell:

```powershell
.\RUN_ACQUIRE_REAL_V08_POWERSHELL.ps1
```

Or on Windows Git Bash:

```bash
bash RUN_ACQUIRE_REAL_V08_GIT_BASH.sh
```

Or separately:

```bash
python scripts/acquire_real_federal_v08.py --list
python scripts/acquire_real_federal_v08.py --fetch-all-cbo
python scripts/replay_real_v08.py --require-originals
python scripts/acquire_real_federal_v08.py --id cps_asec_2026_csv --id cps_asec_2026_replicates --id cms_medicare_2026_expanded --id irs_soi_2023_zip_agi
python scripts/replay_real_v08.py --require-originals
PYTHONPATH=src python -m unittest discover -s tests -q
```

The download inventory includes **18 CBO + seven other source entries**; this is a scoped operational intake, **not** the full universe of federal data. The pre-existing 51-entry research catalog is preserved separately. BLS 2025 Interview/Diary public-use datasets are confirmed on BLS's official landing page, but their direct 2025 CSV URLs were not reliably recoverable in this session, and the program **intentionally refuses to invent a URL**. BLS documents missing October/November 2025 data and publishes adjustments; no national VAT-incidence score can be inferred from the current CE aggregate tables alone.

The `.github/workflows/acquire-official-data.yml` workflow is also included. To use it, commit the extracted project to a GitHub repository and run the workflow manually. It is **not** deployed or run on a GitHub runner in this chat. Public microdata archives may use significant Actions storage and are uploaded only when selected.

## Data-source and inference boundaries

- **CBO:** February 2026 vintage only; 18 Git-pinned originals needed. Detail spending account values are in **millions**, aggregate 10-year budget in **billions**; account budget authority is **not outlay**. `strict_value_pivot` rejects overlapping (year,variable) keys in the 116 duplicate trust-fund records and 11 duplicated tax-parameter records.
- **Census CPS ASEC 2026:** 88,026 total household records; 53,321 interviewed households. Household income field is `HTOTVAL`, quintile/5%-rank is `HPCTCUT`, not imaginary `HTOTVAL8`/`HPCTCUT2`. `HSUP_WGT` has two implied decimals. Census 2026 public file includes person/household survey data and replicate weights; a credible distributional standard error needs survey-design treatment.
- **IRS:** `23zpallagi.csv` is ZIP × AGI group aggregated statistics. It is **not** individual tax-return microdata. Public tax-return aggregates do not determine within-cell correlations, filing status, credits or elasticity.
- **CMS:** Medicare 2026 expanded supplementary ZIP describes actuarial baselines, not a legislative reform score or a Medicare HI solvency certificate.
- **Social Security:** SSA option-year actuarial results measure **calendar-year percentages of current-law taxable payroll** and are not automatically converted to fiscal-year cash receipts.
- **JCT:** confidential production return samples and complete internal scoring software are unavailable as ordinary public downloads. A public model can be independently calibrated, but it is never attributed to JCT as its official combined score.

**National reform score status: `NOT_ESTABLISHED` for all twelve provisions.** The deterministic CBO FY2036 static deficit-gap threshold is **$1,714.022728075 billion**, but no measured combination of proposals is claimed to have reached it. The FY2036 one-year debt-ratio-stability threshold of **$1,042.80050811994 billion** is a different policy objective, not a proof of long-run solvency.

## Sources

- CBO official repository: https://github.com/US-CBO/cbo-data
- Census 2026 ASEC: https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html
- CPS 2026 sample record counts: https://cps.ipums.org/cps/sample_sizes.shtml
- BLS CE PUMD: https://www.bls.gov/cex/pumd_data.htm
- CMS 2026 Trustees: https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds
- IRS SOI: https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-returns
- Full earlier FiscalRazor source/status documentation is retained in this package.
