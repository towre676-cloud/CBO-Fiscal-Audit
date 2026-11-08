# Census CPS ASEC design-based sampling uncertainty

Input `replicate_index,estimate` CSV: exactly 160 distinct indices 1–160, numeric finite sample statistics recomputed independently with each *actual official replicate weight vector*. All 160 should be present; no assumed or generated substitutes. The `--full-estimate` is produced from the official full weight vector for the **same exact estimator**.

Metadata JSON required fields: survey, survey_year, source_url, official_weights_file_sha256, statistic_definition, replicate_estimators_method, replicate_estimate_csv_sha256.

Example invocation (AFTER genuine data and metadata exist):

```
PYTHONPATH=src python scripts/check_survey_uncertainty.py \
  --replicates data/processed/repl_real_estimates.csv \
  --metadata data/processed/repl_real_estimates_metadata.json \
  --full-estimate "<actual point estimate>" \
  --out results/survey_estimate_uncertainty.json
```

Do not literally pass `<actual point estimate>`; obtain it from the official source-linked full-weight estimator. This is not a bundled demonstration dataset.
