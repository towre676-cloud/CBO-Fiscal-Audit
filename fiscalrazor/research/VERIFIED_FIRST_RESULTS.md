# First exact research results: accounting identities and statutory mechanics

**Status.** Mathematical statements in this document are proved algebraic consequences of the *chosen hypothetical draft*, or arithmetic consequences of the stated CBO February 2026 published baseline. They are **not** estimates of behavioral response, macroeconomic feedback, national collections, distributional effects or actuarial solvency.

## Result A — Fiscal primary-balance target identity

Let `Y` be nominal FY2036 GDP in billions of dollars, `D` the positive annual deficit, `I` net interest, and `P=D−I` the positive primary deficit (negative signed primary balance). Then a 3%-GDP deficit ceiling, keeping the baseline GDP unchanged, requires direct improvement plus net interest response equal to at least

`G = D − 0.03Y`.

The published CBO February 2026 retained source observations are `Y=46712.1423975`, `D=3115.387`, `I=2144.336`, `P=971.051`. Thus `G=1714.022728075`. If net interest were unchanged, the post-reform primary balance would have to be a **surplus** of `I−0.03Y = 742.971728075` billion. The proof is simple substitution into `deficit = interest − signed_primary_balance`; it does not supply any policy's contribution.

A full period's improvement is not the product `10 × G` because the baseline, GDP, interest, legal commencement and collection timing change annually. The script produces each year's independent target in `results/v06/static_fiscal_target_2027_2036.csv`.

## Result B — The extended OASDI tax base has an exact non-overlap decomposition

Let `w≥0` be wages from one employer, `B` the statutory old Social Security wage cap, `H=max(B,250000)` for 2028, and `q_y` the **combined employee+employer extra rate** from §107 (`q_2028=0.002`; `q_2032=0.010`). Set `L=min(w,B)` and `E=max(0,w−H)`. The *proposed* combined gross statutory tax is `(0.124+q_y)(L+E)` and the baseline is `0.124L`. Subtracting gives the exact decomposition

`ΔT(w,y)= 0.124 E + q_y L + q_y E`.

The final term is the **interaction**. It must occur exactly once. This formula is continuous but its marginal burden changes at wage base and high-band thresholds, making its economic incidence sensitive to the wage distribution near those kinks. It does not imply the new tax can be collected without payroll administration changes or that it equals net unified-budget improvement.

**Hand-verifiable synthetic example:** with wages `$350,000` and **hypothetical** 2028 `B=$192,300` (the public actual 2027 wage maximum, explicitly **not** a forecast for 2028), the extended taxable high band is `$100,000`. The new high band adds `$12,400`, the baseline-band rate phase adds `$384.60`, and their interaction adds `$200`: total **$12,984.60** in additional combined employee/employer statutory OASDI taxes. Excludes income tax and compensation responses. Verified by code regression tests.

## Result C — A high-earnings threshold independent of employer splitting

Let covered income arise from components `w_1,...,w_n` (employers and/or covered self-employment), with `W=sum_i w_i` and `E=max(0,W−H)`. Assign high-band tax bases `e_i = E w_i / W` for `W>0`, and `e_i=0` for `W=0`. Then **sum_i e_i = E** exactly. Splitting a wage into two payers while keeping total covered income unchanged leaves the *aggregate* high-band base and total high-band rate unchanged. This is a direct proof: `sum_i(Ew_i/W)=E(sum_iw_i)/W=E`. The employer proportions redistribute responsibility, rather than letting two sub-threshold employers erase the high-income tax.

**Test:** `$180,000+$180,000` with `H=$250,000` yields aggregate high earnings of `$110,000` and allocations `$55,000/$55,000`. A per-employer `$250,000` threshold would collect **nothing** on the high band, despite `$360,000` of total compensation. The current-law normal OASDI employer wage-base taxation is a **separate law** and is *not* changed into a household-wide cap by this result.

**Open implementation question:** IRS W-2 reconciliation, SECA coordination, privacy-preserving employer notice, required timing, avoidance incentives and litigation over allocation are not tested here. The draft proposes pro rata allocation and delayed employer assessment; congressional counsel and IRS administration must settle details before a valid real-world score.

## Result D — The VAT credit does not neutralize all low-income consumption

For the chosen VAT design, let `P>0` be the official poverty guideline and `C≥0` be *eligible taxable* pre-VAT household consumption. For MAGI `M≤2P`, the full credit is `0.05P` and gross VAT is `0.05C`, so net statutory burden is `0.05(C−P)`. Therefore the credit neutralizes gross VAT **if and only if** `C=P` and gives a net benefit if `C<P` or net tax if `C>P` (before changes in prices, incomes and other tax/benefit systems). Hence claiming the credit *guarantees* all low-income households are made whole would be mathematically false.

For `2P<M<3P`, the credit equals `0.05(3P−M)`, giving `net=0.05[C−(3P−M)]`. These exact boundaries identify what the genuine CPS/CE incidence simulation must measure. No national share of winners or losers can be inferred without observed C, P, M, medical spending, benefits, and survey weights. A filing tax unit and a resident household are not always identical; matching them requires a documented crosswalk.

## Result E — Trust-fund financing is not another unified-budget receipt

Under §112, employee plus employer extra HI taxes are 0.25% of uncapped wages in 2028, 0.50% in 2029 and 0.75% from 2030. For a synthetic `$1,000,000` wage, the incremental combined statutory HI taxes are `$2,500`, `$5,000` and `$7,500`. A deposit into the HI trust fund changes fund cash **and** the associated federal receipt line but must not count as two federal budget revenues. Independent additional interest effects and SMI premium offsets are separate unknowns.

## Result F — Defense authority is not outlays

The legislation fixes annual discretionary **budget authority** ceilings based on a frozen reference. For each spending account `a`, actual outlay effects require calibrated nonnegative spendout coefficients `s_{a,k}` and a time convolution:

`ΔOutlay_(a,y) = sum_(t≤y) ΔBA_(a,t) × s_(a,y−t)`.

No account-level `s` is yet validated in the present archive. It is mathematically impossible to infer FY2028 cash savings from the FY2028 cap alone. The 2026-02 published base-defense BA reference and the draft 95% cap values are retained as explicit **chosen parameters** in `data/v06/defense_ba_cap_locked.csv`, not savings.

## Source and verification scope

CBO, February 2026: https://github.com/US-CBO/cbo-data ; SSA OASDI §§: https://www.ssa.gov/oact/TR/2026/ ; SSA 2027 wage maximum: https://www.ssa.gov/cola/factsheets/2027.html ; Medicare trust funds: https://www.cms.gov/data-research/statistics-trends-and-reports/trustees-report-trust-funds . No full agency source archives were acquired as part of this iteration; the numerical CBO anchors are the previously retained selected extracts, source-verified at the model-data level in the prior work.

## Result G — One-year debt-ratio stability requires a different adjustment than a 3%-GDP deficit ceiling

Let current-year nominal GDP be `Y_t`, prior-year GDP `Y_(t−1)`, public debt `L_(t−1)`, current positive deficit `D_t`, and other financing adjustment `F_t`. The published debt stock-flow identity is `L_t = L_(t−1)+D_t+F_t`. Holding the prior stock, nominal GDP and other financing fixed, the requirement **not to increase the public-debt-to-GDP ratio across these two years** is

`D_t ≤ [L_(t−1) × (Y_t/Y_(t−1) − 1)] − F_t`.

Proof: `L_t/Y_t ≤ L_(t−1)/Y_(t−1)`; multiply by `Y_t>0`, substitute debt stock flow and rearrange. This is an **exact one-period algebraic condition**, not a 75-year sustainability test.

For FY2036, the CBO February 2026 retained values are FY2035 public debt `53103.223B`, FY2035 nominal GDP `45011.4996755B`, FY2036 GDP `46712.1423975B`, FY2036 other financing `−66.219B`, and FY2036 baseline deficit `3115.387B`. The one-year allowed deficit is `2072.586491880...B`, so avoiding a ratio increase relative to the FY2035 baseline requires **1042.800508119...B** of direct improvement *within that frozen one-year comparison*. This is less than the independent 3%-deficit gap `1714.022728075B` because nominal GDP is growing. Both must be reevaluated if the prior-year debt stock, interest rates, growth, other financing or policy parameters change.

The exact annual 2027–2036 frozen one-period calculations appear in `results/v06/one_year_debt_ratio_frozen_diagnostics_2027_2036.csv`. This is part of **our independent stabilization-frontier research**, not an official CBO policy score.
