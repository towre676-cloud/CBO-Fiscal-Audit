#!/usr/bin/env python3
"""Build a partially classified §101 consumer-spending base from BEA and BLS."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from hashlib import file_digest
from io import TextIOWrapper
import json
from pathlib import Path
from zipfile import ZipFile

from replay_bls_ce_2025 import SOURCES as BLS_SOURCES, hierarchy, survey_estimates

BEA_URL = "https://apps.bea.gov/national/Release/TXT/FlatFiles.ZIP"
BEA_SHA256 = "1e1c69badf0f5615f8da3ef4b7ac8d7f250f5d74a6b0a7c5e09eefbca66c0c1c"
TABLE = "U20405"
YEARS = (2023, 2024, 2025)
# Use disjoint subtrees within the published product table. Retain mixed items in the residual.
BUCKETS = {
    "exempt": ("DTMHRC", "DOWNRC", "DPHYRC", "DDENRC", "DHHCRC", "DMLBRC", "DIMCRC"),
    "zero_rated": ("DRXDRC", "DFAVRC", "DGGSRC", "DMILRC"),
    "taxable": ("DAOPRC", "DGARRC", "DSHURC", "DNRDRC", "DAPPRC", "DOPCRC", "DGASRC"),
    "geography_adjustments": ("DNFRRC", "DFORRC"),
}
BLS_CODES = {
    "RNTDWELL": ("DTENRC",),
    "560110": ("DPHYRC",),
    "560210": ("DDENRC",),
    "540000": ("DRXDRC",),
    "550210": ("DNRDRC",),
    "ALCBEVG": ("DAOPRC",),
    "GASFUEL": ("DGASRC",),
}


def read_csv(archive, name):
    return csv.DictReader(TextIOWrapper(archive.open(name), encoding="cp1252", newline=""))


def verify(path, expected):
    with path.open("rb") as handle:
        if file_digest(handle, "sha256").hexdigest() != expected:
            raise ValueError(f"Source hash differs for {path.name}")


def load_bea(path):
    verify(path, BEA_SHA256)
    categories = {code: bucket for bucket, codes in BUCKETS.items() for code in codes}
    if len(categories) != sum(map(len, BUCKETS.values())):
        raise ValueError("Duplicate BEA series assignment")
    required = set(categories) | {"DPCERC", "DGDSRC", "DSERRC", "DTENRC"}
    metadata = {}
    hierarchy_parents = {}
    values = {year: {} for year in YEARS}
    with ZipFile(path) as archive:
        for row in read_csv(archive, "SeriesRegister.txt"):
            code = row["%SeriesCode"]
            lines = [int(key.split(":")[1]) for key in row["TableId:LineNo"].split("|")
                     if key.startswith(TABLE + ":") and int(key.split(":")[1]) < 369]
            if lines:
                hierarchy_parents[code] = row["SeriesCodeParents"].split("|")
            if code in required:
                if len(lines) != 1 or row["DefaultScale"] != "-6" or row["MetricName"] != "Current Dollars":
                    raise ValueError(f"Unexpected BEA series definition for {code}")
                metadata[code] = {"line": lines[0], "label": row["SeriesLabel"]}
        if set(metadata) != required:
            raise ValueError("Missing required BEA series")
        for row in read_csv(archive, "nipadataA.txt"):
            code, year = row["%SeriesCode"], int(row["Period"])
            if code in required and year in values:
                if code in values[year]:
                    raise ValueError("Duplicate BEA annual series value")
                values[year][code] = int(row["Value"].replace(",", ""))

    for code in categories:
        ancestors = list(hierarchy_parents[code])
        visited = {code}
        while ancestors:
            parent = ancestors.pop()
            if parent in visited:
                continue
            if parent in categories:
                raise ValueError(f"Overlapping BEA categories {code} and {parent}")
            visited.add(parent)
            ancestors.extend(hierarchy_parents.get(parent, ()))

    annual = {}
    for year, amounts in values.items():
        if amounts.keys() != required or abs(amounts["DPCERC"] - amounts["DGDSRC"] - amounts["DSERRC"]) > 1:
            raise ValueError(f"BEA goods and services do not reconcile to PCE in {year}: missing {required - amounts.keys()}")
        totals = {bucket: sum(amounts[code] for code in codes) for bucket, codes in BUCKETS.items()}
        if any(amounts[code] < 0 for bucket, codes in BUCKETS.items() if bucket != "geography_adjustments"
               for code in codes):
            raise ValueError("Unexpected negative signed expenditure in assigned categories")
        domestic_proxy = amounts["DPCERC"] - totals["geography_adjustments"]
        unclassified = domestic_proxy - sum(totals[b] for b in ("exempt", "zero_rated", "taxable"))
        if unclassified < 0:
            raise ValueError("BEA categories exceed the destination proxy")
        upper = totals["taxable"] + unclassified
        annual[year] = {
            "pce_million": amounts["DPCERC"],
            "pce_before_net_geography_adjustments_million": domestic_proxy,
            **{f"{bucket}_million": total for bucket, total in totals.items()},
            "unclassified_million": unclassified,
            "classification_only_base_million": [totals["taxable"], upper],
            "static_5pct_product_million": [str(Decimal(".05") * value) for value in (totals["taxable"], upper)],
            "line_values_million": amounts,
        }
    return annual, metadata


def replay(bea, ce_dir):
    annual, metadata = load_bea(bea)
    for name, digest in BLS_SOURCES.items():
        verify(ce_dir / name, digest)
    with ZipFile(ce_dir / "stubs.zip") as stubs:
        mapping = hierarchy(stubs, BLS_CODES)
    with ZipFile(ce_dir / "intrvw25.zip") as interview, ZipFile(ce_dir / "diary25.zip") as diary:
        i, _, _ = survey_estimates(interview, "I", mapping, True, BLS_CODES)
        d, _, _ = survey_estimates(diary, "D", mapping, True, BLS_CODES)
    return {
        "classification": "PARTIAL_PRODUCT_MAPPING_NO_INVOICE_REVENUE_OR_HOUSEHOLD_INCIDENCE",
        "bea_source": BEA_URL,
        "bea_archive_sha256": BEA_SHA256,
        "bea_buckets": BUCKETS,
        "bea_series": metadata,
        "bea_calendar_year": annual,
        "bls_archives_sha256": BLS_SOURCES,
        "bls_category_comparisons_2025": {
            code: {"bls_annual_usd_per_consumer_unit": round(i[code][0] + d[code][0], 2),
                   "bea_conceptual_series": series,
                   "bea_million": sum(annual[2025]["line_values_million"][key] for key in series)}
            for code, series in BLS_CODES.items()
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bea", type=Path)
    parser.add_argument("ce_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.bea, args.ce_dir), indent=2, sort_keys=True))
