"""Run deterministic law gates, official-baseline arithmetic and synthetic fixtures."""
from __future__ import annotations
import sys,csv,json
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v06_law import validate_spec,baseline_gap,payroll_decomposition,hi_mechanical_new_tax,vat_rebate_assessment,admit_national_score,MissingEvidence,scenario,defense_caps
from fiscal_data.v06_frontier import robust_target_status, one_year_debt_ratio_stability

def run():
    validate_spec()
    dest=ROOT/'results/v06';dest.mkdir(parents=True,exist_ok=True)
    data=baseline_gap()
    with (dest/'static_fiscal_target_2027_2036.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    drows=one_year_debt_ratio_stability()
    with (dest/'one_year_debt_ratio_frozen_diagnostics_2027_2036.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(drows[0]));writer.writeheader();writer.writerows(drows)
    fx=[{'fixture_name':'ONE_EMPLOYER_ONE_WORKER_2028_350K_USD_AND_HYPOTHETICAL_192300_WAGE_BASE',
         'source':'SYNTHETIC_HAND_EXAMPLE_NOT_2028_SSA_WAGE_BASE_OR_REAL_PERSON',
         'oasdi':{k:str(v) for k,v in payroll_decomposition(350000,2028,192300).items()},
         'additional_hi_statutory_tax_dollars':str(hi_mechanical_new_tax(350000,2028))},
        {'fixture_name':'SYNTHETIC_HOUSEHOLD_NOT_NATIONAL_INCIDENCE','source':'SYNTHETIC_POVERTY_GUIDELINE_AND_CONSUMPTION',
         'vat':{k:str(v) for k,v in vat_rebate_assessment(20000,20000,20000).items()}}]
    (dest/'synthetic_fixtures_NOT_NATIONAL_ESTIMATES.json').write_text(json.dumps(fx,indent=2)+'\n')
    try:
        admit_national_score([],[])
        score='ERROR_SHOULD_HAVE_FAILED'
    except MissingEvidence:score='UNSCORED_FAIL_CLOSED'
    frontier=robust_target_status(2036,{}, {})
    status={'project':'FiscalRazor v0.6.0','legal_specification':'12 fully parameterized research provisions; not enactable legal bill without counsel review',
       'baseline_source':'CBO February 2026 machine-readable excerpts retained from v0.5; no original complete CBO file locally',
       'legislative_policy_current_law_score':score,'official_government_scoring_status':'NOT_OBTAINED',
       'real_national_household_incidence':'NOT_COMPUTED_NO_MICRODATA',
       'real_medicare_reform_outlay_effect':'NOT_COMPUTED_NO_CLAIMS_AND_REBASING',
       'real_SSA_75_year_joint_solvency':'NOT_COMPUTED_NO_JOINT_COHORT_MODEL',
       'fiscal_target_FY2036_bn':data[-1]['static_improvement_required_bn'],
       'frozen_one_year_flat_debt_GDP_FY2036_required_bn':drows[-1]['frozen_one_year_debt_ratio_improvement_required_bn'],
       'independent_frontier':frontier,'test_fixtures':'SYNTHETIC_ONLY','policy_status':'UNSCORED'}
    (dest/'research_status.json').write_text(json.dumps(status,indent=2)+'\n')
    return status
if __name__=='__main__':print(json.dumps(run(),indent=2))
