"""Build a deterministic, integrity-checked v0.6.0 source release."""
from pathlib import Path
import hashlib,json,zipfile,shutil
BASE=Path(__file__).resolve().parents[1]
ZIP=BASE.parent/'FiscalRazor_v0.6.0_Legislation_And_Research_2026-11-06.zip'
MANIFEST=BASE/'MANIFEST_SHA256.json'
for p in BASE.rglob('__pycache__'):shutil.rmtree(p,ignore_errors=True)
for p in BASE.rglob('*.pyc'):p.unlink(missing_ok=True)
# Remove a superseded first-attempt runner log whose expected count reflected v0.5.
(BASE/'results/v06/inherited_v05_replay.log').unlink(missing_ok=True)
paths=[p for p in sorted(BASE.rglob('*')) if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts and p.suffix!='.pyc']
items=[{'relative_path':p.relative_to(BASE).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
manifest={'algorithm':'sha256','version':'0.6.0','description':'All included files except this manifest; status of government original bytes remains UNACQUIRED','files':items}
MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
allfiles=[*paths,MANIFEST]
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in sorted(allfiles):
  arc=Path(BASE.name)/p.relative_to(BASE)
  z.write(p,arcname=arc.as_posix())
with zipfile.ZipFile(ZIP) as z:
 bad=z.testzip()
 if bad:raise RuntimeError('ZIP CRC failure: '+bad)
 print('ZIP_ENTRIES',len(z.namelist()))
print('ZIP',ZIP,'BYTES',ZIP.stat().st_size,'SHA256',hashlib.sha256(ZIP.read_bytes()).hexdigest(),'MANIFEST_FILES',len(paths))
