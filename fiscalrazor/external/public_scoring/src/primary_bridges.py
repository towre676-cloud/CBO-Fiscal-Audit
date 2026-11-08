"""Source-backed SSA, CMS and national accounts bridges; strictly non-legislative scores.

Figures are excerpts transcribed from named official published tables and checked
for internal arithmetic. Original full-file bytes have NOT been independently
retrieved in the build environment. No trust-fund improvement is automatically
converted into an on-budget federal fiscal-year receipt.
"""
from __future__ import annotations
from decimal import Decimal as D
from collections import defaultdict
import csv, json
from .fiscalrazor import ROOT

SOURCES = {
    'ssa_economy':'https://www.ssa.gov/oact/TR/2026/lr6g1.html',
    'ssa_noninterest':'https://www.ssa.gov/oact/TR/2026/lr6g3.html',
    'ssa_reserves':'https://www.ssa.gov/oact/TR/2026/lr6g2.html',
    'ssa_options':'https://www.ssa.gov/oact/solvency/provisions/tables/table_run214.html',
    'cms_hi':'https://www.cms.gov/oact/tr/2026',
    'bea_pce':'https://fred.stlouisfed.org/release/tables?eid=43861&rid=53',
    'medpac_ma':'https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_ExecutiveSummary_MedPAC_Report_To_Congress_SEC.pdf',
}


def rows(filename):
    with (ROOT/'data'/filename).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def series(filename):
    return {int(r['calendar_year']):r for r in rows(filename)}


def ssa_dollar_equivalents(option_id):
    """SSA rate changes in percentage points * SAME-VINTAGE taxable payroll.

    Returns published precision bounded (±0.005 percentage point, multiplied
    by payroll) numeric translations of SSA's actuarial balance measure.
    NOT a CBO score, federal receipts, or an additive legislative package.
    """
    economy=series('ssa_trustees_2026_economic_cy.csv')
    options=[r for r in rows('ssa_2026_option_benchmarks.csv') if r['option_id']==option_id]
    if len(options)!=11: raise ValueError('Unknown SSA option or incomplete 2026–2036 published series')
    out=[]
    for r in options:
        y=int(r['calendar_year']); p=D(economy[y]['oasdi_taxable_payroll_billion']);rate=D(r['change_annual_balance_pct_of_current_law_taxable_payroll'])
        out.append({
            'calendar_year':y,
            'published_annual_balance_change_pct_taxable_payroll':str(rate),
            'published_taxable_payroll_billion':str(p),
            'derived_nominal_annual_balance_change_billion':str((p*rate/D(100)).quantize(D('.0001'))),
            'rounding_bound_due_to_two_decimal_pct_billion':str((p*D('.005')/D(100)).quantize(D('.0001'))),
            'source_url':r['source_url'],
            'measure':'CY OASDI annual actuarial balance improvement, not FY federal receipts',
            'status':'SINGLE_PROVISION_SSA_DERIVATION_NOT_JOINT_SCORE',
        })
    return out


def ssa_cash_audit():
    problems=[]
    vals=series('ssa_trustees_2026_oasdi_noninterest_cy.csv')
    reserve=series('ssa_trustees_2026_oasdi_reserves_cy.csv')
    p=series('ssa_trustees_2026_economic_cy.csv')
    if set(vals)!=set(range(2026,2037)): problems.append('2026–2036 OASDI noninterest coverage incomplete')
    if set(p)!=set(range(2026,2037)): problems.append('2026–2036 OASDI payroll coverage incomplete')
    if set(reserve)!=set(range(2025,2034)): problems.append('OASDI reserves coverage incomplete')
    for y,r in vals.items():
        for fund in ('oasi','di','oasdi'):
            ni=D(r[f'{fund}_noninterest_income_billion']); c=D(r[f'{fund}_cost_billion']); b=D(r[f'{fund}_noninterest_balance_billion'])
            if abs(ni-c-b)>D(1):problems.append(f'CY{y} {fund} noninterest accounting mismatch')
        for kind in ('noninterest_income','cost','noninterest_balance'):
            if abs(sum(D(r[f'{f}_{kind}_billion']) for f in ('oasi','di'))-D(r[f'oasdi_{kind}_billion']))>D(1):
                problems.append(f'CY{y} OASI+DI {kind} != OASDI')
        if y in reserve:
            if abs(D(reserve[y]['noninterest_income_billion'])-D(r['oasdi_noninterest_income_billion']))>D(1):
                problems.append(f'CY{y} mismatch VI.G2 vs VI.G3 noninterest')
            if abs(D(reserve[y]['cost_billion'])-D(r['oasdi_cost_billion']))>D(1):
                problems.append(f'CY{y} mismatch VI.G2 vs VI.G3 cost')
    prev=None
    for y,r in sorted(reserve.items()):
        ni,it,ti,c,end=[D(r[k]) for k in ('noninterest_income_billion','interest_income_billion','total_income_billion','cost_billion','end_reserves_billion')]
        if abs(ni+it-ti)>D('.11'):problems.append(f'CY{y} OASDI interest reconciliation')
        if prev is not None and abs(prev+ti-c-end)>D('.16'):problems.append(f'CY{y} OASDI stock-flow reserve reconciliation')
        prev=end
    return problems


def cms_hi_audit():
    problems=[];funds=series('cms_trustees_2026_hi_operations_cy.csv')
    if set(funds)!=set(range(2025,2036)): problems.append('CMS HI 2025–2035 coverage incomplete')
    prior=None
    for y,r in sorted(funds.items()):
        a,b,net,res=[D(r[k]) for k in ('total_income_including_interest_billion','total_expenditures_billion','change_in_fund_billion','end_reserves_billion')]
        if abs(a-b-net)>D('.11'): problems.append(f'CY{y} CMS HI published income–expense vs change mismatch')
        if prior is not None and abs(prior+net-res)>D('.16'):problems.append(f'CY{y} CMS HI change vs reserves mismatch')
        prior=res
        if y>=2033 and r['projection_status']!='hypothetical_after_depletion':problems.append(f'CY{y} must flag counterfactual scheduled payouts')
    if D(funds[2032]['end_reserves_billion'])<=0 or D(funds[2033]['end_reserves_billion'])>=0:
        problems.append('2026 report expected HI crossing in 2033')
    return problems


def cms_hi_perturbation(extra_annual_noninterest_income=None,annual_outlay_reduction=None):
    """First-order stock-flow delta, frozen published interest and behavior.

    A WHAT-IF accounting calculator, not an actuarial score or a prediction
    of the quarter of depletion. Excludes effects of reserve changes on earned
    interest, Medicare beneficiary behavior, enrollment, taxes and other funds.
    Only tested with synthetic changes; supplied changes are user assumptions.
    """
    extra_annual_noninterest_income=extra_annual_noninterest_income or {}
    annual_outlay_reduction=annual_outlay_reduction or {}
    years=series('cms_trustees_2026_hi_operations_cy.csv')
    if not set(extra_annual_noninterest_income).issubset(years) or not set(annual_outlay_reduction).issubset(years):
        raise ValueError('HI supported CY2025–2035 only')
    cumulative=D(0);out=[]
    for y,r in sorted(years.items()):
        if y==2025:
            out.append({'calendar_year':y,'baseline_reserves_billion':r['end_reserves_billion'],
                        'illustrative_reserves_billion':r['end_reserves_billion'],'status':'ACTUAL_2025_ANCHOR'})
            continue
        delta=D(extra_annual_noninterest_income.get(y,0))+D(annual_outlay_reduction.get(y,0))
        if not delta.is_finite():raise ValueError('Nonfinite HI hypothetical change')
        cumulative+=delta
        out.append({'calendar_year':y,
                    'baseline_reserves_billion':r['end_reserves_billion'],
                    'illustrative_reserves_billion':str((D(r['end_reserves_billion'])+cumulative).quantize(D('.1'))),
                    'cumulative_user_assumed_change_billion':str(cumulative),
                    'status':'NON_ACTUARIAL_FIRST_ORDER_FIXED_INTEREST_SCENARIO'})
    return {'rows':out,'official_reported_depletion':'CY2033 Q2',
            'depletion_prediction':'NOT_VALIDATED',
            'federal_FY_score':'NOT_ESTABLISHED',
            'warning':'Changes in trust fund interest, economy, enrollment, premium financing and plan responses not modeled.'}


def bea_pce_audit():
    vals={r['category_id']:D(r['nominal_billion']) for r in rows('bea_2025_pce_major_types.csv')}
    tests=[('PCE',vals['GOODS']+vals['SERVICES']),('GOODS',vals['DURABLE']+vals['NONDURABLE']),
           ('NONDURABLE',sum(vals[k] for k in ('FOOD','CLOTHING','GASOLINE','OTHER_NONDURABLE'))),
           ('SERVICES',vals['HOUSEHOLD_SERVICES']+vals['NPISH']),
           ('HOUSEHOLD_SERVICES',sum(vals[k] for k in ('HOUSING','HEALTH','TRANSPORT','RECREATION','FOOD_SERVICES','FINANCIAL','OTHER_SERVICES')))]
    return [f'{a} hierarchy sum differs' for a,b in tests if abs(vals[a]-b)>D('.003')]


def pce_mechanical_reference(rate='0.05',covered_portion=None,compliance=None):
    """BEA CY2025 PCE base, no assertion that all PCE is legally VAT taxable."""
    rate=D(str(rate))
    if not (D(0)<=rate<=D(1)):raise ValueError('Valid ad valorem rate required')
    vals={r['category_id']:D(r['nominal_billion']) for r in rows('bea_2025_pce_major_types.csv')}
    if covered_portion is None or compliance is None:
        return {'pce_billion':str(vals['PCE']),'vat_rate':str(rate),
                'all_pce_times_rate_billion_NOT_SCORE':str((vals['PCE']*rate).quantize(D('.0001'))),
                'taxable_consumption_base':'UNKNOWN',
                'net_vat_revenue':'NOT_ESTABLISHED',
                'reason':'Real tax-base treatment, household rebates, pricing, compliance and economic responses not specified'}
    s,c=D(str(covered_portion)),D(str(compliance))
    if not (D(0)<=s<=1 and D(0)<=c<=1):raise ValueError('Shares must be between zero and one')
    return {'pce_billion':str(vals['PCE']),'assumed_covered_share':str(s),'assumed_compliance':str(c),
            'mechanical_gross_billion':str((vals['PCE']*rate*s*c).quantize(D('.0001'))),
            'rebates_and_economic_effects':'NOT_MODELED',
            'status':'USER_ASSUMPTIONS_2025_PCE_MECHANICAL_NOT_JCT_SCORE'}


def medpac_ma_audit():
    data=json.loads((ROOT/'data/medpac_2026_ma_calibration.json').read_text())
    expected = (D(str(data['favorable_selection_contribution'])) + D(str(data['coding_intensity_contribution']))
                + D(str(data['offset_other_effects_approx'])))
    problems=[]
    if expected != D(str(data['excess_ma_payments'])):
        problems.append('MedPAC 2026 MA overlapping decomposition does not reconcile')
    if not 0 < D(str(data['higher_part_b_premium_contributions_associated_with_ma_billion'])) < D(str(data['excess_ma_payments'])):
        problems.append('MedPAC Part B beneficiary premium association must be positive and below MA total difference')
    return problems

def evidence_audit():
    problems=ssa_cash_audit()+cms_hi_audit()+bea_pce_audit()+medpac_ma_audit()
    return {'verified_internal_arithmetic':not problems,'issues':problems,
            'source_byte_validation':False,'unit':'nominal billions USD, specified calendar years',
            'primary_tables_excerpts':'SSA VI.G1/G2/G3, CMS II.E1, BEA NIPA 2.3.5',
            'official_combined_policy_score':'NOT_ESTABLISHED'}
