"""Exact statutory-base arithmetic for a single worker, NOT an SSA/JCT population score.

The program models a combined employer+employee OASDI rate on W2 wages only;
self-employment, multiple employers, stock options and wages across jobs must
be handled separately. 'No additional benefit credit' matches SSA option E2.5.
"""
from decimal import Decimal as D

def worker_oasdi_overlap(wages,taxable_max,high_threshold,combined_base_rate='0.124',
                         combined_rate_increase='0',increase_applies_high_earnings=False):
    w,m,t,r,delta=map(lambda x:D(str(x)),(wages,taxable_max,high_threshold,combined_base_rate,combined_rate_increase))
    if not all(x.is_finite() for x in (w,m,t,r,delta)) or min(w,m,t,r,delta)<0 or r+delta>1:
        raise ValueError('Invalid wages, tax maximum, threshold or rate')
    normal=min(w,m)
    new_taxable=max(D(0),w-max(m,t))  # no double taxation when m exceeds the $250k threshold
    base=normal*r
    high_only=(normal+new_taxable)*r
    rate_only=normal*(r+delta)
    joint=rate_only+new_taxable*(r+delta if increase_applies_high_earnings else r)
    interaction=joint-base-(high_only-base)-(rate_only-base)
    return dict(wages=str(w),current_law_taxable_wages=str(normal),
      new_high_wage_tax_base=str(new_taxable), current_law_combined_tax=str(base),
      high_earnings_only_increment=str(high_only-base),rate_increase_only_increment=str(rate_only-base),
      joint_tax_increment=str(joint-base), mechanical_interaction=str(interaction),
      measurement='DOLLARS_PER_WORKER_NOT_A_POPULATION_ESTIMATE',
      benefits='no_additional_benefit_credit_assumed',
      scope='W2_wages_single_worker; no income shifting, deductions or JCT interactions')
