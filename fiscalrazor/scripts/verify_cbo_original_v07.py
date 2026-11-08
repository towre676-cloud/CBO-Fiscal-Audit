#!/usr/bin/env python3
"""Reconcile complete 18-file local CBO 2026-02 vintage, verify original Git bytes."""
import sys,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v07_calibration import pins,validate_source,SourceGateError
p=argparse.ArgumentParser();p.add_argument('--source-root',default='downloads/cbo_2026_02_original');p.add_argument('--list',action='store_true');p.add_argument('--require-complete',action='store_true');args=p.parse_args()
base=Path(args.source_root);base=base if base.is_absolute() else ROOT/base
entries=[]
for x in pins():
 file=base/x['path']
 if args.list:
  print(f"{x['expected_csv_rows']:>7} {x['git_blob_sha1']} {x['source_url']}")
  continue
 if not file.is_file():entries.append({'path':x['path'],'status':'MISSING_RAW_BYTES'});continue
 try:entries.append({'status':'ORIGINAL_BYTES_VERIFIED',**validate_source(file,x)})
 except SourceGateError as exc:entries.append({'path':x['path'],'status':'FAIL', 'error':str(exc)})
if args.list:sys.exit(0)
passcount=sum(x['status']=='ORIGINAL_BYTES_VERIFIED' for x in entries)
status='PASS_ORIGINAL_18_FILES' if passcount==len(pins()) else 'INCOMPLETE_OR_INVALID_SOURCE_VINTAGE'
report={'status':status,'raw_files_verified':passcount,'raw_files_required':len(pins()),'entries':entries,
        'joint_reform_score':'NOT_ESTABLISHED','national_household_distribution':'NOT_ESTABLISHED'}
print(json.dumps(report,indent=2))
if args.require_complete and status!='PASS_ORIGINAL_18_FILES':sys.exit(2)
if any(x['status']=='FAIL' for x in entries):sys.exit(3)
