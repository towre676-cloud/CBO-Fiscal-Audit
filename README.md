# FiscalRazor · Federal Fiscal Audit

**Independent, source-auditable research on the United States federal budget, tax law, Social Security, Medicare, and proposed fiscal reform.**

[Research findings](docs/RESEARCH_BRIEF.md) · [Evidence register](docs/EVIDENCE_REGISTER.md) · [Legislative scenario](fiscalrazor/legislation/ILLUSTRATIVE_FISCAL_REFORM_ACT_2027.md) · [Methodology](docs/METHODS_AND_LIMITATIONS.md) · [Reproduce](docs/REPRODUCIBILITY.md) · [CBO source replay](docs/CBO_SOURCE_REPLAY.md) · [Scoring frontier](docs/SCORING_FRONTIER_REPLAY.md)

> **Evidence status — 7 November 2026.** This project is **not** a Congressional Budget Office (CBO), Joint Committee on Taxation (JCT), Social Security Administration (SSA), Centers for Medicare & Medicaid Services (CMS), or Treasury publication or score. Its 12-provision bill is a **research draft, not introduced legislation**. Source-derived historical/projected values, mechanically derived bounds, sample-record statutory calculations, and unscored legislative proposals are separate classes of evidence. The original microdata and agency production models needed for a nationally calibrated, combined estimate have **not** been acquired or independently reproduced here.

## What is published

This repository contains the entire verified FiscalRazor **v1.1.0** research-code snapshot under [`fiscalrazor/`](fiscalrazor/) **unaltered** (including its historical SHA-256 receipts and prior releases), plus a new publication layer with updated documentation, exact-arithmetic fiscal-stability calculations, additional adversarial tests, and CI. Historical notes are retained as artifacts of their own version, not as the current project's scientific conclusion.

| Evidence level | Examples | Permitted conclusion |
|---|---|---|
| **Official source observation** | CBO February 2026 fiscal-year projections; SSA/CMS trustees' published outputs | An agency reported a value under stated assumptions. |
| **Verified excerpt / reproducible arithmetic** | 2027–2036 deficit and one-year debt-ratio target gaps, fixed-base VAT algebra | The derivation follows *if the source excerpt is accurate*; not a policy score. |
| **Independent statutory mechanism** | Sample-record payroll, surtax, health exclusion, and rebate interactions | The code computes the defined toy/record-level law for supported input variables. |
| **Historical policy analogue** | Separately published CBO/JCT budget options | Context for magnitude and methodology only; **not additive**. |
| **Not yet established** | Joint national reform score, 75-year post-reform solvency, national household incidence | **No aggregate claim.** |

## Reproduced benchmark: FY2036

All dollar values below are **billions of nominal USD**, derived from the pinned **February 2026** CBO baseline, not a November 2026 revised current-law forecast.

| CBO datum / independent computation | FY2036 |
|---|---:|
| Projected receipts | $8,300.755B |
| Projected outlays | $11,416.142B |
| Projected annual deficit | $3,115.387B |
| Net interest | $2,144.336B |
| Official projected nominal GDP | $46,712.1423975B |
| **Static improvement required for a 3% GDP annual deficit** | **$1,714.022728075B** |
| **Static improvement required to prevent a one-year rise in debt/GDP (2035→2036)** | **$1,042.80050812B** |

These are **two different objectives**. The second is conditional on holding FY2035 debt, FY2035/FY2036 nominal GDP, FY2036 non-deficit financing, and all other baseline assumptions fixed. Neither establishes that any reform can produce the required improvements.

[Inspect the complete annual table](publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv), its [implementation](publication/fiscal_accounting.py), and its [adversarial tests](publication/tests/test_fiscal_accounting.py).

## Run in three commands

Python **3.11+** is supported. Core and publication arithmetic use the standard library; the preserved public-scoring test suite additionally requires `beautifulsoup4` (`python -m pip install beautifulsoup4==4.14.3`).

```bash
# 1. Preserve/verify the original v1.1 source distribution
(cd fiscalrazor && python scripts/verify_manifest_v11.py)

# 2. Run both inherited suites
(cd fiscalrazor && PYTHONPATH=src python -m unittest discover -s tests -q)
(cd fiscalrazor/external/public_scoring && python -m unittest discover -s tests -q)

# 3. Rebuild and test this publication's exact CBO reference calculations
python scripts/build_publication.py
python -m unittest discover -s publication/tests -q
```

The above operations **do not download** the full original government archives and **do not execute official agency estimators**. For the full-data acquisition contract and official file paths see [the reproducibility instructions](docs/REPRODUCIBILITY.md). Large public-use datasets and any confidential records are intentionally omitted from this repository.

## Research program

The **legislative scenario** defines twelve proposed tax, spending, and entitlement provisions and 66 pairwise relationships. The open scientific questions include baseline-vintage consistency, fiscal-year collection timing, appropriation spendout, SS and HI solvency, behavioral interactions, long-run debt dynamics, and tax-benefit household distribution under the actual survey design. Read the [claim/evidence register](docs/EVIDENCE_REGISTER.md), [mathematical methods](docs/METHODS_AND_LIMITATIONS.md), and [prioritized research frontier](docs/NEXT_EXPERIMENTS.md) before extending results.

## Data and attribution

Primary references: [CBO February 2026 outlook](https://www.cbo.gov/publication/61882), [CBO machine-readable dataset](https://github.com/US-CBO/cbo-data), [2026 SSA Trustees report](https://www.ssa.gov/oact/TR/2026/), [2026 Medicare Trustees](https://www.cms.gov/oact/tr/2026), [JCT tax-estimation methodology](https://www.jct.gov/publications/2026/revenue-estimating-process-and-microeconomic-research-2026/), [Census CPS ASEC](https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html), and [BLS Consumer Expenditure](https://www.bls.gov/cex/pumd_data.htm).

**No official affiliation or endorsement.** Agency data and publications retain their own terms and attribution. No unrestricted license is assigned to this independent repository in the absence of a selected license; see [PUBLICATION_NOTICE.md](PUBLICATION_NOTICE.md).
