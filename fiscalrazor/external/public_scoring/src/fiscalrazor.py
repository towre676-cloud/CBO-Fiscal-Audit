"""Public-source fiscal-score audit; never claims to reproduce official CBO/JCT/SSA/CMS.

All budget amounts are nominal fiscal-year billions. SSA option amounts are
calendar-year PERCENTAGES of current-law OASDI taxable payroll, never dollars.
"""
from __future__ import annotations
import csv
import json
import argparse
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CBO_SRC = 'https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/budget/ten_year_budget/annual_fy_2026-02.csv'
CBO_GDP_SRC = 'https://raw.githubusercontent.com/US-CBO/cbo-data/main/data/economic/historical_economic/annual_fy_2026-02.csv'


def _rows(name):
    with (ROOT / 'data' / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def baseline_rows():
    rows = _rows('cbo_2026_02_baseline_excerpt.csv')
    assert [int(r['year']) for r in rows] == list(range(2026, 2037)), 'Wrong FY range'
    return rows


def gdp_rows():
    rows = _rows('cbo_2026_02_fy_nominal_gdp_excerpt.csv')
    if [int(r['year']) for r in rows] != list(range(2026, 2037)):
        raise ValueError('Wrong CBO FY nominal GDP range')
    return rows


def audit_baseline():
    """Check accounting identities against exact CBO rounded CSV excerpt."""
    problems = []
    gdp = {int(r['year']):D(r['nominal_gdp_billion']) for r in gdp_rows()}
    for r in baseline_rows():
        y = int(r['year'])
        rev, outlay, deficit = map(D, (r['revenue_billion'],r['outlays_billion'],r['deficit_billion']))
        interest, primary = D(r['net_interest_billion']), D(r['primary_deficit_billion'])
        if abs(rev - outlay - deficit) > D('0.002'):
            problems.append(f'FY{y}: revenue - outlays != deficit')
        if abs(deficit + interest - primary) > D('0.002'):
            problems.append(f'FY{y}: total - interest != primary deficit')
        debt, pct = D(r['debt_public_billion']),D(r['debt_public_gdp_pct'])
        if debt <= 0 or pct <= 0:
            problems.append(f'FY{y}: positive debt and percent required')
        if gdp.get(y, D(0)) <= 0:
            problems.append(f'FY{y}: missing or nonpositive GDP')
        elif abs(debt / gdp[y] * D(100) - pct) > D('0.00055'):
            problems.append(f'FY{y}: debt/GDP percentage differs from published rounded ratio')
    return problems


def audit_jct():
    rows = _rows('jct_2026_corporate_illustration.csv')
    values = [D(r['ten_year_billion']) for r in rows]
    if len(values) != 10 or values[0] != 350 or sum(values) != 180:
        return ['JCT illustrative breakdown does not reconcile $350B -> $180B']
    if any(r['status'] != 'JCT_ILLUSTRATIVE_NOT_OFFICIAL_SCORE' for r in rows):
        return ['JCT illustration lost its NON-OFFICIAL metadata']
    return []


def ssa_option_series(option_id):
    rows = [r for r in _rows('ssa_2026_option_benchmarks.csv') if r['option_id'] == option_id]
    if len(rows) != 11:
        raise ValueError('Unknown or incomplete SSA option benchmark')
    return [(int(r['calendar_year']), D(r['change_annual_balance_pct_of_current_law_taxable_payroll'])) for r in rows]


def audit_ssa():
    rows = _rows('ssa_2026_option_benchmarks.csv')
    ids = sorted(set(r['option_id'] for r in rows))
    problems = []
    if len(ids)!=3 or len(rows)!=33:
        problems.append('SSA benchmark inventory unexpected')
    for k in ids:
        vals = ssa_option_series(k)
        if [y for y,v in vals] != list(range(2026,2037)):
            problems.append('SSA years wrong for '+k)
        if any(D(v)<0 for _,v in vals):
            problems.append('Unexpected negative recorded annual balance for '+k)
        if any('CY_NOT_a_FY_dollar_score' not in r['status'] for r in rows if r['option_id']==k):
            problems.append('Missing basis marker for '+k)
    byid = {k:dict(ssa_option_series(k)) for k in ids}
    if byid['E2.5_high_earner_tax_250k_no_benefit_credit'][2036] != D('2.53'):
        problems.append('SSA E2.5 2036 anchor mismatch')
    if byid['E1.10_oasdi_rate_plus_0p1_per_year_2028_2037'][2036] != D('0.86'):
        problems.append('SSA E1.10 2036 anchor mismatch')
    if byid['B1.2_progressive_price_indexing_2033_30th_pct'][2036] != D('0.01'):
        problems.append('SSA B1.2 2036 anchor mismatch')
    return problems


def full_cbo_csv_check(csv_path: Path):
    """Cross-check local transcription against downloaded full official long-format CBO CSV.

    Rejects wrong headers, missing year/variable coverage, and incorrect values.
    Requires exact matching values, not ±1% tolerances.
    """
    mapping = {
        'revenue_billion':'proj_rev_total',
        'outlays_billion':'proj_outlays_total',
        'deficit_billion':'proj_deficit_total',
        'net_interest_billion':'proj_outlays_net_interest',
        'primary_deficit_billion':'proj_primary_deficit',
        'debt_public_billion':'proj_debt_held_by_public',
        'debt_public_gdp_pct':'proj_debt_held_by_public_gdp_share',
    }
    lookup = {}
    with csv_path.open(newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f)
        if not {'date','variable','value'}.issubset(rd.fieldnames or []):
            raise ValueError('Not an official-format CBO long-format CSV')
        for r in rd:
            if r['variable'] in mapping.values() and r['date'].startswith('FY'):
                k = (int(r['date'][2:]), r['variable'])
                if k in lookup:
                    raise ValueError(f'Duplicate CBO key: {k}')
                lookup[k] = D(r['value'])
    mismatches=[]
    for r in baseline_rows():
        y=int(r['year'])
        for column,var in mapping.items():
            if (y,var) not in lookup:
                mismatches.append(f'Missing FY{y} {var}')
            elif lookup[y,var] != D(r[column]):
                mismatches.append(f'FY{y} {var}: transcribed {r[column]}, official {lookup[y,var]}')
    return mismatches


def fiscal_year_gap_path(target_gdp_share=D('0.03')):
    """Published CBO fiscal-year arithmetic, not a legislative scoring result."""
    if target_gdp_share < 0 or target_gdp_share > 1:
        raise ValueError('Invalid target share; use 0.03 for 3%')
    gdps={int(r['year']):D(r['nominal_gdp_billion']) for r in gdp_rows()}
    out=[]
    for r in baseline_rows():
        year=int(r['year']); gdp=gdps[year];deficit=-D(r['deficit_billion'])
        target=gdp*target_gdp_share
        out.append(dict(year=year,
            nominal_gdp_billion=str(gdp), baseline_deficit_billion=str(deficit),
            baseline_deficit_pct_gdp=str((deficit/gdp*100).quantize(D('.0001'))),
            deficit_at_target_billion=str(target.quantize(D('.01'))),
            gap_to_target_billion=str((deficit-target).quantize(D('.01'))),
            status='BASELINE_ARITHMETIC_ONLY_NOT_A_POLICY_SCORE'))
    return out


def target_2036():
    entry=next(x for x in fiscal_year_gap_path() if x['year']==2036)
    return dict(year=2036, nominal_gdp_billion=entry['nominal_gdp_billion'],
        baseline_deficit_billion=str(-D(entry['baseline_deficit_billion'])),
        target_deficit_3pct_gdp_billion=entry['deficit_at_target_billion'],
        required_reduction_before_policy_feedback_billion=entry['gap_to_target_billion'],
        status='baseline_target_only_NOT_A_POLICY_SCORE',
        denominator='direct official CBO FY2036 nominal GDP variable gdp, vintage 2026-02')


def full_cbo_gdp_csv_check(csv_path: Path):
    """Cross-check all 11 GDP excerpt values against the original official CBO CSV."""
    lookup={}
    with csv_path.open(newline='',encoding='utf-8-sig') as f:
        rdr=csv.DictReader(f)
        if not {'date','variable','value'}.issubset(rdr.fieldnames or []):
            raise ValueError('Not an official-format CBO economic long-format CSV')
        for r in rdr:
            if r['variable']=='gdp' and r['date'].startswith('FY'):
                y=int(r['date'][2:])
                if y in lookup: raise ValueError(f'Duplicate GDP year FY{y}')
                lookup[y]=D(r['value'])
    problems=[]
    for r in gdp_rows():
        year=int(r['year']); transcribed=D(r['nominal_gdp_billion'])
        if year not in lookup: problems.append(f'Missing GDP FY{year}')
        elif lookup[year] != transcribed:
            problems.append(f'GDP FY{year} differs: excerpt {transcribed}, CBO {lookup[year]}')
    return problems


def score_status():
    provisions=json.loads((ROOT/'data'/'provisions.json').read_text(encoding='utf8'))
    return dict(total_provisions=len(provisions),scored=sum(p['status']!='UNSCORED' for p in provisions),
        unscored=[p['id'] for p in provisions if p['status']=='UNSCORED'],
        combined_score='NOT_ESTABLISHED',
        missing='legislative text, tax microsimulation, actuarial reproductions, disaggregated expenditure policy effects, behavioral interactions, debt service and distribution')


def audit():
    problems = audit_baseline()+audit_jct()+audit_ssa()
    return dict(tested='CBO budget/GDP excerpt internal accounting; JCT illustrative sum; SSA benchmark transcription anchors',
        problem_count=len(problems),problems=problems,
        external_fresh_full_dataset_verification=False,
        reason='Official full CSVs must first be downloaded and passed to --check-official-cbo and --check-official-gdp.')


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['baseline','targets','status','audit','ssa','jct','check-official-cbo','check-official-gdp'])
    ap.add_argument('--id',help='SSA option id for ssa command')
    ap.add_argument('--path',type=Path,help='Full original CBO FY2026-02 CSV for checksum-equivalent value check')
    a=ap.parse_args(argv)
    if a.command=='baseline': data={'FY2036':next(r for r in baseline_rows() if r['year']=='2036'), 'target':target_2036()}
    elif a.command=='targets': data={'target_share':0.03,'years':fiscal_year_gap_path()}
    elif a.command=='status': data=score_status()
    elif a.command=='audit': data=audit()
    elif a.command=='ssa':
        if not a.id: ap.error('ssa requires --id (see data/ssa_2026_option_benchmarks.csv)')
        data={'option':a.id,'basis':'calendar year, change in OASDI annual balance as PERCENT OF CURRENT LAW TAXABLE PAYROLL',
              'values':[(y,str(v)) for y,v in ssa_option_series(a.id)],'combine_as_federal_FY_savings':False}
    elif a.command=='jct': data={'illustration_ten_year_billion':sum(D(r['ten_year_billion']) for r in _rows('jct_2026_corporate_illustration.csv')),
        'method':'JCT worked TEACHING EXAMPLE, not official legislative score'}
    else:
        if not a.path: ap.error(f'{a.command} requires --path downloaded.csv')
        if a.command=='check-official-cbo':
            issues=full_cbo_csv_check(a.path); source=CBO_SRC
        else:
            issues=full_cbo_gdp_csv_check(a.path);source=CBO_GDP_SRC
        data={'matched':not issues,'issues':issues,'source':source}
    print(json.dumps(data,indent=2,default=str))
    if a.command in ('audit','check-official-cbo','check-official-gdp') and (data.get('problem_count',0) or data.get('issues')):
        raise SystemExit(1)

if __name__=='__main__':
    main()
