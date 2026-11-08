# FiscalRazor Data Foundation — works in a recent Windows 11 PowerShell, Python >=3.11 installed.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$env:PYTHONPATH = Join-Path $root 'src'
python scripts/build_catalog.py
python scripts/check_everything.py
Write-Host 'Local reproducibility checked. For downloads on an internet-connected PC:'
Write-Host 'python scripts/fetch_sources.py --id cbo_budget_10yr'
Write-Host 'python scripts/fetch_sources.py --category households --allow-large'
Write-Host 'python scripts/fetch_sources.py --all-direct --allow-large'
