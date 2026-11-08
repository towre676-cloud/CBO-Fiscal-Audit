#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}/src"
python scripts/build_catalog.py
python scripts/check_everything.py
printf '\nAcquire full public data on an internet-connected machine with:\n'
printf 'PYTHONPATH=src python scripts/fetch_sources.py --all-direct --allow-large\n'
