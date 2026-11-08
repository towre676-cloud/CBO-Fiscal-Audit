# Run on Windows 11 PowerShell; Python 3.11+ installed, internet access required.
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
py -3 scripts/acquire_real_federal_v08.py --fetch-all-cbo
if ($LASTEXITCODE -ne 0) {throw 'CBO original-source download/verification failed'}
py -3 scripts/replay_real_v08.py --require-originals
if ($LASTEXITCODE -ne 0) {throw 'CBO original-source calibration failed'}
py -3 scripts/acquire_real_federal_v08.py --id cps_asec_2026_csv --id cps_asec_2026_replicates --id cms_medicare_2026_expanded --id irs_soi_2023_zip_agi
if ($LASTEXITCODE -ne 0) {throw 'One or more public-use downloads failed'}
py -3 scripts/replay_real_v08.py --require-originals
if ($LASTEXITCODE -ne 0) {throw 'Census/IRS/CMS replay failed'}
$env:PYTHONPATH = 'src'
py -3 -m unittest discover -s tests -q
if ($LASTEXITCODE -ne 0) {throw 'FiscalRazor unit tests failed'}
