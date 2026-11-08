#!/usr/bin/env python3
"""Replay a household-income calibration from the Census 2026 CPS ASEC CSV ZIP."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from hashlib import file_digest
from io import TextIOWrapper
import json
from math import fsum, isfinite, sqrt
from pathlib import Path
from zipfile import ZipFile

SOURCE_URL = "https://www2.census.gov/programs-surveys/cps/datasets/2026/march/asecpub26csv.zip"
SOURCE_SHA256 = "fe819d0d2fc4470c282e76c247b8aa8b6054811619730307e9f2fe6186707d93"
PUBLISHED_MEDIAN = 87460
PUBLISHED_MARGIN = 1040
PUBLISHED_HOUSEHOLDS_THOUSANDS = 137100
BIN_WIDTH = 2500
REPLICATES = 160
WEIGHT_NAMES = [f"pwwgt{i}" for i in range(REPLICATES + 1)]
# Half the CPS centiweight unit plus half the replicate file's four-decimal unit.
BASE_WEIGHT_TOLERANCE = 0.005051


def records(archive, member, columns):
    with archive.open(member) as raw:
        reader = csv.reader(TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        header = next(reader)
        if any(header.count(column) != 1 for column in columns):
            raise ValueError(f"Missing or repeated required field in {member}")
        indexes = [header.index(column) for column in columns]
        for row in reader:
            if len(row) != len(header):
                raise ValueError(f"Unexpected row width in {member}")
            yield tuple(row[i] for i in indexes)


def grouped_median(bins):
    half = fsum(bins.values()) / 2
    if half <= 0:
        raise ValueError("Positive household weight is required")
    below = 0.0
    for lower, weight in sorted(bins.items()):
        if weight > 0 and below + weight >= half:
            return lower + BIN_WIDTH * (half - below) / weight
        below += weight
    raise ValueError("Median bin missing")


def replay(path):
    with path.open("rb") as handle:
        sha256 = file_digest(handle, "sha256").hexdigest()
    if sha256 != SOURCE_SHA256:
        raise ValueError("Archive SHA-256 differs from the retained Census acquisition")

    household_bins = Counter()
    replicate_bins = [Counter() for _ in range(REPLICATES)]
    households = {}
    interviewed = set()
    total_records = 0
    with ZipFile(path) as archive:
        for seq, interview, kind, rank, income, weight in records(
            archive, "hhpub26.csv", ["H_SEQ", "H_HHTYPE", "HRHTYPE", "HPCTCUT", "HTOTVAL", "HSUP_WGT"]
        ):
            total_records += 1
            if interview != "1":
                continue
            if seq in interviewed:
                raise ValueError("Duplicate interviewed household key")
            interviewed.add(seq)
            # HRHTYPE 9 and 10 identify group quarters in the Census dictionary.
            if int(kind) in (9, 10):
                continue
            if not (1 <= int(kind) <= 8 and 1 <= int(rank) <= 20 and int(weight) > 0):
                raise ValueError("Invalid income-household universe or full-sample weight")
            income_bin = int(income) // BIN_WIDTH * BIN_WIDTH
            households[seq] = (income_bin, int(weight))
            household_bins[income_bin] += int(weight)

        reference = {}
        for seq, position, relationship, weight in records(
            archive, "pppub26.csv", ["PH_SEQ", "PPPOS", "A_EXPRRP", "MARSUPWT"]
        ):
            if seq not in households or relationship not in ("1", "2"):
                continue
            if position != "41" or seq in reference:
                raise ValueError("Unexpected reference-person key")
            reference[seq] = int(weight)
        if reference.keys() != households.keys():
            raise ValueError("Reference-person join is incomplete")

        matched = set()
        for position, seq, base_weight, *weights in records(
            archive, "asec_csv_repwgt_2026.csv", ["PPPOS", "h_seq", *WEIGHT_NAMES]
        ):
            if position != "41" or seq not in households:
                continue
            income_bin, weight = households[seq]
            base_difference = abs(float(base_weight) - weight / 100)
            if seq in matched or reference[seq] != weight or not base_difference <= BASE_WEIGHT_TOLERANCE:
                raise ValueError("Replicate join failed the full-sample weight check")
            matched.add(seq)
            for bins, raw_weight in zip(replicate_bins, weights, strict=True):
                replicate_weight = float(raw_weight)
                if not isfinite(replicate_weight) or replicate_weight < 0:
                    raise ValueError("Invalid replicate weight")
                bins[income_bin] += replicate_weight
        if matched != households.keys():
            raise ValueError("Replicate-weight join is incomplete")

    median = grouped_median(household_bins)
    deviations = [grouped_median(bins) - median for bins in replicate_bins]
    standard_error = sqrt(4 / REPLICATES * fsum(delta ** 2 for delta in deviations))
    return {
        "source_url": SOURCE_URL,
        "source_sha256": sha256,
        "source_archive_bytes": path.stat().st_size,
        "household_file_records": total_records,
        "interviewed_records_including_group_quarters": len(interviewed),
        "households_in_income_universe": len(households),
        "weighted_households": sum(household_bins.values()) / 100,
        "replicates_used": REPLICATES,
        "grouped_median_usd": round(median, 2),
        "replicate_standard_error_usd": round(standard_error, 2),
        "replicate_90_percent_margin_usd": round(1.645 * standard_error, 2),
        "census_published_households_thousands": PUBLISHED_HOUSEHOLDS_THOUSANDS,
        "census_published_median_usd": PUBLISHED_MEDIAN,
        "census_published_90_percent_margin_usd": PUBLISHED_MARGIN,
        "median_difference_usd": round(median - PUBLISHED_MEDIAN, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Original Census asecpub26csv.zip")
    parser.add_argument("--output", type=Path, help="Write the aggregate receipt to a JSON file")
    args = parser.parse_args()
    result = json.dumps(replay(args.archive), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
