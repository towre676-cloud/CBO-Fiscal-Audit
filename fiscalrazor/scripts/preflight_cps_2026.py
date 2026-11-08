#!/usr/bin/env python3
"""2026 Census ASEC genuine-archive status and exact row-count preflight.

To validate all record counts pass three actual member paths after --list.
"""
import argparse,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.cps_preflight import inspect_archive,CPSDataError
p=argparse.ArgumentParser()
p.add_argument('--zip',default=str(BASE/'data/raw/cps_asec_2026_csv/asecpub26csv.zip'))
p.add_argument('--household-file');p.add_argument('--family-file');p.add_argument('--person-file')
p.add_argument('--list',action='store_true',help='list members without claiming any row-count validation')
a=p.parse_args()
mp=[a.household_file,a.family_file,a.person_file]
if any(mp) and not all(mp):p.error('all three exact filenames required')
try:
 result=inspect_archive(a.zip,dict(zip(('household','family','person'),mp)) if all(mp) else None)
 print(json.dumps(result,indent=2))
except (CPSDataError,FileNotFoundError) as e:
 sys.exit('SOURCE_NOT_VERIFIED: '+str(e))
