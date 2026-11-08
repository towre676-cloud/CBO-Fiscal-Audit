"""Executable parts of a fixed 12-provision *proposed* law, not a federal score.
All national estimates, price indexes, unknown survey weights, actuarial trajectories,
and agency certifications are fail-closed. All monetary examples are hypothetical.
"""
from __future__ import annotations
from pathlib import Path
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import csv, json, math

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/'legislation/scenario_v06.json'
ALLOWED_STATES={'FULLY_PARAMETERIZED_RESEARCH_PROPOSAL__UNSCORED'}
P={}

class MissingEvidence(ValueError):pass
class BadSpecification(ValueError):pass

def dec(x):
    if isinstance(x,bool) or x is None:raise BadSpecification('not a monetary/rate number')
    try: d=Decimal(str(x))
    except Exception as ex:raise BadSpecification(f'not decimal: {x!r}') from ex
    if not d.is_finite():raise BadSpecification('nonfinite')
    return d

def round1000(x):return dec(x).quantize(Decimal('1E+3'),rounding=ROUND_HALF_UP)

def scenario():return json.loads(SPEC.read_text(encoding='utf-8'))

def policies():return {x['id']:x for x in scenario()['policies']}

EXPECTED_IDS=('vat_5_percent_with_rebates','high_income_surtax',
'itemized_deduction_limits','employer_health_exclusion_cap',
'corporate_tax_rate','oasdi_high_earnings_250k',
'oasdi_base_rate_phaseup','oasdi_progressive_price_index',
'medicare_advantage','medicare_site_neutral','defense_budget','medicare_hi_financing')

def validate_spec():
    obj=scenario();p=obj['policies']; ids=[x['id'] for x in p]
    if tuple(ids)!=EXPECTED_IDS:raise BadSpecification('12 ordered, unique provisions required')
    if len({x['section'] for x in p})!=12:raise BadSpecification('duplicate section')
    for x in p:
        for field in ['id','section','score_lead','effective_date','income_type','deposit','terms','legal_anchor','status','evidence_type']:
            if not x.get(field):raise BadSpecification(f'provision {x.get("id")} lacks {field}')
        if x['status'] not in ALLOWED_STATES or x['official_score'] is not None or x['model_estimate'] is not None:
            raise BadSpecification('unexpected certified or numerical score')
        date.fromisoformat(x['effective_date'])
    t=policies()['oasdi_base_rate_phaseup']['terms']['annual_employee_extra_rate']
    if [dec(v) for v in t.values()] != [dec('0.001')*i for i in range(1,6)]:raise BadSpecification('OASDI rate path malformed')
    h=policies()['medicare_hi_financing']['terms']['extra_employee_and_employer_rate']
    if [dec(v) for v in h.values()]!=[dec('0.00125')*i for i in range(1,4)]:raise BadSpecification('HI rate path malformed')
    return True

def fiscal_year(d:date)->int:
    return d.year+1 if d.month>=10 else d.year

def phase_extra_rate(year):
    y=int(year)
    if y<2028:return Decimal(0)
    return dec(policies()['oasdi_base_rate_phaseup']['terms']['annual_employee_extra_rate'].get(str(min(y,2032))))

def hi_extra_each_side(year):
    y=int(year)
    if y<2028:return Decimal(0)
    return dec(policies()['medicare_hi_financing']['terms']['extra_employee_and_employer_rate'][str(min(y,2030))])

def hi_mechanical_new_tax(wages,year):
    """Change in combined employee+employer HI tax, wages only, no dynamic behavior."""
    w=dec(wages)
    if w<0:raise BadSpecification('negative wages')
    return w*2*hi_extra_each_side(year)

def high_threshold(year, wage_base, awi_2026=None, awi_lagged=None):
    y=int(year);b=dec(wage_base)
    if b<0:raise BadSpecification('negative wage cap')
    if y<2028:raise MissingEvidence('proposed high wage tax inactive before 2028')
    if y==2028:return max(b,Decimal('250000'))
    if awi_2026 is None or awi_lagged is None:raise MissingEvidence('SSA AWI_(y-2) and AWI_2026 required')
    den=dec(awi_2026);num=dec(awi_lagged)
    if den<=0 or num<=0:raise BadSpecification('AWI must be positive')
    return max(b,round1000(Decimal('250000')*num/den))

def payroll_decomposition(wage,year,wage_base,awi_2026=None,awi_lagged=None):
    """Mechanical OASDI changes for one employer and one employee with no other wages.
    Unit: dollars of taxable wages (not collections). Employer and employee together.
    High band and phase-up effects are decomposed into two non-overlapping pieces + interaction.
    """
    y=int(year); w=dec(wage); b=dec(wage_base)
    if w<0 or b<=0:raise BadSpecification('negative wage or nonpositive base')
    low=min(w,b)
    if y<2028:
        return {'baseline_tax': low*dec('.124'),'high_band':Decimal(0),'base_rate':Decimal(0),'interaction':Decimal(0),'increment':Decimal(0),'taxable_low':low,'taxable_high':Decimal(0)}
    h=high_threshold(y,b,awi_2026,awi_lagged)
    high=max(Decimal(0),w-h)
    high_part=dec('.124')*high
    ph=2*phase_extra_rate(y)
    base_part=ph*low
    interaction=ph*high
    total=high_part+base_part+interaction
    return {'baseline_tax': dec('.124')*low,'high_band':high_part,'base_rate':base_part,'interaction':interaction,'increment':total,'taxable_low':low,'taxable_high':high}

def surtax_2028(magi,status):
    """CY2028 static surcharge only. Future years require official index input."""
    if status not in ('single','mfj','mfs','hoh','qualifying_surviving_spouse'):raise BadSpecification('unknown filing status')
    thr=dec(policies()['high_income_surtax']['terms']['threshold_usd_2028'][status]);income=dec(magi)
    return dec('.02')*max(Decimal(0),income-thr)

def itemized_cap_additional_tax_2028(magi,status,itemized_allowed,tax_without_itemized,tax_with_itemized):
    p=policies()['itemized_deduction_limits']['terms'];t=dec(p['eligible_if_MAGI_exceeds_usd_2028'][status]);d=dec(itemized_allowed)
    a=dec(tax_without_itemized);b=dec(tax_with_itemized)
    if d<0 or a<0 or b<0 or b>a:raise BadSpecification('invalid itemized/tax liabilities')
    if dec(magi)<=t:return Decimal(0)
    return max(Decimal(0), (a-b)-dec('.28')*d)

def employer_health_inclusion_2028(premium,tier):
    p=policies()['employer_health_exclusion_cap']['terms']
    if tier not in p['annual_excludable_premium_limit_usd_2028']:raise BadSpecification('unrecognized tier')
    premium=dec(premium)
    if premium<0:raise BadSpecification('negative premium')
    return max(Decimal(0),premium-dec(p['annual_excludable_premium_limit_usd_2028'][tier]))

def vat_rebate_assessment(magi, poverty_guideline, qualifying_consumption):
    """CY2029+ synthetic illustration for eligible consumption and observed guideline.
    No inferred taxable national consumption base.
    """
    income=dec(magi);pov=dec(poverty_guideline);c=dec(qualifying_consumption)
    if income<0 or pov<=0 or c<0:raise BadSpecification('invalid VAT inputs')
    rate=dec('.05');tax=rate*c
    eligibility=max(Decimal(0),min(Decimal(1),(3*pov-income)/pov))
    rebate=rate*pov*eligibility
    return {'gross_vat':tax,'refundable_credit':rebate,'net_before_behavior':tax-rebate,'eligibility_fraction':eligibility}

def corporate_mechanical_2028(affected_taxable_income):
    inc=dec(affected_taxable_income)
    if inc<0:raise BadSpecification('negative affected taxable income; loss rules not included')
    return dec('.01')*inc

def defense_caps():
    return {int(k):dec(v) for k,v in policies()['defense_budget']['terms']['caps_base_defense_BA_billions'].items()}

def admit_national_score(rows, interact_rows):
    """No false joint-score claim. Require full FY2027-36 modelled records + evidence.
    Supports independent estimates only, never sets 'official' automatically.
    """
    P={(r['provision'],int(r['fy'])):r for r in rows}
    required={(i,y) for i in EXPECTED_IDS for y in range(2027,2037)}
    if set(P)!=required or len(P)!=len(rows):raise MissingEvidence('120 exact FY provision-year effects required; missing is not zero')
    receipt_file=ROOT/'data/score_model_receipts_v06.json'
    if not receipt_file.is_file():raise MissingEvidence('no verified source+model score receipts; national score not admitted')
    admission=json.loads(receipt_file.read_text(encoding='utf-8'))
    approved=set(admission.get('admitted_artifact_sha256',[]))
    if not approved:raise MissingEvidence('no admitted score artifacts')
    for key,r in P.items():
        if r.get('source_sha256') not in approved:raise MissingEvidence(f'score artifact is not cryptographically admitted: {key}')
        if 'net_primary_balance_change_bn' not in r or not r.get('source_sha256') or not r.get('source_url') or not r.get('score_method'):
            raise MissingEvidence(f'not grounded {key}')
        dec(r['net_primary_balance_change_bn'])
        if r['score_method']=='synthetic' or r['score_method']=='unverified':raise MissingEvidence('synthetic inputs are not national scores')
    pairs=[('oasdi_high_earnings_250k','oasdi_base_rate_phaseup'),('oasdi_high_earnings_250k','oasdi_progressive_price_index'),
           ('vat_5_percent_with_rebates','high_income_surtax'),('employer_health_exclusion_cap','high_income_surtax'),
           ('corporate_tax_rate','high_income_surtax'),('corporate_tax_rate','itemized_deduction_limits'),
           ('medicare_advantage','medicare_site_neutral'),('medicare_advantage','medicare_hi_financing'),('medicare_site_neutral','medicare_hi_financing')]
    M={(r['a'],r['b'],int(r['fy'])):r for r in interact_rows}
    must={(a,b,y) for (a,b) in pairs for y in range(2027,2037)}
    if set(M)!=must or len(M)!=len(interact_rows):raise MissingEvidence('90 designated interaction-year records required')
    for k,r in M.items():
        if r.get('source_sha256') not in approved:raise MissingEvidence(f'interaction artifact is not admitted: {k}')
        for field in ('net_primary_balance_change_bn','source_url','source_sha256','score_method'):
            if field not in r or not str(r[field]).strip():raise MissingEvidence(f'inadequate interaction evidence {k}')
        dec(r['net_primary_balance_change_bn'])
        if r['score_method']=='synthetic':raise MissingEvidence('synthetic interaction not admissible')
    return {'status':'INDEPENDENT_POTENTIAL_SCORE_NOT_OFFICIAL','year_count':10,'provision_count':12,'interaction_count':9,'source_limitation':'No CBO/JCT/SSA/CMS certification established'}

def baseline_gap(target=Decimal('.03')):
    path=ROOT/'data/verified_tables/cbo_budget_fy2026_2036_21_series.csv'
    gp=ROOT/'data/verified_tables/cbo_gdp_fy2026_2036_official.csv'
    with path.open(newline='',encoding='utf-8') as f:
        budgets={int(x['fy']):x for x in csv.DictReader(f)}
    with gp.open(newline='',encoding='utf-8') as f:
        gdp={int(x['fiscal_year']):dec(x['nominal_gdp_bn']) for x in csv.DictReader(f)}
    rows=[]
    for y in range(2027,2037):
        b=budgets[y];d=-dec(b['proj_deficit_total']);p=-dec(b['proj_primary_deficit']);i=dec(b['proj_outlays_net_interest'])
        if abs(d-(p+i))>dec('.00001'):raise BadSpecification('inconsistent CBO identity')
        gap=max(Decimal(0),d-dec(target)*gdp[y]);break_even=max(Decimal(0), d-i)
        rows.append({'fy':y,'baseline_nominal_gdp_bn':str(gdp[y]),'baseline_deficit_bn':str(d),
            'baseline_primary_deficit_bn':str(p),'baseline_net_interest_bn':str(i),
            'max_deficit_3pct_bn':str(dec(target)*gdp[y]),'static_improvement_required_bn':str(gap),
            'if_net_interest_fixed_target_primary_balance_bn':str(i-dec(target)*gdp[y]),
            'evidence':'CBO_2026_02_OFFICIAL_BASELINE_EXTRACT_NOT_NOV_2026_CURRENT_LAW',
            'policy_effect':'NOT_SCORED'})
    return rows

def high_band_proportional_allocation(covered_compensation_components, threshold):
    """Novel research design for cross-employer / SECA allocation of *extra* high band.
    Does not replace the CURRENT LAW employer-by-employer capped payroll tax base.
    Supports any finite nonnegative component values. No future AWI guessed.
    """
    amounts=[dec(x) for x in covered_compensation_components]
    if not amounts or any(x<0 for x in amounts):raise BadSpecification('invalid covered components')
    t=dec(threshold)
    if t<0:raise BadSpecification('negative high band threshold')
    total=sum(amounts,Decimal(0))
    if total<=t:return [Decimal(0)]*len(amounts)
    above=total-t
    return [above*x/total for x in amounts]
