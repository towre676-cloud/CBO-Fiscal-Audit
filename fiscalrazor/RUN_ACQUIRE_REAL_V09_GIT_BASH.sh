#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH=src
python scripts/acquire_real_federal_v08.py --fetch-all-cbo
python scripts/replay_real_v08.py --require-originals
python scripts/acquire_real_federal_v08.py --fetch-available-public
python scripts/replay_v09.py --require-originals
python scripts/inspect_cps_asec_2026_schema_v09.py
python -m unittest discover -s tests -q
( cd external/public_scoring && python -m unittest discover -s tests -q )
