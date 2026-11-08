#!/usr/bin/env python3
"""Compute genuine CPS household mean income with 160 replicate weights.

Execute only after acquiring the original 2026 Census ZIP and after checking
`verify_local`. A mapping file must specify the exact household CSV member,
160 documented replicate-weight columns, and their implied decimal scale.
Do not guess their names or claim sample adequacy before source checks.
"""
from pathlib import Path
import argparse,csv,io,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.primary_ingest_v08 import verify_local,source_specs,destination,OriginalSourceError
from fiscal_data.v09_survey import streaming_weighted_mean_with_replicates,SurveyEvidenceError

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source-root',default='data/raw/v08_official_origins')
 p.add_argument('--mapping',required=True,help='reviewed JSON mapping with exact CSV member and 160 documented replicate columns')
 p.add_argument('--out',default='results/v09/cps_household_mean_with_sdr.json')
 a=p.parse_args();root=Path(a.source_root);root=root if root.is_absolute() else ROOT/root
 rec=verify_local('cps_asec_2026_csv',root)
 spec=source_specs()['cps_asec_2026_csv'];f=destination(root,'cps_asec_2026_csv',spec)
 m=json.loads(Path(a.mapping).read_text())
 required={'household_member','replicate_fields','replicate_scale','full_weight_scale','income_field','interview_status_field','interview_status_value'}
 if not required<=m.keys():raise SurveyEvidenceError('INCOMPLETE_EXPLICIT_SOURCE_MAPPING')
 # Require documented weight scales BEFORE opening or scanning a huge archive.
 if str(m['replicate_scale'])!=str(m['full_weight_scale']):
  raise SurveyEvidenceError('REPLICATE_WEIGHT_SCALE_REQUIRES_EXPLICIT_TRANSFORMATION')
 if len(m['replicate_fields'])!=160 or len(set(m['replicate_fields']))!=160:
  raise SurveyEvidenceError('DOCUMENTED_160_REPLICATE_COLUMNS_REQUIRED')
 with zipfile.ZipFile(f) as z:
  member=m['household_member']
  if member not in z.namelist():raise SurveyEvidenceError('MAPPED_CSV_MEMBER_NOT_PRESENT')
  with z.open(member) as data:
   rows=csv.DictReader(io.TextIOWrapper(data,encoding='utf-8-sig',newline=''))
   stats=streaming_weighted_mean_with_replicates(rows,value_field=m['income_field'],
     full_weight_field='HSUP_WGT',replicate_fields=m['replicate_fields'],
     weight_scale=m['full_weight_scale'],filter_field=m['interview_status_field'],
     filter_value=m['interview_status_value'],origin_verified=True)
 stats['census_original_sha256']=rec['sha256'];stats['source_url']=rec['source_url']
 stats['admission_state']='CENSUS_CSV_ORIGINAL_AND_160_DOCUMENTED_REPLICATE_MEASURES'
 o=Path(a.out);o=o if o.is_absolute() else ROOT/o;o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(stats,sort_keys=True,indent=2)+'\n')
 print(json.dumps({k:v for k,v in stats.items() if k not in ('replicate_estimates',)},indent=2))
 return 0
if __name__=='__main__':sys.exit(main())
