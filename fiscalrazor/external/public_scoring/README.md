# FiscalRazor: Public Federal Scoring Reconstruction — EXPANDED (2026-11-06)

**Independently executable *research*, not an official CBO/JCT legislative score or SSA/CMS joint actuarial score. No package savings estimate is established.**

### What's new in this expansion

- **56 source records indexed** (40 retained, 16 new), including CBO actual income-distribution source code, CBO September 2026 researcher ZIP and supplemental Excel, IRS SOI 2023 data tables, SSA Trustees 2026 annual economics/OASI/DI, CMS 2026 HI operations, MedPAC 2026 MA payment and beneficiary premium effects.
- **11 SSA economic, 11 OASDI operating-flow, 9 OASDI reserves, 11 CMS HI, and 18 BEA PCE category rows**, with 33 newly derived SSA option-year *annual actuarial balance* dollar-equivalents (never represented as federal FY cash).
- **53 offline unit tests passed** (18 original + 35 additional) of internal accounting, SSA/CMS/BEA excerpts, CBO/JCT original checks, defense spendout lag, Oct-to-Sep cash timing, statutory OASDI wage cap and overlapping tax effects, household weighted deciles, trust-fund cash versus intragovernmental transfers.
- **No fake score:** all twelve provisions and 120 federal fiscal-year effects plus 90 minimum pairwise interaction-year effects remain unestablished. The original source files could not be fetched into the build container, and these are manual web-checked excerpts, not byte-exact source validation.

### New concrete references

SSA's published $250,000 high-earner option E2.5 gives a CY2036 **$433.2625B annual actuarial-balance improvement** when applied to 2026 Trustees payroll (not cash revenues). CMS 2026 Trustees project just **$28.1B HI reserves remaining in CY2032**, with fund depletion **Q2 2033**. MedPAC estimates **$76B higher MA payments versus FFS**, while higher MA payments also contribute **$11B higher Part B beneficiary premiums** in 2026; neither is directly recoverable as federal FY savings. BEA's 2025 PCE × 5% = **$1,043.5075B mechanical reference**, explicitly not a VAT score.

Detailed results: `docs/EXPANSION_RESULTS.md`; detailed 12-policy frontier: `docs/FRONTIER_AND_EVIDENCE_MATRIX.md`; source replay: `docs/SOURCE_INTEGRITY_AND_REPLAY.md`.

### Immediate execution (Python 3.11+; works in Windows Git Bash)

```bash
python -m unittest discover -s tests -q
python scripts/expansion_summary.py
python scripts/export_research_tables.py
python run.py audit
python run.py targets
python scripts/fetch_sources.py --dry-run
```

---

## Original toolkit contents and baseline preserved

**This is a verified-source reconstruction starter, NOT a combined CBO/JCT score and NOT a federal savings estimate.**

Public materials were cross-checked on November 6, 2026. Network access from the build container was unavailable, so the included CBO baseline is an explicitly hand-transcribed excerpt of the official CBO CSV; official external code/PDF/ZIP is linked, not bundled. The CSV values passed internal arithmetic tests. Download scripts let you obtain and hash the underlying official data yourself and compare independent copies.

## What is genuinely done

- Located **the official CBO machine-readable budget, detailed revenues, ~2,000-account spending and trust-fund series, indexed by vintage**. Included published FY2026–2036 budget aggregates and direct nominal GDP values from the matched CBO 2026-02 vintage in `data/` (manually excerpted; replay on full official CSVs for independent verification).
- Located public **executable CBO Budgetary Feedback Model** and official simplified debt-service tool, plus CapTax, rules of thumb, and input-output models. These are **not** CBO's complete production legislative scoring system.
- Reconstructed JCT's **March 2026 explicit, illustrative** corporate-tax arithmetic, matching $350B mechanical vs $180B behavioral/interaction-adjusted across ten years.
- Transcribed three **official SSA single-provision calendar-year actuarial** benchmark series. They are percentages of *current-law OASDI taxable payroll* — not fiscal-year billions, and they are not additive package scores. Combined SSA CY2035 payroll with E2.5 to derive ≈$415.45B of **annual actuarial balance** improvement (not a federal FY cash-flow score; see `src/ssa_derived.py`).
- Indexed CMS HI/SMI actuarial tables, national health expenditure forecasts, MedPAC evidence, IRS/CPS/BLS/BEA public microdata and open-source tax simulators.
- Implemented an offline `python -m unittest` check, provenance registry, duplicate account guard, and **fail-closed** policy-combination interface.

## Quick run (Python 3.11+; standard library)

```bash
cd FiscalRazor_Public_Scoring_Expansion_2026-11-06
python run.py baseline
python run.py audit
python run.py targets  # independent annual 3%-of-GDP baseline gaps, NOT scores
python -c "from src.ssa_derived import approximate_ssa_cy2035_balance_change as a; print(a('E2.5_high_earner_tax_250k_no_benefit_credit'))"
python scripts/check_candidate_score.py data/policy_effects_TEMPLATE.csv data/joint_interactions_TEMPLATE.csv  # expected FAIL-CLOSED
python run.py status
python -m unittest discover -s tests -v
python scripts/fetch_sources.py --dry-run
python scripts/fetch_sources.py --download cbo_annual cbo_gdp cbo_revenue cbo_spending cbo_trust
```

Your live network is required for downloads. Direct CSVs remain in `downloads/` and downloaded file SHA-256 values are written to `downloads/download_manifest.json`. **Do not confuse manual excerpt hashes with the canonical full CSV hash.**

For CBO's public executable economic-to-budget feedback:

```bash
git clone https://github.com/US-CBO/budgetary-feedback-model.git
cd budgetary-feedback-model
conda env create -f environment.yaml
conda activate bfm_venv
python main.py
```

For JCT taxpayer calculations, install and independently calibrate the public Tax-Calculator (https://github.com/PSLmodels/Tax-Calculator) against published IRS SOI totals and JCT score cases; no claim of JCT equivalence is implied.

## Precision

The February 2026 CBO baseline (billions nominal) has FY2036 revenues 8,300.755; outlays 11,416.142; deficit −3,115.387; interest 2,144.336; and public debt 56,152.391. The matched CBO economic CSV *directly* publishes FY2036 nominal GDP as **$46,712.1423975B** (no ratio inference). The 3%-of-GDP target is **$1,401.36B** of annual FY2036 deficit, and the deficit-reduction gap is **$1,714.02B** against this historical-vintage baseline before package-specific macroeconomic/debt-service feedback. The ratio-implied value provides only a secondary consistency check.

**Do not treat that gap as a revenue projection or proof that the bill reaches its target.**

## Trust boundaries

The JCT's confidential actual-return samples and complete official JCT production code are not released. The SSA long-range actuarial model has detailed public documentation but is not distributed as an end-to-end runnable production model. CMS similarly publishes actuarial tables/methodology but not its entire operational scoring system. JCT estimates, SSA provision calculations, and CMS actuarial projections have DIFFERENT objectives and bases. Only Congressional agencies can formally issue their scores.

See `docs/SOURCE_REGISTER.md`, `docs/SCORING_ARCHITECTURE.md`, and `docs/PROOF_GATES.md`.

### Fetch *all* CBO catalog datasets from February 2026, not just handpicked tables

```bash
python scripts/fetch_sources.py --download cbo_catalog
python scripts/fetch_cbo_catalog_all.py --list --vintage 2026-02
python scripts/fetch_cbo_catalog_all.py --fetch --vintage 2026-02
python run.py check-official-cbo --path downloads/cbo_annual.csv
python run.py check-official-gdp --path downloads/cbo_gdp.csv
```

The catalog crawler enumerates all published CSV/JSON distributions with the requested vintage; it records SHA-256, size and source for each. Re-run with different `--vintage` for historical counterfactual benchmarking. The catalog crawler does not automatically include PDF/Excel annexes outside CBO's GitHub public catalog, or restricted agency files; those remain enumerated in the source registry. The tool has **not** been run against live downloads in the file-building container.

### Exact baseline GDP source

The 11-year nominal GDP excerpt derives from `variable=gdp`, `date=FY2026` through `FY2036`, in the official [CBO February 2026 fiscal-year economic CSV](https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv). This source supplies FY2036 GDP directly; no extraction from a rounded public-debt-to-GDP ratio is necessary. `python run.py targets` reports a complete annual FY2026–2036 gap path.
