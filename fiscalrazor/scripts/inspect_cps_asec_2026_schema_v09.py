#!/usr/bin/env python3
"""Discover *actual* Census 2026 ASEC CSV fields from verified local original ZIP.

The proposed mappings are a DATA DISCOVERY REPORT, not a reviewed mapping.
Do not auto-admit a statistic merely because 160 similarly named columns appear.
"""
import argparse,csv,datetime as dt,io,json,re,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.primary_ingest_v08 import verify_local,destination,source_specs,OriginalSourceError

def inspect(root,output):
 receipt=verify_local('cps_asec_2026_csv',root)
 archive=destination(root,'cps_asec_2026_csv',source_specs()['cps_asec_2026_csv'])
 with zipfile.ZipFile(archive) as z:
  result=[]
  for info in z.infolist():
   if info.is_dir() or not info.filename.lower().endswith('.csv'):continue
   with z.open(info) as f:
    header=next(csv.reader(io.TextIOWrapper(f,encoding='utf-8-sig',newline='')),[])
   named={h.upper():h for h in header}
   candidates=[h for h in header if re.search(r'(REPW|REPLICATE|RWT)',h,re.I)]
   result.append({'archive_member':info.filename,'uncompressed_bytes':info.file_size,
     'columns':len(header),'household_weight':'HSUP_WGT' in named,
     'household_total_income':'HTOTVAL' in named,'has_household_type':'H_HHTYPE' in named,
     'replicate_candidate_count':len(candidates),'replicate_candidate_names':candidates,
     'status':'CANDIDATE_COLUMNS_REQUIRE_CODEBOOK_AND_UNIVERSE_REVIEW'})
 if not result:raise OriginalSourceError('CPS_ORIGINAL_HAS_NO_CSV_MEMBERS')
 report={'verified_original_sha256':receipt['sha256'],
  'verified_source_url':receipt['source_url'],'observed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
  'mode':'DISCOVERY_ONLY_CANNOT_AUTHORIZE_UNIVERSE_OR_WEIGHT_SCALE',
  'members':result,'must_review':'2026 ASEC data dictionary and official replicate-weight usage instructions'}
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source-root',default='data/raw/v08_official_origins')
 p.add_argument('--output',default='results/v09/cps_asec_2026_schema_discovery.json')
 a=p.parse_args()
 path=Path(a.source_root);path=path if path.is_absolute() else ROOT/path
 out=Path(a.output);out=out if out.is_absolute() else ROOT/out
 r=inspect(path,out)
 print(json.dumps({'verified_original_sha256':r['verified_original_sha256'],
  'members':[(x['archive_member'],x['columns'],x['replicate_candidate_count']) for x in r['members']],
  'status':r['mode']},indent=2))
 return 0
if __name__=='__main__':sys.exit(main())
