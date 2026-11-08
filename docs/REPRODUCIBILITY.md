# How to reproduce the public FiscalRazor repository

**This procedure is divided into two gates:** (A) reproduce the **included public source excerpts and independent formulas**, which needs no network or user data; (B) acquire and verify **complete original datasets**, which requires internet access and has **not** been executed to completion in this publication environment. Do not report gate B as complete because gate A passed.

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

The retained v1.1 source includes multiple acquisition scripts and a GitHub Actions `workflow_dispatch` pipeline. In the source-code root:

```bash
cd fiscalrazor
python scripts/acquire_real_federal_v08.py --fetch-all-cbo
python scripts/replay_real_v08.py --require-originals
python scripts/replay_v09.py --require-originals
```

The acquisition script must download the full **18 CBO February 2026** CSVs. Each must pass the upstream **Git blob SHA-1** in `data/v07/cbo_2026_02_git_pins.json`, along with row counts and the cross-source accounting identities. This is a **source-byte identity check**, not a general proof that the source values are current as of November or that a policy simulation is correct. The raw files are never included in the repository release.

Optional large microdata acquisition for Census/IRS/CMS is supported by the existing scripts and the manual GitHub Actions workflow. Before reusing any importer on a newly released source, inspect the actual provider codebook. Census `HTOTVAL` and survey weights are not valid substitutes for the tax unit and IRS tax return fields; consumer-unit CE data are not BEA PCE and CMS public-use survey records are not complete claims data. Maintain confidential data off GitHub and record SHA digests for authorized datasets.

## C. Freshness, versioning, and uncertainty

The benchmark here is **CBO February 11, 2026**. Later law, tariffs, actual receipts, administrative rules and economic projections can change the current-law baseline. A fresh November baseline must be a separate version and **not silently combined** with February model rows. SSA and Medicare Trustees operate on *calendar-year* bases with specialized actuarial denominators, so a joint model must explicitly fiscalize its cash effects.

For each replication, record repository commit SHA, source catalog revision/Git blob SHA, source date, importer version, units, program vintage, sample counts, weighting rules, validation tolerances, statistical uncertainty and any model-assumption scenarios. Automated release tests should fail if a provenance field is missing.

## D. Reading the archive

The `fiscalrazor/` directory retains the prior published project in full. Its `MANIFEST_SHA256.json` and `SHA256_MANIFEST_V11.txt` are **frozen historical distribution receipts**; do not regenerate them after modifying its included source files. All new research work belongs to `publication/`, `docs/`, or a separately versioned next release until that archive has been intentionally superseded with a new manifest. The surrounding Git commit records the complete new repository snapshot.
