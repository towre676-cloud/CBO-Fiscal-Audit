"""Refuses research scenario totals until EVERY policy-year and interaction-year reviewed."""
import sys, argparse, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.score_gate import audit_candidate

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('impacts',type=Path)
 p.add_argument('interactions',type=Path)
 args=p.parse_args()
 result=audit_candidate(args.impacts,args.interactions)
 print(json.dumps(result,indent=2))
 if not result['gate_passed']:raise SystemExit(1)
if __name__=='__main__':main()
