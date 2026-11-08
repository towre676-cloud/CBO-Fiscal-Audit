"""Independent cross-artifact comparison for FiscalRazor v0.4 & public-scoring expansion.

This module compares separately packaged transcriptions and did NOT independently
fetch raw CBO/SSA/CMS archives. Equality is not source authenticity.
No model output here is a policy score.
"""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlsplit
import csv
import json

ROOT=Path(__file__).resolve().parents[2]
EXT=ROOT/'external'/'public_scoring'
A=ROOT/'data'/'verified_tables'
B=EXT/'data'


def rows(path):
    with path.open(newline='', encoding='utf-8-sig') as fh:return list(csv.DictReader(fh))


def index(path,key):
    data=rows(path)
    idx={}
    for r in data:
        k=r[key]
        if k in idx:raise ValueError(f'duplicate key {path.name}:{k}')
        idx[k]=r
    return idx


def _eq(a,b,name):
    if D(str(a))!=D(str(b)):
        raise AssertionError(f'{name}: {a!r} != {b!r}')


def reconcile_gdp():
    a=index(A/'cbo_gdp_fy2026_2036_official.csv','fiscal_year')
    b=index(B/'cbo_2026_02_fy_nominal_gdp_excerpt.csv','year')
    if set(a)!=set(b): raise AssertionError('GDP year coverage differs')
    for y in a:_eq(a[y]['nominal_gdp_bn'],b[y]['nominal_gdp_billion'],f'FY{y} GDP')
    return len(a)


def reconcile_cbo():
    a=index(A/'cbo_budget_fy2026_2036_21_series.csv','fy')
    b=index(B/'cbo_2026_02_baseline_excerpt.csv','year')
    mapping={'proj_rev_total':'revenue_billion','proj_outlays_total':'outlays_billion',
             'proj_deficit_total':'deficit_billion','proj_outlays_net_interest':'net_interest_billion',
             'proj_primary_deficit':'primary_deficit_billion','proj_debt_held_by_public':'debt_public_billion',
             'proj_debt_held_by_public_gdp_share':'debt_public_gdp_pct'}
    if set(a)!=set(b):raise AssertionError('CBO year coverage differs')
    for y in a:
        for k,v in mapping.items():_eq(a[y][k],b[y][v],f'FY{y} {k}')
    return len(a)*len(mapping)


def reconcile_ssa():
    a=index(A/'ssa_individual_provision_annual_balance_2026_2036.csv','calendar_year')
    b=rows(B/'ssa_2026_option_benchmarks.csv')
    m={'E2.5':'E2_5_delta_annual_balance_pct_payroll','E1.10':'E1_10_delta_annual_balance_pct_payroll',
       'B1.2':'B1_2_delta_annual_balance_pct_payroll'}
    seen=set()
    for r in b:
        k=next((x for x in m if r['option_id'].startswith(x)),None)
        if k is None:raise AssertionError('Unknown SSA option code: '+r['option_id'])
        y=r['calendar_year']; ky=(k,y)
        if ky in seen:raise AssertionError('SSA duplicate option-year')
        seen.add(ky)
        if y not in a:raise AssertionError('SSA year out of range')
        _eq(a[y][m[k]],r['change_annual_balance_pct_of_current_law_taxable_payroll'],f'SSA {k} CY{y}')
    if len(seen)!=33:raise AssertionError(f'SSA option-year coverage {len(seen)} !=33')
    return len(seen)


def reconcile_cms_hi():
    a=index(A/'cms_2026_hi_operations_cy2025_2035.csv','calendar_year')
    b=index(B/'cms_trustees_2026_hi_operations_cy.csv','calendar_year')
    mapping={'income_bn':'total_income_including_interest_billion',
      'expenditures_bn':'total_expenditures_billion',
      'change_in_fund_bn':'change_in_fund_billion',
      'assets_year_end_bn':'end_reserves_billion',
      'assets_to_expenditures_pct':'beginning_assets_to_expenditures_pct'}
    if set(a)!=set(b):raise AssertionError('CMS HI year coverage differs')
    n=0
    for y in a:
        for left,right in mapping.items():
            av=a[y][left];bv=b[y][right]
            if av==bv=='':pass
            else:_eq(av,bv,f'CMS HI CY{y} {left}')
            n+=1
        if {'projected':'intermediate','actual':'actual','hypothetical_after_depletion':'hypothetical_after_depletion'}.get(a[y]['status'])!=b[y]['projection_status']:
            raise AssertionError('CMS actuarial status mismatch')
    return n


def expanded_unique_resources():
    primary=json.loads((ROOT/'data'/'source_catalog.json').read_text())['entries']
    second=json.loads((B/'public_source_registry.json').read_text())
    def normalize(url):
        if not url: return None
        p=urlsplit(url)
        return (p.netloc.lower().removeprefix('www.'),p.path.lower().rstrip('/'))
    all_urls=[]
    for x in primary:all_urls.append(normalize(x.get('download_url') or x.get('landing_url')))
    for x in second:all_urls.append(normalize(x.get('url')))
    return {'our_entries':len(primary),'other_entries':len(second),
      'distinct_normalized_endpoint_paths':len(set(all_urls)),
      'note':'Multiple endpoints may represent one scientific source; not a count of distinct datasets or validated bytes.'}


def static_gap():
    a=index(A/'cbo_budget_fy2026_2036_21_series.csv','fy')['2036']
    gd=index(A/'cbo_gdp_fy2026_2036_official.csv','fiscal_year')['2036']
    deficit=-D(a['proj_deficit_total'])
    target=D(gd['nominal_gdp_bn'])*D('0.03')
    return {'FY2036_gap_bn':str(deficit-target),'FY2036_3pct_target_deficit_bn':str(target),
      'status':'static_baseline_target_NOT_LEGISLATIVE_SCORE'}


def run_comparison():
    comparisons={'CBO_7_indicators_X_11_fy':reconcile_cbo(),
      'CBO_direct_GDP_11_fy':reconcile_gdp(),
      'SSA_3_options_X_11_cy':reconcile_ssa(),
      'CMS_HI_5_numeric_fields_X_11_cy':reconcile_cms_hi()}
    return {'compatible_field_comparisons':comparisons,
      'total_compared':sum(comparisons.values()),
      'source_registry':expanded_unique_resources(),
      '2036_fiscal_target':static_gap(),
      'external_original_archive_bytes_acquired':False,
      'joint_fiscal_score':'UNSCORED','household_distribution':'NOT_ESTABLISHED',
      'official_CBO_JCT_SSA_CMS_combined_score':'NOT_ESTABLISHED'}

if __name__=='__main__':print(json.dumps(run_comparison(),indent=2))
