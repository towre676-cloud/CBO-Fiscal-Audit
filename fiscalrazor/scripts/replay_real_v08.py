#!/usr/bin/env python3
"""Real-data source replay and fiscal objectives; no unsourced national policy score.

The default path reports exact calculations from *published excerpts* while clearly
identifying raw-source acquisition as missing. --require-originals refuses to run
unless all 18 exact CBO files were downloaded and Git-blob-SHA-1 verified locally.
"""
from __future__ import annotations
from pathlib import Path
from decimal import Decimal as D
from collections import Counter
import argparse, csv, datetime as dt, json, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.primary_ingest_v08 import (OriginalSourceError,source_specs,verify_local,status,weighted_household_income_2026,soi_2023_aggregate_checks,final_outlay_checks,destination)
from fiscal_data.research_v08 import annual_objectives,evidence_completion,ALL_PAIR_INTERACTIONS
from fiscal_data.v07_calibration import parse_csv_bytes,strict_value_pivot,six_rank_agi_margins,jensen_top_group_floor
from fiscal_data.v06_law import EXPECTED_IDS

REPORTDIR=ROOT/'results/v08'
RAW=ROOT/'data/raw/v08_official_origins'

def csvwrite(path,rows):
    if not rows:raise OriginalSourceError('EMPTY_REPORT')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def putjson(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,default=str)+'\n',encoding='utf-8')

def expected_pins_receipts():
    return [{'id':k,'path':v['path'],'original_git_blob_sha1':v['expected_git_blob_sha1'],
       'expected_rows':v['expected_csv_rows'],'official_url':v['url'],
       'source_status':'REQUIRES_LOCAL_CRYPTOGRAPHIC_REPLAY'}
       for k,v in source_specs().items() if k.startswith('cbo_')]

def independently_check_full_cbo(raw,*,strict=False):
    st={x['id']:x for x in status(raw)}
    required=[x for x in st.values() if x['id'].startswith('cbo_')]
    missing=[x['id'] for x in required if x['state']!='VERIFIED_ORIGINAL_LOCAL']
    if missing:
       if strict: raise OriginalSourceError('COMPLETE_18_CBO_ORIGINALS_NOT_PRESENT: '+','.join(missing))
       return {'classification':'FULL_CBO_RAW_REPLAY_BLOCKED','missing_cbo_ids':missing,
               'verified_original_cbo_count':18-len(missing),'full_account_reconciliation':None}
    # Source files passed Git blob SHA1, UTF8, row counts independently of copied benchmark tables.
    load=lambda name:parse_csv_bytes(destination(raw,name,source_specs()[name]).read_bytes())
    ten=load('cbo_11');spending=load('cbo_17');fiscal=load('cbo_02');trust=load('cbo_13');tax=load('cbo_18');iit=load('cbo_15')
    out=final_outlay_checks(ten,spending)
    fiscalp=strict_value_pivot(fiscal)
    budgetp=strict_value_pivot(ten)
    for y in range(2026,2037):
        ys=f'FY{y}'
        fromgdp=D(fiscalp[(ys,'gdp')]); from_budget=D(budgetp[(ys,'proj_outlays_total')])
        if fromgdp<=0 or from_budget<=0:raise OriginalSourceError('BAD_CBO_GDP_OR_SPENDING')
    # Do not silently accept the nonunique FY/variable entries of trust-fund and tax series.
    def dups(rows):
        keys=Counter((r['date'],r['variable']) for r in rows)
        return sum(n-1 for n in keys.values() if n>1)
    a,b=dups(trust),dups(tax)
    if a!=116 or b!=11:raise OriginalSourceError('TRUST_OR_TAX_DUPLICATE_SEMANTICS_CHANGED')
    itp=strict_value_pivot(iit)
    if D(itp[('CY2036','rev_iit_returns_total')])!=D('180.5') or D(itp[('CY2036','rev_iit_agi')])!=D('26787.8'):
       raise OriginalSourceError('CBO_TAX_RETURNS_CALIBRATION_CHANGED')
    return {'classification':'CBO_18_ORIGINALS_CRYPTOGRAPHICALLY_VERIFIED_AND_AGGREGATES_REPLAYED',
      'originals':18,'source_rows':sum(int(x['expected_csv_rows']) for x in source_specs().values() if x.get('expected_csv_rows')),
      'annual_spending_account_replay':out,'duplicate_trust_keys':a,'duplicate_tax_keys':b,
      'CY2036_return_millions':str(itp[('CY2036','rev_iit_returns_total')]),
      'CY2036_AGI_billions':str(itp[('CY2036','rev_iit_agi')])}

def full_microdata_if_present(raw):
    out={}
    st={x['id']:x for x in status(raw)}
    if st['cps_asec_2026_csv']['state']=='VERIFIED_ORIGINAL_LOCAL':
      path=destination(raw,'cps_asec_2026_csv',source_specs()['cps_asec_2026_csv'])
      # Identify the real household CSV by its schema, never invent a ZIP member name.
      possible=[]
      with zipfile.ZipFile(path) as z:
        for member in z.namelist():
          if not member.lower().endswith('.csv'):continue
          with z.open(member) as f:
            header=f.readline().decode('utf-8-sig').strip()
          cols={c.upper() for c in next(csv.reader([header]))}
          if {'H_IDNUM','HSUP_WGT','HTOTVAL','HPCTCUT','H_HHTYPE'}<=cols:possible.append(member)
      if len(possible)!=1:raise OriginalSourceError('CPS_UNIQUE_HOUSEHOLD_CSV_NOT_IDENTIFIED')
      out['CPS_2026_household_income']=weighted_household_income_2026(path,possible[0])
    else:out['CPS_2026_household_income']={'status':'BLOCKED_MISSING_ACTUAL_MICRODATA'}
    if st['irs_soi_2023_zip_agi']['state']=='VERIFIED_ORIGINAL_LOCAL':
      path=destination(raw,'irs_soi_2023_zip_agi',source_specs()['irs_soi_2023_zip_agi'])
      out['IRS_2023_ZIP_AGI_aggregate']=soi_2023_aggregate_checks(path)
    else:out['IRS_2023_ZIP_AGI_aggregate']={'status':'BLOCKED_MISSING_ACTUAL_SOURCE'}
    if st['cms_medicare_2026_expanded']['state']=='VERIFIED_ORIGINAL_LOCAL':
      path=destination(raw,'cms_medicare_2026_expanded',source_specs()['cms_medicare_2026_expanded'])
      with zipfile.ZipFile(path) as z:out['CMS_2026_expanded_files']={
       'status':'REAL_ARCHIVE_RECEIPT_PRESENT_ACTUARIAL_REPLAY_STILL_REQUIRED',
       'members':[{'path':m.filename,'bytes':m.file_size} for m in z.infolist()]}
    else:out['CMS_2026_expanded_files']={'status':'BLOCKED_MISSING_ACTUAL_SOURCE'}
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',default=str(RAW))
    ap.add_argument('--require-originals',action='store_true',help='fail unless all 18 CBO source originals are locally hash-verified')
    a=ap.parse_args();raw=Path(a.root)
    annual=annual_objectives()
    csvwrite(REPORTDIR/'fiscal_objectives_2027_2036.csv',annual)
    csvwrite(REPORTDIR/'cbo_18_original_receipts_required.csv',expected_pins_receipts())
    requirements=evidence_completion(raw)
    putjson(REPORTDIR/'twelve_provision_source_gates.json',requirements)
    info=independently_check_full_cbo(raw,strict=a.require_originals)
    putjson(REPORTDIR/'raw_cbo_replay.json',info)
    micro=full_microdata_if_present(raw)
    putjson(REPORTDIR/'public_microdata_replay.json',micro)
    allstatus=status(raw)
    res={'as_of_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'status':'PUBLISHED_SOURCE_EXCERPT_MATH_ONLY_UNTIL_ORIGINAL_RAW_REPLAY',
      'total_source_entries':len(allstatus),'verified_original_sources':sum(s['state']=='VERIFIED_ORIGINAL_LOCAL' for s in allstatus),
      'raw_cbo_replay':info['classification'],'twelve_reform_provisions':len(EXPECTED_IDS),
      'provision_year_estimates_established':0,'all_pairwise_interactions_required_per_year':len(ALL_PAIR_INTERACTIONS),
      'evidence': 'Official joint CBO/JCT/SSA/CMS score and nationally calibrated household reform incidence NOT_ESTABLISHED',
      'FY2036_objectives':annual[-1]}
    putjson(REPORTDIR/'verification_receipt_v08.json',res)
    print(json.dumps(res,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
