# Expansion update: November 6, 2026

**The original status below is preserved as the first-pass snapshot.** The current additive expansion indexes 56 source records; 53 offline arithmetic/structural tests pass; new SSA, CMS, MedPAC, BEA excerpts and cross-fund accounting are available. Original full-size official files have not been retrieved/replayed; all proposed policy-year and interaction-year fiscal effects remain unscored. See `EXPANSION_RESULTS.md` and `SOURCE_INTEGRITY_AND_REPLAY.md` for current statuses, and do **not** read old “40 sources / 18 tests” counts below as current.

---

# FiscalRazor source and score status — 2026-11-06

## Reproduced *now*

- Official February 2026 CBO long-format CSV endpoints located and manually excerpted for FY2026–2036: seven budget variables and 11 direct nominal GDP observations. The package reproduces its own transcriptions' accounting identities; **the complete original CSVs were not available for independent byte-for-byte validation in the build container**.
- Published CBO FY2036 fiscal deficit baseline: $3,115.387B; direct official FY GDP: $46,712.1423975B; gap to 3%-GDP deficit: $1,714.022728075B, or **$1,714.02B**. These are exact deterministic arithmetic given the quoted source input values, not a policy forecast.
- Official SSA 2026 E2.5, E1.10 and B1.2 individual-provision calendar-year percentage-point annual-balance changes are transcribed for 2026–2036; anchored rows are checked. SSA's 2035 published payroll × E2.5 yields an approximately $415.45B **CY2035 actuarial annual-balance improvement**. This is neither an FY 2035 cash impact nor a standalone Federal deficit score.
- JCT March 2026 published *teaching illustration* totals $350B mechanical → $180B adjusted over ten years. This validates the transcribed illustration's arithmetic only; it does not validate a Tax-Calculator corporate revenue function or provide any other proposed tax rate's score.
- Forty public source URLs indexed and classified; canonical CBO vintage-catalog crawler and download/SHA256 manifest scripts; 18 local automated tests; a fail-closed research score entry checker. All twelve reform provisions remain `UNSCORED`; test gate correctly rejects missing 120 provision-year and 90 designated pairwise interaction-year values.

## What remains unknown, and cannot be represented as accomplished

- Full executable JCT tax-estimating systems, linked confidential IRS tax returns, and the production calibration tables are not publicly released. Public IRS SOI tables can support independent approximate calibration, not identical return-level joint data.
- Full executable SSA long-range OASDI and CMS Medicare OACT production scoring models and all underlying administrative microdata have not been obtained. Published methods and provision output tables **are** available and useful for modular modeling.
- Exact draft legislative text, policy parameters, and tax/expenditure timing for all twelve proposed reforms. An under-specified reform cannot be scored faithfully.
- Any independently validated complete 2027–2036 policy cash-flow ledger, recipient/household distributional results, Medicare HI trust-fund forecast under reforms, aggregated behavioral interactions, or CBO-consistent annual debt-service responses.
- A combined official CBO/JCT estimate or a joint official SSA/CMS actuarial evaluation of the entire package. The $12.11 trillion draft package estimate from earlier discussions is not established by this package.

## Concrete next runnable commands

```
python scripts/fetch_sources.py --download cbo_annual cbo_gdp cbo_revenue cbo_spending cbo_trust cbo_catalog
python run.py check-official-cbo --path downloads/cbo_annual.csv
python run.py check-official-gdp --path downloads/cbo_gdp.csv
python scripts/fetch_cbo_catalog_all.py --list --vintage 2026-02
python scripts/fetch_cbo_catalog_all.py --fetch --vintage 2026-02
python -m unittest discover -s tests -v
python run.py targets
```

Run on a network-connected Python 3.11+ host; this archive retains no source binaries under copyright or agency hosting conditions. The CBO catalog method obtains all documented CSV/JSON files for a chosen vintage **within its official catalog**, not every document or restricted dataset ever created by those agencies. Preserve downloads and their SHA manifests before changing baseline vintage.

**Scoring rules:** No percentage-of-GDP tax conversion without an observed base. No treating a provision's 75-year actuarial percentage as a 10-year FY saving. No treating a published Medicare overpayment estimate as a new bill's budget savings. No quietly setting missing provisions/interactions to zero. No official attribution without official results.
