"""SSA/CMS source table validators and hard legal-account barriers."""
from __future__ import annotations
import csv
from decimal import Decimal
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
D=Decimal

def ssa_rows(path=BASE/'data'/'verified_tables'/'ssa_ivb1_rates_2026_2036.csv'):
    with open(path,encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    if [int(x['year']) for x in rows]!=list(range(2026,2037)): raise ValueError('Incorrect year coverage')
    for r in rows:
        for k in ('oasi','di','combined_oasdi'):
            income=D(r[k+'_income_pct']);cost=D(r[k+'_cost_pct']);balance=D(r[k+'_balance_pct'])
            if abs((income-cost)-balance)>D('0.02'):
                raise ValueError(f"year {r['year']} {k} balance incompatible with income-cost")
        for suffix in ('income_pct','cost_pct','balance_pct'):
            combined=D(r['combined_oasdi_'+suffix]);summed=D(r['oasi_'+suffix])+D(r['di_'+suffix])
            if abs(combined-summed)>D('0.03'):
                raise ValueError(f"year {r['year']} combined OASDI vs OASI+DI mismatch")
    return rows

def trustee_key(path=BASE/'data'/'verified_tables'/'2026_trustee_report_key_results.csv'):
    with open(path,encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    if {x['trust_fund'] for x in rows}!={'OASI','DI','OASDI_illustrative_combined','HI','SMI'}:
        raise ValueError('Trust fund components missing')
    return {x['trust_fund']:x for x in rows}

def validate_solvent(claim, official_combined_actuary_report=None):
    if official_combined_actuary_report is None:
        raise ValueError('UNSCORED: Separate published Trustees tables do not score a joint reform proposal')
    if not official_combined_actuary_report.get('official_source_url') or not official_combined_actuary_report.get('complete_projection'):
        raise ValueError('INCOMPLETE official actuarial source')
    raise ValueError('UNVERIFIED: Manual actuarial audit required; no automated certification by link alone')
