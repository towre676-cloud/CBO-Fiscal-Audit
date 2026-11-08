#!/usr/bin/env python3
"""FiscalRazor v0.9: source-aware baseline, conditional VAT diagnostics, admission inventory.

No fake original bytes, official score or national household estimates.
"""
from __future__ import annotations
from pathlib import Path
import sys,csv,json,datetime as dt,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v09_capacity import write,run,mechanical_taxable_fraction_scenarios
from fiscal_data.primary_ingest_v08 import status,OriginalSourceError,source_specs
from fiscal_data.research_v08 import annual_objectives,evidence_completion,ALL_PAIR_INTERACTIONS
from fiscal_data.v06_law import EXPECTED_IDS


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source-root',default='data/raw/v08_official_origins')
    a.add_argument('--require-originals',action='store_true')
    a.add_argument('--output-root',default='results/v09')
    args=a.parse_args()
    raw=Path(args.source_root);raw=raw if raw.is_absolute() else ROOT/raw
    out=Path(args.output_root);out=out if out.is_absolute() else ROOT/out
    out.mkdir(parents=True,exist_ok=True)
    sources=status(raw)
    verified=[x for x in sources if x['state']=='VERIFIED_ORIGINAL_LOCAL']
    v_cbo=[x for x in verified if x['id'].startswith('cbo_')]
    if args.require_originals and len(v_cbo)!=18:
        raise OriginalSourceError('REQUIRES_ALL_EIGHTEEN_CBO_ORIGINAL_SOURCE_BYTES_WITH_GIT_HASHES')
    rows=write(out/'cbo_fy_pce_all_base_vat_capacity_2027_2036.csv', raw_root=raw,
               require_originals=args.require_originals)
    with (out/'hypothetical_vat_base_fraction_sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
        scenarios=mechanical_taxable_fraction_scenarios()
        w=csv.DictWriter(f,fieldnames=list(scenarios[0]));w.writeheader();w.writerows(scenarios)
    gates=evidence_completion(raw)
    names=[x['policy_id'] for x in gates]
    if len(names)!=12 or set(names)!=set(EXPECTED_IDS):raise OriginalSourceError('TWELVE_PROVISIONS_NOT_PRESERVED')
    if len(ALL_PAIR_INTERACTIONS)!=66:raise OriginalSourceError('SIXTY_SIX_PAIRWISE_GRAPH_CHANGED')
    # Persist the full inventory, not only successful sources. Non-CBO URLs with
    # HTTPS receipts remain weaker than CBO's publisher-Git-pinned originals.
    (out/'source_admission_status.json').write_text(json.dumps(sources,indent=2,sort_keys=True)+'\n')
    (out/'provision_admission_status.json').write_text(json.dumps(gates,indent=2,sort_keys=True)+'\n')
    d=rows[-1]
    report={
     'as_of_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
     'vintage':'CBO_FEBRUARY_2026_FROZEN',
     'original_public_sources_verified_locally':len(verified),
     'cbo_full_vintage_verified_locally':len(v_cbo)==18,
     'cbo_original_files_verified':len(v_cbo),
     'cbo_files_required':18,
     'government_original_source_definitions':len(sources),
     'registered_provisions':len(EXPECTED_IDS),
     'all_pairwise_interactions':len(ALL_PAIR_INTERACTIONS),
     'FY2036_fiscal_gap_bn':d['three_percent_deficit_gap_bn'],
     'FY2036_CBO_projected_PCE_bn':d['cbo_pce_fy_bn'],
     'FY2036_5pct_all_PCE_gross_mechanical_bn':d['gross_all_pce_mechanical_bn'],
     'FY2036_5pct_all_PCE_less_20pct_rebate_mechanical_bn':d['net_after_rebate_mechanical_bn'],
     'FY2036_5pct_all_PCE_mechanical_gap_remaining_bn':d['gap_less_mechanical_net_bn'],
     'FY2036_all_PCE_rate_to_close_gap_mechanically_at_20pct_rebate':d['minimum_gross_all_pce_rate_to_close_gap_at_current_rebate_share'],
     'cbo_pce_evidence_status':d['source_integrity'],
     'official_CBO_JCT_combined_score':'NOT_ISSUED',
     'official_SSA_OASDI_joint_score':'NOT_ISSUED',
     'official_CMS_HI_joint_score':'NOT_ISSUED',
     'national_household_reform_incidence':'NOT_ESTABLISHED',
     'status':'SOURCE_PINNED_SELECTED_CBO_BASELINE_MATH_AND_EXECUTABLE_IMPORTERS_ONLY',
     'zero_fabricated_microdata':'REQUIRED',
     'explicit_limit':'These are mathematical benchmarks; NOT independently estimated tax receipts or policy effects.'}
    (out/'evidence_status.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True,indent=2));return 0
if __name__=='__main__':sys.exit(main())
