"""Verified static budget identities, no policy forecast by default.
Money in billions nominal USD. CBO deficit source uses NEGATIVE sign.
"""
from __future__ import annotations
import csv
from decimal import Decimal
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
BUDGET_FILE=BASE/'data'/'verified_tables'/'cbo_budget_fy2026_2036_21_series.csv'
ACTUAL_FILE=BASE/'data'/'verified_tables'/'treasury_fy2026_reported_actuals.csv'
GDP_FILE=BASE/'data'/'verified_tables'/'cbo_gdp_fy2026_2036_official.csv'
D=Decimal

def read_budget(path=BUDGET_FILE):
    with open(path, newline='', encoding='utf-8') as f:
        raw=list(csv.DictReader(f))
    if not raw: raise ValueError('CBO budget source empty')
    result={}
    for row in raw:
        yr=int(row.pop('fy'))
        if yr in result: raise ValueError('Duplicate fiscal year')
        result[yr]={k:D(str(v)) for k,v in row.items() if v not in (None,'')}
    return result

def read_actual(path=ACTUAL_FILE):
    with open(path, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if len(rows)!=1 or rows[0]['fy']!='2026': raise ValueError('Actual fiscal year provenance mismatch')
    r=rows[0]
    if D(r['outlays_bn'])-D(r['receipts_bn'])!=D(r['deficit_bn']):
        raise ValueError('Treasury receipts/outlays/deficit mismatch')
    return r

def verify_budget(budget=None):
    budget=budget or read_budget()
    findings=[]
    for year,b in sorted(budget.items()):
        deficit=-b['proj_deficit_total']
        primary=-b['proj_primary_deficit']
        interest=b['proj_outlays_net_interest']
        if abs(deficit-(primary+interest))>D('0.002'):
            raise ValueError(f'FY{year}: deficit != primary deficit + net interest')
        if abs(b['proj_outlays_total']-b['proj_rev_total']-deficit)>D('0.002'):
            raise ValueError(f'FY{year}: outlays != receipts + deficit')
        if abs(b['proj_outlays_total']-(b['proj_outlays_mandatory']+b['proj_outlays_discretionary']+interest))>D('0.002'):
            raise ValueError(f'FY{year}: budget partitions differ')
        if abs(b['proj_outlays_discretionary']-b['proj_disc_defense']-b['proj_disc_nondefense'])>D('0.002'):
            raise ValueError(f'FY{year}: defense + nondefense mismatch')
        if b['proj_mand_social_security']+b['proj_mand_medicare']+b['proj_mand_medicaid']>b['proj_outlays_mandatory']:
            raise ValueError(f'FY{year}: mandatory subcomponents exceed total')
        if year>min(budget):
            prior=budget[year-1]['proj_debt_held_by_public']
            delta=b['proj_debt_held_by_public']-prior
            expected=-b['proj_deficit_total']+b['proj_debt_change_other_financing']
            if abs(delta-expected)>D('0.002'):
                raise ValueError(f'FY{year}: debt stock change != deficit + other financing')
        findings.append({'year':year,'deficit_bn':deficit,'primary_deficit_bn':primary,'net_interest_bn':interest,'debt_bn':b['proj_debt_held_by_public'],'debt_pct_gdp':b['proj_debt_held_by_public_gdp_share']})
    return findings

def read_direct_gdp(path=GDP_FILE):
    """CBO fiscal-year nominal GDP, published directly in Feb 2026 economic data.

    Rejects missing years, duplicate years, and misalignment to the budget vintage.
    """
    with open(path, newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=11: raise ValueError('Official GDP coverage incomplete')
    years=[int(x['fiscal_year']) for x in rows]
    if years!=list(range(2026,2037)): raise ValueError('GDP years must be FY2026..FY2036')
    values={int(x['fiscal_year']):D(x['nominal_gdp_bn']) for x in rows}
    if any(v<=0 for v in values.values()): raise ValueError('GDP must be positive')
    budget=read_budget()
    for yr,gdp in values.items():
        observed=budget[yr]['proj_debt_held_by_public_gdp_share']
        computed=budget[yr]['proj_debt_held_by_public']/gdp*D(100)
        # CBO publishes the debt/GDP percentage to three decimal places.
        if abs(computed-observed)>D('0.0015'):
            raise ValueError(f'FY{yr}: GDP does not reconcile to debt/GDP')
    return values

def target_gap_2036(deficit_share_pct=Decimal('3.0'), gdp_path=GDP_FILE):
    b=read_budget()[2036]
    if not D(0)<D(str(deficit_share_pct))<D(20): raise ValueError('Invalid target percentage')
    gdp=read_direct_gdp(gdp_path)[2036]
    allowable=gdp*D(str(deficit_share_pct))/D(100)
    gap=-b['proj_deficit_total']-allowable
    return {'fiscal_year':2036,'gdp_official_bn':gdp,'target_pct':D(str(deficit_share_pct)),
            'allowed_deficit_bn':allowable,'gap_bn':gap,
            'source_basis':'CBO_2026_02_DIRECT_FY_GDP_AND_BUDGET_STATIC_NOT_UPDATED_LAW'}
