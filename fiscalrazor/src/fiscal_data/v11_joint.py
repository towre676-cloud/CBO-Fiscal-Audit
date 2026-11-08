"""FiscalRazor v1.1: joint PERSON-LEVEL mechanical statutory incidence.

Policy parameters follow legislation/scenario_v06.json, not current law. Every
person, employer, tax unit and household distinction is explicit. Reported
results are statutory liability *increments*, not economic incidence, and are
calendar-year, not federal-fiscal-year cash receipts or official policy scores.

Unsupported components are null, NOT zero; input records must be supplied by
an authenticated data pipeline before population-level conclusions can follow.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Mapping

from fiscal_data.v06_law import phase_extra_rate, hi_extra_each_side

class Unidentified(ValueError):
    """Required legal/data dimension is missing; do not substitute zero."""

D=Decimal
ALLOWED_STATUS={'single','mfj','mfs','hoh','qualifying_surviving_spouse'}
SURTAX_2028={'single':'500000','mfj':'1000000','mfs':'500000','hoh':'750000','qualifying_surviving_spouse':'1000000'}
DEDUCTION_MAGI_2028={'single':'300000','mfj':'600000','mfs':'300000','hoh':'450000','qualifying_surviving_spouse':'600000'}
MEDICARE_ADDITIONAL_THRESHOLD={'single':'200000','mfj':'250000','mfs':'125000','hoh':'200000','qualifying_surviving_spouse':'200000'}
PREMIUM_LIMIT_2028={'self_only':'13000','family':'31000'}


def num(value, label):
    if isinstance(value,bool):raise Unidentified(f'{label}: Boolean is not a number')
    try:
        z=D(str(value))
    except (InvalidOperation,ValueError,TypeError):raise Unidentified(f'{label}: not a number')
    if not z.is_finite():raise Unidentified(f'{label}: nonfinite')
    return z

def nonneg(v,label):
    n=num(v,label)
    if n<0:raise Unidentified(f'{label}: negative')
    return n

def indexed_value(case, field, year, year2028_value):
    if year==2028:return D(year2028_value)
    # Future indexed amounts require a legally recorded index calculation;
    # we do not use CPI estimates without the statutory base/rounding rules.
    if field not in case:raise Unidentified(f'{field} needed for {year}; no invented inflation indexing')
    return nonneg(case[field],field)

def _person(p,year,wage_base,case):
    """Return incremental OASDI/HI components and health wages for one person."""
    if nonneg(p.get('self_employment_income_usd',0),'self_employment_income_usd') != 0:
        raise Unidentified('SECA not implemented in this wage-only model; refusing to omit it')
    emps=p.get('employers')
    if not isinstance(emps,list) or not emps:
        raise Unidentified('each person needs at least one employer; do not silently infer coverage')
    emp_ids=set(); base_w=[]; new_w=[]; health_extra=D(0); insured=0
    for e in emps:
        ident=e.get('id')
        if not isinstance(ident,str) or not ident.strip() or ident in emp_ids:
            raise Unidentified('employer id missing or duplicated within person')
        emp_ids.add(ident)
        if e.get('covered_under_OASDI_and_HI') is not True:
            raise Unidentified('wage must be explicitly documented as FICA covered')
        old=nonneg(e.get('cash_wages_usd'),'cash_wages_usd')
        health=nonneg(e.get('employer_health_cost_usd',0),'employer_health_cost_usd')
        extra=D(0)
        if health>0:
            if e.get('health_cost_includes_section125_pretax') is not True:
                raise Unidentified('health cost must include applicable Section 125 pre-tax premiums')
            insured+=1
            if insured>1:raise Unidentified('multiple health plans for same person require coordination')
            tier=e.get('coverage_tier')
            if tier not in PREMIUM_LIMIT_2028:raise Unidentified('missing health coverage tier')
            if year>=2028:
                if year==2028: cap=D(PREMIUM_LIMIT_2028[tier])
                else:
                    caps=case.get('indexed_health_caps_usd',{})
                    if not isinstance(caps,dict) or tier not in caps:raise Unidentified('indexed health exclusion cap missing')
                    cap=nonneg(caps[tier],f'health cap {tier}')
                extra=max(D(0),health-cap)
        base_w.append(old);new_w.append(old+extra);health_extra+=extra
    old_total=sum(base_w,D(0));new_total=sum(new_w,D(0))
    old_employee_os=D('.062')*min(old_total,wage_base)
    old_employer_os=D('.062')*sum((min(x,wage_base) for x in base_w),D(0))
    if year<2028:
        ph=D(0);high=D(0); threshold=None
    else:
        ph=phase_extra_rate(year)
        if year==2028:threshold=max(D('250000'),wage_base)
        else:
            if 'indexed_high_band_threshold_usd' not in case:raise Unidentified('future indexed high earnings threshold missing')
            threshold=max(wage_base,nonneg(case['indexed_high_band_threshold_usd'],'high band threshold'))
        high=max(D(0),new_total-threshold)
    new_employee_os=(D('.062')+ph)*(min(new_total,wage_base)+high)
    new_employer_os=(D('.062')+ph)*(sum((min(x,wage_base) for x in new_w),D(0))+high)
    # New high-band employer tax is allocated across employers by new wages.
    # Current-law employer OASDI cap is still per employer; thus full statutory
    # employer tax can change when the number of employers changes. The extra
    # *high band* remains invariant to employer splitting.
    employer_high_allocation=[(high*x/new_total if new_total else D(0)) for x in new_w]
    # Exact additive decomposition in employer/employee statutory tax dollars.
    low_old_employee=min(old_total,wage_base);low_new_employee=min(new_total,wage_base)
    low_old_employer=sum((min(x,wage_base) for x in base_w),D(0))
    low_new_employer=sum((min(x,wage_base) for x in new_w),D(0))
    decomp={
      'old_rate_new_low_band_coverage_increment_usd':D('.062')*(low_new_employee-low_old_employee + low_new_employer-low_old_employer),
      'old_rate_new_high_band_tax_usd':D('.124')*high,
      'phaseup_on_existing_low_band_usd':ph*(low_new_employee+low_new_employer),
      'phaseup_on_new_high_band_interaction_usd':D(2)*ph*high}
    if sum(decomp.values(),D(0))!=(new_employee_os+new_employer_os-old_employee_os-old_employer_os):
        raise Unidentified('OASDI statutory decomposition failed internal accounting')
    old_hi=(D('.0145')*old_total,D('.0145')*old_total)
    new_hi_rate=D('.0145')+hi_extra_each_side(year)
    new_hi=(new_hi_rate*new_total,new_hi_rate*new_total)
    return dict(person_id=p.get('id'), old_wages_usd=old_total,new_wages_usd=new_total,
        health_inclusion_usd=health_extra, new_high_band_usd=high,
        employer_high_band_allocations_usd=employer_high_allocation,
        oasdi_statutory_decomposition_usd=decomp,
        new_high_band_threshold_usd=threshold,
        oasdi_employee_increment_usd=new_employee_os-old_employee_os,
        oasdi_employer_increment_usd=new_employer_os-old_employer_os,
        hi_employee_increment_usd=new_hi[0]-old_hi[0],
        hi_employer_increment_usd=new_hi[1]-old_hi[1],
        old_total_wages_usd=old_total,new_total_wages_usd=new_total)

def joint_wage_vat(case:Mapping):
    year=case.get('calendar_year')
    if not isinstance(year,int) or year<2028 or year>2036:raise Unidentified('supported proposal years: 2028..2036')
    status=case.get('filing_status')
    if status not in ALLOWED_STATUS:raise Unidentified('invalid filing status')
    if case.get('household_is_one_tax_unit') is not True:
        raise Unidentified('multi-tax-unit household mapping not validated; no VAT credit assumption')
    wage_base=nonneg(case.get('official_oasdi_wage_base_usd'),'official_oasdi_wage_base_usd')
    if wage_base<=0:raise Unidentified('nonpositive OASDI wage base')
    p=case.get('persons')
    if not isinstance(p,list) or not p:raise Unidentified('persons[] required')
    if len(p)>2 or (len(p)>1 and status!='mfj'):
        raise Unidentified('tax-unit model supports at most two wage earners and only MFJ permits two')
    people=[_person(x,year,wage_base,case) for x in p]
    ids=[x['person_id'] for x in people]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise Unidentified('person IDs absent or duplicated')
    health=sum((x['health_inclusion_usd'] for x in people),D(0))
    magi_base=nonneg(case.get('baseline_tax_unit_magi_usd'),'baseline_tax_unit_magi_usd')
    magi_after=magi_base+health
    threshold=indexed_value(case,'indexed_surtax_threshold_usd',year,SURTAX_2028[status])
    surtax=D('.02')*max(D(0),magi_after-threshold)
    surtax_counterfactual_without_health=D('.02')*max(D(0),magi_base-threshold)
    itemized_rule=indexed_value(case,'indexed_itemized_magi_threshold_usd',year,DEDUCTION_MAGI_2028[status])
    itemized_delta=D(0) if magi_after<=itemized_rule else None
    health_income_delta=None
    pre=case.get('baseline_income_tax_before_reform_usd')
    post=case.get('income_tax_after_health_inclusion_before_other_sections_usd')
    if pre is not None and post is not None:
        health_income_delta=num(post,'post health income tax')-num(pre,'pre health income tax')
    if magi_after>itemized_rule:
        needed=['post_health_income_tax_without_itemized_usd','post_health_income_tax_with_itemized_usd','post_health_allowed_itemized_usd']
        if all(x in case for x in needed):
            without=nonneg(case[needed[0]],needed[0]);withit=nonneg(case[needed[1]],needed[1]);ded=nonneg(case[needed[2]],needed[2])
            if withit>without:raise Unidentified('itemized tax must not exceed tax without itemization in this statutory input')
            if post is not None and withit!=num(post,'post health tax'):raise Unidentified('itemization tax inputs conflict with post health liability')
            itemized_delta=max(D(0),(without-withit)-D('.28')*ded)
    total_old_wages=sum((x['old_wages_usd'] for x in people),D(0))
    total_new_wages=sum((x['new_wages_usd'] for x in people),D(0))
    add_thr=D(MEDICARE_ADDITIONAL_THRESHOLD[status])
    add_medicare_delta=D('.009')*(max(D(0),total_new_wages-add_thr)-max(D(0),total_old_wages-add_thr))
    oasdi_employee=sum((x['oasdi_employee_increment_usd'] for x in people),D(0))
    oasdi_employer=sum((x['oasdi_employer_increment_usd'] for x in people),D(0))
    hi_employee=sum((x['hi_employee_increment_usd'] for x in people),D(0))
    hi_employer=sum((x['hi_employer_increment_usd'] for x in people),D(0))
    vat_gross=vat_credit=vat_net=None
    if year>=2029:
        taxable=nonneg(case.get('classified_final_taxable_consumption_usd'),'classified_final_taxable_consumption_usd')
        poverty=nonneg(case.get('documented_hhs_poverty_guideline_usd'),'documented_hhs_poverty_guideline_usd')
        if poverty<=0:raise Unidentified('poverty guideline must be >0')
        vat_gross=taxable*D('.05')
        eligibility=max(D(0),min(D(1),(D(3)*poverty-magi_after)/poverty))
        vat_credit=D('.05')*poverty*eligibility
        vat_net=vat_gross-vat_credit
    unresolved=[]
    if health_income_delta is None:unresolved.append('104_FEDERAL_INCOME_TAX_AFTER_HEALTH_INCLUSION')
    if itemized_delta is None:unresolved.append('103_ITEMIZED_LIMIT_TAX_CALCULATOR')
    unresolved+=['105_CORPORATE_TAX_BENEFICIAL_INCIDENCE','108_PROGRESSIVE_BENEFIT_COHORTS',
      '109_MEDICARE_ADVANTAGE_PAYMENT_AND_PREMIUM', '110_SITE_NEUTRAL_PROVIDER_AND_PREMIUM',
      '111_DEFENSE_OUTLAY_AND_HOUSEHOLD_EFFECTS', 'MACRO_RESPONSES', 'FISCAL_YEAR_CASH_TIMING',
      'ALL_OTHER_LEGAL_CREDIT_TAX_AND_COMPLIANCE_INTERACTIONS']
    if year==2028: vat_net=D(0);vat_gross=D(0);vat_credit=D(0)
    components={'102_income_surtax_usd':surtax,'102_surtax_health_interaction_usd':surtax-surtax_counterfactual_without_health,
       '103_itemized_limitation_usd':itemized_delta,'104_health_wage_inclusion_usd':health,
       '104_income_tax_change_usd':health_income_delta,
       '106_107_oasdi_employee_increment_usd':oasdi_employee,
       '106_107_oasdi_employer_increment_usd':oasdi_employer,
       '112_hi_employee_increment_usd':hi_employee,
       '112_hi_employer_increment_usd':hi_employer,
       'additional_medicare_existing_0_9pct_delta_usd':add_medicare_delta,
       '101_vat_gross_usd':vat_gross,'101_refundable_vat_credit_usd':vat_credit,
       '101_vat_net_usd':vat_net}
    can_total=health_income_delta is not None and itemized_delta is not None
    identified_subtotal=(surtax+itemized_delta+health_income_delta+oasdi_employee+oasdi_employer+hi_employee+hi_employer+add_medicare_delta+vat_net) if can_total else None
    return {'calendar_year':year,'filing_status':status,'tax_unit_magi_before_usd':magi_base,
      'tax_unit_magi_after_health_usd':magi_after,'people':people,'components':components,
      'identified_statutory_liability_subtotal_usd':identified_subtotal,
      'full_12_provision_result':None,'unresolved':unresolved,
      'evidence_status':'RECORD_LEVEL_STATIC_MECHANICAL_NEVER_NATIONAL_SCORE',
      'statutory_payer_not_economic_burden':True,
      'fiscal_cash_timing':None,'source_record_provenance':case.get('source_record_provenance','UNSPECIFIED')}

def assert_not_national_score(_records):
    raise Unidentified('No 12-provision national estimate without sample/join/reweighting, linked income tax engine, Medicare and SSA benefit models, macro and timing calibration')
