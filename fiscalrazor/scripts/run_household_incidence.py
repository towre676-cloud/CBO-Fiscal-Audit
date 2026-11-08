#!/usr/bin/env python3
"""Produce *real* household distribution only from independently sourced, documented outputs.
Refuses empty/missing provenance and never fabricates source household records.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.distribution import load_records,analyze,summarize_subpopulations,export

p=argparse.ArgumentParser(description='Distribution on real household-level modeled outcomes')
p.add_argument('--households',type=Path,required=True,help='CSV with 11 required columns, each row a unique household')
p.add_argument('--metadata',type=Path,required=True,help='JSON with dataset and model provenance')
p.add_argument('--out',type=Path,default=BASE/'results'/'household_distribution.csv')
a=p.parse_args()
if not a.metadata.exists():p.error('Missing source/model metadata; no household result')
m=json.loads(a.metadata.read_text())
required=['population_source_url','population_edition','reference_year','policy_simulator','policy_simulator_version','tax_calendar_year','policy_rule_source','source_records_sha256','weight_scaling_documentation','tax_unit_to_household_crosswalk']
missing=[key for key in required if not m.get(key)]
if missing:p.error('Missing provenance fields: '+', '.join(missing))
if not a.households.is_file():p.error('Household-level policy-model output not found; no result')
realsha=hashlib.sha256(a.households.read_bytes()).hexdigest()
if realsha!=m['source_records_sha256']:p.error('HOUSEHOLD_DATA_SHA256_MISMATCH')
if str(m['tax_calendar_year'])!=str(m['reference_year']) and not m.get('calibration_method'):
 p.error('Projection-year vs source-year mismatch; a calibrated population aging/inflation method is required')
rows=load_records(a.households)
result=analyze(rows)
a.out.parent.mkdir(parents=True,exist_ok=True)
export(result,a.out)
subgroups=a.out.with_name(a.out.stem+'_subgroups.csv')
export(summarize_subpopulations(rows),subgroups)
record={'state':'INDEPENDENT_DESCRIPTIVE_DISTRIBUTION_NOT_AGENCY_SCORE','input_sha256':realsha,'metadata':m,'analyzed_household_records':len(rows),'output_csv':str(a.out)}
a.out.with_suffix('.receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print('ANALYZED',len(rows),'households; output',a.out,'agency score: NO')
