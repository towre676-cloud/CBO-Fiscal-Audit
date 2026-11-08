# Scoring frontier and source replays

The CBO February 2026 baseline is now reproducible from its 18 pinned originals. The next scoring step is to construct policy-specific inputs that reconcile to independent benchmarks. These replays establish three additional pieces of that baseline.

## §101 credit exposure on the 2025 Census population

The 2026 CPS ASEC identifies Census-modeled tax units with `TAX_ID` and reports modeled filing status, dependent pointers and federal AGI. The replay groups people within each survey household, checks the person count, identifies single and head-of-household returns and validates joint filers with reciprocal spouse links. A dependent filer's separately reported AGI stays outside the principal return. The calculation sums unit-level credit exposure within each household and then applies the Census household weight.

| Result | Observed value |
|---|---:|
| Survey households | 53,321 |
| Census-modeled units | 72,955 |
| Households with multiple modeled units, weighted share | 28.04% |
| Units with principal-return AGI resolved | 57,701 |
| Unresolved units, including 15,101 modeled nonfiler units | 15,254 |
| Resolved filers with modeled AGI used directly | $53.04B |
| Lower conditional scenario | $47.51B |
| Upper conditional scenario | $84.48B |

The two scenarios assume every member of a modeled unit qualifies, the 2025 HHS guideline applies by household location, and participation is complete. For resolved returns, the interval assumes §101 MAGI exceeds modeled AGI by an amount between $0 and $5,000. The $5,000 limit is a sensitivity choice. For unresolved units, the lower scenario allows zero credit and the upper scenario allows the formula's full credit. Those unresolved units account for $31.43B, about 85% of the scenario width. The reported range is conditional on these inputs. Changes in statutory MAGI, residency, qualifying persons, or take-up can move the result outside it. The calculation applies the draft formula to 2025 observations. The proposed effective date is 2029.

The [aggregate receipt](../publication/results/cps_2025_vat_credit_scenarios.json) breaks out each Census household-income quintile. It contains no spending allocation, VAT burden, or linked CE record. Sources: [Census tax model](https://www.census.gov/topics/income-poverty/income/guidance/tax-model.html), [2025 tax model notes](https://www2.census.gov/programs-surveys/demo/guidance/income-poverty/user-note/TY2025-tax-model-external-user-notes.pdf), and [2025 HHS guidelines](https://www.govinfo.gov/content/pkg/FR-2025-01-17/html/2025-01377.htm).

## BLS spending calibration

The replay uses the original 2025 Interview and Diary archives and the official integrated UCC hierarchy. It applies the October–November lapse adjustments to interview expenditure months and scope, and to Diary full-sample and replicate weights. It estimates the all-consumer-unit mean and a standard error using all 44 replicates, with source-specific denominators. The sample program targets approximation of the published estimates. These are the observed residuals.

| Annual dollars per consumer unit | Adjusted replay | BLS Table 1 | Difference |
|---|---:|---:|---:|
| Total | $82,029.27 | $81,905 | +$124.27 |
| Food | $10,648.14 | $10,633 | +$15.14 |
| Housing | $27,788.79 | $27,790 | −$1.21 |
| Transportation | $13,488.94 | $13,492 | −$3.06 |
| Health care | $6,485.27 | $6,470 | +$15.27 |

The Interview denominator reproduces the published population of 137.994 million consumer units at its stated precision. Dropping the adjustments would give $81,704.06 of total spending in this replay. A VAT base requires a separate BEA/PCE bridge and treatment of zero-rated, exempt and mixed categories. The [receipt](../publication/results/bls_ce_2025_replay.json) includes both adjusted and unadjusted results. Sources: [BLS release](https://www.bls.gov/news.release/cesan.htm), [BLS lapse treatment and sample code](https://www.bls.gov/cex/ce-pumd-2025-shutdown-impact.htm), and [UCC hierarchy](https://www.bls.gov/cex/pumd_doc.htm).

## SSA and CMS trust-fund baselines

The replay checks annual income minus cost and the separate reserve roll-forward for OASI, DI and Medicare HI, to each agency's displayed precision. It verifies 29 cash identities and 26 reserve identities. SSA publishes unavailable OASI reserve cells from 2032 onward in its intermediate operations table. CMS publishes an illustrative negative HI balance of −$56.909B in 2033 under continued scheduled spending. That accounting value represents a shortfall after projected reserve depletion. The ledger preserves the difference in agency conventions.

The [receipt](../publication/results/trustee_2026_baselines.json) also retains 75 annual SSA noninterest-income and scheduled-cost observations for each fund and 75 CMS HI income and cost rates through 2100. It checks the separate SSA values against SSA's combined table to the nearest published billion. HI rates use CMS taxable payroll as their denominator. The series stay in their published calendar years and units. Sources: [SSA short-range tables](https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html), [SSA annual long-range table](https://www.ssa.gov/oact/tr/2026/lr6g3.html), and [CMS expanded trustee tables](https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds).

## IRS geographic return benchmarks

The [IRS receipt](../publication/results/irs_2023_zip_margins.json) covers 166,732 disclosed 2023 ZIP-by-AGI cells and state subtotal cells. Across the 50 states and DC, state subtotals report 156,881,630 returns and $15.173 trillion of AGI. Named ZIPs plus the disclosure bucket `99999` reproduce the state-subtotal AGI exactly, while their published rounded return counts sum to 75,360 more than the state subtotals. Use the state subtotal rows for a return-count control. The 2023 benchmark is appropriate for a matched 2023 CPS replay and precedes the 2025 credit scenarios above. Sources: [IRS release](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2023-zip-code-data-soi) and [record layout and disclosure methods](https://www.irs.gov/pub/irs-soi/23zpdoc.docx).

## Open work in dependency order

| Step | Inputs and acceptance criterion |
|---|---|
| Finalize the §101 tax-household definition | Specify MAGI add-backs, residency, dependent treatment and nonfiler participation. Reconcile modeled filing units to same-year IRS counts and AGI margins. Validate on a second year before projecting to 2029. |
| Build the §101 VAT base and incidence bridge | Map UCC and BEA PCE components to statutory categories, retain mixed buckets as intervals and reconcile to both sources. Use an auditable cross-survey statistical match with sensitivity to alternative joint distributions. |
| Calibrate the other 11 provisions | Build baseline and policy runs for surtax, deductions, employer health, corporate, OASDI financing and benefits, Medicare Advantage and site-neutral payments, defense and HI financing. Use actual tax, employer, provider, enrollment, service and spending-account benchmarks at each appropriate unit. |
| Close the combined fiscal ledger | Fiscalize calendar and contract-year effects. Evaluate 66 pairwise interactions and the higher-order residual, then reconcile receipts, outlays, interest and financing to debt stocks. |
| Run post-reform OASI, DI and HI valuation | Apply cohort-specific benefit and revenue changes to separate fund projections under common economic scenarios. Check each fund's reserves and 75-year actuarial balance, with quarterly cash near depletion. |
| Obtain external scoring | The authorized agencies would need agreed legislative text and their own production inputs and validation. Independent public-source modeling remains separately labeled. |
