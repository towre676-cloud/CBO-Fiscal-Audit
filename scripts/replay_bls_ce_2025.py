#!/usr/bin/env python3
"""Replay BLS 2025 integrated consumer spending with the official lapse adjustments."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import file_digest
import json
from math import fsum, isfinite, sqrt
from pathlib import Path
from zipfile import ZipFile

from replay_cps_households import records

SOURCES = {
    "intrvw25.zip": "d68d09c237cd14a1c6992f902f972662b40d283e63877e90932a17f5674c2038",
    "diary25.zip": "6140fe25bdfa85b7f341afad40e75a0c23ca552c6cecc0b2438837003455a89c",
    "stubs.zip": "4e872e7be2ce0923dfa3e7b82f81d28e21d166946a6b390f0b8ee25a42dcc833",
}
TABLE_1 = {"TOTALEXP": 81905, "FOODTOTL": 10633, "HOUSING": 27790, "TRANS": 13492, "HEALTH": 6470}
WEIGHTS = ["FINLWT21", *(f"WTREP{i:02d}" for i in range(1, 45))]
INTERVIEW_PERIODS = ("251x", "252", "253", "254", "261")
DIARY_PERIODS = ("251", "252", "253", "254")


def hierarchy(archive):
    active = {}
    mapping = {}
    for line in archive.read("stubs/CE-HG-Integ-2025.txt").decode("cp1252").splitlines():
        if not line.startswith("1"):
            continue
        level = int(line[3])
        code = line[69:77].strip()
        survey = line[79]
        active = {rank: group for rank, group in active.items() if rank < level}
        if code in TABLE_1:
            active[level] = code
        if active and survey in ("I", "D"):
            key = survey, code
            if key in mapping:
                raise ValueError("Duplicate UCC in selected expenditure hierarchy")
            mapping[key] = tuple(active.values())
    if {group for values in mapping.values() for group in values} != TABLE_1.keys():
        raise ValueError("Incomplete BLS expenditure hierarchy")
    return mapping


def scope(period, month):
    if period == "251x":
        return month - 1
    if period == "261":
        return 3.5 if month == 1 else 4 - month
    return {8: 3.5, 9: 5.5, 12: 5.5}.get(month, 3)


def survey_estimates(archive, survey, mapping, adjusted):
    interview = survey == "I"
    prefix = "intrvw25" if interview else "diary25"
    periods = INTERVIEW_PERIODS if interview else DIARY_PERIODS
    estimates = {code: [0.0] * len(WEIGHTS) for code in TABLE_1}
    population = [0.0] * len(WEIGHTS)
    count = 0
    for period in periods:
        unit_weights = {}
        unit_file = "fmli" if interview else "fmld"
        month_field = "QINTRVMO" if interview else "STRTMNTH"
        for key, month, *weights in records(archive, f"{prefix}/{unit_file}{period}.csv",
                                             ["NEWID", month_field, *WEIGHTS]):
            month = int(month)
            if key in unit_weights or not 1 <= month <= 12:
                raise ValueError("Invalid CE consumer-unit key or month")
            factor = 2 if not interview and adjusted and month in (9, 12) else 1
            if not interview:
                months = 3
            elif adjusted:
                months = scope(period, month)
            else:
                months = month - 1 if period == "251x" else 4 - month if period == "261" else 3
            numeric = [float(w) * factor for w in weights]
            if any(not isfinite(w) or w < 0 for w in numeric):
                raise ValueError("Invalid CE final or replicate weight")
            unit_weights[key] = numeric
            for i, weight in enumerate(numeric):
                population[i] += weight * months / 12
        count += len(unit_weights)

        expenditures = defaultdict(Counter)
        if interview:
            files = [("mtbi", "COST", "REF_YR", "REF_MO"), ("itbi", "VALUE", "REFYR", "REFMO")]
            for name, value, year, month in files:
                for key, ucc, pub, amount, yr, mo in records(
                    archive, f"{prefix}/{name}{period}.csv", ["NEWID", "UCC", "PUBFLAG", value, year, month]
                ):
                    groups = mapping.get((survey, ucc))
                    if pub != "2" or yr != "2025" or not groups:
                        continue
                    factor = {7: 1.5, 8: 3, 9: 3, 10: 1.5}.get(int(mo), 1) if adjusted else 1
                    if ucc in ("005520", "005420", "005620"):
                        factor *= 4
                    for group in groups:
                        expenditures[key][group] += factor * float(amount or 0)
        else:
            for name, value in [("expd", "COST"), ("dtbd", "AMOUNT")]:
                for key, ucc, pub, amount in records(
                    archive, f"{prefix}/{name}{period}.csv", ["NEWID", "UCC", "PUB_FLAG", value]
                ):
                    groups = mapping.get((survey, ucc))
                    if pub != "2" or not groups:
                        continue
                    for group in groups:
                        expenditures[key][group] += 13 * float(amount or 0)

        # BLS's sample program keeps only rows present in the family-file join.
        for key, group_costs in expenditures.items():
            weights = unit_weights.get(key)
            if weights is None:
                continue
            for group, cost in group_costs.items():
                for i, weight in enumerate(weights):
                    estimates[group][i] += cost * weight
    if min(population) <= 0:
        raise ValueError("CE population denominator is missing")
    means = {group: [total / pop for total, pop in zip(totals, population, strict=True)]
             for group, totals in estimates.items()}
    return means, population[0], count


def replay(source_dir):
    for name, expected in SOURCES.items():
        with (source_dir / name).open("rb") as handle:
            if file_digest(handle, "sha256").hexdigest() != expected:
                raise ValueError(f"Source archive SHA-256 differs for {name}")
    with ZipFile(source_dir / "stubs.zip") as stubs:
        mapping = hierarchy(stubs)
    with ZipFile(source_dir / "intrvw25.zip") as interview, ZipFile(source_dir / "diary25.zip") as diary:
        im, ip, ic = survey_estimates(interview, "I", mapping, True)
        dm, dp, dc = survey_estimates(diary, "D", mapping, True)
        naive_i, _, _ = survey_estimates(interview, "I", mapping, False)
        naive_d, _, _ = survey_estimates(diary, "D", mapping, False)
    lines = {}
    for group, published in TABLE_1.items():
        means = [i + d for i, d in zip(im[group], dm[group], strict=True)]
        estimate = means[0]
        se = sqrt(4 / 44 * fsum((replicate - estimate) ** 2 for replicate in means[1:]))
        lines[group] = {"adjusted_usd": round(estimate, 2),
                        "without_lapse_adjustment_usd": round(naive_i[group][0] + naive_d[group][0], 2),
                        "replicate_standard_error_usd": round(se, 2),
                        "published_usd": published, "difference_usd": round(estimate - published, 2)}
    return {"source_sha256": SOURCES, "ce_interview_population": round(ip, 2),
            "ce_diary_population": round(dp, 2), "interview_family_rows": ic, "diary_family_rows": dc,
            "replicates": 44, "annual_expenditures_per_consumer_unit": lines}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(args.source_dir), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
