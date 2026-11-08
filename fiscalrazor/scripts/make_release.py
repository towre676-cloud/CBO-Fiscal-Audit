#!/usr/bin/env python3
"""Create self-verifying, deterministic FiscalRazor ZIP with canonical SHA-256 manifest.

Run check_everything.py first. Never includes acquired raw confidential or large
survey files; those are locally retained with separately minted SHA receipts.
"""
from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=Path(sys.argv[1] if len(sys.argv)>1 else ROOT.parent/'FiscalRazor_v0.4.0.zip').resolve()
SKIP={'.pyc','.pyo'}

def allowed(path):
    rel=path.relative_to(ROOT)
    return path.is_file() and path!=ROOT/'MANIFEST_SHA256.json' and not any(p in ('__pycache__','.git','.pytest_cache','raw') for p in rel.parts) and path.suffix not in SKIP

files=sorted((p for p in ROOT.rglob('*') if allowed(p)),key=lambda p:p.relative_to(ROOT).as_posix())
manifest={'algorithm':'sha256','files':[{'relative_path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,
                                          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if ROOT==TARGET or ROOT in TARGET.parents:sys.exit('Output ZIP must not be inside the project directory')
TARGET.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files+[ROOT/'MANIFEST_SHA256.json']:
        arc=f'{ROOT.name}/{p.relative_to(ROOT).as_posix()}'
        zi=zipfile.ZipInfo(arc,date_time=(1980,1,1,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=(0o100644<<16)
        z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('RELEASE',TARGET,'sha256',hashlib.sha256(TARGET.read_bytes()).hexdigest(),
      'project_files',len(files)+1,'bytes',TARGET.stat().st_size)
