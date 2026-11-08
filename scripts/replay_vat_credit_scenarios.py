#!/usr/bin/env python3
"""Evaluate conditional §101 credit exposure on the 2026 CPS ASEC public-use file."""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import file_digest
import json
from pathlib import Path
from zipfile import ZipFile

from replay_cps_households import SOURCE_SHA256, SOURCE_URL, records

HHS_2025 = "https://www.govinfo.gov/content/pkg/FR-2025-01-17/html/2025-01377.htm"
GUIDELINES = {2: (19550, 6880), 15: (17990, 6330)}
DEFAULT_GUIDELINE = (15650, 5500)
MAGI_UPLIFT_USD = 5000


def credit_cents(income_usd, guideline_usd):
    # Exact integer form of .05 * P * clamp((3P - MAGI)/P, 0, 1).
    return 5 * max(0, min(guideline_usd, 3 * guideline_usd - income_usd))


def filer_agi(members):
    """Return principal-return AGI, leaving nonfilers and ambiguous rows unresolved."""
    principals = [row for row in members if row[2] != 6 and row[3] == 0]
    if len(principals) == 1 and principals[0][2] in (4, 5):
        return principals[0][4]
    if len(principals) == 2:
        first, second = principals
        if first[2] == second[2] and first[2] in (1, 2, 3):
            reciprocal = first[1] == second[0] and second[1] == first[0]
            if reciprocal and (first[4] == 0 or second[4] == 0):
                return first[4] + second[4]
    return None


def dollars(weighted_cents):
    return f"{weighted_cents // 10000}.{weighted_cents % 10000:04d}"


def replay(path):
    with path.open("rb") as stream:
        if file_digest(stream, "sha256").hexdigest() != SOURCE_SHA256:
            raise ValueError("Census archive differs from the pinned 2026 release")
    homes = {}
    members = defaultdict(list)
    with ZipFile(path) as archive:
        for seq, interview, kind, rank, state, weight, size in records(
            archive, "hhpub26.csv",
            ["H_SEQ", "H_HHTYPE", "HRHTYPE", "HPCTCUT", "GESTFIPS", "HSUP_WGT", "H_NUMPER"],
        ):
            if interview != "1" or int(kind) in (9, 10):
                continue
            if seq in homes or not (1 <= int(kind) <= 8 and 1 <= int(rank) <= 20):
                raise ValueError("Unexpected household key or income quintile")
            homes[seq] = (int(state), int(weight), int(size), (int(rank) - 1) // 4 + 1)
        for seq, unit, line, spouse, status, dependent, agi in records(
            archive, "pppub26.csv",
            ["PH_SEQ", "TAX_ID", "A_LINENO", "A_SPOUSE", "FILESTAT", "DEP_STAT", "AGI"],
        ):
            if seq in homes:
                members[seq].append((unit, *map(int, (line, spouse, status, dependent, agi))))

    fields = ("households", "household_weight", "multiple_unit_household_weight", "tax_units",
              "resolved_filer_units", "unresolved_units", "nonfiler_units",
              "lower_credit", "upper_credit", "agi_proxy_credit", "unresolved_max_credit")
    sums = {q: dict.fromkeys(fields, 0) for q in range(1, 6)}
    for seq, (state, weight, size, q) in homes.items():
        people = members[seq]
        lines = {person[1] for person in people}
        if weight <= 0 or size <= 0 or size != len(people) or len(lines) != size:
            raise ValueError("Person records do not reconcile with Census household size")
        if any(int(row[0]) <= 0 or not 1 <= row[3] <= 6 or (row[4] and row[4] not in lines)
               for row in people):
            raise ValueError("Invalid tax-unit key, filing status, or dependent pointer")
        groups = defaultdict(list)
        for unit, *person in people:
            groups[unit].append(person)
        s = sums[q]
        s["households"] += 1
        s["household_weight"] += weight
        s["multiple_unit_household_weight"] += weight * (len(groups) > 1)
        s["tax_units"] += len(groups)
        base, increment = GUIDELINES.get(state, DEFAULT_GUIDELINE)
        for unit_members in groups.values():
            guideline = base + increment * (len(unit_members) - 1)
            agi = filer_agi(unit_members)
            if agi is None:
                s["unresolved_units"] += 1
                s["nonfiler_units"] += all(row[2] == 6 for row in unit_members)
                cap = weight * 5 * guideline
                s["unresolved_max_credit"] += cap
                s["upper_credit"] += cap
                continue
            s["resolved_filer_units"] += 1
            lower = weight * credit_cents(agi + MAGI_UPLIFT_USD, guideline)
            upper = weight * credit_cents(agi, guideline)
            s["lower_credit"] += lower
            s["upper_credit"] += upper
            s["agi_proxy_credit"] += upper

    def reported(s):
        return {
            **{name: s[name] for name in fields[:7] if not name.endswith("weight")},
            "weighted_households": s["household_weight"] / 100,
            "weighted_multi_unit_households": s["multiple_unit_household_weight"] / 100,
            **{f"{name}_usd": dollars(s[name]) for name in fields[7:]},
        }

    return {
        "classification": "CONDITIONAL_2025_CREDIT_EXPOSURE_NOT_POLICY_SCORE",
        "source_url": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "guidelines_url": HHS_2025,
        "filer_magi_minus_model_agi_range_usd": [0, MAGI_UPLIFT_USD],
        "total": reported({key: sum(s[key] for s in sums.values()) for key in fields}),
        "by_census_household_income_quintile": {q: reported(s) for q, s in sums.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(args.archive), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
