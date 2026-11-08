#!/usr/bin/env python3
"""Replay 2023 IRS SOI geographic AGI margins with disclosure buckets separated."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
from hashlib import file_digest
import json
from pathlib import Path

SOURCE_URL = "https://www.irs.gov/pub/irs-soi/23zpallagi.csv"
SOURCE_SHA256 = "e312d7b865f0761527697611a35bfff036c20b27e173bd4253821f99b24ad8d7"


def replay(path):
    with path.open("rb") as handle:
        if file_digest(handle, "sha256").hexdigest() != SOURCE_SHA256:
            raise ValueError("IRS CSV differs from the retained 2023 acquisition")
    bins = defaultdict(Counter)
    keys = set()
    state_bins = set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = [column.upper() for column in next(reader)]
        indexes = [header.index(column) for column in ("STATE", "ZIPCODE", "AGI_STUB", "N1", "A00100")]
        for row in reader:
            state, zipcode, stub, count, agi = (row[index] for index in indexes)
            code = int(zipcode)
            key = (state, code, stub)
            if key in keys or not 0 <= code <= 99999 or not 1 <= int(stub) <= 6:
                raise ValueError("Duplicate or invalid IRS ZIP-AGI cell")
            keys.add(key)
            count, agi = Decimal(count), Decimal(agi)
            if count < 0 or count % 10 or agi != agi.to_integral_value():
                raise ValueError("Unexpected IRS return count or rounding")
            group = "state_total" if code == 0 else "other" if code == 99999 else "named_zip"
            if group == "state_total":
                state_bins.add((state, stub))
            bins[stub][f"{group}_cells"] += 1
            bins[stub][f"{group}_returns"] += int(count)
            bins[stub][f"{group}_agi_thousands_usd"] += int(agi)

    states = {state for state, _, _ in keys}
    if len(states) != 51 or len(state_bins) != 51 * 6:
        raise ValueError("Expected six brackets for every state and DC")
    total = Counter()
    for counts in bins.values():
        total.update(counts)
    return {"classification": "2023_IRS_SOI_GEOGRAPHIC_BASELINE",
            "source_url": SOURCE_URL, "source_sha256": SOURCE_SHA256, "csv_rows": len(keys),
            "state_and_dc_count": len(states), "totals": dict(total),
            "by_irs_agi_stub": {stub: dict(counts) for stub, counts in bins.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(args.csv_file), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
