# FiscalRazor v0.7 — third cross-session reconciliation

**Comparison source:** other session's `FiscalRazor_Primary_Source_Calibration_2026-11-06.zip` and `SOURCE_CALIBRATION_REPORT_2026_11_06.md` (Library, November 6, 2026). **Current base:** our reproducible 12-provision `FiscalRazor_v0.6.0`, preserved here. The other session's *written evidence* and source manifest were inspected, and all 18 raw-source Git object identities were independently re-fetched from `US-CBO/cbo-data`. **The other session's ZIP bytes could not be mounted for independent code execution during this turn. Its source code has therefore not been represented as merged or fully replayed.** This v0.7 is a new independently implemented **compatibility/calibration bridge** on top of v0.6, not a falsely claimed byte-for-byte merger of both codebases.

## 1. Reconciled content

| Subject | Latest other-session work | Our 0.6 | v0.7 disposition |
|---|---|---|---|
| CBO source scope | All 18 official Feb-2026 CSV distributions, 97,459 rows accessed as complete connector text | Selected aggregates, 51-resource discovery registry | Add all 18 pinned Git blob SHA-1 IDs and expected rows; *no raw files bundled*; runnable byte gate |
| Account detail | 21,769 rows, 1,979/account-year, 1,712 Treasury IDs | Defense BA cap and budget identity tests | Add account-level `outlays` (millions) to official aggregate reconciliation; no false BA=outlay equivalence |
| Individual tax | 180.5M CY2036 returns; $26,787.8B AGI; five cumulative top-group shares | 2% MAGI surtax legal proposal, no national microdata | Add **six disjoint AGI rank margins**, Jensen partial identification; do not call aggregates household microdata or equate 5% AGI example to 2% MAGI law |
| OASI/DI/HI | Annual, cumulative and reserve sources require semantic de-duplication | Separate trusts and report gates | Add fail-closed duplicate-key parser; no silent pivot, especially 116 repeated trust keys |
| Federal tax-law parameters | 2026–36 projected SALT/standard deduction, 2030 reset | Effective dates locked 2028–29 | Retain law timing; regenerate dependent policy effects only after raw source and official-current-law vintage matching |
| Consumer spending | BLS 2025 quintile published aggregates, shutdown adjustment | BLS 2025 special missing-month logic and survey tests | Preserve v0.6 module; note aggregate consumer units != tax returns != CPS households |
| Program scoring | All 12 provisions and designated 9 interaction categories still UNSCORED | Templates for 120 provision-years and 90 pair-years | Keep all effects unfilled. The total fiscal savings remains NOT_ESTABLISHED |

Source-level checks in this turn independently confirmed 18 Git blobs and row counts (the four most policy-sensitive are):
`ten_year_budget/annual_fy_2026-02.csv` (3,333 rows); `trust_fund/annual_fy_2026-02.csv` (728 rows and 116 repeated date-variable keys); `revenue_detail/annual_cy_iit_2026-02.csv` (795 rows); `tax_parameters/annual_cy_2026-02.csv` (2,033 rows, 11 repeated keys). The official source data also independently verify CY2036 individual return count 180.5 million, AGI $26,787.8B and top 1% AGI share 23.0%. All other 14 file identities and row counts were independently fetched and matched. Full account-level text was parsed as quote-aware CSV and each FY2026–2036 aggregate outlay, including defense, was reconciled to our CBO excerpt values.

## 2. Exact calculations already possible from published aggregates

1. FY2036 CBO baseline revenue $8,300.755B minus outlays $11,416.142B = signed deficit −$3,115.387B. Its signed primary balance is −$971.051B and interest is $2,144.336B. FY nominal GDP $46,712.1423975B; a frozen-baseline annual deficit of 3% GDP requires $1,714.022728075B improvement. This is an algebraic **target**, not an official policy result.
2. The CY2036 return-AGI rank margins have six disjoint groups: bottom 50% 11.2%, 50–75% 18.4%, 75–90% 20.4%, 90–95% 11.2%, 95–99% 15.8%, top 1% 23.0%; these sum to 100% AGI, and their individual return masses sum to 180.5 million. This is *marginal distribution only*.
3. From top 1% AGI $6,161.194B and 1.805M returns, Jensen gives an aggregate floor on hypothetical AGI above a **uniform $1M per-return threshold** of $4,356.194B. At a deliberately hypothetical 5% mechanical rate the floor is $217.8097B, with an upper bound of $308.0597B if the individual AGIs are nonnegative. Neither is a legislative score: no MAGI, filing status, phase-ins, behavioral shifts, cash fiscalization, avoidance, or broader tax interactions are modeled.
4. The exact same rank-group AGI and return totals can support different liabilities under nonlinear taxation; hence no unique household incidence can be inferred from the 84 published aggregate margins. We demonstrate this with synthetic two-return counterexamples.

## 3. Original-source admission rules

- A source becomes `ORIGINAL_BYTES_VERIFIED` only after locally downloading the exact CSV and successfully matching **Git blob SHA-1 computed over `b'blob '+len+NUL+filebytes`**, row count and schema. Git blob IDs are NOT SHA-256 file checksums.
- A metadata pin alone is `SOURCE_IDENTITY_KNOWN`, not a locally acquired dataset.
- `annual_fy` and `annual_cy` cannot be mixed or automatically fiscalized. `spending_detail` outlays and budget authority are in **millions**, while `ten_year_budget` totals are **billions**.
- Duplicate CBO trust-fund period keys must be assigned annual/cumulative semantics. Unknown duplicate keys are rejected. Exact duplicate tax-parameter rows can be safely collapsed only after an explicit opt-in, never silently.
- Published CE **consumer unit** totals and survey weights cannot be merged with CBO tax return groups by group ID; Census CPS **households/persons** are yet another observation universe.
- The 2036 static gap, partial AGI bound, and synthetic fixture tests are not forecasts of the 12-provision law.

## 4. Execution and next decisions

```
python scripts/replay_all_v06.py
PYTHONPATH=src python -m unittest discover -s calibration/tests -v
python scripts/verify_cbo_original_v07.py --list
python scripts/verify_cbo_original_v07.py --source-root downloads/cbo_2026_02_original --require-complete
```

The last command **must fail (exit code 2) while source raw files are absent**. Once originals arrive on a networked computer, the source verifier should accept exactly 18 pinned verified CSVs and their original Git SHA-1. Only then promote account-level and tax aggregates from excerpt-derived to local byte-replayed.

**Immediate priorities:** (a) locally acquire all 18 original CBO files and replay spending + trust-fund ambiguities; (b) select appropriate public-use IRS/CPS/BLS/CMS microdata and verify codebooks, joins, weighting and missing-month rules; (c) calibrate model to current-law federal budget and independent held-out tax/SSA/CMS scenarios; (d) execute the 12 specified provisions with interactions and credible effects, then evaluate 2036 deficit/GDP, 75-year solvency, and household incidence separately. Do not assign fake 2028–36 scores or a single arbitrary 15% overlap factor.

Sources: https://github.com/US-CBO/cbo-data ; https://www.cbo.gov/data ; https://www.bls.gov/news.release/archives/cesan_10292026.htm ; https://www.bls.gov/cex/ce-pumd-2025-shutdown-impact.htm ; https://www.ssa.gov/oact/trsum/ ; https://www.cms.gov/oact/tr/2026 .

## 5. Additional independently reproduced account-level benchmark

All 18 source Git object identities and reported row counts were independently re-fetched using the official GitHub repository connector. The largest spending file was returned via the **repository contents** endpoint (not the raw file endpoint, which rejected its size). The full 3,659,443-character CSV text was parsed with quoted-field handling, yielding **21,769 accounts-by-year entries; 1,979 per fiscal year; 1,712 distinct TINs** and no malformed field counts. Summing its `outlays` in millions exactly reproduces the official top-level spending totals in all 11 years, including FY2036 $11,416,142 million total and $1,100,000 million defense; defense FY2036 budget authority $1,136,537 million is distinct. The source-derived annual 11-row summary is in `results/v07/cbo_spending_connector_verified_2026_2036.csv`. **Raw local original CSV bytes are not in the ZIP.**
