"""Table-faithful CMS Medicare 2026 baseline and carefully bounded algebra.

All data are published one-decimal BILLIONS of nominal dollars, CALENDAR years.
Additional inflow is a purely algebraic counterfactual, NOT a policy score.
"""
from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import csv

D=Decimal
BASE=Path(__file__).resolve().parents[2]
HI=BASE/'data/verified_tables/cms_2026_hi_operations_cy2025_2035.csv'
SMI=BASE/'data/verified_tables/cms_2026_smi_operations_cy2025_2035.csv'
MONEY=('income_bn','expenditures_bn','change_in_fund_bn','assets_year_end_bn')
ROUND_TOL=D('0.151')   # sums/differences of separately rounded one-decimal columns

def rows(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        result=list(csv.DictReader(f))
    if not result: raise ValueError('EMPTY_MEDICARE_SOURCE')
    for r in result:
        r['calendar_year']=int(r['calendar_year'])
        for field in MONEY:
            r[field]=D(r[field])
    return result

def validate_hi(path=HI):
    result=rows(path)
    if [r['calendar_year'] for r in result]!=list(range(2025,2036)):
        raise ValueError('HI_YEAR_COVERAGE_REQUIRED_2025_2035')
    if result[0]['status']!='actual': raise ValueError('2025_HI_MUST_BE_ACTUAL')
    if any(r['status']!='projected' for r in result[1:8]):
        raise ValueError('PRE_EXHAUSTION_HI_PROJECTED')
    if any(r['status']!='hypothetical_after_depletion' for r in result[8:]):
        raise ValueError('HI_POST_DEPLETION_NOT_LEGAL_CASH')
    for i,r in enumerate(result):
        if abs(r['income_bn']-r['expenditures_bn']-r['change_in_fund_bn'])>ROUND_TOL:
            raise ValueError(f"HI_FLOW_MISMATCH_{r['calendar_year']}")
        if i and abs(result[i-1]['assets_year_end_bn']+r['change_in_fund_bn']-r['assets_year_end_bn'])>ROUND_TOL:
            raise ValueError(f"HI_STOCK_FLOW_MISMATCH_{r['calendar_year']}")
        pct=r['assets_to_expenditures_pct']
        if i<9:
            if pct=='': raise ValueError('HI_EXPECTED_ASSET_RATIO_MISSING')
            prev_assets=D('237.5') if i==0 else result[i-1]['assets_year_end_bn']
            ratio=prev_assets/r['expenditures_bn']*D(100)
            if abs(ratio-D(pct))>D('0.60'):
                raise ValueError('HI_ASSET_RATIO_MISMATCH')
        elif pct!='': raise ValueError('NO_RATIO_POST_DEPLETION')
    if (result[8]['calendar_year'],result[8]['assets_year_end_bn'])!=(2033,D('-56.9')):
        raise ValueError('2033_HI_DEPLETION_SOURCE_ANCHOR')
    return result

def validate_smi(path=SMI):
    data=rows(path)
    grouped={name: [r for r in data if r.get('account')==name] for name in ('B','D','SMI')}
    if len(data)!=33 or any([r['calendar_year'] for r in rs]!=list(range(2025,2036)) for rs in grouped.values()):
        raise ValueError('SMI_ACCOUNTS_AND_YEARS_INCOMPLETE')
    for name,rs in grouped.items():
        for i,r in enumerate(rs):
            if r['status']!=('actual' if i==0 else 'projected'):
                raise ValueError('INVALID_SMI_STATUS')
            if abs(r['income_bn']-r['expenditures_bn']-r['change_in_fund_bn'])>ROUND_TOL:
                raise ValueError('SMI_ACCOUNT_FLOW_MISMATCH')
            if i and abs(rs[i-1]['assets_year_end_bn']+r['change_in_fund_bn']-r['assets_year_end_bn'])>ROUND_TOL:
                raise ValueError('SMI_ACCOUNT_STOCK_MISMATCH')
    for i in range(11):
        for field in MONEY:
            if abs(grouped['B'][i][field]+grouped['D'][i][field]-grouped['SMI'][i][field])>ROUND_TOL:
                raise ValueError(f'SMI_B_PLUS_D_TOTAL_{field}_{2025+i}')
    return grouped

def uniform_incremental_hi_inflow_floor(start_year=2027,end_year=2035, reserve_target_bn=D(0)):
    """Lower bound on a uniform *additional* positive HI income each year.

    Holds historical CMS expense/income/interest baseline unchanged; assumes
    contributions arrive early enough each year for year-end testing only.
    This is NOT a scored law, and cannot establish intra-year solvency or
    return-to-100% reserve adequacy.
    """
    if not isinstance(start_year,int) or not isinstance(end_year,int) or start_year!=2027 or not 2027<=end_year<=2035:
        raise ValueError('ONLY_2027_START_AND_PUBLISHED_HORIZON_SUPPORTED')
    target=D(str(reserve_target_bn))
    if not target.is_finite() or target<0: raise ValueError('NONNEGATIVE_FINITE_RESERVE_TARGET_REQUIRED')
    data=validate_hi()
    requirements={}
    for r in data:
        y=r['calendar_year']
        if start_year<=y<=end_year:
            requirements[y]=max(D(0),(target-r['assets_year_end_bn'])/D(y-start_year+1))
    bind=max(requirements,key=requirements.get)
    floor=requirements[bind]
    trajectory={y: next(r['assets_year_end_bn'] for r in data if r['calendar_year']==y)+floor*(y-start_year+1) for y in requirements}
    return {'annual_increment_bn':floor,'binding_calendar_year':bind,'target_reserves_bn':target,
            'year_end_path_bn':trajectory,'requirements_by_year_bn':requirements,
            'interpretation':'FIXED_BASELINE_ALGEBRA_ONLY_NOT_ACTUARIAL_OR_BUDGET_SCORE',
            'cash_timing':'ASSUMED_AVAILABLE_BEFORE_YEAR_END_NO_QUARTERLY_GUARANTEE'}

def end_of_2034_balance_needed_for_2035_full_reserve():
    """Uniform additional inflow CY2027-34 to make START-2035 assets >= CY2035 costs.

    This does NOT solve the short-range 100% contingency adequacy test in all
    years; 2027 begins with 50% current-law assets/expenses.
    """
    data=validate_hi();a2034=next(r['assets_year_end_bn'] for r in data if r['calendar_year']==2034)
    e2035=next(r['expenditures_bn'] for r in data if r['calendar_year']==2035)
    return (e2035-a2034)/D(8)

def refuse_smi_to_hi_transfer(amount,account):
    if account!='HI': raise ValueError('SMI_FUNDS_ARE_NOT_HI_FINANCING')
    return D(str(amount))
