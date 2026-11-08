"""Source-disciplined fiscal target/frontier analysis. Never guesses a provision's score."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .v06_law import dec, EXPECTED_IDS, baseline_gap, MissingEvidence

PAIRS=(('oasdi_high_earnings_250k','oasdi_base_rate_phaseup'),
 ('oasdi_high_earnings_250k','oasdi_progressive_price_index'),
 ('vat_5_percent_with_rebates','high_income_surtax'),
 ('employer_health_exclusion_cap','high_income_surtax'),
 ('corporate_tax_rate','high_income_surtax'),
 ('corporate_tax_rate','itemized_deduction_limits'),
 ('medicare_advantage','medicare_site_neutral'),
 ('medicare_advantage','medicare_hi_financing'),
 ('medicare_site_neutral','medicare_hi_financing'))

@dataclass(frozen=True)
class EffectBound:
    low: Decimal
    high: Decimal
    source_url: str
    source_sha256: str
    basis: str
    matched_current_law: bool
    def __post_init__(self):
        if dec(self.low)>dec(self.high):raise ValueError('lower bound exceeds upper')
        if not self.source_url or len(self.source_sha256)!=64 or self.basis not in ('MODELED','EMPIRICAL','LEGISLATIVE_ZERO'):
            raise MissingEvidence('missing verifiable effect bound source')
        if not self.matched_current_law:raise MissingEvidence('source not matched to frozen baseline')

def robust_target_status(fy,policy_bounds:dict,interaction_bounds:dict,interest_bound:EffectBound|None=None):
    """Valid for supplied already-net improvement intervals, where all required
    interactions are covered. 'Provably sufficient' is conditional on the bounds;
    this routine does not certify a policy model or the bounds' scientific validity.
    """
    required=set(EXPECTED_IDS);ip=set(PAIRS)
    if set(policy_bounds)!=required or set(interaction_bounds)!=ip or interest_bound is None:
        return {'status':'NOT_DETERMINABLE','reason':'all 12 estimated policy bounds, 9 interaction bounds and net interest bound required','policy_count':len(policy_bounds),'interaction_count':len(interaction_bounds)}
    allbounds=[*policy_bounds.values(),*interaction_bounds.values(),interest_bound]
    lo=sum((dec(x.low) for x in allbounds),Decimal(0))
    hi=sum((dec(x.high) for x in allbounds),Decimal(0))
    gap=dec(next(x['static_improvement_required_bn'] for x in baseline_gap() if x['fy']==int(fy)))
    return {'status':('CONDITIONALLY_SUFFICIENT_IF_BOUNDS_VALID' if lo>=gap else 'CONDITIONALLY_INSUFFICIENT_IF_BOUNDS_VALID' if hi<gap else 'BOUND_INTERVAL_STRADDLES_TARGET'),
            'fy':int(fy),'required_bn':str(gap),'minimum_bn':str(lo),'maximum_bn':str(hi),
            'official_score':'NOT_AVAILABLE','note':'One-year static criterion only; no claim about joint enactment, trust fund solvency, or long-run sustainability'}

def one_year_debt_ratio_stability():
    """Frozen prior debt/current GDP and CBO other-financing diagnostics.
    This is NOT a 10-year reform-debt trajectory or dynamic policy score.
    """
    from pathlib import Path
    import csv
    from .v06_law import ROOT,BadSpecification
    with (ROOT/'data/verified_tables/cbo_budget_fy2026_2036_21_series.csv').open(newline='') as f:
        b={int(x['fy']):x for x in csv.DictReader(f)}
    with (ROOT/'data/verified_tables/cbo_gdp_fy2026_2036_official.csv').open(newline='') as f:
        g={int(x['fiscal_year']):dec(x['nominal_gdp_bn']) for x in csv.DictReader(f)}
    out=[]
    for y in range(2027,2037):
        prev=dec(b[y-1]['proj_debt_held_by_public'])
        current=dec(b[y]['proj_debt_held_by_public'])
        current_deficit=-dec(b[y]['proj_deficit_total'])
        other=dec(b[y]['proj_debt_change_other_financing'])
        if abs(prev+current_deficit+other-current)>Decimal('.0000001'):
            raise BadSpecification('CBO debt stock/deficit/other financing identity broken')
        allowed=current_deficit-(current-(prev*g[y]/g[y-1]))
        improvement=max(Decimal(0),current_deficit-allowed)
        out.append({'fy':y,'prior_public_debt_bn':str(prev),
         'prior_fy_gdp_bn':str(g[y-1]),'current_fy_gdp_bn':str(g[y]),
         'current_baseline_public_debt_bn':str(current),
         'baseline_deficit_bn':str(current_deficit),
         'other_financing_adjustment_bn':str(other),
         'deficit_ceiling_to_keep_prior_debt_gdp_ratio_bn':str(allowed),
         'frozen_one_year_debt_ratio_improvement_required_bn':str(improvement),
         'scope':'ONE_YEAR_FROZEN_PREVIOUS_DEBT_GDP_OTHER_FINANCING_NOT_10YR_SOLVENCY'})
    return out
