#!/usr/bin/env python3
"""Acquire real official source files (CBO 18, Census, BLS, CMS, IRS) when network permits.

No synthetic substitution. BLS 2025 direct URLs must be resolved from live page.
All origins and receipt status listed in results/v08/original_sources_status.json.
"""
from __future__ import annotations
from pathlib import Path
import argparse,csv,json,sys,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.primary_ingest_v08 import source_specs,download_source,status,verify_local,OriginalSourceError

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--root',default='data/raw/v08_official_origins',help='destination root')
 p.add_argument('--list',action='store_true')
 p.add_argument('--verify',action='store_true')
 p.add_argument('--fetch-all-cbo',action='store_true')
 p.add_argument('--fetch-public-use',action='store_true')
 p.add_argument('--fetch-available-public',action='store_true',help='Fetch all public entries with grounded direct URLs; leave unresolved BLS paths explicitly BLOCKED')
 p.add_argument('--id',action='append',default=[])
 p.add_argument('--report',default='results/v08/original_sources_status.json')
 a=p.parse_args();base=Path(a.root);base=base if base.is_absolute() else ROOT/base
 specs=source_specs();requested=list(dict.fromkeys(a.id + ([k for k in specs if k.startswith('cbo_')] if a.fetch_all_cbo else []) + ([k for k in specs if not k.startswith('cbo_')] if a.fetch_public_use else []) + ([k for k,v in specs.items() if not k.startswith('cbo_') and v.get('url')] if a.fetch_available_public else [])))
 for name in requested:
  if name not in specs:raise SystemExit('Unknown source '+name)
 if a.list:
  for name,s in specs.items():print(name, s.get('url') or '[USE AGENCY DOWNLOAD PAGE]', s['access_type'],sep=' | ')
 for name in requested:
  try:
   if a.verify:r=verify_local(name,base)
   else:r=download_source(name,base)
   print('VERIFIED', name, r['sha256'],r['bytes'],flush=True)
  except (OriginalSourceError,OSError,Exception) as e:
   print('FAILED',name,type(e).__name__,str(e)[:400],file=sys.stderr,flush=True)
 results=status(base)
 report=Path(a.report);report=report if report.is_absolute() else ROOT/report
 report.parent.mkdir(parents=True,exist_ok=True)
 obj={'reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_root':str(base),
      'source_origins':len(results),'verified_originals':sum(r['state']=='VERIFIED_ORIGINAL_LOCAL' for r in results),
      'total_cbo_required':18,'verified_cbo':sum(r['state']=='VERIFIED_ORIGINAL_LOCAL' and r['id'].startswith('cbo_') for r in results),
      'official_joint_score':'NOT_AVAILABLE','national_household_incidence':'NOT_CALCULATED',
      'sources':results}
 report.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 print('STATUS',obj['verified_originals'],'/',obj['source_origins'],'VERIFIED ORIGINAL FILES')
 if requested and any(s['id'] in requested and s['state']!='VERIFIED_ORIGINAL_LOCAL' for s in results):return 2
 return 0
if __name__=='__main__':sys.exit(main())
