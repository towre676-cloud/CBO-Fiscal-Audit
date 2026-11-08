"""Transparent weighted distributional analysis for supplied household microdata.

The code performs actual arithmetic, but a synthetic sample cannot establish
US distributional effects. Public CPS ASEC, Consumer Expenditure, and IRS SOI
records need proper linkage and calibration; no confidential returns are used.
"""
from decimal import Decimal as D
from dataclasses import dataclass

@dataclass(frozen=True)
class Household:
    ident: str
    weight: D
    baseline_disposable_income: D
    taxable_spending_ex_vat: D
    adults: int
    children: int


def household_vat_effect(households,rate,adult_rebate=0,child_rebate=0):
    """Tax-exclusive VAT arithmetic; no price-incidence or behavior model."""
    rate=D(str(rate));a=D(str(adult_rebate));c=D(str(child_rebate))
    if not (D(0)<=rate<=1) or a<0 or c<0:raise ValueError('Invalid VAT/rebate parameters')
    out=[];seen=set()
    for h in households:
        if h.ident in seen: raise ValueError('Duplicate household identifier')
        seen.add(h.ident)
        if not (h.weight.is_finite() and h.weight>0 and h.baseline_disposable_income.is_finite() and
                h.baseline_disposable_income>=0 and h.taxable_spending_ex_vat.is_finite() and h.taxable_spending_ex_vat>=0):
            raise ValueError('Invalid household weight/income/spending')
        if h.adults<0 or h.children<0 or h.adults+h.children<=0:raise ValueError('Invalid family members')
        vat=rate*h.taxable_spending_ex_vat
        rebate=h.adults*a+h.children*c
        out.append({'ident':h.ident,'weight':h.weight,'income':h.baseline_disposable_income,
                    'gross_vat':vat,'rebate':rebate,'net_vat_burden':vat-rebate})
    return out


def weighted_distribution(rows,groups=10):
    """Equal-weight income ranks using fractional split of survey weights.

    Splitting a weighted observation across percentile boundaries makes each
    group exactly 1/groups of population, even with sparse public use data.
    """
    if not rows:raise ValueError('Empty population')
    if not (isinstance(groups,int) and groups>0):raise ValueError('Invalid groups')
    arr=sorted(rows,key=lambda r:(r['income'],r['ident']))
    total=sum((r['weight'] for r in arr),D(0));target=total/D(groups)
    sums=[{'weight':D(0),'gross_vat':D(0),'rebate':D(0),'net_vat_burden':D(0),'income':D(0)} for _ in range(groups)]
    k=0
    for r in arr:
        remain=r['weight']
        while remain>0:
            if k>=groups:raise ValueError('Weight accounting exceeded groups')
            room=target-sums[k]['weight'];allocation=min(remain,room)
            for name in sums[k]:sums[k][name]+=allocation*(r[name] if name!='weight' else D(1))
            remain-=allocation
            if sums[k]['weight']>=target and k<groups-1:k+=1
    output=[]
    for i,g in enumerate(sums,1):
        output.append({'group':i,'weighted_population':str(g['weight']),
                       'average_baseline_income':str(g['income']/g['weight']),
                       'average_gross_vat':str(g['gross_vat']/g['weight']),
                       'average_rebate':str(g['rebate']/g['weight']),
                       'average_net_vat_burden':str(g['net_vat_burden']/g['weight'])})
    return output


def population_quality_gate(household_rows,real_sample=False,pce_coverage_ratio=None):
    """Refuses nationally representative claims without documented real data."""
    if not real_sample:return {'passed':False,'reasons':['Synthetic/unverified records cannot support real US income incidence']}
    if pce_coverage_ratio is None:return {'passed':False,'reasons':['Missing BEA PCE gross-up/crosswalk calibration']}
    ratio=D(str(pce_coverage_ratio))
    if not ratio.is_finite() or abs(ratio-1)>D('.01'):
        return {'passed':False,'reasons':['BEA PCE calibration must be within documented 1% research gate']}
    if not household_rows:return {'passed':False,'reasons':['Missing household microdata']}
    return {'passed':False,'reasons':['Tax, medical, transfer and asset cross-imputation still needs external validation']}
