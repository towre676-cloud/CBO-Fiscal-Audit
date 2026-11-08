"""Run local cross-agency public evidence benchmarks; no policy package scored."""
import sys,json
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.primary_bridges import ssa_dollar_equivalents, series, evidence_audit, pce_mechanical_reference
from src.fiscalrazor import target_2036
from src.payroll_interactions import worker_oasdi_overlap
from src.score_gate import audit_candidate

p='E2.5_high_earner_tax_250k_no_benefit_credit'
ssa=ssa_dollar_equivalents(p)
status=audit_candidate(ROOT/'data/policy_effects_TEMPLATE.csv',ROOT/'data/joint_interactions_TEMPLATE.csv')
example=worker_oasdi_overlap(300000,192300,250000,combined_rate_increase='.01',increase_applies_high_earnings=True)
report={
  'project':'FiscalRazor / independent public-source actuarial + accounting bridges',
  'cbo_fy2036_3pct_gap_billion':target_2036(),
  'ssa_E2p5_cy2027_balance_equivalent_billion':ssa[1]['derived_nominal_annual_balance_change_billion'],
  'ssa_E2p5_cy2035_balance_equivalent_billion':ssa[9]['derived_nominal_annual_balance_change_billion'],
  'ssa_E2p5_cy2036_balance_equivalent_billion':ssa[10]['derived_nominal_annual_balance_change_billion'],
  'ssa_measure':'annual-balance point-in-time change as % current-law payroll (not federal FY revenue)',
  'cms_hi_CY2032_end_reserves_billion':series('cms_trustees_2026_hi_operations_cy.csv')[2032]['end_reserves_billion'],
  'cms_hi_CY2033_reserve_hypothetical_billion':series('cms_trustees_2026_hi_operations_cy.csv')[2033]['end_reserves_billion'],
  'pce_CY2025_5pct_entire_base_not_a_tax_score':pce_mechanical_reference()['all_pce_times_rate_billion_NOT_SCORE'],
  'oasdi_worker_2027_hypothetical_joint_interaction_dollars':example['mechanical_interaction'],
  'provision_year_rows_missing':next(x for x in status['problems'] if x.startswith('missing') and 'provision-year' in x),
  'interaction_year_rows_missing':next(x for x in status['problems'] if x.startswith('missing') and 'interaction-year' in x),
  'primary_tables_arithmetic':evidence_audit(),
  'official_complete_policy_score':'NOT_ESTABLISHED',
  'external_source_files_verified_original_bytes':False}
print(json.dumps(report,indent=2,default=str))
