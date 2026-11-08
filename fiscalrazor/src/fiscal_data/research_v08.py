"""Exact fiscal-baseline arithmetic and evidence feasibility, not official policy scoring."""
from __future__ import annotations
from decimal import Decimal
from pathlib import Path
from collections import defaultdict
import csv,json,itertools
from fiscal_data.v06_law import EXPECTED_IDS
from fiscal_data.primary_ingest_v08 import OriginalSourceError,source_specs,status
ROOT=Path(__file__).resolve().parents[2]
D=Decimal

NEEDS={
 'vat_5_percent_with_rebates':('cbo_11','cps_asec_2026_csv','bls_ce_2025_interview_csv'),
 'high_income_surtax':('cbo_11','cbo_15','irs_soi_2023_zip_agi'),
 'itemized_deduction_limits':('cbo_11','cbo_15','irs_soi_2023_zip_agi'),
 'employer_health_exclusion_cap':('cbo_11','irs_soi_2023_zip_agi','cps_asec_2026_csv'),
 'corporate_tax_rate':('cbo_11','cbo_16'),
 'oasdi_high_earnings_250k':('cbo_11','cps_asec_2026_csv'),
 'oasdi_base_rate_phaseup':('cbo_11','cps_asec_2026_csv'),
 'oasdi_progressive_price_index':('cbo_13','cps_asec_2026_csv'),
 'medicare_advantage':('cbo_13','cms_medicare_2026_expanded'),
 'medicare_site_neutral':('cbo_13','cms_medicare_2026_expanded'),
 'defense_budget':('cbo_17','cbo_11'),
 'medicare_hi_financing':('cbo_13','cms_medicare_2026_expanded'),
}

ALL_PAIR_INTERACTIONS=tuple(itertools.combinations(EXPECTED_IDS,2))

def read_baseline():
 with (ROOT/'data/verified_tables/cbo_budget_fy2026_2036_21_series.csv').open(newline='') as f:
  budget={int(r['fy']):r for r in csv.DictReader(f)}
 with (ROOT/'data/verified_tables/cbo_gdp_fy2026_2036_official.csv').open(newline='') as f:
  gdp={int(r['fiscal_year']):D(r['nominal_gdp_bn']) for r in csv.DictReader(f)}
 if set(range(2026,2037))!=set(budget) or set(range(2026,2037))!=set(gdp):
  raise OriginalSourceError('INCOMPLETE_FROZEN_BASELINE')
 return budget,gdp


def annual_objectives():
 budget,gdp=read_baseline();rows=[]
 for yr in range(2027,2037):
  b=budget[yr];debt=D(b['proj_debt_held_by_public']);prev=D(budget[yr-1]['proj_debt_held_by_public']);
  deficit=-D(b['proj_deficit_total']);interest=D(b['proj_outlays_net_interest']);
  primary=-D(b['proj_primary_deficit']);rev=D(b['proj_rev_total']);out=D(b['proj_outlays_total'])
  if abs(deficit-(out-rev))>D('.000001') or abs(deficit-primary-interest)>D('.000001'):
   raise OriginalSourceError('FISCAL_IDENTITY_BROKEN')
  target_deficit=D('.03')*gdp[yr]
  extra_funding_to_freeze=max(D(0),debt-prev*gdp[yr]/gdp[yr-1]);
  rows.append({'fy':yr,'baseline_deficit_bn':str(deficit),'baseline_interest_bn':str(interest),
   'baseline_primary_deficit_bn':str(primary),'baseline_public_debt_bn':str(debt),
   'nominal_gdp_bn':str(gdp[yr]),'three_percent_deficit_limit_bn':str(target_deficit),
   'three_percent_gap_bn':str(max(D(0),deficit-target_deficit)),
   'one_year_debt_ratio_improvement_bn':str(extra_funding_to_freeze),
   'classification':'STATIC_ACCOUNTING_REQUIREMENT_FIXED_OTHER_FINANCING_AND_GDP_NOT_PACKAGE_SCORE'})
 return rows


def evidence_completion(raw_root):
 entries={r['id']:r for r in status(raw_root)}
 result=[]
 for law in EXPECTED_IDS:
  require=NEEDS[law]
  missing=[x for x in require if entries[x]['state']!='VERIFIED_ORIGINAL_LOCAL']
  result.append({'policy_id':law,'primary_required_sources':list(require),
                 'missing_required_sources':missing,
                 'raw_input_gate':'READY_FOR_DATA_MODELING' if not missing else 'BLOCKED_ORIGINAL_DATA',
                 'national_policy_score':'NOT_ESTABLISHED',
                 'notes':'Raw inputs alone do not establish model calibration, interactions, or official scoring.'})
 return result


def interval_target(provision_bounds,interaction_bounds,year,interest_bounds=None,higher_order_residual_bounds=None):
 """Bound total improvement from independent interval estimates.
 Requires 12 provision-year, all 66 two-way interactions, explicit higher-order remainder
 and separately documented interest bounds. No default-zero for unknown effects.
 """
 if not 2027<=year<=2036:raise OriginalSourceError('BAD_FISCAL_YEAR')
 from fiscal_data.v06_law import baseline_gap
 required=set(EXPECTED_IDS)
 if set(provision_bounds)!=required:raise OriginalSourceError('ALL_TWELVE_PROVISION_BOUNDS_REQUIRED')
 if not isinstance(interaction_bounds,dict) or set(interaction_bounds)!=set(ALL_PAIR_INTERACTIONS):
  raise OriginalSourceError('ALL_SIXTY_SIX_INTERACTION_BOUNDS_REQUIRED')
 if interest_bounds is None:raise OriginalSourceError('DEBT_INTEREST_FEEDBACK_BOUNDS_MISSING')
 if higher_order_residual_bounds is None:raise OriginalSourceError('HIGHER_ORDER_INTERACTION_REMAINDER_BOUNDS_MISSING')
 all_bounds=[*provision_bounds.values(),*interaction_bounds.values(),higher_order_residual_bounds,interest_bounds]
 bounds=[]
 for pair in all_bounds:
  if len(pair)!=2:raise OriginalSourceError('BAD_INTERVAL')
  lo,hi=D(str(pair[0])),D(str(pair[1]))
  if not (lo.is_finite() and hi.is_finite()) or lo>hi:raise OriginalSourceError('INVALID_INTERVAL')
  bounds.append((lo,hi))
 l=sum((x[0] for x in bounds),D(0));u=sum((x[1] for x in bounds),D(0))
 gap=next(D(x['static_improvement_required_bn']) for x in baseline_gap() if x['fy']==year)
 return {'fy':year,'lower_possible_improvement_bn':str(l),'upper_possible_improvement_bn':str(u),
   'static_target_gap_bn':str(gap),'logical_result':('CONDITIONALLY_REJECT_TARGET' if u<gap
    else 'CONDITIONALLY_GUARANTEE_TARGET' if l>=gap else 'CONDITIONALLY_INDETERMINATE'),
   'qualification':'MATHEMATICAL_INTERVAL_CHECK_ONLY. Inputs need independent empirical provenance; not a score.'}
