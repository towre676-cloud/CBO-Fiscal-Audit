#!/usr/bin/env python3
"""Validate packaging boundaries and exact benchmarks without network access."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    legacy=ROOT/'fiscalrazor'
    if not (legacy/'SHA256_MANIFEST_V11.txt').exists():
        sys.exit('Missing intact historic source distribution')
    if not (ROOT/'publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv').exists():
        sys.exit('Missing publication table')
    # Run inherited historical manifest BEFORE any test/analysis that may regenerate outputs.
    p=subprocess.run([sys.executable,'scripts/verify_manifest_v11.py'],cwd=legacy,text=True,capture_output=True)
    if p.returncode:
        print(p.stdout,p.stderr,file=sys.stderr);sys.exit(1)
    print(p.stdout.strip())
    sys.path.insert(0,str(ROOT))
    from publication.fiscal_accounting import annual_targets, EvidenceError
    from decimal import Decimal as D
    rows=annual_targets()
    if len(rows)!=10 or D(rows[-1]['three_percent_deficit_target_gap_bn'])!=D('1714.022728075'):
        sys.exit('Unexpected benchmark arithmetic')
    # Prevent accidental publication of raw government archives, personal microdata or credentials.
    unsafe=[]
    for f in ROOT.rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(ROOT)
        if '__pycache__' in rel.parts or f.suffix.lower() in {'.pyc','.pyo'}: continue
        if any(x in rel.parts for x in ['.git','.venv','raw']):unsafe.append(str(rel))
        if f.suffix.lower() in {'.pem','.key','.p12'}:unsafe.append(str(rel))
    if unsafe:sys.exit('Unsafe paths in publishable tree: '+repr(unsafe[:8]))
    print(json.dumps({'status':'PUBLICATION_REPLAY_PASSED','cbo_reference_years':len(rows),
                      'v11_historical_archive':'HASH_VERIFIED','raw_original_government_files_embedded':0,
                      'policy_joint_score':'NOT_ESTABLISHED'},indent=2))
