# Research brief: fiscal constraints, partial identification and actuarial separation

**Version:** independent publication supplement, 7 November 2026. **Frozen reference:** CBO *Budget and Economic Outlook: 2026–2036*, February 11, 2026. **Claim type:** independently reproduced arithmetic on cited CBO excerpts, not a new official policy score.

## Result 1 — Two fiscal-stability objectives have materially different thresholds

Let federal fiscal-year nominal GDP be \(Y_t\), public debt at year-end be \(B_t\), and the positive annual deficit be \(F_t\). Let \(A_t\) be other financing adjustments, so that the CBO baseline reconciles as

\[
B_t=B_{t-1}+F_t+A_t.
\]

A **3%-of-GDP annual deficit** objective requires a direct static improvement

\[
\Delta F_t^{(3\%)}=\max\{0,F_t-0.03Y_t\}.
\]

A separate **one-year non-increasing public debt/GDP** objective requires

\[
\Delta B_t^{(\text{stasis})}=\max\{0,B_t-B_{t-1}Y_t/Y_{t-1}\}.
\]

For FY2036, published data yield annual deficit \(F_{2036}=3{,}115.387\) billion dollars, GDP \(Y_{2036}=46{,}712.1423975\), public debt \(B_{2036}=56{,}152.391\), and FY2035 counterparts \(Y_{2035}=45{,}011.4996755\), \(B_{2035}=53{,}103.223\). The exact static thresholds are therefore **$1,714.022728075 billion** for the deficit ratio and **$1,042.8005081199 billion** for one-year debt-ratio stasis. No additional 2026 law is assumed to have been scored into this frozen baseline.

The difference is economically important: *meeting a deficit threshold is neither necessary nor sufficient for achieving a specified debt trajectory without specifying growth, other financing, and timing*. This is a one-year counterfactual calculation and not a 75-year solvency proof.

## Result 2 — Full-PCE VAT arithmetic is a sensitivity boundary, not a tax-base estimate

CBO's February 2026 fiscal-year PCE series gives FY2036 nominal personal consumption expenditures of **$31,989.63122405 billion**. In a **purely mechanical** model with a 5% tax-exclusive rate, the entire PCE base taxed without any price or behavior change, and an assumed rebate equal to 20% of *gross* collections:

\[
\text{gross}=0.05\times31{,}989.63122405=1{,}599.4815612025\,\text{billion},
\]

\[
\text{net before administrative costs}=0.8\times\text{gross}=1{,}279.5852489620\,\text{billion}.
\]

It falls approximately **$434.437479113 billion short** of the 3%-deficit reference gap. The **proposed bill does not enact an across-the-board 20%-of-collections rebate**: §101 actually specifies an income- and poverty-guideline-indexed refundable credit. Exemptions, input credits, imputed items, cross-border consumption, government spending, compliance, tax-inclusive versus exclusive pricing and consumer responses all matter. This stylized quantity is **not** the maximum legally possible VAT revenue or a JCT estimate.

## Result 3 — FY budget flows, Social Security solvency, and Medicare HI must be separate

The 2026 OASDI Trustees' intermediate case projects **OASI reserve depletion in Q4 2032**, while the **separately constituted DI fund** remains funded through the 75-year horizon. A hypothetical combination would deplete in Q3 2034; combined is not automatically an authorized transfer. The Trustees report a **-4.42% of taxable payroll** 75-year actuarial balance for hypothetical combined OASDI, compared with **-4.55%** for OASI and **+0.13%** for DI. [Official SSA trustees' summary](https://www.ssa.gov/oact/TRSUM/).

For Medicare, the 2026 Trustees' summary projects **HI (Part A) depletion in Q2 2033** and reports a **-0.56% of HI taxable payroll** 75-year actuarial balance. HI taxable payroll is *uncapped*, unlike Social Security's capped contribution-and-benefit-base payroll. SMI Parts B/D are financed differently. [2026 trustees summary](https://www.ssa.gov/oact/trsum/).

These are **baseline actuarial outputs**. They are not evaluated effects of the twelve-provision bill, and one institution's actuarial percentages cannot simply be converted into federal fiscal-year cash effects or summed with another institution's figures.

## Result 4 — Aggregate tax marginals identify bounds, not returns

The February 2026 CBO tax-distribution file provides rank-group aggregates but not the joint return-level distribution of income, deduction choices, filing status, health coverage, capital gains and benefit participation. For a hypothetical tax on *AGI* of the form \(\tau\max(0,x-K)\), convexity gives, for a group of \(n\) returns with aggregate AGI \(S\):

\[
\sum_i\tau(x_i-K)_+\ge \tau(S-nK)_+.
\]

This is a Jensen lower bound on mechanical liability, **not** a revenue score or identified incidence. The statutory §102 surcharge uses **MAGI** (AGI plus specific add-backs) with filing-status-dependent thresholds; aggregate AGI shares cannot produce its actual score. CBO's tax-return groups are **not** consumer expenditure units or CPS households, and cannot be joined by rank alone. Full source constraints and examples are in [`research/V10_SUBSTANTIVE_POTENTIAL_FINDINGS.md`](../fiscalrazor/research/V10_SUBSTANTIVE_POTENTIAL_FINDINGS.md).

## Result 5 — Necessary, not sufficient, evidence for an affirmative result

A package with positive direct primary balance effects can still fail to stabilize debt if interest feedback, macro changes and payment lags offset them; a package with positive unified-budget effects may still fail OASI or HI legal solvency; a rebate may still leave low-income people net tax payers. Therefore an affirmative reform result needs a **single matched baseline** and explicit reconciliation of **(i)** legally specified taxes/outlays, **(ii)** first-order and interactive effects, **(iii)** fiscal-year timing, **(iv)** net interest and financing, **(v)** separate trust-fund reserves and long-run adequacy, and **(vi)** weighted household distribution and uncertainty.

This repo implements useful pieces of that chain but does **not** claim to have finished the combined computation.

## Reproduce

```bash
python scripts/build_publication.py
python -m unittest discover -s publication/tests -q
```

The CSV is [`publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv`](../publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv). Values are sourced from the project's verbatim CBO **excerpts**, which identify upstream Git blobs; the full byte-identical originals must still be obtained separately to close the external replay requirement.
