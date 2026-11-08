"""Build source-distinguished v1.0 policy-potential results; never a full joint score."""
from __future__ import annotations
from pathlib import Path
import csv,sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v10_potential import *
OUT=ROOT/'results/v10';OUT.mkdir(parents=True,exist_ok=True)
def v(x):return '' if x is None else str(x)
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows([{k:v(val) for k,val in x.items()} for x in rows])
    print(f'{path.relative_to(ROOT)} {len(rows)} rows')

def main():
    targets=[target_gap(y) for y in range(2027,2037)]
    options=analogue_comparison()
    ssa=ssa_annual_balance_equivalents()
    hi=hi_scenarios()
    thresholds=hi_thresholds()
    vat=[mechanical_consumption_benchmark(y) for y in range(2027,2037)]
    household=vat_household_thresholds_by_poverty_multiple()
    vat_bounds=[vat_fixed_base_capacity(y) for y in range(2027,2037)]
    top1=[drafted_surtax_cy2028_top1_mechanical_lower_bound()]
    defense=defense_budget_authority_reduction_path()
    for p,r in [('cbo_fy_target_gaps.csv',targets),('2024_cbo_option_analogues_FY2034_NOT_ADDITIVE.csv',options),
                ('ssa_2026_annual_balance_equivalents_NOT_FY.csv',ssa),('cms_2026_hi_frozen_three_scenarios_NOT_OACT_SCORE.csv',hi),
                ('cms_hi_reserve_thresholds_NOT_SCORE.csv',thresholds),('pce_total_gross_vat_benchmark_NOT_TAX_BASE.csv',vat),
                ('vat_household_break_even_SYMBOLIC_NOT_NATIONAL.csv',household),
                ('vat_fixed_all_pce_capacity_bound_NOT_LEGAL_TAX_BASE.csv',vat_bounds),
                ('cbo2028_top1_drafted_Magi_surtax_liability_lower_bound_NOT_SCORE.csv',top1),
                ('defense_budget_authority_deltas_NOT_FY_OUTLAYS.csv',defense)]:
        write_csv(OUT/p,r)
    core={
        'baseline_gap_2034_bn':str(target_gap(2034)['static_gap_to_3pct_bn']),
        'baseline_gap_2036_bn':str(target_gap(2036)['static_gap_to_3pct_bn']),
        'analogue_count':len(options),'analogue_nonnull_count':sum(x['official_analogue_bn'] is not None for x in options),
        'hi_rows':len(hi),'ssa_years':len(ssa),
        'options_are_not_additive':True,'policy_score_status':'NONE_ESTABLISHED',
        'household_incidence_status':'NONE_ESTABLISHED_ORIGINAL_CPS_MICRODATA_NOT_INGESTED',
        'original_data_status':'NO_BYTE_COMPLETE_NEW_ORIGINALS_PRODUCED_BY_THIS_MODULE',
        'HI_thresholds':[{k:v(val) for k,val in x.items()} for x in thresholds],
        'first_year_2028_surtax_mechanical_lower_bound_top1_bn':str(top1[0]['nonbehavioral_top1_MAGI_surtax_liability_lower_bound_bn']),
        '2034_defense_mechanical_BA_delta_bn':str(next(x['mechanical_base_BA_delta_bn'] for x in defense if x['fy']==2034)),
        'vat_fixed_base_upper_2034_bn':str(vat_fixed_base_capacity(2034)['fixed_all_pce_gross_bn']),
        'vat_fixed_base_uncovered_gap_2036_bn':str(vat_fixed_base_capacity(2036)['uncovered_gap_even_with_all_pce_taxed_and_no_rebates_bn']),
        'CMS_frozen_model_notice':'Models payroll proceeds against Trustees baseline; not official OACT rescore. Annual cost rate rounded to 2 decimal percentage points.'}
    (OUT/'potential_research_receipt.json').write_text(json.dumps(core,indent=2)+'\n',encoding='utf-8')
    print('RECEIPT: '+json.dumps(core)[:2200]);return core
if __name__=='__main__':main()
