"""Admission status over ALL sources; hashes actual local bytes when present.
Does not use excerpts to pretend original archives exist.
"""
from __future__ import annotations
import sys,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.acquisition import inventory,verify_local,AcquisitionError,registry

def run():
    rows=inventory();out=ROOT/'results/v06';out.mkdir(parents=True,exist_ok=True)
    names=['id','category','agency','status','bytes','source_url']
    with (out/'source_acquisition_status_2026_11_06.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows([{k:r.get(k,'') for k in names} for r in rows])
    report={'sources':len(rows),'materialized_originals':sum(r['status']=='MATERIALIZED_VERIFIED_BYTES' for r in rows),
      'not_acquired_direct':sum(r['status']=='NOT_ACQUIRED' for r in rows),
      'landing_or_API_only':sum(r['status']=='LANDING_OR_API_ONLY' for r in rows),
      'fail_closed':'NO_ACQUIRED_SOURCE_MAY_BE_CLAIMED_FROM_EXCERPTS_OR_WEB_PAGE_METADATA',
      'acquisition_script':'python scripts/acquire_priority_v06.py --group cbo_core',
      'source_of_truth':'data/source_catalog.json; data/acquisition_receipts.json if original byte download succeeds'}
    (out/'source_gate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
