# FiscalRazor v1.0 — Evaluating the actual potential of the 12-provision proposal

**Evidence cut:** November 7, 2026. **Status:** Independently reproduced partial-identification laboratory, NOT the complete 2026-law reform score. Full current-law fiscal, beneficiary, and household joint models remain open.

## Executive finding

The package has several independently measurable components capable of materially improving federal finances or entitlement reserve balances. However, **no mathematically defensible combined 12-provision fiscal estimate exists yet**. All standalone government option analogues below are from **December 12, 2024**, under a different law and baseline; their FY2034 dollar amounts cannot be summed or directly ported to the proposed 2028–2029 laws.

Numerically exact source-baseline fiscal objective:

* **FY2034:** $1,517.300 billion reduction needed to reach a 3%-of-GDP deficit, prior to policy feedback.
* **FY2036:** $1,714.023 billion.

### Twelve provisions and the nearest independently published CBO option, FY2034

The amounts are **independent FY2034 CBO/JCT budget option deficit reductions** in billions of dollars. They are NOT scores for our law, except that the +1pp corporate option is comparatively close; that too has a different start date and tax baseline.

| Section | Our drafted policy | Official FY2034 analogous option (billions) | Mismatch |
|---|---|---:|---|
| §101 | 5% VAT + income-tested credit | $290.0 | Narrow-base VAT excludes categories; 2026 start; no draft-equivalent refundable credit ([source](https://www.cbo.gov/budget-options/60961)) |
| §102 | 2% high-income MAGI surtax | $133.9 | Official AGI surtax starts at $100k/$200k, not $500k/$1m MAGI ([source](https://www.cbo.gov/budget-options/60938)) |
| §103 | High-income 28% itemization benefit cap | $249.5 | Official cap is 15% broadly, not our 28% high-income limit ([source](https://www.cbo.gov/budget-options/60939)) |
| §104 | Employer health exclusion annual cap | $100.0 | Official cap includes accounts, not identical premium terms ([source](https://www.cbo.gov/budget-options/60953)) |
| §105 | Corporate 21% → 22% | $15.7 | Close rate change; tax-law vintage and effective date differ ([source](https://www.cbo.gov/budget-options/60956)) |
| §106 | Additional OASDI above indexed $250k | $192.0 | Official threshold remains nominally $250k; our threshold indexed, starts later ([source](https://www.cbo.gov/budget-options/60955)) |
| §107 | Phased combined +1pp OASDI | $155.0 | Official 1% new tax covers uncapped payroll and general revenues; ours is OASDI-covered base ([source](https://www.cbo.gov/budget-options/60954)) |
| §108 | Progressive-price PIA indexing | not available | SSA option only; CY actuarial, not an FY federal score ([source](https://www.ssa.gov/oact/solvency/provisions/tables/table_run153.html)) |
| §109 | MA coding + benchmark rules | $85.0 | Official uniform 10% benchmark cut, not our coding + 105% cap ([source](https://www.cbo.gov/budget-options/60900)) |
| §110 | Site-neutral clinic visit payments | $26.4 | Official option covers most HOPD services, broader than visits ([source](https://www.cbo.gov/budget-options/60908)) |
| §111 | 5% defense base-BA ceiling | not available | No matching annual BA-to-outlay score ([source](https://www.cbo.gov/budget-options/60920)) |
| §112 | Phased combined +0.75pp HI rate | not available | Trust-fund mechanical tax model below; no matching FY policy score ([source](https://www.cms.gov/oact/tr/2026)) |

**The table is deliberately non-additive.** Historic option choices overlap through wage incidence, payroll and individual tax offsets, enrollment, eligibility, medical pricing and federal cash timing. Many option estimates include netting. No blank may be replaced by zero. The 2024 baseline assumed different tax law from legislation enacted in 2025; the bill has different thresholds, effective dates and exemptions.

## Fixed-base VAT mathematical constraint

This calculation assumes *every dollar* of CBO projected nominal personal consumption expenditures (PCE) is taxable under a flat 5% tax-exclusive rate, 100% statutory compliance, no change in spending or prices, and **zero household rebate**. It is an intentionally generous reference envelope conditional on the VAT universe being a subset of PCE, **not a strict upper bound for all legally possible VAT bases**.

| FY | CBO projected nominal PCE ($B) | Hypothetical 5% all-PCE gross ($B) | Gap to 3% deficit ($B) | Residual even with no rebate ($B) |
|---|---:|---:|---:|---:|
| 2034 | 29,571.8 | 1,478.6 | 1,517.3 | **38.7** |
| 2036 | 31,989.6 | 1,599.5 | 1,714.0 | **114.5** |

Our actual §101 excludes food, actual medical care, rents, tuition, imputed finance and other areas, and pays a specific income-related refundable credit. Therefore **the all-PCE benchmark is not the legally proposed VAT result**. CBO/JCT estimated its separate 2024 narrow-base 5%-VAT option at **$290 billion FY2034**, versus its broad-base option at **$440 billion**. Both estimates are measured under a different law/base/start date and without our refundable credit. Source: https://www.cbo.gov/budget-options/60961

## Household credit: a mathematical distributional warning from the exact proposed law

Let **P** equal the contemporaneous HHS poverty guideline applicable to the tax household, **Y** its MAGI, and **C** its VAT-taxable consumption, under full pass-through. Our draft §101 defines credit `0.05 * P * clamp((3P-Y)/P,0,1)` and gross VAT `0.05*C`. Therefore:

* **Y ≤ 2P:** credit = 0.05P; net VAT = 0.05(C−P). A household loses money mechanically whenever C exceeds P, despite a full credit.
* **2P < Y < 3P:** credit = 0.05(3P−Y); net VAT = 0.05(C+Y−3P). Break-even taxable consumption falls from P toward zero as Y rises.
* **Y ≥ 3P:** credit = 0 and net VAT = 0.05C.

For example, if a household has Y=1.5P and C=1.25P, it pays a net 0.0125P under the draft VAT+credit in the no-price-response case. This is a symbolic example, **not a nationally weighted poverty incidence estimate**. Other payroll, health and income tax provisions are excluded from this example. It demonstrates that the current rebate design does not guarantee every lower-income household is held harmless.

**Reform improvement to test:** a refundable credit scaled to directly measured eligible consumption for low-income households or a targeted supplemental credit may improve protection, but its population cost must be estimated using validated CPS ASEC + BLS Consumer Expenditure data, consistent poverty units, payment timing and nonfiler takeup.

## Medicare HI: frozen 2026 Trustees three-scenario test

§112 imposes extra combined HI contributions of 0.25pp in 2028, 0.50pp in 2029, 0.75pp from 2030 onward. For each scenario in the official CMS 2026 Trustees Table III.B5, this module recovers the projected HI taxable-payroll base `annual expenditures / (published cost rate / 100)`, then adds the new contributions to published baseline reserves without behavioral or interest feedback. **These are not actuarial rescoring results.** The table is rounded by CMS.

| Trustees scenario | 2035 frozen-model year-end assets ($B) | 2035 assets / 2035 expenditures | Full-phase extra HI rate to give 100% 2035 reserve under same model |
|---|---:|---:|---:|
| Low Cost | 1,821.7 | 224.3% | 0.039 percentage points |
| Intermediate | 655.4 | 74.7% | 0.925 percentage points |
| High Cost | -381.5 | -40.2% | 1.934 percentage points |

The reference §112 reaches 0.75pp in 2030. Intermediate 2035 reserves stay positive but below the 100% reserve convention; high-cost projections turn negative in **2033** even after the new payroll levy. The rate-scaling estimates require all earlier years of the phase-in to scale proportionally, and reaching 100% **at end-2035 alone** says nothing about within-year liquidity, preceding-year reserve standards or 75-year actuarial balance.

Source: https://www.cms.gov/oact/tr/2026. No formal recomputation of the Office of the Actuary long-range model has occurred.

## Social Security: demonstrated substantial standalone effects but incomplete reform

SSA 2026 single-provision estimate E2.5: CY2036 +2.53pp of *current-law taxable payroll*; payroll projection $17,125B, hence annual balance equivalent **$433.26B**. This is not our indexed-high-threshold §106 (which starts in 2028), and it is not a federal FY deficit score. Source: https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html

§107 mechanical contribution on the capped current-law OASDI wage base at CY2036 is 1% × $17,125B = **$171.25B**. This excludes the §106 high-income donut, employer-to-worker wage adjustment, income tax offset, fiscalization and benefits. The current-law OASI and DI funds still need separate annual reserves and 75-year combined actuarial testing.

In particular, the CBO/JCT FY2034 **$192B net federal budget option** for taxing income above fixed nominal $250k cannot be equated with the SSA CY2034 E2.5 **~$400.8B actuarial annual-balance equivalent**. They have different timing, tax bases, scopes and estimands. Source: https://www.cbo.gov/budget-options/60955.

## Two more directly quantified pieces of our exact draft

### Section 102: a lower bound on 2028 high-income surtax liability using real CBO aggregates

CBO projects CY2028 **172.1 million individual returns**, **$20,074.8 billion adjusted gross income**, and **22.9% of AGI** held by the highest-income 1% of returns (original CBO February 2026 revenue-detail file, Git blob `2507f312912b0ff6475690c20a1a56d175772276`). Therefore the top 1% represents **1.721 million returns** and **$4,597.1292 billion AGI**.

Our exact §102 imposes 2% on each return's MAGI above a threshold no larger than **$1 million in CY2028**. MAGI is at least AGI under our specified addbacks. Therefore, for this top-1% group, the positive-part inequality gives:

`sum_i max(0, MAGI_i − threshold_i) >= max(0, sum_i AGI_i − $1M × N)`

`>= max(0, $4,597.1292B − $1,721B) = $2,876.1292B`.

The **first-year top-1% mechanical surtax liability is therefore at least $57.522584 billion** under the unmodified CBO-projected aggregate distribution. This is a rigorous lower bound conditional on those projections and on nonbehavioral taxpayer income, regardless of how income varies within the top 1%. It is NOT a fiscal receipt estimate: it excludes avoidance, taxable income changes, filing time, credits, wage incidence and fiscalization; it also omits all other filers. Government source: https://github.com/US-CBO/cbo-data/blob/main/data/budget/revenue_detail/annual_cy_iit_2026-02.csv

### Section 111: defense spending authority is not immediate spending

From the frozen February 2026 defense budget-authority series, the 2034 base-defense BA estimate is **$1,085.340 billion**; §111 caps it at **$1,031.073 billion**, a mechanical BA difference of **$54.267 billion**. The 2036 BA difference is **$56.826 billion**. These are appropriations authority changes, not confirmed outlay or deficit savings in those fiscal years. Account-level spendout patterns and existing obligations determine when and how cash flows change.

## What this does and does not close

**Completed:** original v0.9 project preserved, four kinds of source-distinguished calculation, nine official individual-policy comparator values, thirty-three CMS scenario observations, 11 SSA actuarial observation years, ten CBO fiscal target gaps, exact VAT household rebate break-even algebra, executable guards against combining the distinct quantities, regression tests.

**Not completed:** full original CBO source-byte acquisition in this container, full original CPS/BLS/IRS/CMS microdata ingestion, representative household-level tax-benefit incidence, CMS 75-year reform run, separate OASI/DI actuarial joint reform, current-law twelve-provision CBO/JCT fiscal score, economic feedback, and validation against an official enacted-bill score. Those are actual unresolved scientific obligations.

**Research priority:** obtain original-source bytes on a networked machine; reproduce official baseline totals under current law; match a held-out enactment or historical policy; implement a single joint twelve-provision model with all 66 pair interactions and higher-order sensitivity, then stress-test debt and trust funds under alternate scenarios. Do not replace missing effects with an invented overlap factor.
