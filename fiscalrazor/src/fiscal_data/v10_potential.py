"""FiscalRazor v1.0: partial-identification and agency-analogue scoring laboratory.

This module produces deterministic, clearly distinguished calculations:
- CBO FY baseline fiscal gaps are official published baseline numbers;
- CBO/JCT Dec-2024 *single policy* option figures are analogues only;
- SSA published single-provision annual actuarial balances are CY, not FY;
- Medicare HI frozen-baseline payroll additions are mechanical illustrations.

It deliberately DOES NOT estimate joint savings, household incidence or official scores.
"""
from __future__ import annotations
from pathlib import Path
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from typing import Any
import csv, json

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'data'/'v10'

class EvidenceBoundary(ValueError):
    pass

def D(x):
    try:
        z=Decimal(str(x))
    except (InvalidOperation,TypeError) as ex:
        raise EvidenceBoundary(f'non-numeric evidence: {x!r}') from ex
    if not z.is_finite():
        raise EvidenceBoundary('non-finite evidence')
    return z

def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def legal_spec():
    from fiscal_data.v06_law import scenario,validate_spec
    validate_spec()
    return scenario()

def analogues():
    data=json.loads((EVIDENCE/'cbo_2024_policy_analogues.json').read_text(encoding='utf-8'))
    rows=data['rows']
    if data['fiscal_year']!=2034 or len(rows)!=12 or {r['section'] for r in rows}!=set(range(101,113)):
        raise EvidenceBoundary('unexpected official analogue metadata/rows')
    for r in rows:
        if not r['status'].startswith(('ANALOGUE_ONLY','CLOSE_POLICY_ANALOGUE','NO_MATCHED')):
            raise EvidenceBoundary('option is not an exact combined 2026-law score')
        if r['deficit_improvement_bn'] is not None and D(r['deficit_improvement_bn'])<0:
            raise EvidenceBoundary('option sign must be a positive deficit improvement')
    return rows

def _official_baselines():
    budgets={int(r['fy']):r for r in read_csv(ROOT/'data/verified_tables/cbo_budget_fy2026_2036_21_series.csv')}
    gdps={int(r['fiscal_year']):D(r['nominal_gdp_bn']) for r in read_csv(ROOT/'data/verified_tables/cbo_gdp_fy2026_2036_official.csv')}
    if set(range(2027,2037)) - set(budgets) or set(range(2027,2037)) - set(gdps):
        raise EvidenceBoundary('missing fiscal baseline year')
    return budgets,gdps

def target_gap(fy:int):
    budgets,gdps=_official_baselines()
    if fy not in range(2027,2037):raise EvidenceBoundary('unsupported baseline vintage year')
    row=budgets[fy]
    revenue=D(row['proj_rev_total'])
    outlay=D(row['proj_outlays_total'])
    d=-D(row['proj_deficit_total'])
    interest=D(row['proj_outlays_net_interest'])
    primary=-D(row['proj_primary_deficit'])
    if abs((outlay-revenue)-d)>D('.00001') or abs((interest+primary)-d)>D('.00001'):
        raise EvidenceBoundary('inconsistent official baseline components')
    gap=d-D('.03')*gdps[fy]
    return dict(fy=fy,baseline_deficit_bn=d,nominal_gdp_bn=gdps[fy],
                baseline_interest_bn=interest,baseline_primary_deficit_bn=primary,
                static_gap_to_3pct_bn=max(D(0),gap),
                baseline_vintage='CBO_FEB_2026_NOT_LATEST_ADJUSTED',
                source='https://github.com/US-CBO/cbo-data',
                applicability='MATHEMATICAL_TARGET_NOT_A_REFORM_SCORE')

def analogue_comparison(fy=2034):
    if fy!=2034:raise EvidenceBoundary('CBO 2024 option analogue estimates available only for matched FY2034; no extrapolation')
    g=target_gap(fy)['static_gap_to_3pct_bn']
    out=[]
    for r in analogues():
        x={**r,'comparator_fy':fy,'baseline_vintage':'CBO_DEC_2024',
           'our_law_score':'UNSCORED','combinable':False,
           'evidence_status':'OFFICIAL_SINGLE_OPTION_DIFFERENT_POLICY_NO_JOINT_INFERENCE'}
        if r['deficit_improvement_bn'] is not None:
            effect=D(r['deficit_improvement_bn'])
            x['official_analogue_bn']=effect
            x['comparator_as_pct_of_2026_baseline_target']=effect/g*100
        else:
            x['official_analogue_bn']=None
            x['comparator_as_pct_of_2026_baseline_target']=None
        out.append(x)
    return out

def cannot_combine_comparators(rows):
    if any(r.get('combinable') is not False or r.get('our_law_score')!='UNSCORED' for r in rows):
        raise EvidenceBoundary('bad analogue guard')
    raise EvidenceBoundary('Official individual-option analogues are non-additive, different law, different dates, different baseline')

def ssa_annual_balance_equivalents():
    a={int(x['calendar_year']):x for x in read_csv(ROOT/'data/verified_tables/ssa_individual_provision_annual_balance_2026_2036.csv')}
    p={int(x['calendar_year']):D(x['oasdi_taxable_payroll_billion']) for x in read_csv(ROOT/'external/public_scoring/data/ssa_trustees_2026_economic_cy.csv')}
    if set(a)!=set(p) or len(a)!=11:raise EvidenceBoundary('SSA standalone series incomplete')
    result=[]
    for y in sorted(a):
        row={'calendar_year':y,'current_law_oasdi_taxable_payroll_bn':p[y],
             'source_status':'SSA_2026_STANDALONE_SINGLE_PROVISION_NOT_OUR_LEGISLATION',
             'score_status':'ACTUARIAL_ANNUAL_BALANCE_EQUIVALENT_NOT_FY_CASH'}
        for key,col in [('E2_5','E2_5_delta_annual_balance_pct_payroll'),('E1_10','E1_10_delta_annual_balance_pct_payroll'),('B1_2','B1_2_delta_annual_balance_pct_payroll')]:
            row[key+'_annual_balance_delta_pp']=D(a[y][col]);row[key+'_balance_dollar_equiv_bn']=p[y]*D(a[y][col])/100
        if y>=2032:row['our_107_1pp_base_oasdi_mechanical_bn']=p[y]/100
        else:row['our_107_1pp_base_oasdi_mechanical_bn']=None
        result.append(row)
    return result

def hi_scenarios():
    from fiscal_data.v06_law import hi_extra_each_side
    rows=read_csv(EVIDENCE/'cms_2026_hi_b5_three_scenarios.csv')
    expected={(y,s) for y in range(2025,2036) for s in ('intermediate','low_cost','high_cost')}
    observed={(int(x['calendar_year']),x['scenario']) for x in rows}
    if len(rows)!=33 or observed!=expected:
        raise EvidenceBoundary('incomplete or duplicate CMS annual scenario tables')
    by_s=defaultdict(list)
    for r in rows:
        by_s[r['scenario']].append(r)
    result=[]
    for scenario,srows in by_s.items():
        cum=D(0)
        for r in sorted(srows,key=lambda x:int(x['calendar_year'])):
            y=int(r['calendar_year']);exp=D(r['expenditures_bn']); cost_rate=D(r['hi_cost_rate_pct_taxable_payroll']);baseline=D(r['baseline_year_end_assets_bn'])
            if exp<=0 or cost_rate<=0:raise EvidenceBoundary('invalid HI annual cost or payroll base')
            payroll=exp*100/cost_rate
            extra_rate=2*hi_extra_each_side(y)
            additional=payroll*extra_rate
            cum+=additional
            model_assets=baseline+cum
            result.append({'calendar_year':y,'scenario':scenario,'hi_expenditures_bn':exp,
                'source_reported_cost_rate_pct_payroll':cost_rate,
                'implied_hi_taxable_payroll_bn':payroll,
                'baseline_end_assets_bn':baseline,'draft112_extra_combined_hi_rate_pp':extra_rate*100,
                'new_mechanical_hi_tax_bn':additional,'cum_mechanical_hi_tax_bn':cum,
                'frozen_baseline_year_end_assets_bn':model_assets,
                'frozen_year_end_reserve_ratio_pct':model_assets/exp*100,
                'status':'HYPOTHETICAL_FROZEN_BASELINE_NOT_HI_ACTUARIAL_RESCORING',
                'source':r['source_url'],'source_table':r['source_table']})
    return sorted(result,key=lambda x:(x['scenario'],x['calendar_year']))

def hi_thresholds():
    rows=hi_scenarios();res=[]
    for scenario in ('low_cost','intermediate','high_cost'):
        subset=sorted([r for r in rows if r['scenario']==scenario],key=lambda r:r['calendar_year'])
        end=subset[-1]
        extra=end['cum_mechanical_hi_tax_bn']
        if extra<=0:raise EvidenceBoundary('expected positive model additional HI tax')
        # Uniform scalar applied to all annual draft 112 combined rates, zero elsewhere.
        # For each y, A_base(y)+scale*cumulative_extra(y)>=0.
        risk0=max([max(D(0),-r['baseline_end_assets_bn']/r['cum_mechanical_hi_tax_bn'])
                   for r in subset if r['cum_mechanical_hi_tax_bn']>0]+[D(0)])
        risk100=max([max(D(0),(r['hi_expenditures_bn']-r['baseline_end_assets_bn'])/r['cum_mechanical_hi_tax_bn'])
                   for r in subset if r['cum_mechanical_hi_tax_bn']>0]+[D(0)])
        required_2035_100=(end['hi_expenditures_bn']-end['baseline_end_assets_bn'])/extra
        res.append({'scenario':scenario,
                    'year_end_assets_2035_with_draft_bn':end['frozen_baseline_year_end_assets_bn'],
                    'year_end_2035_reserve_ratio_pct':end['frozen_year_end_reserve_ratio_pct'],
                    'years_after_policy_start':8,
                    'min_scalar_for_nonnegative_yearend_assets_2028_2035':risk0,
                    'min_scalar_for_100pct_yearend_reserve_each_year_2028_2035':risk100,
                    'min_scalar_for_100pct_yearend_reserve_in_2035_only':required_2035_100,
                    'funding_rate_full_phase_pp_if_scaled_to_2035_100pct':required_2035_100*D('.75'),
                    'status':'MATHEMATICAL_SCALAR_ONLY_DOES_NOT_GUARANTEE_WITHIN_YEAR_LIQUIDITY_OR_75Y_SOLVENCY'})
    return res

def mechanical_consumption_benchmark(fy=2034):
    pce={int(x['fiscal_year']):D(x['pce_nominal_billions']) for x in read_csv(ROOT/'data/v09/cbo_fy_pce_2027_2036_source_excerpt.csv')}
    if fy not in pce:raise EvidenceBoundary('PCE reference unavailable')
    return {'fy':fy,'cbo_fy_pce_bn':pce[fy],
            'upper_static_gross_5pct_all_pce_bn':pce[fy]*D('.05'),
            'percent_of_2026_3pct_gap_all_pce_gross':pce[fy]*D('.05')/target_gap(fy)['static_gap_to_3pct_bn']*100,
            'NOT_AN_ESTIMATE_OF_OUR_VAT':'FULL_PCE_INCLUDES_EXEMPT_TAXABLE_IMPUTED_SPENDING_AND_NO_CREDIT'}

def refuse_national_score():
    raise EvidenceBoundary('Joint reform effects cannot be identified from aggregate CBO/SSA/CMS option analogues and no calibrated microdata')

def vat_household_thresholds_by_poverty_multiple():
    """Exact symbolic incidence of section 101 refundable credit in units of P,
    the household's HHS poverty guideline, under full 5% pass-through.
    This is a structural observation, never population-weighted or a welfare score.
    """
    # Y/P values. Consumption C/P at break-even = max(0,min(1,3-Y/P)).
    out=[]
    for y in ['0','1','1.5','2','2.25','2.5','2.75','3','4']:
        ym=D(y)
        credit_base=max(D(0), min(D(1), D(3)-ym))
        out.append({'annual_MAGI_over_HHS_guideline':ym,
                    'rebate_as_share_of_HHS_guideline':D('.05')*credit_base,
                    'taxable_consumption_over_guideline_at_net_VAT_zero':credit_base,
                    'tax_on_C_equal_1_25P_less_rebate_over_P':D('.05')*(D('1.25')-credit_base),
                    'status':'EXACT_LEGAL_STATIC_HOUSEHOLD_INCENTIVE_WITH_EXOGENOUS_P_NO_NATIONAL_INCIDENCE'})
    return out

def vat_fixed_base_capacity(fy=2034):
    m=mechanical_consumption_benchmark(fy)
    g=target_gap(fy)['static_gap_to_3pct_bn']
    gross=m['upper_static_gross_5pct_all_pce_bn']
    return {'fy':fy,'fixed_all_pce_gross_bn':gross,'static_3pct_gap_bn':g,
            'uncovered_gap_even_with_all_pce_taxed_and_no_rebates_bn':max(D(0),g-gross),
            'assumptions':'5PCT_TAX_EXCLUSIVE_FIXED_NOMINAL_CBO_PCE_BASE_NO_CONSUMPTION_RESPONSE_NO_REBATES_FULL_COMPLIANCE',
            'caution':'NOT_AN_OFFICIAL_SCORE_AND_NOT_A_STRICT_BOUND_FOR_ALL_POSSIBLE_VAT_BASES'}

def drafted_surtax_cy2028_top1_mechanical_lower_bound():
    """Convexity/positive-part bound on actual draft §102, first year only.

    For every filing unit i, proposed MAGI >= AGI and highest statutory surtax
    threshold is 1 million USD in 2028. Thus sum (MAGI_i-T_i)+ >=
    (sum AGI_i - 1m * num returns)_+ for *any* group. Official CBO reported
    top-1%-of-return AGI share and total return counts fix the group margins.
    No distribution inside that group is assumed. This is a mechanical liability
    lower bound with no behavioral response, filing timing or national model.
    """
    rows=read_csv(EVIDENCE/'cbo_2026_02_top1_cy2028_iit_excerpt.csv')
    if len(rows)!=1:raise EvidenceBoundary('missing sourced 2028 revenue margin')
    x=rows[0]
    if int(x['calendar_year'])!=2028 or x['cbo_git_blob_sha1']!='2507f312912b0ff6475690c20a1a56d175772276':
        raise EvidenceBoundary('incorrect source vintage')
    for field in ('returns_total_million','total_agi_bn','top1_agi_share_pct'):
        if D(x[field])<=0:raise EvidenceBoundary('invalid aggregate margin')
    if D(x['top1_agi_share_pct'])>100:raise EvidenceBoundary('AGI share is not a percent')
    agi_top_bn=D(x['total_agi_bn'])*D(x['top1_agi_share_pct'])/100
    n_top_m=D(x['returns_total_million'])/100
    # one million USD per return * one million returns = one trillion USD = 1000 billion
    # n_top_m million returns * $1m = n_top_m * 1000 billion USD
    threshold_max_usd=D('1000000')
    raw_top_bn=threshold_max_usd*n_top_m / D('1000') # million USD * million returns / 1000 => billions
    lower_base_bn=max(D(0),agi_top_bn-raw_top_bn)
    lower_liability_bn=D('.02')*lower_base_bn
    return {'calendar_year':2028,'all_returns_million':D(x['returns_total_million']),
         'top1_returns_million':n_top_m,
         'top1_AGI_share_pct':D(x['top1_agi_share_pct']),
         'top1_AGI_total_bn':agi_top_bn,'max_2028_surtax_threshold_usd':threshold_max_usd,
         'top1_aggregate_threshold_equivalent_bn':raw_top_bn,
         'nonbehavioral_top1_MAGI_surtax_base_lower_bound_bn':lower_base_bn,
         'nonbehavioral_top1_MAGI_surtax_liability_lower_bound_bn':lower_liability_bn,
         'status':'EXACT_CONDITIONAL_AGGREGATE_PARTIAL_IDENTIFICATION_NOT_TAX_REVENUE_FORECAST',
         'source':x['source_url'],'source_git_blob_sha1':x['cbo_git_blob_sha1']}

def defense_budget_authority_reduction_path():
    rows=read_csv(ROOT/'data/v06/defense_ba_cap_locked.csv')
    if len(rows)!=9 or set(int(x['fy']) for x in rows)!=set(range(2028,2037)):
        raise EvidenceBoundary('expected nine distinct draft BA ceiling years')
    out=[]
    for x in rows:
        baseline=D(x['cbo_2026_02_defense_base_BA_bn'])
        ceiling=D(x['draft_95pct_nominal_cap_bn'])
        amount=baseline-ceiling
        if amount<0 or abs(ceiling/baseline-D('.95'))>D('.000002'):
            raise EvidenceBoundary('defense BA cap not 95% baseline')
        out.append({'fy':int(x['fy']),'source_CBO_base_defense_BA_bn':baseline,
                    'draft_defense_BA_ceiling_bn':ceiling,'mechanical_base_BA_delta_bn':amount,
                    'fiscal_year_outlay_delta_bn':None,
                    'status':'MECHANICAL_BUDGET_AUTHORITY_NOT_CASH_OUTLAY_SCORE',
                    'source_variable':x['CBO_variable']})
    return out
