# Current release: v0.9.0

Read **[README_V09.md](README_V09.md)** for current source-admission and research results. Historical notes below are retained for provenance.

# FiscalRazor v0.8.0 — Real-Source Intake and Independent Research

**START HERE: [README_V08.md](README_V08.md)**. The v0.8 release actually attempts government archive downloads and records failed network transport, provides Git-SHA-pinned CBO sources, provenance-checked source importers, corrected CPS household schema, a source-completeness matrix for all 12 provisions, a 66-interaction interval gate and a GitHub Actions workflow to run when connected. It preserves all earlier legislation and scores but **does not claim raw government datasets were acquired in this isolated container or any national reform scored.**

---

# FiscalRazor v0.6.0 — preserved earlier handoff

**[Start with README_V06.md](README_V06.md)** for the 12-provision legal research specification, the independent stabilization work, source-acquisition sequence, and all v0.6 verification commands. The following material is the preserved v0.5.0 handoff.

---

# FiscalRazor v0.5.0 — cross-session integration

**Status:** independently tested reconciliation of FiscalRazor v0.4.0 and the November 6 Public Scoring Expansion. No combined policy score, no household incidence estimate, and no official CBO/JCT/SSA/CMS scored legislation. The complete original public source archives are not included or represented as acquired.

**One-command verification** on Python 3.11+: `python scripts/replay_all_v05.py`, followed by `python scripts/verify_package.py`. The latter checks all packaged file hashes. The replay executes 161 test cases across the two independently retained codebases, including 7 new cross-project checks of 176 overlapping published numeric fields. Source originals and agency production models have not been independently replayed.

**Main result:** [docs/RECONCILIATION_2026_11_06.md](docs/RECONCILIATION_2026_11_06.md). Original second-session code and tests are preserved in `external/public_scoring/`; the added integrated comparator is `src/fiscal_data/reconcile_public.py` and its numerical receipt is `results/v05_reconciliation.json`.

**Source-package exact SHA-256:** `docs/SOURCE_PACKAGE_PROVENANCE.json`. Source registry entries: 51 vs 56, with simple host/path normalization giving 93 navigable endpoint paths, not 93 distinct original government datasets.

---

## Previous v0.4.0 project instructions retained below

# FiscalRazor · v0.4.0 — Medicare actuarial baseline and household-source preflight

**Prepared November 6, 2026.** Goal: build an auditable data and research engine for federal budget, tax, Social Security, Medicare and household reform analysis. No unscored policy savings are presented as facts.

## Exactly what has been executed

- 51 public sources identified; 20 CBO exact-version files have GitHub identity SHA-1 recorded and/or checked through directory/file metadata. Additional official landing pages and direct public-use endpoints are documented. The 51 do not claim to comprise every useful public dataset.
- Materialized and tested: **231 selected CBO fiscal values plus 11 directly published FY GDP values** (21 variables by 11 years, FY2026–FY2036), **11 annual rows of SSA IV.B1 plus 33 single-provision SSA actuarial points** (OASI/DI/combined OASDI, years 2026–2036), **2026 SSA/CMS trustee summary**, **FY2026 Treasury totals**; JCT 10-line 2026 illustrative tax-scoring example. These are source-grounded extracts, not full official archives.
- Acquisition of complete large CBO/Census/CMS/IRS archives: **not completed in the cloud sandbox** because it has no usable outbound download connection. Direct download URLs, immutable CBO Git blob hashes and a validated fetch-and-admit script are included for use on a connected computer.
- The main audit rejects incorrect budget identities, debt financing omissions, bad cross-fund arithmetic, expired/unsupported raw files, missing household incidence data, missing joint CBO/JCT score and other unsupported claims. See `results/checks.json` for the actual test count.
- Independent fiscal gap: CBO's February 2026 FY2036 3%-of-GDP deficit gap is $1,714.022728075B using the direct CBO fiscal-year GDP source. This is NOT a combined policy effect or an updated November current-law forecast.

## Reproduce locally (Windows 11 Git Bash or PowerShell, Python 3.11+)

```bash
cd FiscalRazor_v0_4
export PYTHONPATH=src
python scripts/check_everything.py
python scripts/fetch_sources.py --inventory
```

To acquire **all directly linked public source files**, from a working internet connection (some may be very large):

```bash
python scripts/fetch_sources.py --all-direct --allow-large
```

For a smaller, first-stage fetch:

```bash
python scripts/fetch_sources.py --id cbo_budget_10yr --id cbo_budget_history --id cbo_spending_detail --id cbo_trust_funds --id ssa_oasdi_2026_excel
python scripts/fetch_sources.py --id cps_asec_2026_csv --id cps_asec_2026_repwgt --allow-large
python scripts/fetch_sources.py --id cbo_household_research_2023
python scripts/fetch_sources.py --inventory
```

Every file receives a SHA-256 receipt. CBO downloads must reproduce their verified exact Git blob SHA-1 or are rejected. The source registry has 51 entries in `data/source_catalog.json`. Some are officially verified landing pages or APIs requiring an additional acquisition adapter; `--all-direct` cannot fetch those and does not claim to.

Verify the original CBO file against the 231 selected source cells:

```bash
PYTHONPATH=src python - <<'PY'
from fiscal_data.cbo_source import validate_full_source
print(validate_full_source())
PY
```

Inspect the actual Census CSV archive after download (no guessed column names):

```bash
python scripts/inspect_households.py data/raw/cps_asec_2026_csv/asecpub26csv.zip
```

Household incidence uses *actual before/after household policy-model records*: not available here, so no household tax result was produced. See `schemas/household_incidence_input.md` and `scripts/run_household_incidence.py` for the required inputs, provenance and output.

## Direct outputs

- `dashboard.html`: usable offline, 11-year CBO table, 11-year SSA table, verified source list and actuarial dates; no outside assets.
- `results/verified_baseline_2026_2036.csv`: source-derived annual fiscal table.
- `results/source_acquisition_inventory.csv`: exact source statuses. `NOT_ACQUIRED` means source found but not materialized.
- `results/objective_2036.json`: static accounting target derived from CBO.
- `results/verification_status.json`: executed/blocked status of science and data.
- `data/projection_reconciliation_events.csv`: verified 2026 tariff revision and FY2026 actual-vs-CBO difference, **not applied as an invented annual path**.
- `data/official_score_admission_template.json`: missing combined government scores explicitly recorded as not issued.
- `docs/ARCHITECTURE.md` and `docs/OPERATING_PLAN.md`: technical specifications for advancing all four evidence streams.

## Definitions of success

`PASSED_INCLUDED_DATA_AND_SOFTWARE` means our included sources passed the specified arithmetic and corruption tests. A verified SHA validates file identity, not substantive scientific correctness. `NOT_ACQUIRED` is not a passing source result. An official CBO/JCT/SSA/CMS score can only be credited when the corresponding agency has actually issued it for one precisely specified package, and independent audit has confirmed what it covers.

## Public source pointers

CBO public releases: https://www.cbo.gov/data/budget-economic-data

CBO machine-readable release versions: https://github.com/US-CBO/cbo-data

SSA 2026 single-year tables: https://www.ssa.gov/oact/tr/2026/lrIndex.html

CMS Medicare Trustees: https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds

Census ASEC 2026: https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html

CBO household distribution 2023: https://www.cbo.gov/publication/62761

Treasury MTS actuals: https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/

JCT tax expenditure estimate: https://www.jct.gov/getattachment/fe301c56-965c-48c9-ac06-52b7b6765b05/x-45-25.pdf

Tax-Calculator 6.9.0: https://taxcalc.pslmodels.org/

## Survey uncertainty: CPS ASEC's actual design

The implemented `fiscal_data.survey` module uses the Census Bureau's **160 successive-difference replicates** and documented variance formula

`Var(theta) = (4/160) * sum_{r=1}^{160} (theta_r - theta_full)^2`.

The module **does not fabricate 160 replicates**: all 160 must be computed from the same estimator with the actual 2026 Census replicate weights and exact household / tax-unit join. It refuses missing or duplicated replicate indices, NaN/infinite values, and input lacking source and weight SHA-256 metadata. The 160-replicate formula estimates survey sampling variance, **not policy parameter, imputation, macroeconomic, or model uncertainty**. See `docs/SURVEY_UNCERTAINTY.md` and `scripts/check_survey_uncertainty.py`.

For the latest result of the executable tests, see `results/checks.json` rather than relying on a version-number promise.

## Session reconciliation, v0.3

Incorporates source-verified changes from the November 6 Public Scoring Reconstruction:
CBO direct FY GDP, three SSA option-year benchmark series, and the JCT ten-line
corporate-tax estimating **illustration**. These are tested independent public
benchmarks, not a joint score. See `docs/RECONCILIATION_WITH_PUBLIC_SCORING.md`.

The other session's research documents were inspected. Its archived ZIP was found
in the Library, but its internal code was not independently executed or byte-replayed
in this runtime. This v0.3 code is a fresh integration of verified source observations
into our working v0.2 engine, **not** a claim of bit-for-bit source merge.

## v0.4.0 — completed Medicare and household-data preflight (November 6, 2026)

- Source-table transcripts: 2026 Medicare Trustees **II.E1** (11 HI calendar-year rows, 2025–2035) and **II.F1** (33 B, D and SMI account-year rows). Every row is validated using rounded cashflow, asset rollforward and B+D=SMI identities; the 2025 data are actual and later rows are Trustees' projected/hypothetical outputs. These transcripts are **not** the full 2026 CMS expanded source ZIP.
- Independently computed fixed-baseline HI result: an additional **$32.944444...B per calendar year in 2027–2035** would be required to keep *year-end* HI balances nonnegative through 2035, holding all published cashflows and interest fixed. The 2035 beginning-of-year **100% reserve target alone** would require an additional $130.725B annually over 2027–2034 under a different fixed-path construction. Neither is an actuarially scored law or a budget saving. See `docs/MEDICARE_ACTUARIAL_FIRST_PASS.md`.
- First cash-account reconciliation: CY2035 Medicare gross trust-fund expenditures $2,543.1B and CBO FY2035 net mandatory Medicare outlays $2,154.893B are *not directly comparable*. The numeric difference is expressly classified `NONCOMPARABLE_UNRECONCILED`, not savings.
- CMS published HI 75-year actuarial deficit is **0.56% of uncapped HI taxable payroll** (0.65% for a change beginning at depletion in 2033). Never apply the **capped OASDI** denominator to these figures.
- BLS Consumer Expenditure 2025 special missing-month adjustments have dedicated fail-closed code for Interview expenses, MO_SCOPE and Diary weights; these rules have **not** been run on the original PUMD, which remains unacquired.
- Census 2026 CPS ASEC public CSV ZIP preflight can verify archive identity and the independently reported counts (88,026 households; 61,133 families; 134,729 persons) **after actual ZIP download** and an explicit mapping of its true members. No national household incidence has yet been produced.
- Catalog expanded to **51 source records**; complete original raw dataset archives still **0 acquired** in this environment, so whole-file integrity against all official upstream files and official joint scoring are not accomplished.

Re-run in an extracted project directory with Python 3.11 or later:

```bash
export PYTHONPATH=src
python scripts/analyze_medicare_2026.py
python scripts/check_everything.py
python scripts/verify_package.py
python scripts/preflight_cps_2026.py --help
```

The archive manifest validates original distributed bytes. Scripts that intentionally regenerate `dashboard.html` or `results/` may update those outputs and therefore invalidate the frozen archive manifest until packaging is repeated; check the archive manifest *before* editing or regenerating.

**Evidence boundary:** The mathematical HI thresholds are fixed-baseline algebra; official CMS HI/SMI actuarial reform scores and combined CBO/JCT/SSA/CMS scoring remain unavailable without one complete legislative specification and the relevant agency analysis.
