"""Explicit ownership of each unscored policy effect in federal ledger accounts."""
from pathlib import Path
import sys,csv,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v06_law import EXPECTED_IDS, policies
x=[
 ('VAT output and input credits; household refund','VAT minus refunds, filing/avoidance, product mix','General receipts and refundable tax credits','IRS taxpayers + CE/BEA consumption; HHS guidelines','JCT/CBO'),
 ('2% on MAGI above status threshold','TY liability converted through withholding/settlement','Individual income tax','IRS SOI and microsimulation tax-unit records','JCT'),
 ('Max tax benefit of itemized deductions 28%','Recompute liability under current §68/§164','Individual income tax','IRS tax returns with deduction types and current tax liabilities','JCT'),
 ('Include employer health premium exceeding tier cap','Wages + payroll/income interactions + coverage responses','Income/HI/OASDI payroll taxes, no duplicate §106','Employer premium survey and administrative wage records','JCT/CBO'),
 ('C corporation §11 rate +1pp','Corporation liability, CAMT/BEAT/international responses','Corporate income tax; cross tax','IRS corporation data and business response model','JCT'),
 ('High OASDI band >H_y; no benefits credited','Pro-rata cross-employer high band, FICA/SECA fiscalization','OASI/DI allocated contributions','SSA covered wages/AWI and IRS employer-by-employee receipts','SSA/JCT'),
 ('0.1pp each employer/employee extra per year 2028–32','Additional tax on low band + high band interaction','OASI/DI contributions','SSA payroll distribution; 106 interaction','SSA/JCT'),
 ('B1.2 progressive PIA price indexing for newly eligible 2033+','Cohort-specific cost-rate effect and reserve flow','OASI and DI benefits, survivor/disability','SSA cohort AIME, claims and indexation model','SSA/CBO'),
 ('MA coding downward adjustment >=8.5% + benchmark <=105% FFS','Payment bids, risk scores, rebates and utilization','Part A HI; Part B SMI; premium offsets','CMS plan/county/risk files and MA bids','CMS/CBO'),
 ('Site-neutral combined visit payment cap','Claims by HCPCS, site, wage locality; migration','Part B SMI and any Part A spillovers','CMS claim site/coding and provider geography','CMS/CBO'),
 ('Nominal defense discretionary BA caps FY2028–36','Convolve BA change with account-specific spendout rates','Defense outlays; other financing and macro','CBO account-level baseline/BA, OMB contract outlays','CBO'),
 ('0.25->0.75pp combined uncapped HI payroll increase','Wage and SECA basis, income tax deductions','HI-only contributions, not another general receipt','CMS HI uncapped taxable payroll / SSA wages / IRS','CMS/JCT/CBO')]
assert len(x)==12
fields=['provision_id','section','effective_date','mechanism','cash_translation_rule','budget_ownership','unavailable_primary_data','score_lead','national_effect_status']
with (ROOT/'data/v06/provision_cash_and_fund_ownership.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fields);w.writeheader()
 for id,(m,fiscal,owner,input,lead) in zip(EXPECTED_IDS,x):
  a=policies()[id];w.writerow(dict(provision_id=id,section=a['section'],effective_date=a['effective_date'],mechanism=m,cash_translation_rule=fiscal,budget_ownership=owner,unavailable_primary_data=input,score_lead=lead,national_effect_status='UNSCORED_MISSING_JOINT_SOURCE_DATA'))
