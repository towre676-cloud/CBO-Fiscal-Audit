#!/usr/bin/env python3
"""Compare 2023 modeled CPS filings with same-income-year IRS geographic margins."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from decimal import Decimal
from hashlib import file_digest
import json
from pathlib import Path
from zipfile import ZipFile

from replay_cps_households import records
from replay_irs_zip_margins import SOURCE_SHA256 as IRS_SHA256, SOURCE_URL as IRS_URL
from replay_vat_credit_scenarios import filer_agi

CPS_SHA256 = "cdb39cdac34bef99dd0940ab28e306f692404c2eea44d85dfd634214872a0a09"
CPS_URL = "https://www2.census.gov/programs-surveys/cps/datasets/2024/march/asecpub24csv.zip"
THRESHOLDS = (25_000, 50_000, 75_000, 100_000, 200_000)


def verify(path, expected):
    with path.open("rb") as handle:
        if file_digest(handle, "sha256").hexdigest() != expected:
            raise ValueError(f"Unexpected original source hash: {path.name}")


def irs_state_cells(path, fields):
    cells = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = [column.upper() for column in next(reader)]
        fips, zip_code, stub = map(header.index, ("STATEFIPS", "ZIPCODE", "AGI_STUB"))
        indexes = [header.index(field) for field in fields]
        for row in reader:
            if int(row[zip_code]) != 0:
                continue
            key = int(row[fips]), int(row[stub])
            if key in cells:
                raise ValueError("Duplicate IRS state subtotal cell")
            cells[key] = tuple(int(Decimal(row[i])) for i in indexes)
    if len(cells) != 306 or any({b for s, b in cells if s == state} != set(range(1, 7))
                                for state in {s for s, _ in cells}):
        raise ValueError("Incomplete IRS state subtotal data")
    return cells


def irs_cells(path):
    return {key: (count, agi * 1000)
            for key, (count, agi) in irs_state_cells(path, ("N1", "A00100")).items()}


@dataclass(frozen=True)
class ModeledReturn:
    state: int
    agi: int
    person_weight: int
    household_weight: int
    kind: str
    status: int


def cps_returns(path, survey_year=2024):
    suffix = survey_year % 100
    homes = {}
    groups = defaultdict(list)
    diagnostics = Counter()
    with ZipFile(path) as archive:
        for seq, interview, kind, state, weight, size in records(
            archive, f"hhpub{suffix:02d}.csv", ["H_SEQ", "H_HHTYPE", "HRHTYPE", "GESTFIPS", "HSUP_WGT", "H_NUMPER"]
        ):
            if interview == "1" and 1 <= int(kind) <= 8:
                if seq in homes:
                    raise ValueError("Duplicate CPS household")
                homes[seq] = tuple(map(int, (state, weight, size)))
        observed_sizes = Counter()
        for seq, unit, line, spouse, status, dep, agi, weight in records(
            archive, f"pppub{suffix:02d}.csv",
            ["PH_SEQ", "TAX_ID", "A_LINENO", "A_SPOUSE", "FILESTAT", "DEP_STAT", "AGI", "MARSUPWT"],
        ):
            if seq in homes:
                observed_sizes[seq] += 1
                groups[seq, unit].append(tuple(map(int, (line, spouse, status, dep, agi, weight))))
    if any(observed_sizes[seq] != size for seq, (_, _, size) in homes.items()):
        raise ValueError("CPS person and household counts differ")

    returns = []
    for (seq, _), members in groups.items():
        state, household_weight, _ = homes[seq]
        agi = filer_agi(members)
        if agi is not None:
            principals = [row for row in members if row[2] != 6 and row[3] == 0]
            # Joint members normally have identical weights. Preserve any discordance in the receipt.
            diagnostics["joint_with_different_person_weights"] += len({row[5] for row in principals}) > 1
            head = max(principals, key=lambda row: (row[4] != 0, -row[0]))
            returns.append(ModeledReturn(state, agi, head[5], household_weight, "principal", head[2]))
        else:
            diagnostics["unresolved_or_nonfiler_units"] += 1
        for row in members:
            if row[2] == 5 and row[3] != 0:
                returns.append(ModeledReturn(state, row[4], row[5], household_weight, "dependent", row[2]))
            elif row[2] != 6 and row[3] != 0:
                diagnostics["dependent_other_filing_status"] += 1
    return returns, diagnostics, len(homes), len(groups)


def cps_cells(path):
    returns, diagnostics, households, units = cps_returns(path)
    cells = defaultdict(Counter)
    for row in returns:
        if row.agi <= 0:
            diagnostics[f"{row.kind}_nonpositive_returns"] += 1
            if row.agi == 0:
                diagnostics[f"{row.kind}_zero_agi_person_weight"] += row.person_weight
            continue
        cell = cells[row.state, bisect_right(THRESHOLDS, row.agi) + 1]
        diagnostics[f"{row.kind}_positive_agi_sample_returns"] += 1
        for label, weight in (("person", row.person_weight), ("household", row.household_weight)):
            cell[f"{label}_count"] += weight
            cell[f"{label}_agi"] += weight * row.agi
    return cells, dict(diagnostics), households, units


def comparison(cps, irs):
    count, agi = irs
    return {"irs_returns": count, "irs_agi_usd": agi,
            **{f"cps_{label}_{field}": cps[f"{label}_{name}"] / 100
               for label in ("person", "household")
               for name, field in (("count", "weighted_returns"), ("agi", "weighted_agi_usd"))}}


def replay(cps, irs, state_output=None):
    verify(cps, CPS_SHA256)
    verify(irs, IRS_SHA256)
    controls = irs_cells(irs)
    modeled, diagnostics, households, units = cps_cells(cps)
    if set(modeled) - controls.keys():
        raise ValueError("CPS state or AGI stub absent from IRS controls")
    census_by_stub = defaultdict(Counter)
    irs_by_stub = defaultdict(lambda: [0, 0])
    for (state, stub), (count, agi) in controls.items():
        census_by_stub[stub].update(modeled[state, stub])
        irs_by_stub[stub][0] += count
        irs_by_stub[stub][1] += agi
    total_census = Counter()
    for margin in census_by_stub.values():
        total_census.update(margin)
    totals = comparison(total_census, tuple(map(sum, zip(*irs_by_stub.values()))))
    if state_output is not None:
        state_rows = [
            {"state_fips": f"{state:02d}", "agi_stub": stub, **comparison(modeled[state, stub], controls[state, stub])}
            for state, stub in sorted(controls)
        ]
        with state_output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=state_rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(state_rows)
    return {
        "classification": "UNREWEIGHTED_SAME_YEAR_CPS_IRS_MARGINS",
        "income_year": 2023,
        "cps_source": CPS_URL, "cps_archive_sha256": CPS_SHA256,
        "irs_source": IRS_URL, "irs_csv_sha256": IRS_SHA256,
        "cps_households": households, "cps_modeled_tax_units": units,
        "cps_filing_diagnostics": diagnostics,
        "total": totals,
        "by_positive_agi_stub": {stub: comparison(census_by_stub[stub], irs_by_stub[stub])
                                 for stub in sorted(irs_by_stub)},
        "state_by_stub_cells": len(controls),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cps", type=Path)
    parser.add_argument("irs", type=Path)
    parser.add_argument("--state-output", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.cps, args.irs, args.state_output), indent=2, sort_keys=True))
