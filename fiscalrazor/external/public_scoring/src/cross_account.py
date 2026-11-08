"""Unified-budget versus trust-fund accounting for ILLUSTRATIVE fiscal-year cash.

This is a classification/conservation engine, not a CBO/SSA/CMS score.
External receipts and outlays are counted ONCE in unified primary cash;
Treasury transfers and special-issue trust-fund interest are NOT new
outside-the-federal-government revenue. The latter may change fund reserves
without improving the consolidated federal balance.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from decimal import Decimal as D

FUNDS=frozenset(('GENERAL','OASI','DI','HI','SMI'))
EXTERNAL=frozenset(('external_receipt','external_outlay'))
INTERNAL=frozenset(('intragovernmental_transfer','trust_fund_interest_credit'))

@dataclass(frozen=True)
class CashEffect:
    fiscal_year:int
    unique_accounting_key:str
    instrument:str
    kind:str
    amount_billion:D
    account:str='GENERAL'
    source_fund:str=''
    destination_fund:str=''
    evidence_status:str='USER_ASSUMED_OR_SYNTHETIC'


def reconcile_cash_ledger(effects, first_fy=2027, last_fy=2036):
    """Classify signed *changes* in FY public cash and intra-agency flows.

    For an external receipt positive amount = higher public payment to govt.
    For an external outlay positive amount = higher public payment by govt.
    Internal amount positive moves money from `source_fund` to `destination_fund`.
    No assumption here can pass an official or independent validation gate.
    """
    if not (isinstance(first_fy,int) and isinstance(last_fy,int) and first_fy<=last_fy):
        raise ValueError('Invalid fiscal period')
    unified=defaultdict(D); account=defaultdict(lambda:defaultdict(D))
    external=defaultdict(lambda:{'receipts':D(0),'outlays':D(0)})
    seen=set();count=0
    for item in effects:
        if not isinstance(item,CashEffect):raise TypeError('CashEffect required, not a generic untyped score')
        y=item.fiscal_year
        if not isinstance(y,int) or y<first_fy or y>last_fy:
            raise ValueError(f'Fiscal year outside declared window: {y}')
        key=(y,item.unique_accounting_key)
        if not item.unique_accounting_key.strip() or key in seen:raise ValueError('Duplicate or empty year/account ownership')
        seen.add(key)
        if not item.instrument.strip():raise ValueError('Instrument required')
        if item.kind not in EXTERNAL | INTERNAL: raise ValueError('Unknown cash effect classification')
        val=D(str(item.amount_billion))
        if not val.is_finite():raise ValueError('Non-finite amount')
        if item.kind in EXTERNAL:
            if item.account not in FUNDS: raise ValueError('Unknown recipient/spending account')
            if item.source_fund or item.destination_fund:raise ValueError('External event may not also carry an internal transfer')
            if item.kind=='external_receipt':
                unified[y]+=val;account[y][item.account]+=val;external[y]['receipts']+=val
            else:
                unified[y]-=val;account[y][item.account]-=val;external[y]['outlays']+=val
        else:
            a,b=item.source_fund,item.destination_fund
            if a not in FUNDS or b not in FUNDS or a==b:
                raise ValueError('Internal entries require distinct legal fund source and destination')
            if item.kind=='trust_fund_interest_credit' and (a!='GENERAL' or b not in ('OASI','DI','HI')):
                raise ValueError('Special issue interest classification only GENERAL -> OASI/DI/HI')
            account[y][a]-=val;account[y][b]+=val
            # Intrafederal money is not new public taxes nor third-party spending.
        count+=1
    output=[]
    for y in range(first_fy,last_fy+1):
        bal=unified[y]
        byfund={f:account[y][f] for f in sorted(FUNDS)}
        if sum(byfund.values(),D(0))!=bal:raise AssertionError('Consolidated cash does not reconcile')
        output.append({'fiscal_year':y,'delta_unified_primary_balance_billion':str(bal),
             'delta_public_receipts_billion':str(external[y]['receipts']),
             'delta_public_noninterest_outlays_billion':str(external[y]['outlays']),
             'by_fund_balance_change_billion':{k:str(v) for k,v in byfund.items()},
             'internal_flows_add_to_unified_savings':False,
             'status':'CLASSIFIED_CASH_FLOWS_NOT_ACTUARIAL_OR_LEGISLATIVE_SCORE'})
    return {'years':output,'entry_count':count,'independently_approved':False,
        'unified_policy_score':'NOT_ESTABLISHED','net_interest_and_macro_feedback':'NOT_ESTABLISHED',
        'trust_fund_depletion_forecast':'NOT_ESTABLISHED'}
