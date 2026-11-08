# Census 2026 CPS ASEC survey uncertainty — operational contract

**Method source:** U.S. Census Bureau, *2026 CPS ASEC public-use technical documentation and 2026 replicate-weight usage instruction*, https://www.census.gov/data/datasets/2026/demo/cps/cps-asec-2026.html ; replicated formula also visible in the 2024 Census CPS ASEC Technical Documentation (Census publication, not assistant-derived).

For a single full-sample statistic \(\widehat\theta_0\), compute the exact same statistic under each of the **160 official replicate-weight vectors**, obtaining \(\widehat\theta_r\) for \(r=1,\dots,160\). Use the Census prescribed variance

\[
\widehat{\mathrm{Var}}(\widehat\theta_0) = \frac{4}{160}\sum_{r=1}^{160}(\widehat\theta_r-\widehat\theta_0)^2.
\]

The standard error is its nonnegative square root. For nonlinear statistics—such as means, poverty rates, the fraction of households losing and income-decile thresholds—**recompute the complete statistic in each replicate** rather than merely multiplying final full-sample statistics by replicate weights. Do not treat a person-level weight as a household-level weight; honor the Census survey universe, keyed identifier, income period and the source layout.

A 2026 external replicate-weight record must be matched to the correct CPS ASEC person/household record using *documented official Census record keys*. Matching by row number, age, income or assumed row sorting is forbidden. Check the join coverage and duplicated/missing IDs before running the statistic. The 2026 CSV distribution may already include replicate weights; avoid double-joining or counting them twice.

The script `scripts/check_survey_uncertainty.py` accepts a CSV containing exactly `replicate_index,estimate` with indices 1 through 160, `--full-estimate`, and a JSON provenance document with fields: `survey=CPS_ASEC`, `survey_year=2026`, `source_url`, `official_weights_file_sha256`, `statistic_definition`, `replicate_estimators_method`, and `replicate_estimate_csv_sha256`. The script runs only after actual data are present and generates a source-linked result. It deliberately has no included synthetic population masquerading as a Census result.

**Not established:** national distributional consequences of any named fiscal reform, survey sampling intervals for an unavailable household model, or uncertainty from behavioral responses. Those require executed source-based simulations, and the latter requires independent uncertainty modeling.
