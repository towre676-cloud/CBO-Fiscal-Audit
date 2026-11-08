#!/usr/bin/env python3
"""Verify content manifest (no timestamps, no source-dependent environment details)."""
from pathlib import Path
import hashlib,json,sys
BASE=Path(__file__).resolve().parents[1]
MANIFEST=BASE/'MANIFEST_SHA256.json'
if not MANIFEST.is_file():sys.exit('FAIL: missing MANIFEST_SHA256.json')
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
if manifest['algorithm']!='sha256':sys.exit('FAIL: unsupported hash algorithm')
missing=[];bad=[]
for item in manifest['files']:
    p=(BASE/item['relative_path']).resolve()
    if BASE not in p.parents or not p.is_file():missing.append(item['relative_path']);continue
    b=p.read_bytes()
    if len(b)!=item['size_bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']:bad.append(item['relative_path'])
if missing or bad:
    print('MISSING',missing,'INVALID',bad)
    sys.exit(1)
print('PASS',len(manifest['files']),'manifest entries; verified content')
