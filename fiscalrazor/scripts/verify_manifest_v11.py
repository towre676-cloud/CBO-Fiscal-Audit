"""Verify that SHA256_MANIFEST_V11.txt exactly inventories packaged files."""
from pathlib import Path
import hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'SHA256_MANIFEST_V11.txt'
EXCL={'SHA256_MANIFEST_V11.txt'}

def run():
    if not MAN.is_file():raise RuntimeError('manifest missing')
    expected={}
    for l in MAN.read_text(encoding='utf-8').splitlines():
        if not l.strip():continue
        if '  ' not in l:raise RuntimeError('bad manifest row')
        h,rel=l.split('  ',1)
        if len(h)!=64 or not rel or rel in expected:raise RuntimeError('bad hash or duplicate path')
        expected[rel]=h
    present={p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and p.name not in EXCL}
    missing=set(expected)-set(present);surprise=set(present)-set(expected)
    if missing or surprise:raise RuntimeError(f'file-set mismatch missing={sorted(missing)[:8]} unexpected={sorted(surprise)[:8]}')
    for name,path in present.items():
        h=hashlib.sha256(path.read_bytes()).hexdigest()
        if h != expected[name]:raise RuntimeError('hash mismatch: '+name)
    print(f'V11 SHA-256 verified {len(present)} tracked files')
    return len(present)

if __name__=='__main__':
    try:run()
    except Exception as e:print(e,file=sys.stderr);sys.exit(1)
