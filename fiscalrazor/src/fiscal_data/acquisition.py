"""Fail-closed fetching and provenance for official public datasets.
Run on an INTERNET-CONNECTED machine. Any locally supplied file can also be admitted
under the exact same hash/structure gate. An HTTP success is NOT a policy score.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import urllib.error

BASE=Path(__file__).resolve().parents[2]
CATALOG=BASE/'data'/'source_catalog.json'
RECEIPTS=BASE/'data'/'acquisition_receipts.json'
class AcquisitionError(RuntimeError): pass

def registry():
    data=json.loads(CATALOG.read_text())
    entries=data['entries']
    if len({r['id'] for r in entries})!=len(entries): raise AcquisitionError('duplicate source id')
    return {x['id']:x for x in entries}

def sha256_bytes(data:bytes)->str: return hashlib.sha256(data).hexdigest()

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\x00'+data).hexdigest()

def admit_bytes(entry,data:bytes):
    if not data: raise AcquisitionError('EMPTY_DATA_REJECTED')
    expected=entry.get('expected_git_blob_sha1')
    if expected and git_blob_sha1(data)!=expected:
        raise AcquisitionError('SOURCE_BLOB_MISMATCH '+entry['id'])
    # A source path with CSV extension cannot be a login page or cloud CDN block page.
    target=(entry.get('download_url') or '').split('?')[0].lower()
    if target.endswith(('.csv','.txt')) and (data[:200].lstrip().lower().startswith(b'<!doctype html') or data[:200].lstrip().lower().startswith(b'<html')):
        raise AcquisitionError('HTML_RETURNED_INSTEAD_OF_DATA')
    if target.endswith('.zip') and not data.startswith(b'PK\x03\x04'):
        raise AcquisitionError('ZIP_MAGIC_MISMATCH')
    if target.endswith('.gz') and not data.startswith(b'\x1f\x8b'):
        raise AcquisitionError('GZIP_MAGIC_MISMATCH')
    if target.endswith('.xlsx') and not data.startswith(b'PK\x03\x04'):
        raise AcquisitionError('XLSX_MAGIC_MISMATCH')
    if target.endswith('.pdf') and not data.startswith(b'%PDF'):
        raise AcquisitionError('PDF_MAGIC_MISMATCH')
    return sha256_bytes(data)

def raw_target(entry):
    if entry['fetch_mode']!='download': raise AcquisitionError('No verified direct endpoint for '+entry['id'])
    # Catalog provides no relative path for non-CBO official sources; sandbox them by id and URL basename.
    relative=entry.get('local_path') or ('data/raw/'+entry['id']+'/'+Path(entry['download_url'].split('?')[0]).name)
    dest=(BASE/relative).resolve()
    if BASE not in dest.parents: raise AcquisitionError('path traversal detected')
    return dest

def _read_receipts():
    if not RECEIPTS.exists(): return {'source_entries':{}}
    return json.loads(RECEIPTS.read_text())

def verify_local(id):
    entry=registry()[id]
    path=raw_target(entry)
    if not path.is_file(): raise AcquisitionError('NOT_MATERIALIZED')
    data=path.read_bytes()
    sha=admit_bytes(entry,data)
    receipt=_read_receipts()['source_entries'].get(id)
    if not receipt or receipt.get('sha256')!=sha:
        raise AcquisitionError('MISSING_OR_MISMATCHED_DOWNLOAD_RECEIPT')
    return {'id':id,'bytes':len(data),'sha256':sha,'local_path':str(path.relative_to(BASE))}

def acquire(id,max_bytes=250_000_000,force=False,retries=2):
    entry=registry().get(id)
    if not entry: raise AcquisitionError('Unknown catalog source: '+id)
    if entry['fetch_mode']!='download': raise AcquisitionError('No direct, verified URL: '+id)
    dest=raw_target(entry)
    if dest.exists() and not force:return verify_local(id)
    url=entry['download_url']; data=None
    for n in range(retries+1):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'FiscalRazor-Research/0.2 (public datasets; provenance-locked)','Accept':'*/*'})
            with urllib.request.urlopen(request,timeout=80) as response:
                clen=response.headers.get('Content-Length')
                if clen is not None and int(clen)>max_bytes: raise AcquisitionError('EXCEEDS_MAX_BYTES '+id)
                chunks=[]; read=0
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    read+=len(block)
                    if read>max_bytes: raise AcquisitionError('EXCEEDS_MAX_BYTES '+id)
                    chunks.append(block)
                data=b''.join(chunks)
            break
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            if n==retries:raise AcquisitionError('NETWORK_FAILED '+id+': '+str(e)) from e
            time.sleep(1+n)
    sha=admit_bytes(entry,data)
    dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_name(dest.name+'.download')
    tmp.write_bytes(data)
    tmp.replace(dest)
    receipts=_read_receipts()
    receipts['source_entries'][id]={'source_url':url,'sha256':sha,'expected_git_blob_sha1':entry.get('expected_git_blob_sha1'),
                                    'size_bytes':len(data),'acquired_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                                    'path':str(dest.relative_to(BASE)),'state':'MATERIALIZED_VERIFIED_BYTES'}
    RECEIPTS.write_text(json.dumps(receipts,sort_keys=True,indent=2)+'\n')
    return verify_local(id)

def inventory():
    rows=[]
    for id,entry in registry().items():
        try: p=verify_local(id);status='MATERIALIZED_VERIFIED_BYTES'
        except AcquisitionError: p={};status='NOT_ACQUIRED' if entry['fetch_mode']=='download' else 'LANDING_OR_API_ONLY'
        rows.append({'id':id,'category':entry['category'],'agency':entry['agency'], 'status':status,'bytes':p.get('bytes',0),'source_url':entry['download_url'] or entry['landing_url']})
    return rows
