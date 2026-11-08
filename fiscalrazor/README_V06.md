# FiscalRazor v0.6.0 — Legally Specified Scenario & Independent Stabilization Research

**Prepared November 6, 2026. The 12 provisions are a hypothetical research scenario, not enacted law or a legislatively vetted bill. It has no official or validated combined score.**

## What is executable now

1. `legislation/ILLUSTRATIVE_FISCAL_REFORM_ACT_2027.md` — explicit legislative **research** draft for 12 reforms, including tax bases, rates, indexing, statutory anchors, fund ownership, phase-ins, exceptions, administrative responsibilities and fiscal-year timing. Cross-reference, agency administrative and legal counsel questions remain explicitly marked.
2. `legislation/scenario_v06.json` — exact machine-readable locked parameters (no policy estimates or invented scoring fields).
3. `src/fiscal_data/v06_law.py` — statutory first-pass mechanical models for the new 2028 high-income surcharge, OASDI high band and rate, HI taxes, 2029 VAT rebate, employer-plan exclusion cap and 22% corporate-rate mechanical component. No survey-weighted estimation is attempted without actual records. The multiple-employer high band allocation is **pro rata** with a split-invariance test, not a per-employer avoidance loophole.
4. `src/fiscal_data/v06_frontier.py` — two separate annual frozen-baseline fiscal-target diagnostics: an annual deficit ceiling of 3% of GDP and a one-year non-increasing public-debt-to-GDP ratio. This module also refuses to claim robust feasibility when any of the 12 policy, 9 mandatory interaction or net-interest bounds is missing.
5. `scripts/acquire_priority_v06.py` — stage the original CBO, SSA, CMS, Census and household sources for hash-verifiable downloading from an **internet-connected** Python environment. `scripts/source_gate_v06.py` reports what bytes have actually been acquired.
6. `data/v06/provision_year_120_UNSCORED_TEMPLATE.csv` and `interaction_year_90_UNSCORED_TEMPLATE.csv` — zero substitutions forbidden. Also includes `all_policy_pairs_66.csv` and 12-row federal cash/fund ownership map.
7. `research/OUR_RESEARCH_PROGRAM.md` and `research/VERIFIED_FIRST_RESULTS.md` — **our own** fiscal-stability and policy-geometry research program, algebraic results, robust frontier design and falsifiable next experiments.
8. `policy_workbench_v06.html` — portable offline overview with all 12 provisions, original-source status, and **clearly hypothetical** wage / VAT examples. No online dependencies.

## What is actually observed

Selected government-published source excerpts retained from the v0.5 reconciliation: 21 CBO FY variables × 11 years, direct nominal GDP for 11 years, SSA single-provision benchmarks, 2026 CMS 11-year HI/SMI tables, JCT's teaching illustration, and limited Treasury data. **None of the 51 source entries has a complete original public-source file acquired and admitted in this runtime**. The registry has 37 direct-download candidates and 14 landing/API sources. Even a future successful download does **not** equal a validated tax/actuarial reform estimate. Original JCT and agency confidential administrative samples are not public and are not promised.

### Two distinct FY2036 target calculations using CBO February 2026 projections

- **Deficit below 3% GDP:** annual improvement of **$1,714.022728075 billion** if baseline GDP is frozen.
- **Prevent ratio rise in FY2036 versus FY2035, one-year frozen comparison:** **$1,042.80050811994 billion** improvement if the prior debt stock, other financing and GDP path are frozen.

These differences are algebraic; neither is a scored measure, nor a guarantee of solvency after FY2036.

## Start on Windows 11 (Git Bash / PowerShell)

Install Python 3.11+ for this project's standard-library modules. Unpack the ZIP and work from its single root directory.

```bash
python scripts/source_gate_v06.py
python scripts/run_v06.py
python scripts/replay_all_v06.py
python scripts/verify_package.py
```

Acquire original government files from an internet-connected environment (the current cloud container has no usable network); transactions may require gigabytes for large archives and processing:

```bash
python scripts/acquire_priority_v06.py --list
python scripts/acquire_priority_v06.py --group cbo_core --max-mb 200
python scripts/acquire_priority_v06.py --group actuarial --max-mb 300
python scripts/acquire_priority_v06.py --group household --max-mb 300
python scripts/source_gate_v06.py
```

Source receipts and sha256 checks are required before model calibration. If any download fails, the script returns a nonzero exit code and does not count the file as acquired. The official 2026 Census CPS ASEC is a large ZIP (about 133 MB) and CMS provides expanded Medicare tables in a ZIP. See `docs/V06_DATA_ACQUISITION_AND_CALIBRATION.md`.

**Optional external Tax-Calculator:** as of October 30, 2026, current release 6.9.0 dropped Python 3.12 and earlier compatibility and removed its old AGI-surtax parameter. Use a separate supported Python environment for that release and implement the actual defined MAGI surtax in supplementary code; do not treat any default AGI surtax as available.

## Automated verification

Run `python scripts/replay_all_v06.py`. The release records the actual results of the local inherited+v0.6 suite and the external public-scoring suite separately. They verify code behavior and overlapping excerpt alignment, **not** national impacts. A fresh extraction re-runs the source-gate, mathematical results, both suites, and content manifest.

## Evidence thresholds still open

- Download *original* CBO, SSA, CMS, Census, BLS, BEA, IRS public releases and verify schema/record counts and hashes;
- Reproduce published baseline tables *from those original files*, with full provenance to source cells;
- Implement income-tax and payroll fiscalization, including rate changes and employee/employer allocation;
- Reproduce independent SSA single-provision policy curves and calculate joint OASI/DI 75-year results;
- Reproduce CMS HI/SMI accounts and estimate MA/site-neutral provider-level policy consequences;
- Run and calibrate genuine national weighted CPS ASEC + CE + SOI household incidence with all Census replicate weights;
- Produce a complete unified budget and interest feedback score, and robust feasible-frontier evidence;
- Obtain actual official agency scores if available for the same legally settled text.

**Nothing in this archive establishes a national savings total, 75-year joint entitlement solvency, real household reform incidence, or agency approval.**

## Read first

- [Legal research draft](legislation/ILLUSTRATIVE_FISCAL_REFORM_ACT_2027.md)
- [Own research and exact results](research/VERIFIED_FIRST_RESULTS.md)
- [Full source-acquisition and calibration plan](docs/V06_DATA_ACQUISITION_AND_CALIBRATION.md)
- [Portable overview](policy_workbench_v06.html)
- [Status receipts](results/v06/research_status.json)
