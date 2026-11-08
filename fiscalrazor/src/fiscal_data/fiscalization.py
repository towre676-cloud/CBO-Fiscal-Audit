"""Tax/budget timing with explicit CY liability vs FY CASH type gates.

Includes NO JCT-estimated timing shares. Monthly CASH data can be regrouped
exactly. Calendar-year LIABILITIES cannot be converted to CASH without a
separate, source-described payment model.
"""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
from datetime import date
import re

D=Decimal
MONTH_RE=re.compile(r'^([12][0-9]{3})-(0[1-9]|1[0-2])$')
CASH='cash_receipt_or_outlay'
LIABILITY='calendar_year_tax_liability'

def _amount(v):
    try: x=D(str(v))
    except Exception as ex:raise ValueError('NOT_A_NUMERIC_CASH_AMOUNT') from ex
    if not x.is_finite():raise ValueError('NON_FINITE_CASH_AMOUNT')
    return x

def fiscal_year(yyyy_mm):
    m=MONTH_RE.fullmatch(yyyy_mm)
    if not m:raise ValueError('INVALID_YYYY_MM')
    year,month=int(m.group(1)),int(m.group(2))
    return year+(month>=10)

def fiscalize_cash_months(records):
    """Every input row requires the external source's actual cash basis.

    Missing months are NOT silently imputed as zero: this groups observed cash
    events only; full FY coverage is a separate upstream obligation.
    """
    sums=defaultdict(lambda:D(0)); years_by_date=set()
    for row in records:
        if row.get('basis')!=CASH:
            raise ValueError('NOT_CASH_PROVENANCE_CANNOT_FISCALIZE')
        date_str=row.get('cash_month','')
        fy=fiscal_year(date_str)
        account=row.get('account')
        if not account or not isinstance(account,str):raise ValueError('MISSING_ACCOUNT_OWNER')
        pair=(date_str,account)
        if pair in years_by_date:raise ValueError('REPEATED_CASH_MONTH_ACCOUNT_ROW')
        years_by_date.add(pair)
        sums[(fy,account)]+=_amount(row['amount_bn'])
    if not sums:raise ValueError('NO_CASH_EVENTS')
    return dict(sorted(sums.items()))

def hypothetical_monthly_liability_allocation(cy_amounts, monthly_shares):
    """A sensitivity-only tax LIABILITY allocation, NEVER FY revenue.

    Shares by CY must be explicitly supplied for all 12 months and add to 1;
    this routine cannot emit fiscalized cash scores.
    """
    out=[]
    for cy,value in sorted(cy_amounts.items()):
        if not 1900<=int(cy)<=2200:raise ValueError('INVALID_CY')
        shares=monthly_shares.get(int(cy))
        if shares is None or set(shares)!=set(range(1,13)):
            raise ValueError('EXPLICIT_12_MONTH_ALLOCATION_REQUIRED')
        weights={m:_amount(v) for m,v in shares.items()}
        if any(v<0 for v in weights.values()) or sum(weights.values(),D(0))!=D(1):
            raise ValueError('MONTHLY_SHARES_MUST_SUM_TO_ONE')
        for month in range(1,13):
            out.append({'calendar_month':f'{int(cy):04d}-{month:02d}',
                        'allocated_liability_bn':_amount(value)*weights[month],
                        'basis':LIABILITY,
                        'note':'illustrative_liability_allocation_NOT_FY_RECEIPTS'})
    return out

def verify_budget_change_row(row):
    """A score bridge must reconcile direct cash, interest and financing.

    This checks supplied independently modeled delta components; does not
    generate economic effects, debt feedback, or a joint score itself.
    """
    needed={'fy','delta_receipts_bn','delta_noninterest_outlays_bn','delta_net_interest_bn',
            'delta_debt_other_financing_bn','source_kind'}
    if not needed.issubset(row):raise ValueError('MISSING_BUDGET_BRIDGE_FIELDS')
    if row['source_kind'] not in ('independently_modeled_hypothesis','official_joint_score'):
        raise ValueError('UNSUPPORTED_PROVENANCE_KIND')
    if row['source_kind']=='official_joint_score':
        if not row.get('official_document_url') or not row.get('publication_date'):
            raise ValueError('OFFICIAL_SCORE_CITATION_REQUIRED')
    receipts=_amount(row['delta_receipts_bn']);outlay=_amount(row['delta_noninterest_outlays_bn'])
    interest=_amount(row['delta_net_interest_bn']);other=_amount(row['delta_debt_other_financing_bn'])
    balance=receipts-outlay-interest
    debt_change=-balance+other
    return {'fy':int(row['fy']),'delta_primary_balance_bn':receipts-outlay,
            'delta_total_balance_bn':balance,'delta_debt_financing_bn':debt_change,
            'source_kind':row['source_kind']}
