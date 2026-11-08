"""First-order policy CAPACITY bounds with all assumptions explicit.

No claim of national revenue, static JCT score, household incidence, or solvency.
February 2026 CBO annual FY PCE; gross ceiling only for a levy restricted to
that fixed PCE universe. Not a ceiling for all possible legislative VAT bases.
"""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
import csv, hashlib, json
from fiscal_data.research_v08 import annual_objectives
from fiscal_data.primary_ingest_v08 import verify_local, destination, source_specs, OriginalSourceError
ROOT = Path(__file__).resolve().parents[2]
REF = ROOT/'data/v09/cbo_fy_pce_2027_2036_source_excerpt.csv'
GIT_SHA = 'e0799d7972696a65823e5d90cf36486d21903520'

def _read_excerpts():
    with REF.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if len(rows)!=10:raise OriginalSourceError('CBO_PCE_EXPECTED_TEN_ANNUAL_VALUES')
    observed={}
    for r in rows:
        y=int(r['fiscal_year']); value=D(r['pce_nominal_billions'])
        if y in observed or r['source_git_blob_sha1']!=GIT_SHA or r['source_variable']!='pce' or value<=0:
            raise OriginalSourceError('CBO_PCE_EXCERPT_INVARIANT_FAILED')
        observed[y]=value
    if set(observed)!=set(range(2027,2037)):raise OriginalSourceError('CBO_PCE_INCOMPLETE')
    return observed

def original_cbo_pce_if_present(raw_root):
    # Accept ONLY a fully verified original CBO source; never overwrite excerpt
    # because an incomplete or manually edited CSV happens to have matching rows.
    verify_local('cbo_02',raw_root)
    p=destination(raw_root,'cbo_02',source_specs()['cbo_02'])
    from fiscal_data.v07_calibration import parse_csv_bytes, strict_value_pivot
    data=strict_value_pivot(parse_csv_bytes(p.read_bytes()))
    return {y:D(data[(f'FY{y}','pce')]) for y in range(2027,2037)}

def run(*,raw_root=None,require_originals=False,vat_rate='0.05',rebate_fraction='0.20'):
    rate=D(str(vat_rate)); rebate=D(str(rebate_fraction))
    if not rate.is_finite() or not rebate.is_finite() or not D(0)<=rate<=D(1) or not D(0)<=rebate<=D(1):
        raise OriginalSourceError('VAT_RATE_OR_REBATE_OUTSIDE_ZERO_ONE')
    pce=_read_excerpts();cls='OFFICIAL_GIT_SOURCE_EXCERPT_NOT_FULL_ORIGINAL'
    if raw_root is not None:
        try:
            original=original_cbo_pce_if_present(raw_root)
            if original!=pce:raise OriginalSourceError('CBO_PCE_EXCERPT_DISAGREES_WITH_VERIFIED_ORIGINAL')
            cls='LOCAL_RAW_SOURCE_GIT_SHA1_VERIFIED'
        except OriginalSourceError as e:
            # Missing is an admissible excerpt-only case; a present corrupt file
            # must always fail, even in exploratory mode.
            p=destination(raw_root,'cbo_02',source_specs()['cbo_02'])
            if require_originals or p.exists():raise
    elif require_originals:
        raise OriginalSourceError('CBO_ORIGINAL_PCE_NOT_LOCALLY_VERIFIED')
    out=[]
    for o in annual_objectives():
        y=int(o['fy']); gross=pce[y]*rate; rb=gross*rebate; net=gross-rb
        gap=D(o['three_percent_gap_bn']); balance=gap-net
        out.append({'fy':y, 'cbo_pce_fy_bn':str(pce[y]),
            'statutory_tax_exclusive_rate':str(rate), 'rebate_fraction_of_gross':str(rebate),
            'gross_all_pce_mechanical_bn':str(gross), 'reserve_for_rebates_bn':str(rb),
            'net_after_rebate_mechanical_bn':str(net),
            'three_percent_deficit_gap_bn':str(gap),
            'gap_less_mechanical_net_bn':str(balance),
            'fraction_of_target_covered_mechanically':str(net/gap if gap>0 else D(1)),
            'minimum_gross_all_pce_rate_to_close_gap_at_current_rebate_share':
              str(gap/(pce[y]*(D(1)-rebate)) if rebate<D(1) else D('Infinity')),
            'source_integrity':cls,
            'interpretation':'STYLIZED_FIXED_BASE_ALL_PCE_CAPACITY_NOT_VAT_REVENUE_ESTIMATE'})
    return out

def write(path,**kwargs):
    rows=run(**kwargs);Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows


def mechanical_taxable_fraction_scenarios(*, fractions=('0.50','0.60','0.70','0.80','0.90','1.00'),
                                          vat_rate='0.05',rebate_fraction='0.20'):
    """Fixed-baseline sensitivity only. Fractions are analyst-selected HYPOTHESES.

    The real VAT tax base requires BEA product-level mapping, statutory exemptions,
    purchases by government and visitors, and enforcement evidence. None are assumed.
    """
    from decimal import Decimal
    rows=run(vat_rate=vat_rate,rebate_fraction=rebate_fraction)
    output=[]
    for f0 in fractions:
        f=Decimal(str(f0))
        if not f.is_finite() or f<=0 or f>1:raise OriginalSourceError('HYPOTHETICAL_TAXABLE_FRACTION_OUT_OF_RANGE')
        for row in rows:
            base=Decimal(row['cbo_pce_fy_bn'])*f
            net=base*Decimal(str(vat_rate))*(Decimal(1)-Decimal(str(rebate_fraction)))
            gap=Decimal(row['three_percent_deficit_gap_bn'])
            need=gap/(base*(Decimal(1)-Decimal(str(rebate_fraction)))) if Decimal(str(rebate_fraction))<1 else Decimal('Infinity')
            output.append({'fy':row['fy'],'hypothetical_taxable_share_of_pce':str(f),
                'hypothetical_taxable_consumption_bn':str(base),
                'hypothetical_net_receipts_bn':str(net),
                'three_percent_target_gap_bn':str(gap),
                'remaining_gap_bn':str(gap-net),
                'minimum_static_rate_to_close_gap_at_rebate_share':str(need),
                'classification':'STYLIZED_MECHANICAL_NOT_OFFICIAL_OR_ESTIMATED_TAX_BASE'})
    return output
