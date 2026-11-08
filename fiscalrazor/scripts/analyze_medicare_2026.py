#!/usr/bin/env python3
"""Reproduce official Medicare Trustees II.E1 / II.F1 and exact funding floors.

No data are inferred from unavailable CMS full ZIP; source rows in this
repository are transcriptions of the two clearly cited public PDF tables.
"""
from __future__ import annotations
import csv,sys,json
from decimal import Decimal
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.medicare_cash import validate_hi,validate_smi,uniform_incremental_hi_inflow_floor,end_of_2034_balance_needed_for_2035_full_reserve
from fiscal_data.accounting import read_budget
D=Decimal

def cast(x):
 if isinstance(x,Decimal):return str(x)
 if isinstance(x,dict):return {str(k):cast(v) for k,v in x.items()}
 if isinstance(x,list):return [cast(v) for v in x]
 return x

def main():
 hi=validate_hi();smi=validate_smi();cbo=read_budget();out=BASE/'results';out.mkdir(exist_ok=True)
 rows=[]
 for i,h in enumerate(hi):
  y=h['calendar_year'];b=smi['B'][i];d=smi['D'][i];s=smi['SMI'][i]
  rows.append({'cy':y,'hi_gross_expenditure_bn':h['expenditures_bn'],
               'smi_part_b_gross_expenditure_bn':b['expenditures_bn'],
               'smi_part_d_gross_expenditure_bn':d['expenditures_bn'],
               'smi_gross_expenditure_bn':s['expenditures_bn'],
               'total_medicare_trust_fund_expenditure_bn':h['expenditures_bn']+s['expenditures_bn'],
               'hi_reported_year_end_assets_bn':h['assets_year_end_bn'],
               'hi_post_depletion_hypothetical':h['status']=='hypothetical_after_depletion'})
 with (out/'cms_medicare_2026_annual_operations_verified.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 flo=uniform_incremental_hi_inflow_floor()
 results={
  'metadata':{'as_of':'2026-11-06','source':'https://www.cms.gov/oact/tr/2026',
              'tables':['II.E1','II.F1'],'time_basis':'CALENDAR_YEAR',
              'fiscal_effect_status':'NONE_POLICY_NOT_SCORED','cms_full_zip_materialized':False},
  '2025_medicare_gross_trustfund_expenditure_bn':rows[0]['total_medicare_trust_fund_expenditure_bn'],
  '2035_medicare_gross_trustfund_expenditure_bn':rows[-1]['total_medicare_trust_fund_expenditure_bn'],
  '2025_2035_expenditure_growth_factor':rows[-1]['total_medicare_trust_fund_expenditure_bn']/rows[0]['total_medicare_trust_fund_expenditure_bn'],
  'hi_2033_quarter_of_depletion':'Q2 per CMS text; not inferred from annual rows',
  'hi_uniform_income_floor_2027_2035':flo,
  'uniform_2027_2034_income_for_100percent_beginning_2035_target_bn_per_year':end_of_2034_balance_needed_for_2035_full_reserve(),
  'cbo_medicare_comparison_caution':{
       'cms_cy2035_hi_plus_smi_gross_expenditure_bn':rows[-1]['total_medicare_trust_fund_expenditure_bn'],
       'cbo_fy2035_net_medicare_budget_outlay_bn':cbo[2035]['proj_mand_medicare'],
       'numeric_gap_bn':rows[-1]['total_medicare_trust_fund_expenditure_bn']-cbo[2035]['proj_mand_medicare'],
       'accounting_status':'NONCOMPARABLE_UNRECONCILED_CY_GROSS_VS_FY_NET; DO_NOT_SUBTRACT_AS_SAVINGS'
   },
  'actuarial_75_year_cms':{'immediate_income_increase_pct_of_uncapped_HI_taxable_payroll':D('.56'),
                          'if_delayed_to_2033_pct_of_uncapped_HI_taxable_payroll':D('.65'),
                          'period':'CY2026_2100','source':'CMS_2026_TR_III_B_printed_page_69',
                          'status':'PUBLISHED_ACTUARIAL_EQUIVALENCE_NOT_A_LEGISLATIVE_SCORE'}
 }
 (out/'medicare_2026_funding_analysis.json').write_text(json.dumps(cast(results),indent=2,sort_keys=True)+'\n')
 print('HI/SMI rows',len(hi),sum(len(z) for z in smi.values()))
 print('Gross 2025/2035',results['2025_medicare_gross_trustfund_expenditure_bn'],results['2035_medicare_gross_trustfund_expenditure_bn'])
 print('2035 zero end-year HI floor',flo['annual_increment_bn'])
 print('HI 2035 beginning 100% target floor',results['uniform_2027_2034_income_for_100percent_beginning_2035_target_bn_per_year'])
 print('CBO-CMS bridge gap NOT SAVINGS',results['cbo_medicare_comparison_caution']['numeric_gap_bn'])
if __name__=='__main__':main()
