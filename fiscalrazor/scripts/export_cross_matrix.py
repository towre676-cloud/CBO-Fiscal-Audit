"""Generate per-field independently packaged source transcription comparison receipt.

Does not authenticate original government source bytes.
"""
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.reconcile_public import A,B,rows,reconcile_cbo,reconcile_gdp,reconcile_ssa,reconcile_cms_hi
receipt=[]
def add(subject,year,key,val1,val2):
    from decimal import Decimal
    status='MATCH' if Decimal(str(val1))==Decimal(str(val2)) else 'CONFLICT'
    receipt.append(dict(subject=subject,year=year,field=key,session_A_value=val1,session_B_value=val2,status=status,
        source_quality='TWO_AGREEING_SECONDARY_EXCERPTS_ORIGINAL_BYTES_UNVERIFIED'))

A_c={r['fy']:r for r in rows(A/'cbo_budget_fy2026_2036_21_series.csv')}
B_c={r['year']:r for r in rows(B/'cbo_2026_02_baseline_excerpt.csv')}
map_c={'proj_rev_total':'revenue_billion','proj_outlays_total':'outlays_billion',
 'proj_deficit_total':'deficit_billion','proj_outlays_net_interest':'net_interest_billion',
 'proj_primary_deficit':'primary_deficit_billion','proj_debt_held_by_public':'debt_public_billion',
 'proj_debt_held_by_public_gdp_share':'debt_public_gdp_pct'}
for year,a in sorted(A_c.items()):
 b=B_c[year]
 for k,kb in map_c.items(): add('CBO_budget',year,k,a[k],b[kb])
A_g={r['fiscal_year']:r for r in rows(A/'cbo_gdp_fy2026_2036_official.csv')}
B_g={r['year']:r for r in rows(B/'cbo_2026_02_fy_nominal_gdp_excerpt.csv')}
for year,a in sorted(A_g.items()): add('CBO_gdp',year,'nominal_gdp_bn',a['nominal_gdp_bn'],B_g[year]['nominal_gdp_billion'])
A_s={r['calendar_year']:r for r in rows(A/'ssa_individual_provision_annual_balance_2026_2036.csv')}
field_s={'E2.5':'E2_5_delta_annual_balance_pct_payroll','E1.10':'E1_10_delta_annual_balance_pct_payroll','B1.2':'B1_2_delta_annual_balance_pct_payroll'}
for b in rows(B/'ssa_2026_option_benchmarks.csv'):
 k=next(k for k in field_s if b['option_id'].startswith(k));year=b['calendar_year']
 add('SSA_single_option',year,k,A_s[year][field_s[k]],b['change_annual_balance_pct_of_current_law_taxable_payroll'])
A_h={r['calendar_year']:r for r in rows(A/'cms_2026_hi_operations_cy2025_2035.csv')}
B_h={r['calendar_year']:r for r in rows(B/'cms_trustees_2026_hi_operations_cy.csv')}
map_h={'income_bn':'total_income_including_interest_billion','expenditures_bn':'total_expenditures_billion',
 'change_in_fund_bn':'change_in_fund_billion','assets_year_end_bn':'end_reserves_billion',
 'assets_to_expenditures_pct':'beginning_assets_to_expenditures_pct'}
for year,a in sorted(A_h.items()):
 b=B_h[year]
 for k,kb in map_h.items():
  if a[k]==''==b[kb]:
   receipt.append(dict(subject='CMS_HI',year=year,field=k,session_A_value='',session_B_value='',status='MATCH_MISSING_BOTH',source_quality='TWO_AGREEING_SECONDARY_EXCERPTS_ORIGINAL_BYTES_UNVERIFIED'))
  else:add('CMS_HI',year,k,a[k],b[kb])
assert len(receipt)==176,(len(receipt),'expected 176 fields')
assert not any(r['status']=='CONFLICT' for r in receipt)
p=ROOT/'results'/'cross_source_alignment_176.csv';p.parent.mkdir(exist_ok=True)
with p.open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=list(receipt[0]));w.writeheader();w.writerows(receipt)
print(p,'matched 176 fields')
