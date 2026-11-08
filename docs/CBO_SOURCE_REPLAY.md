# February 2026 CBO original-source replay

FiscalRazor acquired the full February 2026 machine-readable release covered by its 18-file catalog and checked the bytes against the pinned publisher Git blobs. The [replay receipt](../publication/results/cbo_2026_original_source_replay.json) records the path, URL, byte count, Git SHA-1, SHA-256, and CSV record count for every file.

| Check | Observed result |
|---|---:|
| Original CSVs matching publisher Git blob SHA-1 | 18 |
| Total CSV data records | 95,209 |
| Published inputs matching original data exactly | 252 |
| Spending-detail data records | 21,769 |
| Unique Treasury account identifiers | 1,712 |
| Fiscal years with total and defense outlays reconciled | 11 |

The 252 exact matches consist of 231 FY2026–2036 budget values, 11 fiscal-year GDP values and 10 fiscal-year PCE values. The inherited account check allows up to $1 million of rounding difference per fiscal year for total outlays and the defense subtotal. The source data give FY2036 discretionary defense budget authority of $1,136.537 billion and discretionary defense outlays of $1,100.0 billion. A change in authority requires an explicit spendout schedule before it can be translated into a cash effect.

## Catalog correction

The frozen v1.1 metadata recorded 4,725 data records in `data/economic/long_term_economic/lfp_rates_2026-02.csv`. The original with Git blob SHA-1 `45bb06e63748ebd376cc8f0c6081be5938df49ef` contains 2,475. This changes the catalog total from 97,459 to 95,209. All other 17 recorded counts matched. The publication replay corrects the count for that exact blob and preserves the original v1.1 archive.

## Reproduction and scope

Run `python scripts/replay_cbo_originals.py` from the repository root. The no-argument replay fetches the official CSVs over HTTPS, checks the existing publisher pins and emits the aggregate receipt. See the [reproduction instructions](REPRODUCIBILITY.md) for offline replay. The CBO result validates the frozen baseline inputs and account bridge. The combined fiscal score, household incidence and post-reform actuarial projections require additional empirical and statutory inputs.
