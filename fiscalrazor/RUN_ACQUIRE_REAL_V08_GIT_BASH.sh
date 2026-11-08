#!/usr/bin/env bash
# Run on Windows Git Bash with Python 3.11+ and full access to public data hosts.
set -euo pipefail
cd "$(dirname "$0")"
python scripts/acquire_real_federal_v08.py --fetch-all-cbo
python scripts/replay_real_v08.py --require-originals
# ~hundreds of MB; source data are publicly available, not confidential tax returns.
python scripts/acquire_real_federal_v08.py --id cps_asec_2026_csv --id cps_asec_2026_replicates --id cms_medicare_2026_expanded --id irs_soi_2023_zip_agi
python scripts/replay_real_v08.py --require-originals
PYTHONPATH=src python -m unittest discover -s tests -q
