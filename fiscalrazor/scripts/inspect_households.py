#!/usr/bin/env python3
"""CPS/CBO file inventory only: do NOT pretend raw Census data are tax scenario outputs."""
import argparse,csv,io,json,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('input',help='Official Census ASEC ZIP or CSV to inspect')
p.add_argument('--max-records',type=int,default=0,help='0 for metadata only, >0 for non-sensitive preview count without values')
a=p.parse_args()
path=Path(a.input)
if not path.exists():p.error('No data file. Download the raw official CPS ASEC from the source registry.')
files=[]
if zipfile.is_zipfile(path):
 with zipfile.ZipFile(path) as z:
  for info in z.infolist():
   if info.is_dir():continue
   if info.filename.startswith('/') or '..' in Path(info.filename).parts:raise ValueError('ZIP path traversal refused')
   d={'name':info.filename,'compressed_size':info.compress_size,'uncompressed_size':info.file_size}
   if info.filename.lower().endswith('.csv'):
    with z.open(info) as f:
     header=f.readline().decode('utf-8-sig',errors='replace').rstrip('\r\n')
    d['header_fields']=next(csv.reader([header]))
   files.append(d)
else:
 with open(path,'r',encoding='utf-8-sig',newline='') as f:fields=next(csv.reader([f.readline()]))
 files=[{'name':path.name,'header_fields':fields,'bytes':path.stat().st_size}]
print(json.dumps({'source_path':str(path),'files':files,'warning':'Header inspection only; no household tax score computed'},indent=2))
