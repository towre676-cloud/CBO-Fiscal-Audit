# FiscalRazor v0.9.0 — Original-source admission and measured baseline capacity

**Build date:** 2026-11-07. This is an independent fiscal research codebase, **not** an official CBO, JCT, SSA, or CMS score. All 12 draft provisions, the 66 possible pairwise interactions, and the independent debt-stability work are preserved from v0.8. Existing earlier version READMEs remain for provenance.

## New completed work

1. **Original agency source discovery.** The matched U.S. CBO 2026-02 catalog has 18 repository file identities with Git blob SHA-1 pins. The full raw files are **not stored** in this ZIP. `src/fiscal_data/primary_ingest_v08.py` accepts originals only after publisher hash, count, format, HTTPS acquisition receipt, and local integrity checks (Git SHA-1 for CBO; captured HTTPS origin + SHA-256 for public-use sources without publisher SHA). It rejects inconsistent and incomplete raw data.
2. **Official FY2027–2036 CBO consumption benchmark.** Ten `pce` observations from `data/economic/historical_economic/annual_fy_2026-02.csv`, Git blob `e0799d7972696a65823e5d90cf36486d21903520`, are preserved as source excerpts in `data/v09`. Values are FY nominal **billions USD**, not calendar-year household expenses. They are NOT a complete original byte-level copy.
3. **Mechanical VAT-capacity calculation**, `src/fiscal_data/v09_capacity.py`. For 5% tax-exclusive VAT on all projected PCE, 100% compliance and 20% of gross receipts reserved for rebates, FY2036 math is gross $1,599.481561B, after rebate $1,279.585249B, and $434.437479B below the frozen CBO February 2026 gap to a 3%-GDP deficit. All-PCE fixed-base rate to close FY2036 gap is 6.697571%. This is NOT a realistic VAT revenue score, a statement that PCE equals taxable consumption, or a legislative recommendation. We supply a 60-row sensitivity table for *hypothetical* taxable-PCE fractions 50–100%. Every scenario is explicitly labeled assumed.
4. **2026 CPS ASEC 160-replicate variance estimator**, `src/fiscal_data/v09_survey.py`: full-sample weighted mean, 160 replicate-weight means, SDR SE = sqrt(4/160 * sum((replicate-full)^2)), and an O(160)-memory streaming implementation. It rejects undocumented columns, broken weights, incomplete replicates and incorrect eligibility. `scripts/estimate_cps_2026_sdr_v09.py` requires the actual Census ZIP and an explicit reviewed record/member/weight mapping; no national descriptive household result is published in the absence of original microdata.
5. **Fixed a real downloader defect:** IRS 2023 ZIP/AGI `23zpallagi.csv` is about 209 MB, exceeding the prior 150 MB cap. Source maximum is now 260 MB with independent size, HTTPS and CSV validation. 2024 BLS CE Interview and Diary official direct CSV archives are registered for an appropriate historical baseline; 2025 direct archive availability must be rechecked, including BLS's documented October–November noncollection restrictions. IRS ZIP AGI data remain **geographic aggregates**, never individual tax returns.
6. **Stronger gates:** a present but corrupted CBO original fails even in exploratory mode, and excerpt rows use explicit checks rather than Python `assert`, which disappears under `-O`. Twelve-provision/66-pair inventory is checked on every replay. The strict original-source replay intentionally fails while originals are missing.

## Exact existing evidence status in this release

| Evidence | State |
|---|---|
| CBO catalog paths, row counts and publisher Git blobs | Verified via public repository connectors; 18 entries |
| FY2027–2036 CBO PCE and frozen deficit-target excerpts | Source-pinned, arithmetic replayable |
| Complete CBO original files present in release | **0 of 18** |
| 2026 CPS household original ZIP and separate replicate original | **Not locally acquired** |
| BLS CE 2024/2025 original PUMD in this release | **Not locally acquired** |
| CMS expanded Medicare 2026 original ZIP | **Not locally acquired** |
| IRS original 2023 ZIP AGI CSV | **Not locally acquired** |
| Nationally calibrated tax/benefit/consumption household reform model | **Not established** |
| Independent combined cash-flow / OASI / DI / HI reform forecasts | **Not established** |
| Official CBO/JCT/SSA/CMS combined score | **Not issued** |

There is **no claim** that all federal reform science can be finished from public data alone: protected JCT linked tax-return samples, agency production scorers and unpublished policy assumptions are inaccessible as unrestricted public downloads; an official score requires legislative text and agency action.

## Commands, Python 3.11+

```bash
# Offline: exact source-excerpt math and the evidence gate; never converts excerpts into originals
PYTHONPATH=src python scripts/replay_v09.py
PYTHONPATH=src python -m unittest discover -s tests -q
(cd external/public_scoring && python -m unittest discover -s tests -q)

# On a network-connected machine, fetch and verify the real originals
python scripts/acquire_real_federal_v08.py --fetch-all-cbo
python scripts/replay_real_v08.py --require-originals
python scripts/acquire_real_federal_v08.py --fetch-available-public
PYTHONPATH=src python scripts/replay_v09.py --require-originals

# CPS household statistical estimates require a reviewed mapping and source admission.
# DO NOT fill mapping fields by guessing from similar past-year data.
python scripts/estimate_cps_2026_sdr_v09.py --mapping docs/CPS_MAPPING_REVIEWED_BY_OPERATOR.json
```

First execute `python scripts/inspect_cps_asec_2026_schema_v09.py` to inspect the actual verified Census ZIP and discover candidate column names without certifying them. The last command deliberately requires an operator-prepared JSON file that is **not shipped as a falsely verified mapping**. Consult Census's 2026 ASEC dictionary and replicate-weight instructions. Census publishes both its 2026 CSV (including replicate weights) and its separate ASCII replicate-weight distribution; do not join them by row order unless the official usage instructions establish that invariant. Document keys and record universe explicitly.

### Fiscal methods and limitations

- FY PCE is a national-accounts *measurement* with consumption and imputation details; it cannot be used as a statutory taxable VAT base without BEA PCE product-level allocation and legal rules.
- The 20% rebate share is an explicit toy allocation. Actual credits must be simulated at household level and fiscally reconciled; no estimated rebate adequacy is implied.
- Static gaps are from the **February 2026** CBO baseline, not a fresh 2026-Nov-law forecast. The source vintage must be frozen before any scoring experiments.
- No independent interest or general-equilibrium model is deployed in this release. Source-data admission is necessary but insufficient for legislative scoring.
- A 12-provision package requires all 120 year-specific effects, interactions, feedback, 75-year entitlement obligations, and nationally representative household data. Unmeasured values stay missing, never silently zero.

## Main outputs

- `results/v09/cbo_fy_pce_all_base_vat_capacity_2027_2036.csv` — 10 source-pinned annual rows.
- `results/v09/hypothetical_vat_base_fraction_sensitivity.csv` — 60 assumption-labeled stress rows.
- `results/v09/evidence_status.json`, `source_admission_status.json`, `provision_admission_status.json` — machine-readable gates.
- `data/v09/cbo_fy_pce_2027_2036_source_excerpt.csv` and `data/v09/source_receipts.json` — exact evidence lineage.

## Official starting points

- CBO original data: https://github.com/US-CBO/cbo-data/blob/main/data/economic/historical_economic/annual_fy_2026-02.csv
- CBO February 2026 baseline: https://www.cbo.gov/publication/61882
- Census CPS ASEC 2026, dictionary, replicate files: https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html
- IRS ZIP AGI public aggregates: https://www.irs.gov/pub/irs-soi/23zpallagi.csv
- BLS CE public-use data: https://www.bls.gov/cex/pumd_data.htm
- BLS 2025 noncollection warning: https://www.bls.gov/cex/ce-pumd-2025-shutdown-impact.htm
- CMS Medicare 2026 annual/supplement: https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds
