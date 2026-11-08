"""Fiscal-year cash mapping of calendar-year series under explicitly specified monthly schedules.

Use ONLY after the policy component has been independently estimated as monthly
cash. A uniform schedule is a pedagogical timing transformation, not evidence
about JCT's actual quarterly estimated-tax or settlement payment distributions.
"""
from decimal import Decimal as D


def fiscalize_calendar_cash(cy_cash: dict, months: dict | None=None, first_fy=2027,last_fy=2036):
    """FY y = October-December CY(y-1) plus January-September CY(y).

    By default only: flat monthly cash distribution. months optional mapping
    of 1..12 to fractions summing to 1, shared across years.
    """
    if months is None: months={m:D(1)/D(12) for m in range(1,13)}
    if set(months)!=set(range(1,13)):raise ValueError('Require 12 calendar-month weights')
    weights={m:D(str(v)) for m,v in months.items()}
    if any(not v.is_finite() or v<0 for v in weights.values()) or abs(sum(weights.values())-1)>D('0.00000001'):
        raise ValueError('Month weights must be a finite, nonnegative distribution totaling 1')
    if not isinstance(first_fy,int) or not isinstance(last_fy,int) or first_fy>last_fy:
        raise ValueError('Invalid fiscal year range')
    expected=set(range(first_fy-1,last_fy+1))
    if not expected.issubset(cy_cash):raise ValueError(f'Missing CY cash-flow values: {sorted(expected-set(cy_cash))}')
    prior_share=sum(weights[m] for m in (10,11,12))
    now_share=sum(weights[m] for m in range(1,10))
    output={}
    for fy in range(first_fy,last_fy+1):
        prev,now=D(str(cy_cash[fy-1])),D(str(cy_cash[fy]))
        if not (prev.is_finite() and now.is_finite()):raise ValueError('Nonfinite CY cash flow')
        output[fy]=prev*prior_share+now*now_share
    return output


def rate_to_fy_exercise(ssa_series):
    """Timing demonstration ONLY: actuarial balances aren't cash collections.

    Explicitly prohibited as a federal tax-receipts estimator. Kept solely
    to quantify the calendar boundary sensitivity of published SSA measures.
    """
    vals={r['calendar_year']:D(r['derived_nominal_annual_balance_change_billion']) for r in ssa_series}
    fy=fiscalize_calendar_cash(vals)
    return [{'fiscal_year':y,'pure_timing_exercise_billion':str(v.quantize(D('.0001'))),
             'status':'NOT_VALID_AS_FY_TAX_REVENUE_OR_FEDERAL_SCORE'} for y,v in fy.items()]
