"""Household incidence analyzer: require *real mapped record-level* policy outputs.
No inferred tax effect from Census income alone. Input records are policy simulation output,
not raw CPS, which does not contain reform tax liabilities.
"""
from __future__ import annotations
import csv
from decimal import Decimal
from pathlib import Path
D=Decimal
REQUIRED=('household_id','weight','market_income','base_federal_tax','reform_federal_tax','base_transfers','reform_transfers','people','children','seniors','disabled')

def load_records(filepath):
    with open(filepath,newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not all(k in reader.fieldnames for k in REQUIRED):
            raise ValueError('Missing required modeled household incidence fields: '+', '.join(x for x in REQUIRED if x not in (reader.fieldnames or [])))
        rows=list(reader)
    if not rows: raise ValueError('No records')
    ids=set()
    for row in rows:
        if not row['household_id'] or row['household_id'] in ids: raise ValueError('Missing or duplicate household key')
        ids.add(row['household_id'])
        for k in REQUIRED[1:]:
            try: row[k]=D(row[k])
            except Exception as e: raise ValueError('Invalid numeric field '+k) from e
        if row['weight']<=0 or row['people']<=0: raise ValueError('Non-positive sampling weight or people')
        for flag in ('children','seniors','disabled'):
            if row[flag] not in (D(0),D(1)): raise ValueError(flag+' is expected boolean 0/1')
        # Tax amounts can be negative for refundable credits; transfers are nonnegative by schema.
        if row['base_transfers']<0 or row['reform_transfers']<0: raise ValueError('Negative transfers unsupported')
    return rows

def weighted_decile_fragments(records):
    """Exact equal-weight bins sorted by BASE market income, fractional splits at boundaries."""
    ordered=sorted(records,key=lambda r:(r['market_income'],r['household_id']))
    total=sum((r['weight'] for r in ordered),D(0))
    step=total/D(10)
    result=[[] for _ in range(10)]
    pos=D(0)
    for r in ordered:
        remaining=r['weight']
        while remaining>0:
            bin_idx=min(9,int(pos/step))
            boundary=total if bin_idx==9 else step*(bin_idx+1)
            take=min(remaining,boundary-pos)
            if take<=0: raise ArithmeticError('Decile interval failed to progress')
            result[bin_idx].append((r,take))
            pos+=take; remaining-=take
    if abs(pos-total)>D('0.000001'): raise ArithmeticError('Weighted mass not conserved')
    return result

def analyze(records):
    weighted=weighted_decile_fragments(records)
    report=[]
    for i,parts in enumerate(weighted,1):
        mass=sum((w for _,w in parts),D(0))
        def mean(fn): return sum((fn(r)*w for r,w in parts),D(0))/mass
        changes=lambda r: (r['base_federal_tax']-r['reform_federal_tax'])+(r['reform_transfers']-r['base_transfers'])
        loss=sum((w for r,w in parts if changes(r)<0),D(0))
        report.append({'decile':i,'weight':mass,'mean_market_income':mean(lambda r:r['market_income']),
                       'average_disposable_change':mean(changes),
                       'share_losing_pct':loss/mass*D(100),
                       'average_tax_change':mean(lambda r:r['reform_federal_tax']-r['base_federal_tax']),
                       'average_transfer_change':mean(lambda r:r['reform_transfers']-r['base_transfers'])})
    return report

def summarize_subpopulations(records):
    effects=lambda r:(r['base_federal_tax']-r['reform_federal_tax'])+(r['reform_transfers']-r['base_transfers'])
    groups={'all':records,'children_households':[x for x in records if x['children']==1],
            'senior_households':[x for x in records if x['seniors']==1],
            'disabled_member_households':[x for x in records if x['disabled']==1]}
    out=[]
    for name,rs in groups.items():
        mass=sum((r['weight'] for r in rs),D(0))
        out.append({'group':name,'weighted_households':mass,'mean_change':(sum((effects(r)*r['weight'] for r in rs),D(0))/mass if mass else None)})
    return out

def export(report,path):
    if not report: raise ValueError('Nothing to export')
    with open(path,'w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report[0]));writer.writeheader()
        for r in report:writer.writerow({k:str(v) if v is not None else '' for k,v in r.items()})
