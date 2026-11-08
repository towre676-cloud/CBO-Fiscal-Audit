"""Run source-grounded published-aggregate diagnostics and synthetic joint tests.

Never consumes unverified tax microdata or labels synthetic records national.
"""
from pathlib import Path
from decimal import Decimal
import csv,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v11_joint import joint_wage_vat
from fiscal_data.v11_published import ce_quintile_exposure,ce_vs_bea_2025_coverage_diagnostic, ssa_mechanical_rate_phaseup,vat_pce_fiscal_gap,hi_rounding_sensitivity,high_cost_min_scale_rounding

def export_rows(path,rows):
    if not rows:raise ValueError('empty result')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def jdump(path,v):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(v,indent=2,default=str,ensure_ascii=False)+'\n',encoding='utf-8')

# Deliberately synthetic full-field illustrative cases, NEVER survey/microdata.
TOY_CASES=[
 {'calendar_year':2028,'filing_status':'single','household_is_one_tax_unit':True,
  'baseline_tax_unit_magi_usd':'498000','official_oasdi_wage_base_usd':'190000',
  'persons':[{'id':'toy_P1','employers':[{'id':'employer_1','cash_wages_usd':'498000','covered_under_OASDI_and_HI':True,
      'employer_health_cost_usd':'17000','coverage_tier':'self_only','health_cost_includes_section125_pretax':True}]}],
  'baseline_income_tax_before_reform_usd':'105000',
  'income_tax_after_health_inclusion_before_other_sections_usd':'106300',
  'post_health_income_tax_without_itemized_usd':'118000',
  'post_health_income_tax_with_itemized_usd':'106300',
  'post_health_allowed_itemized_usd':'35000',
  'source_record_provenance':'SYNTHETIC_FIXTURE_NOT_US_POPULATION'},
 {'calendar_year':2029,'filing_status':'mfj','household_is_one_tax_unit':True,
  'baseline_tax_unit_magi_usd':'52000','official_oasdi_wage_base_usd':'200000',
  'indexed_high_band_threshold_usd':'255000','indexed_surtax_threshold_usd':'1030000',
  'indexed_itemized_magi_threshold_usd':'618000',
  'indexed_health_caps_usd':{'family':'32000','self_only':'13400'},
  'persons':[{'id':'toy_P1','employers':[{'id':'employer_1','cash_wages_usd':'50000','covered_under_OASDI_and_HI':True,
      'employer_health_cost_usd':'0'}]}, {'id':'toy_P2','employers':[{'id':'employer_2','cash_wages_usd':'0','covered_under_OASDI_and_HI':True,
      'employer_health_cost_usd':'0'}]}],
  'classified_final_taxable_consumption_usd':'30000',
  'documented_hhs_poverty_guideline_usd':'20000',
  'source_record_provenance':'SYNTHETIC_FIXTURE_ALL_THRESHOLDS_HYPOTHETICAL_NOT_2029_LAW'}]

def main():
    dest=ROOT/'results/v11'
    export_rows(dest/'bls_2025_quintile_hypothetical_50pct_taxable_NOT_INCIDENCE.csv',ce_quintile_exposure())
    r=[]
    for f in ('0','0.25','0.50','0.75','1'):
        r.extend(ce_quintile_exposure(Decimal(f)))
    export_rows(dest/'bls_2025_exposure_sensitivity_NOT_VAT_SCORE.csv',r)
    export_rows(dest/'ssa_2026_source_phaseup_base_only_CY_NOT_FY.csv',ssa_mechanical_rate_phaseup())
    export_rows(dest/'cbo_fy_pce_and_static_target_NO_POLICY_SCORE.csv',vat_pce_fiscal_gap())
    export_rows(dest/'cms_hi_rounding_sensitivity_CY_NOT_RESCORING.csv',hi_rounding_sensitivity())
    jdump(dest/'hi_high_cost_rounding_reserve_threshold_NOT_OACT.json',high_cost_min_scale_rounding())
    jdump(dest/'bls_bea_2025_noncomparable_totals_bridge.json',ce_vs_bea_2025_coverage_diagnostic())
    jdump(dest/'joint_statutory_toy_cases_NOT_MICRODATA.json',[joint_wage_vat(c) for c in TOY_CASES])
    # Copy policy-readiness matrix into result dashboard folder for review.
    from shutil import copyfile
    copyfile(ROOT/'data/v11/joint_policy_readiness.csv',dest/'joint_policy_readiness_NOT_SCORED.csv')
    jdump(dest/'v11_evidence_status.json',{'status':'INDEPENDENT_RESEARCH_NO_NATIONAL_COMBINED_SCORE',
       'full_CBO_original_files_physically_admitted_in_this_archive':0,
       'real_CPS_2026_ASEC_person_household_microdata_analysed':False,
       'real_BLS_2025_CE_PUMD_analysed':False,
       'real_IRS_individual_return_microdata_analysed':False,
       'real_CMS_claims_beneficiary_microdata_analysed':False,
       'published_aggregate_inputs':'CBO 2026-02, SSA 2026, CMS 2026, BLS CE 2025, BEA PCE 2025',
       'record_level_model':'mechanical employee/employer wage/VAT/income surtax with strict inputs',
       'unpriced':'full individual income-tax response without taxcalc, corporate shifts, OASI+DI cohort benefits, MA, site-neutral, defense cash, macro, interactions, FY cash timing',
       'no_original_data_fabricated':True})
    print('v1.1 outputs:',len(list(dest.iterdir())))
    print('CE vs BEA:',ce_vs_bea_2025_coverage_diagnostic())
    print('HI high-cost threshold:',high_cost_min_scale_rounding())
    print('SSA 2036 base-rate increment:',ssa_mechanical_rate_phaseup()[-1]['constant_base_additional_OASDI_tax_liability_bn'])

if __name__=='__main__':main()
