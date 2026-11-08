"""Discover & optionally download ALL files in CBO's public catalog for a vintage.

Usage (networked machine):
 python scripts/fetch_sources.py --download cbo_catalog
 python scripts/fetch_cbo_catalog_all.py --list
 python scripts/fetch_cbo_catalog_all.py --fetch --vintage 2026-02

No file is advertised as a policy estimate; checksums recorded on download.
"""
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from urllib.request import Request,urlopen
import argparse, hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
RAW='https://raw.githubusercontent.com/US-CBO/cbo-data/main/'

def catalog_entries(catalog:dict,vintage='2026-02'):
    out=[]
    for ds in catalog.get('datasets',[]):
        for dist in ds.get('distribution',[]):
            if dist.get('vintage')!=vintage:continue
            rel=dist.get('downloadURL')
            if not isinstance(rel,str) or rel.startswith('/') or '://' in rel or ':' in rel or '\\' in rel or '..' in PurePosixPath(rel).parts:
                continue
            if not (rel.endswith('.csv') or rel.endswith('.json')):continue
            out.append(dict(dataset=ds.get('identifier'),vintage=vintage,relative_path=rel,
                url=RAW+quote(rel,safe='/'),media_type=dist.get('mediaType'),file_type=dist.get('file_type')))
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--catalog',type=Path,default=ROOT/'downloads/cbo_catalog.json')
    p.add_argument('--vintage',default='2026-02')
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--list',action='store_true')
    g.add_argument('--fetch',action='store_true')
    p.add_argument('--cap-per-file-mb',type=int,default=80)
    p.add_argument('--timeout',type=int,default=120)
    args=p.parse_args()
    if not args.catalog.exists():p.error('Missing official catalog. First run: python scripts/fetch_sources.py --download cbo_catalog')
    entries=catalog_entries(json.loads(args.catalog.read_text(encoding='utf8')),args.vintage)
    print(f'CBO catalog vintage {args.vintage}: {len(entries)} published distributions')
    if args.list:
        for e in entries:print(f"{e['dataset']} / {e['file_type']} : {e['relative_path']}")
        return
    dest=ROOT/'downloads'/('cbo_vintage_'+args.vintage);dest.mkdir(parents=True,exist_ok=True)
    manifest=[];had_failure=False
    for e in entries:
        path=dest/e['relative_path'];path.parent.mkdir(parents=True,exist_ok=True)
        h=hashlib.sha256();bytes_in=0
        try:
            with urlopen(Request(e['url'],headers={'User-Agent':'FiscalRazor-public-evidence-research/0.1'}),timeout=args.timeout) as src, path.open('wb') as out:
                if src.status!=200:raise ValueError('non-200 status '+str(src.status))
                while True:
                    chunk=src.read(256*1024)
                    if not chunk:break
                    bytes_in+=len(chunk)
                    if bytes_in>args.cap_per_file_mb*1024*1024:raise ValueError('cap exceeded')
                    out.write(chunk);h.update(chunk)
            if not bytes_in:raise ValueError('empty file')
            e.update(status='downloaded',sha256=h.hexdigest(),bytes=bytes_in)
            print('OK',e['relative_path'],bytes_in)
        except Exception as err:
            path.unlink(missing_ok=True);e.update(status='ERROR',error=str(err));had_failure=True
            print('ERROR',e['relative_path'],str(err))
        manifest.append(e)
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    if had_failure:raise SystemExit(1)

if __name__=='__main__':main()
