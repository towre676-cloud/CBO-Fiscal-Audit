"""Export deterministically derived SSA/CMS public-table RESEARCH benchmarks.

No fiscal-year impact, reform savings, agency source-file integrity, or
Congressional score is implied. Original primary-table excerpts remain in data/.
"""
from __future__ import annotations
import sys,csv,json
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.primary_bridges import rows,series,ssa_dollar_equivalents,evidence_audit,pce_mechanical_reference
from src.fiscalrazor import fiscal_year_gap_path


def to_csv(path,items):
    if not items:raise ValueError(f'Empty output {path}')
    fields=list(items[0])
    if any(set(r)!=set(fields) for r in items):raise ValueError('Inconsistent report fields')
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(items)
    return len(items)


def export():
    e=evidence_audit()
    if not e['verified_internal_arithmetic']:raise RuntimeError('Primary-table excerpts failed accounting audit: '+str(e['issues']))
    opts=sorted(set(r['option_id'] for r in rows('ssa_2026_option_benchmarks.csv')))
    data=[]
    for option_id in opts:
        for r in ssa_dollar_equivalents(option_id):data.append({'option_id':option_id,**r})
    ssa_count=to_csv(ROOT/'data/derived_ssa_2026_actuarial_annual_balance_dollar_equivalents.csv',data)
    cms=series('cms_trustees_2026_hi_operations_cy.csv')
    hi=[]
    for y,r in sorted(cms.items()):
        hi.append({'calendar_year':y,'total_income_billion':r['total_income_including_interest_billion'],
            'total_expenses_billion':r['total_expenditures_billion'],
            'hi_fund_income_minus_expense_billion':r['change_in_fund_billion'],
            'hi_projected_end_reserve_billion':r['end_reserves_billion'],
            'source_provenance':r['source_url'], 'depletion_year':'2033 Q2 as reported by CMS Trustees',
            'projection_basis':r['projection_status'],
            'status':'TRUST_FUND_ANNUAL_OPERATIONS_NOT_FEDERAL_FY_DEFICIT_SCORE'})
    cms_count=to_csv(ROOT/'data/derived_cms_2026_hi_annual_operations.csv',hi)
    out={'expanded_source_records':len(json.loads((ROOT/'data/public_source_registry.json').read_text())),
         'ssa_provision_year_derived':ssa_count,'cms_hi_year_rows':cms_count,
         'internal_math_validation':e,'pce_baseline_reference':pce_mechanical_reference(),
         'combined_package_score':'NOT_ESTABLISHED',
         'external_agency_raw_files_locally_revalidated':False}
    (ROOT/'receipts/EXPANSION_DATA_EXPORT.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__':print(json.dumps(export(),indent=2))
