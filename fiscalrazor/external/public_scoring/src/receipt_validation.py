"""Require local source + code digests before accepting a 'reviewed' score row.

This is an INTEGRITY gate, not proof of estimate correctness nor accreditation
by any government body. Full source blobs MUST be independently downloaded;
no such blobs are shipped with the current package.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from .fiscalrazor import ROOT

HEX_SHA=re.compile(r'^[0-9a-f]{64}$')


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def row_fingerprint(row):
    """Canonical receipt binding excludes review flag and receipt location."""
    keys={k:v for k,v in row.items() if k not in ('reproduction_receipt','review_status')}
    return hashlib.sha256(json.dumps(keys,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def _allowed_file(filepath, prefix):
    if not isinstance(filepath,str) or not filepath.strip():return None
    try:
        path=(ROOT/filepath).resolve(strict=True)
        parent=(ROOT/prefix).resolve()
        if not path.is_relative_to(parent) or not path.is_file():return None
        return path
    except (OSError,ValueError):return None


def validate_replay_receipt(row):
    receipt=_allowed_file(row.get('reproduction_receipt',''),'receipts')
    if receipt is None or receipt.suffix!='.json':
        return ['Reviewed impact requires an existing JSON replay receipt inside receipts/']
    try:
        j=json.loads(receipt.read_text(encoding='utf8'))
    except (OSError,ValueError):
        return ['Unreadable or invalid replay receipt JSON']
    errors=[]
    if not isinstance(j,dict):return ['Replay receipt must be JSON object']
    for key,val in [('source_url',row['source_url']),('baseline_vintage','2026-02'),('row_sha256',row_fingerprint(row))]:
        if j.get(key)!=val:errors.append(f'Replay receipt {key} does not bind to submitted row')
    if j.get('independent_review_complete') is not True or not str(j.get('reviewer','')).strip():
        errors.append('Replay receipt lacks recorded independent reviewer completion')
    for file_key,hash_key,folder in [('source_original_path','source_original_sha256','downloads'),
            ('calculation_code_path','calculation_code_sha256','scripts')]:
        path=_allowed_file(j.get(file_key,''),folder)
        digest=j.get(hash_key)
        if path is None or not HEX_SHA.fullmatch(str(digest)) or sha256(path)!=digest:
            errors.append(f'Replay receipt {file_key} missing or SHA256 mismatch')
    return errors
