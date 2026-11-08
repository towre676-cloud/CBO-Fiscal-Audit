# How to reproduce the public FiscalRazor repository

The original public-scoring test module imports `beautifulsoup4` for its SSA HTML parser; install it with `python -m pip install beautifulsoup4==4.14.3` before running that suite on a fresh environment. The trustee baseline replay and its tests also use this dependency. The root GitHub CI installs it.

**This procedure is divided into two gates:** (A) reproduce the **included public source excerpts and independent formulas**, which needs no network or user data; (B) acquire and verify **complete original datasets**, which requires internet access on first acquisition. The February 2026 CBO replay has passed. Other agencies and model-calibration stages have separate evidence requirements.

## A. Included-data and software replay (Python 3.11+)

```bash
# From the repository root:
(cd fiscalrazor && python scripts/verify_manifest_v11.py)
(cd fiscalrazor && PYTHONPATH=src python -m unittest discover -s tests -q)
(cd fiscalrazor/external/public_scoring && python -m unittest discover -s tests -q)
python -m unittest discover -s publication/tests -q
python scripts/build_publication.py
```

On Windows 11, run in Git Bash (the `PYTHONPATH=src` environment assignment requires a POSIX shell). Equivalent PowerShell for the core suite is `cd fiscalrazor; $env:PYTHONPATH='src'; py -m unittest discover -s tests -q`; restore directory after running. Run the external suite **from its own directory**, because it imports its local `src` package.

Expected counts in the audited original source: **339 core, 53 other-session, 13 new publication** tests (counts may change with future maintenance). Tests of record-level formulas and excerpt arithmetic are **not** a calibration to national outcomes. For a detailed description see [Methods](METHODS_AND_LIMITATIONS.md).

The deterministic output is [`publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv`](../publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv). The new test suite includes deliberate duplicate-year corruption, inconsistent debt-flow identities, non-finite rates, and altered source references.

## B. Original government-source replay (network required)

Run the publication-layer replay from the repository root:

```bash
python scripts/replay_cbo_originals.py --output cbo_replay.json
```

For an offline replay, add `--source-dir /path/to/source-root` with the original CSVs at the `data/…` paths recorded in the [checked-in receipt](../publication/results/cbo_2026_original_source_replay.json). Each file must match its publisher Git blob SHA-1, CSV shape and corrected record count. The replay also checks the budget and economic excerpts against those bytes and reconciles spending-account outlays and defense subtotals. Compare your JSON with the checked-in receipt. The raw files stay outside the repository.

The historical v1.1 CBO pin file incorrectly expects 4,725 labor-force participation records for the matching blob. The publication replay verifies all 2,475 records in that blob and leaves the historical archive intact. See [the source replay note](CBO_SOURCE_REPLAY.md) for the scope and findings.

For the 2026 CPS ASEC household-income replay, acquire the CSV ZIP with embedded replicate weights from the [Census release page](https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html). Then run:

```bash
python scripts/replay_cps_households.py /path/to/asecpub26csv.zip --output cps_replay.json
```

Compare it with the [checked-in household receipt](../publication/results/cps_asec_2026_household_income_replay.json). See [methods and benchmark deviations](CPS_HOUSEHOLD_REPLAY.md).

The [scoring frontier](SCORING_FRONTIER_REPLAY.md) documents four additional replays. Keep the downloaded originals in a separate source directory. Place the BLS Interview, Diary and hierarchy archives there as `intrvw25.zip`, `diary25.zip` and `stubs.zip`. For the trustee replay, save the SSA operations page as `ssa.html`, SSA VI.G3 as `ssa_long.html`, and the CMS expanded archive as `cms.zip`. The sources are linked from the scoring frontier and receipts.

```bash
python scripts/replay_vat_credit_scenarios.py /path/to/asecpub26csv.zip
python scripts/replay_bls_ce_2025.py /path/to/source-dir
python scripts/replay_trustee_baselines.py /path/to/source-dir
python scripts/replay_irs_zip_margins.py /path/to/23zpallagi.csv
```

Each command accepts `--output` for an aggregate JSON receipt. Compare against the tracked receipts under `publication/results/`.

The [provision calibration](CALIBRATION_AND_PROVISION_REPLAY.md) adds three further replays. Use the linked BEA flat-file archive, 2024 CPS ZIP and IRS 2023 geographic CSV. For the provision replay, save SSA VI.G1 as `payroll_ssa.html`, the SSA B1.2 page as `ssa_b12.html` and the CMS archive as `cms.zip` in a source directory. The CBO source directory must have the layout described above.

```bash
python scripts/replay_same_year_tax_units.py /path/to/cps24.zip /path/to/23zpallagi.csv --state-output state_margins.csv
python scripts/replay_vat_spending_base.py /path/to/FlatFiles.ZIP /path/to/ce-sources
python scripts/replay_provision_mechanics.py /path/to/trustee-sources /path/to/cbo-sources
```

## C. Freshness, versioning, and uncertainty

The benchmark here is **CBO February 11, 2026**. Later law, tariffs, actual receipts, administrative rules and economic projections can change the current-law baseline. A fresh November baseline must be a separate version and **not silently combined** with February model rows. SSA and Medicare Trustees operate on *calendar-year* bases with specialized actuarial denominators, so a joint model must explicitly fiscalize its cash effects.

For each replication, record repository commit SHA, source catalog revision/Git blob SHA, source date, importer version, units, program vintage, sample counts, weighting rules, validation tolerances, statistical uncertainty and any model-assumption scenarios. Automated release tests should fail if a provenance field is missing.

## D. Reading the archive

The `fiscalrazor/` directory retains the prior published project in full. Its `MANIFEST_SHA256.json` and `SHA256_MANIFEST_V11.txt` are **frozen historical distribution receipts**; do not regenerate them after modifying its included source files. All new research work belongs to `publication/`, `docs/`, or a separately versioned next release until that archive has been intentionally superseded with a new manifest. The surrounding Git commit records the complete new repository snapshot.
