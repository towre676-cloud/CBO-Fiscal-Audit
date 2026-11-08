$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:PYTHONPATH = 'src'
& python scripts/acquire_real_federal_v08.py --fetch-all-cbo
if ($LASTEXITCODE -ne 0) { throw 'CBO download or verification failed' }
& python scripts/replay_real_v08.py --require-originals
if ($LASTEXITCODE -ne 0) { throw 'CBO original replay failed' }
& python scripts/acquire_real_federal_v08.py --fetch-available-public
if ($LASTEXITCODE -ne 0) { throw 'Public-use acquisition failed; consult receipt before proceeding' }
& python scripts/replay_v09.py --require-originals
if ($LASTEXITCODE -ne 0) { throw 'Strict source gate failed' }
& python scripts/inspect_cps_asec_2026_schema_v09.py
if ($LASTEXITCODE -ne 0) { throw 'Census verified-source schema discovery failed' }
& python -m unittest discover -s tests -q
if ($LASTEXITCODE -ne 0) { throw 'FiscalRazor test suite failed' }
