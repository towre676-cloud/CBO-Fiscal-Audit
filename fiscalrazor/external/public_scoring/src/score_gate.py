"""Fail-closed, provenance-controlled interface for *research* primary-budget scenarios.

Cannot issue an official estimate or a net-interest-adjusted score. Does NOT
accept an arbitrary global behavior 'haircut' or let unscored line-items be zero.
"""
from __future__ import annotations
import csv, json
from pathlib import Path
from decimal import Decimal as D, InvalidOperation
from collections import defaultdict
from .fiscalrazor import ROOT
from .receipt_validation import validate_replay_receipt

FISCAL_YEARS = set(range(2027,2037))
REQUIRED_FIELDS = {'provision_id','fiscal_year','accounting_key','delta_receipts_billion',
  'delta_noninterest_outlays_billion','source_url','reproduction_receipt','review_status','baseline_vintage','measurement_basis'}
VALID_REVIEW = 'independently_reproduced_and_reviewed'
INTERACTION_FIELDS = {'provision_a','provision_b','fiscal_year','delta_primary_balance_billion',
    'source_url','reproduction_receipt','review_status','baseline_vintage'}


def read_csv(path, fields):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not fields.issubset(set(reader.fieldnames or [])):
            raise ValueError('missing required columns: '+ ', '.join(sorted(fields - set(reader.fieldnames or []))))
        return list(reader)


def pair_id(a,b):
    if a==b: raise ValueError('An interaction needs two distinct provisions')
    return tuple(sorted([a,b]))


def audit_candidate(impact_path, interaction_path):
    """Returns problems and safe conditional direct/primary impact WITHOUT NET INTEREST.

    A completely reviewed ledger can yield a *research* primary cash-flow estimate,
    but it cannot be mislabeled as a combined CBO/JCT/SSA/CMS score.
    """
    provisions=json.loads((ROOT/'data/provisions.json').read_text(encoding='utf8'))
    names={p['id'] for p in provisions}
    edges=json.loads((ROOT/'data/interaction_registry.json').read_text(encoding='utf8'))
    required_pairs={pair_id(*edge) for edge in edges}
    errors=[]; direct=defaultdict(D); interactions=defaultdict(D)
    seen_account=set(); provision_coverage=set(); pair_coverage=set()
    impacts=read_csv(impact_path,REQUIRED_FIELDS)
    ints=read_csv(interaction_path,INTERACTION_FIELDS)
    for i,r in enumerate(impacts,2):
        p=r['provision_id'];y=int(r['fiscal_year']) if r['fiscal_year'].isdigit() else -1
        if p not in names or y not in FISCAL_YEARS: errors.append(f'impacts row {i}: unknown policy/year');continue
        provision_coverage.add((p,y))
        key=(y,r['accounting_key'].strip())
        if not key[1] or key in seen_account: errors.append(f'impacts row {i}: duplicate/empty account-year key')
        seen_account.add(key)
        if r['review_status'] != VALID_REVIEW or r['baseline_vintage']!='2026-02':
            errors.append(f'impacts row {i}: not independently reviewed against frozen 2026-02 baseline')
        if r['measurement_basis']!='federal_fy_nominal_billions_cash':
            errors.append(f'impacts row {i}: tax liability/CY/BA cannot be entered as FY cash flows')
        if not r['source_url'].startswith('https://') or not r['reproduction_receipt'].strip():
            errors.append(f'impacts row {i}: source and replay receipt missing')
        else:
            errors.extend(f'impacts row {i}: {reason}' for reason in validate_replay_receipt(r))
        try: amount = D(r['delta_receipts_billion'])-D(r['delta_noninterest_outlays_billion'])
        except InvalidOperation:errors.append(f'impacts row {i}: missing/nonnumeric dollar effect');continue
        if not amount.is_finite(): errors.append(f'impacts row {i}: nonfinite effect');continue
        direct[y]+=amount
    for i,r in enumerate(ints,2):
        a,b=r['provision_a'],r['provision_b']
        y=int(r['fiscal_year']) if r['fiscal_year'].isdigit() else -1
        try:pair=pair_id(a,b)
        except ValueError: errors.append(f'interactions row {i}: not pair');continue
        if a not in names or b not in names or y not in FISCAL_YEARS:
            errors.append(f'interactions row {i}: unknown policy/year');continue
        key=(pair,y)
        if key in pair_coverage: errors.append(f'interactions row {i}: duplicated pair-year')
        pair_coverage.add(key)
        if pair not in required_pairs: errors.append(f'interactions row {i}: undeclared model cross-effect')
        if (r['review_status']!=VALID_REVIEW or r['baseline_vintage']!='2026-02'
                or not r['source_url'].startswith('https://') or not r['reproduction_receipt'].strip()):
            errors.append(f'interactions row {i}: missing provenance/review')
        if r['source_url'].startswith('https://') and r['reproduction_receipt'].strip():
            errors.extend(f'interactions row {i}: {reason}' for reason in validate_replay_receipt(r))
        try: value=D(r['delta_primary_balance_billion'])
        except InvalidOperation:errors.append(f'interactions row {i}: nonnumeric');continue
        if not value.is_finite():errors.append(f'interactions row {i}: nonfinite');continue
        interactions[y]+=value
    expected={(p,y) for p in names for y in FISCAL_YEARS}
    missing=expected-provision_coverage
    if missing: errors.append(f'missing {len(missing)} provision-year effects, cannot silently set to zero')
    missing_edges={(edge,y) for edge in required_pairs for y in FISCAL_YEARS}-pair_coverage
    if missing_edges: errors.append(f'missing {len(missing_edges)} interaction-year effects')
    result=dict(gate_passed=not errors,problems=errors,num_policy_rows=len(impacts),
        num_interaction_rows=len(ints),debt_service='NOT_ESTIMATED',
        official_agency_status='NOT_AN_OFFICIAL_SCORE',
        combined_federal_net_savings='NOT_ESTABLISHED')
    if not errors:
        result['conditional_research_primary_balance_impact_billion']={str(y):str(direct[y]+interactions[y]) for y in sorted(FISCAL_YEARS)}
    return result
