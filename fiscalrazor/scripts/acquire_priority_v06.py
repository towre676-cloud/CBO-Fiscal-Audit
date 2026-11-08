"""Connected-host safe downloader; no placeholder bytes or silently assumed success.

Usage:
  python scripts/acquire_priority_v06.py --list
  python scripts/acquire_priority_v06.py --group cbo_core
  python scripts/acquire_priority_v06.py --group household --max-mb 220
  python scripts/acquire_priority_v06.py --group actuarial
  python scripts/acquire_priority_v06.py --group all --max-mb 500
"""
import sys,argparse,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.acquisition import registry,acquire,inventory,AcquisitionError

GROUPS={
'cbo_core':['cbo_budget_10yr','cbo_fy_gdp_2026_02_raw','cbo_spending_detail','cbo_revenue_detail','cbo_trust_funds','cbo_budget_history','cbo_tax_parameters'],
'actuarial':['ssa_oasdi_2026_excel','cms_trustees_2026'],
'household':['cps_asec_2026_csv','cps_asec_2026_repwgt','cps_asec_2026_layout','cbo_household_research_2023'],
'macro':['cbo_econ_calendar','cbo_econ_fiscal','cbo_population','cbo_mortality','cbo_fertility']
}
GROUPS['all']=list(dict.fromkeys(sum(GROUPS.values(),[])))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--group',choices=GROUPS,default='cbo_core');parser.add_argument('--list',action='store_true');parser.add_argument('--max-mb',type=int,default=200);parser.add_argument('--force',action='store_true');parser.add_argument('--inventory',action='store_true');args=parser.parse_args()
 if args.list:
  print(json.dumps(GROUPS,indent=2));return
 if args.inventory:
  rows=inventory();print(json.dumps(rows,indent=2));return
 receipts=[]
 for id in GROUPS[args.group]:
  try:r=acquire(id,max_bytes=args.max_mb*1024*1024,force=args.force);receipts.append({'id':id,'status':'SUCCESS','sha256':r['sha256'],'bytes':r['bytes']});print('ACQUIRED',id,r['bytes'],r['sha256'])
  except (AcquisitionError,Exception) as err:receipts.append({'id':id,'status':'FAILED','error':str(err)});print('NOT_ACQUIRED',id,err,file=sys.stderr)
 out=ROOT/'results/v06/acquisition_run_results.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(receipts,indent=2)+'\n')
 if any(r['status']=='FAILED' for r in receipts):sys.exit(1)
if __name__=='__main__':main()
