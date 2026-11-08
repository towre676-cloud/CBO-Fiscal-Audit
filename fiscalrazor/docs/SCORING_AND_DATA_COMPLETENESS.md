# Boundary between public-source reproduction, independent policy scoring and official agency certification

## Public source coverage (as of November 6, 2026)

The catalog is a **non-exhaustive core starting dataset**, not a claim to hold all U.S. federal data. The inventory enumerates 46 source entries covering CBO full budget and economic revisions, SSA 2026 trustees, CMS 2026 expanded Medicare tables, Census March 2026 ASEC including person / household and 160 replicate weights, CBO September 2026 household distribution research, Treasury FiscalData, IRS SOI, JCT tax expenditures, BEA, BLS, OMB, Census ACS/SIPP, Federal Reserve SCF, and tax-model documentation. Twenty CBO Git repository files have verified blob identities.

**Already materialized here:** selected 231 CBO fiscal cells, selected 2026–2036 SSA rates, 2026 trust-fund summary points, FY2026 Treasury annual totals, with their source citation and extract-provenance record.

**Not materialized here:** original CBO archive files (even though verified Git source identities exist), SSA Excel source, CMS 2026 ZIP, Census 2026 ASEC microdata and replicate weight archives, full CBO 2026 household research datasets, JCT PDF, IRS microdata, BEA/BLS source files. A connected computer must run the acquisition CLI and validate the original bytes. An official source URL is not an acquired dataset.

## Strictly different products

1. **Original data archive:** authenticated source byte stream, dated release, source URL, content SHA-256, optional exact Git blob SHA-1, immutable receipt, official data dictionary.
2. **Descriptive estimate:** mathematically reproduced from a named data archive, including actual survey sampling variance where needed. It is not a policy change estimate.
3. **Independent static fiscal score:** specified legislation, exact current-law baseline date, human/behavioral assumptions, complete ten-year primary budget effects, interrelated tax interactions, and receipts/outlays/debt reconciliation.
4. **Independent dynamic score:** macroeconomic responses, interest-rate path and endogenous receipts and outlays with identified estimation error.
5. **Independent SSA and CMS solvency studies:** separate OASI, DI, HI and SMI actuarial identities, trust-fund valuation dates, intermediate / low / high cost cases, loss-of-reserve dates, affordability and actuarial balance.
6. **Official cross-agency scores:** created by the named agencies themselves (CBO/JCT, SSA Office of the Chief Actuary, CMS Office of the Actuary) for the same **fully drafted and legally specified** provisions, matching valuation date / revision / units, before a claim of government certification.

The current repository establishes portions of products 1 and 2 **only for the retained source extracts**. It has no official score, and no tested national reform incidence. It does not mark any missing item as zero, favorable, or complete.

## High-priority missing source adapters

- Census CSV ZIP parser and dictionary-driven person/household/family linkage; before/after tax-unit crosswalk to IRS/Tax-Calculator; independent weighted estimate replication against official Census reference figures.
- Full SSA Excel import and intermediate/low/high cost assumptions; separately reproduce annual reserves and payability in each statutory trust fund.
- Medicare 2026 CMS supplementary ZIP extraction into dated Part A, B, D, HI and SMI series; avoid transfers between unrelated trust funds.
- Treasury MTS API keyset and historical revisions; align cash accounting with FY and budget authorities.
- IRS SOI aggregates and raw access conditions; validate tax model against the precise year and taxpayer unit.
- CBO September 2026 distribution of household income and taxes and 2026 CPI / ACS / MEPS to confirm demographic and health effects rather than speculate.

## National fiscal model versioning

Never attach October 2026 NIPA translation as a new February ten-year budget baseline. Never mechanically spread a ten-year amendment across individual years. CBO February 2026 is the declared baseline vintage; FY2026 actuals and the August 2026 tariff memo are dated **reconciliation evidence**, not a fully re-estimated FY2027–36 forecast. A new complete current-law baseline must be separately obtained when released and every model result re-dated accordingly.
