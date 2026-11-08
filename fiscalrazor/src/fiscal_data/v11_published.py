"""Public-data partial-identification, not a legislative/household score.

2025 BLS published *quintile means* are aggregated consumer units, not persons,
CPS households or federal tax units. Applying a hypothetical VAT factor to
those means is a ratio-of-means diagnostic, not an estimated personal burden.
The 2026-vintage SSA calendar-year actuarial payroll values and CBO fiscal-year
budget & PCE data deliberately remain in distinct result tables.
"""
from __future__ import annotations
from pathlib import Path
from decimal import Decimal
import csv
from fiscal_data.v06_law import phase_extra_rate
from fiscal_data.v10_potential import target_gap,hi_scenarios

D=Decimal
ROOT=Path(__file__).resolve().parents[2]
BLS_SOURCE='https://www.bls.gov/news.release/archives/cesan_10292026.htm'
SSA_SOURCE='https://www.ssa.gov/OACT/TR/2026/lr6g1.html'
CMS_SOURCE='https://www.cms.gov/oact/tr/2026'


def read_rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))


def ce_quintile_exposure(taxable_fraction=D('.5'),rate=D('.05')):
    f=D(str(taxable_fraction));t=D(str(rate))
    if f<0 or f>1 or t<0:raise ValueError('taxable fraction must be 0..1 and rate >=0')
    rows=read_rows(ROOT/'data/v11/bls_ce_2025_published_quintile_means.csv')
    if len(rows)!=5:raise ValueError('five BLS income quintiles required')
    out=[]
    for q in rows:
        units=D(q['consumer_units_thousands'])*1000
        income=D(q['mean_pretax_income_usd']);spending=D(q['mean_total_expenditures_usd'])
        if income<=0 or spending<0 or units<=0:raise ValueError('bad published BLS means')
        gross=spending*f*t
        out.append({'quintile':int(q['quintile']),
          'published_consumer_units_thousands':q['consumer_units_thousands'],
          'published_mean_pretax_income_usd':income,
          'published_mean_all_expenditures_usd':spending,
          'hypothetical_fraction_all_expenditures_taxed':f,
          'hypothetical_tax_rate':t,
          'hypothetical_annual_tax_on_group_mean_spending_usd':gross,
          'tax_on_group_mean_spending_divided_by_group_mean_income_pct':gross/income*100,
          'hypothetical_weighted_group_exposure_bn':gross*units/D('1000000000'),
          'national_household_incidence':'NOT_IDENTIFIED',
          'rebate_effect':'NOT_IDENTIFIED_BY_BLS_QUINTILE_MEANS',
          'evidence_status':'2025_BLS_PUBLISHED_QUINTILE_MEANS_HYPOTHETICAL_UNIFORM_TAXABLE_SHARE',
          'source_url':BLS_SOURCE})
    return out


def ssa_mechanical_rate_phaseup():
    rows=read_rows(ROOT/'external/public_scoring/data/ssa_trustees_2026_economic_cy.csv')
    by_year={int(q['calendar_year']):q for q in rows}
    if set(range(2027,2037))-by_year.keys():raise ValueError('SSA calendar series incomplete')
    out=[]
    for y in range(2027,2037):
        payroll=D(by_year[y]['oasdi_taxable_payroll_billion'])
        rate=2*phase_extra_rate(y)
        # Extra high band is excluded here. Already-taxed capped base ONLY.
        out.append({'calendar_year':y,'SSA_current_law_taxable_payroll_bn':payroll,
          'statutory_combined_base_rate_increment_pp':rate*100,
          'constant_base_additional_OASDI_tax_liability_bn':payroll*rate,
          'high_earnings_OASDI_addition':'NOT_CALCULATED',
          'income_tax_interaction':'NOT_CALCULATED',
          'FY_cash_or_interest_effect':'NOT_CALCULATED',
          'SSA_actuarial_JOINT_score':'NOT_CALCULATED',
          'evidence_status':'MECHANICAL_CALENDAR_YEAR_CALCULATION_NOT_FY_RECEIPTS',
          'source_url':SSA_SOURCE})
    return out


def vat_pce_fiscal_gap():
    out=[]
    pce=read_rows(ROOT/'data/v09/cbo_fy_pce_2027_2036_source_excerpt.csv')
    idx={int(r['fiscal_year']):D(r['pce_nominal_billions']) for r in pce}
    for y in range(2027,2037):
        g=target_gap(y)
        total=idx[y]
        all_spend_gross=total*D('.05')
        after_hypothetical_20pct_rebate=all_spend_gross*D('.8')
        out.append({'fiscal_year':y,'CBO_FY_PCE_total_bn':total,
          'FY_3pct_deficit_static_target_gap_bn':g['static_gap_to_3pct_bn'],
          'HYPOTHETICAL_full_PCE_gross_5pct_bn':all_spend_gross,
          'HYPOTHETICAL_full_PCE_net_with_20pct_rebate_bn':after_hypothetical_20pct_rebate,
          'gap_less_net_hypothetical_full_PCE_bn':g['static_gap_to_3pct_bn']-after_hypothetical_20pct_rebate,
          'actual_VAT_effect':'NOT_IDENTIFIED',
          'PCE_not_legally_defined_VAT_base':True,
          'source':'https://github.com/US-CBO/cbo-data'})
    return out


def hi_rounding_sensitivity():
    """Bound rounding propagation of published Table III.B5 cells.

    The trustees report shows expenditures rounded to 0.1 billion, and
    cost rate to 0.01 percentage point; model reserves also to 0.1 billion.
    These are tolerance intervals *conditional on source rounding*, not
    economic or forecast uncertainty. The 2026 source is not a 2036 forecast.
    """
    orig=hi_scenarios();res=[];cumulative={s:(D(0),D(0)) for s in ('intermediate','high_cost','low_cost')}
    for row in sorted(orig,key=lambda r:(r['scenario'],r['calendar_year'])):
        scenario=row['scenario'];y=int(row['calendar_year']);exp=row['hi_expenditures_bn'];r=row['source_reported_cost_rate_pct_payroll'];
        expense_lo=exp-D('.05');expense_hi=exp+D('.05')
        r_lo=r-D('.005');r_hi=r+D('.005')
        if expense_lo<=0 or r_lo<=0:raise ValueError('rounding interval hits invalid positive denominator')
        pay_lo=expense_lo*100/r_hi;pay_hi=expense_hi*100/r_lo
        rate=row['draft112_extra_combined_hi_rate_pp']/100
        incr_lo=pay_lo*rate;incr_hi=pay_hi*rate
        prev_lo,prev_hi=cumulative[scenario]
        cum_lo=prev_lo+incr_lo;cum_hi=prev_hi+incr_hi
        cumulative[scenario]=(cum_lo,cum_hi)
        model_base=row['baseline_end_assets_bn']
        res.append({'calendar_year':y,'scenario':scenario,
          'CMS_reported_expenditures_bn':exp,'CMS_reported_cost_rate_pp':r,
          'implied_taxable_payroll_lower_rounding_bn':pay_lo,
          'implied_taxable_payroll_upper_rounding_bn':pay_hi,
          'additional_HI_tax_lower_rounding_bn':incr_lo,
          'additional_HI_tax_upper_rounding_bn':incr_hi,
          'cumulative_extra_HI_tax_lower_rounding_bn':cum_lo,
          'cumulative_extra_HI_tax_upper_rounding_bn':cum_hi,
          'frozen_assets_after_tax_lower_rounding_bn':model_base-D('.05')+cum_lo,
          'frozen_assets_after_tax_upper_rounding_bn':model_base+D('.05')+cum_hi,
          'limitation':'ROUNDING_ONLY_NO_COST_OR_INTEREST_FEEDBACK',
          'source_url':CMS_SOURCE})
    return res


def high_cost_min_scale_rounding():
    rows=hi_rounding_sensitivity();high=[x for x in rows if x['scenario']=='high_cost' and x['calendar_year']>=2028]
    if len(high)!=8:raise ValueError('missing high-cost reserve path')
    # smallest scalar ensuring all 2028-35 year-end reserves nonnegative
    # given worst/best possible printed rounding of both assets and payroll.
    optimistic=max([D(0)]+[max(D(0),(-r['frozen_assets_after_tax_upper_rounding_bn']+r['cumulative_extra_HI_tax_upper_rounding_bn'])/r['cumulative_extra_HI_tax_upper_rounding_bn']) for r in high])
    conservative=max([D(0)]+[max(D(0),(-r['frozen_assets_after_tax_lower_rounding_bn']+r['cumulative_extra_HI_tax_lower_rounding_bn'])/r['cumulative_extra_HI_tax_lower_rounding_bn']) for r in high])
    # the expressions above recover baseline cost (A), then solve A+s*C>=0
    return {'min_scalar_for_nonnegative_2028_2035_yearend_high_cost_optimistic_rounding':optimistic,
            'min_scalar_for_nonnegative_2028_2035_yearend_high_cost_conservative_rounding':conservative,
            'implied_full_phase_combined_HI_extra_rate_pp_optimistic':optimistic*D('.75'),
            'implied_full_phase_combined_HI_extra_rate_pp_conservative':conservative*D('.75'),
            'qualification':'FROZEN_BASELINE_ROUNDING_ONLY_NOT_75_YEAR_ACTUARIAL_SOLVENCY_OR_FULL_RESERVE'}


def ce_vs_bea_2025_coverage_diagnostic():
    ce=ce_quintile_exposure(taxable_fraction=D(1),rate=D('0.05'))
    # The hypothetical 5% exposure is exactly 5% of sum(count*mean spending).
    ce_aggregate=sum((row['hypothetical_weighted_group_exposure_bn'] for row in ce),D(0))/D('.05')
    bea_rows=read_rows(ROOT/'external/public_scoring/data/bea_2025_pce_major_types.csv')
    bea=[r for r in bea_rows if r['category_id']=='PCE' and int(r['calendar_year'])==2025]
    if len(bea)!=1:raise ValueError('BEA 2025 original published PCE benchmark not unique')
    bea_aggregate=D(bea[0]['nominal_billion'])
    if ce_aggregate<=0 or bea_aggregate<=0:raise ValueError('invalid aggregates')
    return {'year':2025,'BLS_quintile_mean_times_consumer_units_bn':ce_aggregate,
      'BEA_annual_PCE_bn':bea_aggregate,
      'ratio_BLS_expanded_survey_to_BEA_PCE':ce_aggregate/bea_aggregate,
      'different_concepts_NOT_a_missing_tax_base_bn':bea_aggregate-ce_aggregate,
      'BLS_source':BLS_SOURCE,'BEA_source':bea[0]['source_url'],
      'measurement':'RATIO_OF_DIFFERENT_STATISTICAL_CONCEPTS;NO_DIRECT_VAT_CALIBRATION;PUB_ROUNDING'}
