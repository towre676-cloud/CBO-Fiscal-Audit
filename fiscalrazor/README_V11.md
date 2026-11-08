# FiscalRazor v1.1 — Actual fiscal-reform research with transparent source boundaries

## What is new

- `src/fiscal_data/v11_joint.py`: one record-level, source-strict *joint mechanical* wage/tax/VAT calculator for §§101–104,106–107,112. Person/employer/tax-unit/household boundaries preserved; health inclusion changes MAGI, surtax, VAT rebate, Medicare and OASDI bases; current-law 0.9% Additional Medicare Tax modeled for fully covered wage cases. Multi-employer and two-worker married cases tested. No self-employment simplification or unrecognized population mapping.
- `src/fiscal_data/v11_published.py`: official aggregate-reference BLS 2025 consumer expenditures by quintile, BEA 2025 PCE comparison, SSA current-law taxable payroll statutory-base rate increments, and source-rounded CMS Trustees HI high-cost liquidity sensitivities. No household microdata results claimed.
- `data/v11/joint_policy_readiness.csv`: line-by-line coverage and missing evidence for all 12 reform provisions.
- `results/v11/*.csv` and `*.json`: reproducible result receipts with explicit non-score status.
- `research/V11_JOINT_RESULTS.md`: technical proof arguments, sources, limitations, further scientific obligations.
- `scripts/evaluate_joint_records_v11.py`: streaming JSONL record engine with pseudonymous IDs, SHA-256 input/output receipts, atomic results, fail-closed errors and no national weighting.

## Run

```bash
# From extracted FiscalRazor_Joint_Research_v1_1 root
PYTHONPATH=src python scripts/run_v11.py
PYTHONPATH=src python scripts/evaluate_joint_records_v11.py --input YOUR_RESEARCH_RECORDS.jsonl --output results/v11/your_record_results.jsonl
PYTHONPATH=src python -m unittest discover -s tests -q
(cd external/public_scoring && python -m unittest discover -s tests -q)
python scripts/verify_manifest_v11.py
```

The package ships with the entire prior v1.0 codebase. It does not ship new original raw agency datasets: BLS 2025 numbers are from its **published release table**, and other aggregates are retained verified-source excerpts. The code does NOT run an official or national combined score.

### Explicit missing items

- Full source original bytes for 18 February 2026 CBO datasets, complete original 2026 Census CPS ASEC+replicate weights, 2025 CE PUMD, IRS public tables/PUF, CMS MCBS/claims: **not acquired locally**.
- Complete JCT tax return data and its production model are confidential and not publicly obtainable. Published tax options are not direct substitutes.
- Full SSA benefit and CMS HI+SMI joint dynamic model: **not reproduced**.
- Full tax-benefit interaction for all 12 sections and national incidence: **not calculated**.
- Interest and macro feedback with appropriations spendout and FY calendar adjustments: **not calculated**.

**Bottom line:** the new contribution is a tested, actual statutory mechanism with stronger public aggregate constraints, not a claim that a complete federal solution has already been scored.
