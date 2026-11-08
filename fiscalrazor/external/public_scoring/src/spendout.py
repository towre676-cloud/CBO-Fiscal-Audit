"""Budget-authority changes -> outlays using account-specific assumed lag weights.

Historical patterns must be supplied and externally calibrated before using
this as an estimate. No default spendout coefficients: a defense BA reduction
is not automatically equal to same-year cash savings.
"""
from decimal import Decimal as D
from collections import defaultdict


def budget_authority_to_outlays(ba_change_by_year,spendout_kernel,through_year=None):
    """Maps signed BA cuts to signed outlay cuts. Full kernel must sum to 1.

    `ba_change_by_year` positive = reduced BA; positive outlays are reduced.
    Allows lag zero to 30; no overlap with other budget accounts.
    """
    if not ba_change_by_year:raise ValueError('Provide annual BA changes')
    if not spendout_kernel or any(not isinstance(k,int) or k<0 or k>30 for k in spendout_kernel):
        raise ValueError('Need explicit 0..30-year lag weights')
    weights={lag:D(str(x)) for lag,x in spendout_kernel.items()}
    if any(not w.is_finite() or w<0 for w in weights.values()) or abs(sum(weights.values())-1)>D('.000000001'):
        raise ValueError('Spendout weights must be nonnegative and sum to one')
    out=defaultdict(D)
    for y,v in ba_change_by_year.items():
        if not isinstance(y,int):raise ValueError('BA years must be integers')
        amt=D(str(v))
        if not amt.is_finite() or amt<0:raise ValueError('BA reduction must be nonnegative and finite')
        for lag,w in weights.items():out[y+lag]+=amt*w
    last=through_year or max(out)
    return {'outlay_reductions_billion':{y:out[y] for y in sorted(out) if y<=last},
            'post_horizon_unspent_billion':sum((v for y,v in out.items() if y>last),D(0)),
            'total_BA_reduction_billion':sum((D(str(x)) for x in ba_change_by_year.values()),D(0)),
            'source_status':'UNVALIDATED_USER_SUPPLIED_SPENDOUT_KERNEL_NOT_CBO_SCORE'}
