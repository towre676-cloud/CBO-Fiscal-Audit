# FiscalRazor v1.0 — Actual Policy Potential, Not a Combined Score

Evidence cutoff: November 7, 2026. This is an executable continuation of the existing v0.9 federal reform research and source-acquisition package.

## Important results produced in this release

- 12 independent published CBO/JCT **December 2024** policy comparator entries (nine have FY2034 values, three have no equivalent), with legal differences preserved and addition forbidden.
- 33 official CMS 2026 Trustees Table III.B5 *input rows*, for low-cost, intermediate, and high-cost HI cash and reserve projections, then policy §112 additional tax under a frozen baseline. No claim of OACT certification.
- 2035 HI reserve adequacy scaling exercises for each scenario, with explicit 2035-only adequacy scope.
- 11 SSA single-option annual actuarial balance equivalents (CY, percentage of current-law taxable payroll; not FY cash).
- A CBO-based rigorous first-year mechanical $57.52B lower bound for the actual §102 surtax among projected top-1% returns; §111 defense-budget authority deltas distinguished from cash-outlay savings.
- A ten-year CBO fiscal target ledger and a ten-year 5%-of-all-PCE theoretical gross-collection benchmark; actual proposed VAT has exclusions and refunds.
- Symbolic household incidence for §101's own refundable credit formula, exposing when nominally rebate-eligible households still pay net VAT.

## Reproduction (Python 3.11+, standard library)

From this project's root:

```bash
PYTHONPATH=src python scripts/run_potential_v10.py
PYTHONPATH=src python scripts/build_v10_report.py
PYTHONPATH=src python scripts/build_v10_dashboard.py
PYTHONPATH=src python -m unittest discover -s tests -q
(cd external/public_scoring && python -m unittest discover -s tests -q)
```

Open `policy_potential_v10.html` directly in a browser, or start with `research/V10_SUBSTANTIVE_POTENTIAL_FINDINGS.md`.

## Evidence status / no false claims

These tests certify code behavior against retained published-reference tables and negative cases. They do NOT verify acquisition of 18 raw original CBO data files, any original CPS ASEC/CE/IRS/CMS administrative or survey microdata, or original SSA/CMS production scoring systems. The 2024 CBO option figures differ from the 2026 CBO baseline and from the drafted 12-provision law. The 2026 Medicare trustees' intermediate/low/high trajectories hold future expenses and incomes fixed and lack a joint dynamic rerun. The original government agencies have not scored this entire proposal.

The preexisting source-acquisition scripts, legal drafting, variance estimators, and public scoring code are preserved, but they must ingest verified originals and pass calibration gates before national household or joint score claims.

This release includes a SHA-256 integrity manifest for all included files, excluding the manifest itself.
