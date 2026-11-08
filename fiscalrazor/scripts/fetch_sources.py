#!/usr/bin/env python3
"""Fetch catalogued public data on network-connected Windows/macOS/Linux. Safe by default."""
import argparse,csv,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from fiscal_data.acquisition import acquire,inventory,registry,AcquisitionError

p=argparse.ArgumentParser(description='Acquire government research data with origin and hash receipts')
p.add_argument('--id',action='append',default=[],help='Verified data source identifier (repeatable)')
p.add_argument('--category',help='Acquire all directly downloaded datasets in this category')
p.add_argument('--all-direct',action='store_true',help='All direct sources. Potentially large; requires --allow-large')
p.add_argument('--allow-large',action='store_true',help='Allow up to 1 GiB per direct dataset; default 250 MB')
p.add_argument('--force',action='store_true',help='Replace old raw file with verified new download (same pinned blob where applicable)')
p.add_argument('--inventory',action='store_true',help='Print current raw data acquisition status only')
args=p.parse_args()
if args.inventory:
 for x in inventory():print(f"{x['id']:<34} {x['status']:<27} {x['bytes']:>12} {x['source_url']}")
 sys.exit(0)
reg=registry()
selected=set(args.id)
if args.category: selected|={x['id'] for x in reg.values() if x['category']==args.category and x['fetch_mode']=='download'}
if args.all_direct:
 if not args.allow_large:p.error('--all-direct requires --allow-large to acknowledge large official files')
 selected|={x['id'] for x in reg.values() if x['fetch_mode']=='download'}
if not selected:p.error('choose --id or --category, or --inventory')
status={}
for id in sorted(selected):
 try:
  result=acquire(id,max_bytes=1_000_000_000 if args.allow_large else 250_000_000,force=args.force)
  status[id]={'status':'PASS',**result};print('PASS',id,result['bytes'])
 except (AcquisitionError,KeyError) as e:
  status[id]={'status':'BLOCKED','reason':str(e)};print('BLOCKED',id,str(e),file=sys.stderr)
report=BASE/'results'/'acquisition_status.json';report.parent.mkdir(exist_ok=True,parents=True)
report.write_text(json.dumps(status,indent=2)+'\n')
sys.exit(1 if any(x['status']!='PASS' for x in status.values()) else 0)
