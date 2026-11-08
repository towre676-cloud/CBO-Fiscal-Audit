#!/usr/bin/env python3
"""Replay the February 2026 CBO baseline directly from pinned publisher files."""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "fiscalrazor" / "src")]

from fiscal_data.primary_ingest_v08 import final_outlay_checks, verify_payload
from fiscal_data.v07_calibration import duplicate_keys, parse_csv_bytes, pins, strict_value_pivot
from publication.fiscal_accounting import EvidenceError, read_inputs

LFP_BLOB = "45bb06e63748ebd376cc8f0c6081be5938df49ef"
MAX_BYTES = 25_000_000
BUDGET = "data/budget/ten_year_budget/annual_fy_2026-02.csv"
ECONOMY = "data/economic/historical_economic/annual_fy_2026-02.csv"
SPENDING = "data/budget/spending_detail/annual_fy_2026-02.csv"


def corrected_row_count(pin):
    # The v1.1 metadata counted 4,725 rows for this exact blob. Its verified bytes
    # contain 2,475 CSV records. Keep the frozen v1.1 manifest intact.
    return 2475 if pin["git_blob_sha1"] == LFP_BLOB else pin["expected_csv_rows"]


def replay(source_dir: Path | None):
    receipts = []
    originals = {}
    catalog = pins()
    if len(catalog) != 18 or len({pin["path"] for pin in catalog}) != 18:
        raise EvidenceError("Expected 18 distinct February 2026 CBO source paths")
    for pin in catalog:
        path = pin["path"]
        if source_dir is None:
            with urlopen(pin["source_url"], timeout=60) as response:
                payload = response.read(MAX_BYTES + 1)
        else:
            with (source_dir / path).open("rb") as handle:
                payload = handle.read(MAX_BYTES + 1)
        count = corrected_row_count(pin)
        verified = verify_payload(payload, {
            "kind": "csv",
            "max_bytes": MAX_BYTES,
            "expected_git_blob_sha1": pin["git_blob_sha1"],
            "expected_csv_rows": count,
        })
        rows = parse_csv_bytes(payload)
        originals[path] = rows
        receipts.append({
            "path": path,
            "source_url": pin["source_url"],
            "git_blob_sha1": verified["git_blob_sha1"],
            "sha256": verified["sha256"],
            "bytes": verified["bytes"],
            "csv_records": count,
            "duplicate_date_variable_rows": sum(len(group) - 1 for group in duplicate_keys(rows).values()),
        })

    budget, gdp, pce = read_inputs()
    raw_budget = strict_value_pivot(originals[BUDGET])
    raw_economy = strict_value_pivot(originals[ECONOMY])
    comparisons = [
        (raw_budget, year, series, value)
        for year, row in budget.items()
        for series, value in row.items()
    ]
    comparisons.extend((raw_economy, year, "gdp", value) for year, value in gdp.items())
    comparisons.extend((raw_economy, year, "pce", value) for year, value in pce.items())
    for pivot, year, series, excerpt in comparisons:
        value = pivot.get((f"FY{year}", series))
        if value is None or Decimal(value) != excerpt:
            raise EvidenceError(f"Original and published excerpt differ for FY{year} {series}")

    return {
        "vintage": "CBO_FEBRUARY_2026",
        "source_files_verified": len(receipts),
        "csv_records_verified": sum(item["csv_records"] for item in receipts),
        "publication_input_cells_matched": len(comparisons),
        "spending_account_replay": final_outlay_checks(originals[BUDGET], originals[SPENDING]),
        "sources": receipts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Offline root containing the official data/ paths")
    parser.add_argument("--output", type=Path, help="Write the aggregate receipt to a JSON file")
    args = parser.parse_args()
    result = json.dumps(replay(args.source_dir), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
