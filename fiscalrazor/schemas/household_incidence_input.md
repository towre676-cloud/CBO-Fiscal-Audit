# Household incidence outcome contract (NOT raw Census schema)

Each household (not tax return, not family, not person) appears once with a stable, anonymized key.
Required columns: `household_id, weight, market_income, base_federal_tax, reform_federal_tax, base_transfers, reform_transfers, people, children, seniors, disabled`.

- `weight`: positive household survey weight, scaled as explicitly documented in metadata. It is never guessed.
- `market_income`: annual before federal taxes/transfers, dollars in a declared reference year and currency. Baseline ranking is by this field; this is NOT automatically CBO's equivalized-income definition.
- `base_federal_tax, reform_federal_tax`: annual net federal household tax incidence, including refundable tax credits (negative values allowed); must come from a dated, reproducible tax simulator or scored source.
- `base_transfers, reform_transfers`: annual household cash-equivalent transfer valuation, nonnegative; avoid adding program valuations already embedded in income.
- `people`: number of people in household (positive); `children,seniors,disabled`: 0/1 indicators for at least one member in indicated group. Groups overlap.
- The analyzer computes (baseline tax - reform tax) + (reform transfers - baseline transfers), with no behavioral responses and no indirect price/incidence effects.
- Census CPS ASEC raw records alone do NOT supply reform taxes. A verified tax-unit-to-household crosswalk is mandatory. The project refuses to substitute a raw income column for a tax estimate.
- `--metadata` requires population data edition, source, model version, model year, scenario rule source, SHA256 of file, weight scaling and crosswalk notes.
- Deciles are equal weighted household populations, based on baseline market income. A record's sample weight may be split fractionally at a decile boundary, avoiding unbalanced bins. This is a survey-tabulation convention, not a claim of fractional households.
- Standard error is NOT generated without verified replicate-weight design and required scaling factor from the relevant Census technical documentation. It must be added before population-level inference.
- No model produced a distributional result in this environment because the Census microdata and policy-model output were not materialized.
