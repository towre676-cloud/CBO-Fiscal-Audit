#!/usr/bin/env python3
"""Census ASEC SDR variance of a measured estimate and 160 measured replicates.

Requires explicit provenance JSON for source weights and estimation methodology.
Does not supply microdata, household tax model, or an official policy result.
"""
import argparse,hashlib,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.survey import load_asec_replicate_estimates,census_asec_sdr
p=argparse.ArgumentParser(description='CPS ASEC survey variance from 160 real replicate estimates')
p.add_argument('--replicates',type=Path,required=True)
p.add_argument('--full-estimate',required=True,help='Exact full-sample estimate, same statistic as replicates')
p.add_argument('--metadata',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
if not a.replicates.is_file() or not a.metadata.is_file():p.error('DATA_AND_PROVENANCE_REQUIRED')
m=json.loads(a.metadata.read_text())
required=('survey','survey_year','source_url','official_weights_file_sha256',
          'statistic_definition','replicate_estimators_method','replicate_estimate_csv_sha256')
if any(not m.get(k) for k in required):p.error('MISSING_REPLICATE_PROVENANCE: '+', '.join(k for k in required if not m.get(k)))
if m['survey']!='CPS_ASEC' or str(m['survey_year'])!='2026':p.error('SOURCE_EDITION_MISMATCH')
sha=hashlib.sha256(a.replicates.read_bytes()).hexdigest()
if sha!=m['replicate_estimate_csv_sha256']:p.error('REPLICATE_ESTIMATE_SHA256_MISMATCH')
result=census_asec_sdr(a.full_estimate,load_asec_replicate_estimates(a.replicates))
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps({'state':'SAMPLED_ESTIMATE_WITH_VERIFIED_INPUT_PROVENANCE_NOT_OFFICIAL_SCORE',
     'statistics':{k:str(v) for k,v in result.items()},'provenance':m},indent=2)+'\n')
print('SDR variance created:',a.out)
