#!/usr/bin/env python3
"""Fit CPS upper-tail return counts and AGI to IRS geographic controls."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass
import json
from math import exp, fsum, isclose, log
from pathlib import Path

from replay_same_year_tax_units import (
    CPS_SHA256, CPS_URL, IRS_SHA256, IRS_URL, THRESHOLDS, cps_returns, irs_state_cells, verify,
)

FLOOR = THRESHOLDS[-1]
TAIL_STUB = len(THRESHOLDS) + 1
FINE_BANDS = (200_000, 500_000, 1_000_000, 1_500_000, 2_000_000, 5_000_000, 10_000_000)
CPS_STATUS = {"joint": (1, 2, 3), "head_of_household": (4,), "single": (5,)}
SOI_STATUS = {
    "all": (1, "All returns"),
    "joint_or_surviving_spouse": (13, "Returns of married persons filing jointly and returns of surviving spouses"),
    "married_separate": (25, "Returns of married persons filing separately"),
    "head_of_household": (37, "Returns of heads of households"),
    "single": (49, "Returns of single persons"),
}
GEO_FIELDS = ("N1", "A00100", "MARS1", "MARS2", "MARS4")
SOURCES = {
    2023: {
        "cps": (CPS_URL, CPS_SHA256),
        "irs": (IRS_URL, IRS_SHA256),
        "soi": ("https://www.irs.gov/pub/irs-soi/23in12ms.xls",
                "549861a1c7b38256abf9506a6111dcf82110266d0168199dfa465a5d61134490"),
    },
    2022: {
        "cps": ("https://www2.census.gov/programs-surveys/cps/datasets/2023/march/asecpub23csv.zip",
                "d2e000250782adfbdd7f29c82b66d866591a30f0d330496698ec19f9c784ce11"),
        "irs": ("https://www.irs.gov/pub/irs-soi/22zpallagi.csv",
                "1402895408f6648e3ea8c8490afec5d1a797368550c957f64a6aa4093de4b2a6"),
        "soi": ("https://www.irs.gov/pub/irs-soi/22in12ms.xls",
                "ffc483e16aa05762c5ac6dfdbfa86250cd4db5969b1cf6db2296539601a54503"),
    },
}


@dataclass(frozen=True)
class Adjustment:
    log_weight_factor: float = 0
    tilt_per_million: float = 0
    excess_income_factor: float = 1

    def apply(self, sample):
        return [(FLOOR + (agi - FLOOR) * self.excess_income_factor,
                 weight * exp(self.log_weight_factor + self.tilt_per_million * (agi - FLOOR) / 1e6))
                for agi, weight in sample]


def margins(sample):
    return fsum(w for _, w in sample), fsum(x * w for x, w in sample)


def fit(sample, count, agi, method):
    """Solve count and AGI constraints, or raise if positive support is inadequate."""
    base_count, base_agi = margins(sample)
    if base_count <= 0 or count <= 0 or agi < FLOOR * count:
        raise ValueError("missing sample support or invalid IRS moments")
    count_log = log(count / base_count)
    if method == "count_only":
        return Adjustment(count_log)
    target = agi / count
    if method == "stretch":
        excess = base_agi / base_count - FLOOR
        if excess <= 0 or target <= FLOOR:
            raise ValueError("positive excess AGI is required for a monotone stretch")
        return Adjustment(count_log, excess_income_factor=(target - FLOOR) / excess)
    if method != "tilt":
        raise ValueError(f"Unknown method: {method}")
    if target == base_agi / base_count:
        return Adjustment(count_log)

    minimum = min(x for x, _ in sample)
    maximum = max(x for x, _ in sample)
    if not minimum < target < maximum:
        raise ValueError("IRS mean outside the interior of observed CPS support")

    def log_mass_and_mean(slope):
        pivot = maximum if slope > 0 else minimum
        weights = [w * exp(slope * (x - pivot) / 1e6) for x, w in sample]
        mass = fsum(weights)
        mean = fsum(w * x for w, (x, _) in zip(weights, sample)) / mass
        return log(mass) + slope * (pivot - FLOOR) / 1e6, mean

    # The tilted mean is increasing, with derivative proportional to AGI variance.
    lower, upper = -1.0, 1.0
    while log_mass_and_mean(lower)[1] > target:
        lower *= 2
    while log_mass_and_mean(upper)[1] < target:
        upper *= 2
    for _ in range(64):
        middle = (lower + upper) / 2
        if log_mass_and_mean(middle)[1] < target:
            lower = middle
        else:
            upper = middle
    slope = (lower + upper) / 2
    log_mass, _ = log_mass_and_mean(slope)
    return Adjustment(log(count) - log_mass, slope)


def pairs(rows, weight="person_weight"):
    return [(row.agi, getattr(row, weight) / 100) for row in rows if getattr(row, weight) > 0]


def checked_fit(sample, count, agi, method):
    adjust = fit(sample, count, agi, method)
    achieved_count, achieved_agi = margins(adjust.apply(sample))
    if not isclose(count, achieved_count, rel_tol=1e-10) or (
        method != "count_only" and not isclose(agi, achieved_agi, rel_tol=1e-10)
    ):
        raise ArithmeticError("Calibrated margins did not reconcile")
    return adjust


def fine_margins(sample):
    buckets = [[] for _ in FINE_BANDS]
    for x, w in sample:
        buckets[bisect_right(FINE_BANDS, x) - 1].append((x, w))
    return {lower: dict(zip(("returns", "agi_usd"), margins(bucket)))
            for lower, bucket in zip(FINE_BANDS, buckets)}


def distribution(sample):
    count, agi = margins(sample)
    quantiles = {}
    ordered = sorted(sample)
    thresholds = iter((0.5, 0.9, 0.99, 0.999))
    threshold = next(thresholds, None)
    running = 0.0
    for x, w in ordered:
        running += w
        while threshold is not None and running >= threshold * count:
            quantiles[str(threshold)] = x
            threshold = next(thresholds, None)
    return {
        "returns": count, "agi_usd": agi, "mean_agi_usd": agi / count,
        "kish_effective_sample_size": count**2 / fsum(w**2 for _, w in sample),
        "max_return_weight_share": max(w for _, w in sample) / count,
        "max_agi_usd": ordered[-1][0], "weighted_quantiles_usd": quantiles,
        "fine_bands": fine_margins(sample),
    }


def soi_fine_bands(path, year):
    import xlrd

    sheet = xlrd.open_workbook(path).sheet_by_name("TBL12")
    if f"Tax Year {year} (" not in sheet.cell_value(0, 0) or sheet.cell_value(2, 1) != "All returns":
        raise ValueError("Unexpected IRS Table 1.2 vintage or layout")
    for col, label in SOI_STATUS.values():
        if (sheet.cell_value(2, col) != label
                or sheet.row_values(7)[col:col + 4] != [-col, -col - 1, -col - 2, -col - 3]):
            raise ValueError("Unexpected IRS Table 1.2 column identifiers")
    result = {status: {} for status in SOI_STATUS}
    for index, lower in enumerate(FINE_BANDS):
        row = sheet.row_values(21 + index)
        label = row[0]
        suffix = f" under ${FINE_BANDS[index + 1]:,}" if index + 1 < len(FINE_BANDS) else " or more"
        if label != f"${lower:,}{suffix}":
            raise ValueError(f"Unexpected IRS Table 1.2 band: {label}")
        for status, (col, _) in SOI_STATUS.items():
            count, agi, itemizers, deductions = row[col:col + 4]
            result[status][lower] = {"returns": int(count), "agi_usd": 1000 * int(agi),
                                     "itemizers": int(itemizers), "itemized_deductions_usd": 1000 * int(deductions)}
    return result


def load_year(folder, year):
    paths = {"cps": folder / f"cps{(year + 1) % 100:02d}.zip",
             "irs": folder / f"irs{year % 100:02d}.csv",
             "soi": folder / f"soi{year % 100:02d}.xls"}
    for name, path in paths.items():
        verify(path, SOURCES[year][name][1])
    rows, diagnostics, households, units = cps_returns(paths["cps"], year + 1)
    cells = irs_state_cells(paths["irs"], GEO_FIELDS)
    if {row.state for row in rows} - {state for state, _ in cells}:
        raise ValueError("Unexpected CPS geography")
    return rows, cells, soi_fine_bands(paths["soi"], year), {
        "unresolved_and_joint_diagnostics": dict(diagnostics), "households": households, "tax_units": units,
    }


def filing_counts(rows):
    return {
        **{status: fsum(r.person_weight for r in rows if r.status in codes) / 100
           for status, codes in CPS_STATUS.items()},
        "single_dependent_subset": fsum(r.person_weight for r in rows if r.kind == "dependent") / 100,
    }


def residual_summary(states, methods):
    result = {}
    for name in methods:
        errors = {}
        for field in ("returns", "agi_usd"):
            absolute = [abs(row[f"{name}_{field}"] - row[f"irs_{field}"]) for row in states]
            controls = [row[f"irs_{field}"] for row in states]
            relative = sorted((error / control, row["state_fips"])
                              for error, control, row in zip(absolute, controls, states))
            errors[field] = {
                "wape": fsum(absolute) / fsum(controls), "median_absolute_relative": relative[25][0],
                "worst_absolute_relative": relative[-1][0], "worst_state_fips": relative[-1][1],
            }
        result[name] = errors
    return result


def evaluate(year, data, frozen=None):
    rows, cells, fine, diagnostics = data
    by_stub = defaultdict(list)
    for row in rows:
        if row.agi > 0:
            by_stub[bisect_right(THRESHOLDS, row.agi) + 1].append(row)
    composition = {}
    for stub, band in sorted(by_stub.items()):
        count, agi, single, joint, head = map(sum, zip(*(v for (s, b), v in cells.items() if b == stub)))
        composition[stub] = {
            "cps_returns_and_agi_usd": margins(pairs(band)),
            "cps_household_weight_returns_and_agi_usd": margins(pairs(band, "household_weight")),
            "cps_principals_only_returns_and_agi_usd": margins(pairs(r for r in band if r.kind == "principal")),
            "cps_filing_counts": filing_counts(band),
            "irs_returns_and_agi_usd": (count, agi * 1000),
            "irs_filing_counts": {"single": single, "joint": joint, "head_of_household": head,
                                  "other_and_rounding": count - single - joint - head},
        }
    tail = by_stub[TAIL_STUB]
    sample = pairs(tail)
    count, agi = composition[TAIL_STUB]["irs_returns_and_agi_usd"]
    fitted = frozen if frozen is not None else {
        name: checked_fit(sample, count, agi, name) for name in ("count_only", "tilt", "stretch")
    }
    variants = {"raw": Adjustment(), **fitted}
    distributions = {name: distribution(adjust.apply(sample)) for name, adjust in variants.items()}
    distributions["household_weight"] = distribution(pairs(tail, "household_weight"))
    status_distributions = {
        method: {status: fine_margins(adjust.apply(pairs(row for row in tail if row.status in codes)))
                 for status, codes in CPS_STATUS.items()}
        for method, adjust in variants.items()
    }
    state_rows = []
    by_state = defaultdict(list)
    for row in tail:
        by_state[row.state].append(row)
    for (state, stub), (irs_count, irs_agi, single, joint, head) in sorted(cells.items()):
        if stub != TAIL_STUB:
            continue
        irs_agi *= 1000
        state_sample = pairs(by_state[state])
        local = {
            "income_year": year, "state_fips": f"{state:02d}", "cps_sample_returns": len(state_sample),
            "cps_max_agi_usd": max((x for x, _ in state_sample), default=None),
            "irs_returns": irs_count, "irs_agi_usd": irs_agi, "irs_joint_returns": joint,
            "irs_single_returns": single, "irs_head_of_household_returns": head,
            **{f"cps_{k}_returns": v for k, v in filing_counts(by_state[state]).items()},
        }
        for name, adjust in variants.items():
            n, total = margins(adjust.apply(state_sample))
            local[f"{name}_returns"], local[f"{name}_agi_usd"] = n, total
            local[f"{name}_returns_relative_error"] = n / irs_count - 1
            local[f"{name}_agi_relative_error"] = total / irs_agi - 1
        if frozen is None:
            for name in ("tilt", "stretch"):
                try:
                    adjust = checked_fit(state_sample, irs_count, irs_agi, name)
                except ValueError as exc:
                    local[f"local_{name}_status"] = str(exc)
                    continue
                adjusted = distribution(adjust.apply(state_sample))
                for field in ("returns", "agi_usd", "kish_effective_sample_size", "max_return_weight_share"):
                    local[f"local_{name}_{field}"] = adjusted[field]
                local[f"local_{name}_status"] = "matched"
        state_rows.append(local)
    return fitted, state_rows, {
        "inputs": {key: {"url": url, "sha256": sha} for key, (url, sha) in SOURCES[year].items()},
        "sample": diagnostics,
        "cps_nonpositive_return_rows_by_kind": {
            kind: sum(row.agi <= 0 and row.kind == kind for row in rows) for kind in ("principal", "dependent")
        },
        "composition_by_agi_stub": composition,
        "irs_national_soi_fine_bands_not_fit": fine,
        "distribution": distributions, "fine_bands_by_cps_filing_status": status_distributions,
        "state_residuals_national_adjustments": residual_summary(state_rows, variants),
    }


def replay(folder, state_output):
    fitted, states23, year23 = evaluate(2023, load_year(folder, 2023))
    _, states22, year22 = evaluate(2022, load_year(folder, 2022), frozen=fitted)
    rows = states23 + states22
    with state_output.open("w", newline="", encoding="utf-8") as handle:
        columns = dict.fromkeys(key for row in rows for key in row)
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return {
        "classification": "RESEARCH_CALIBRATION_OF_GEOGRAPHIC_RETURN_AND_AGI_MARGINS",
        "fit_income_year": 2023, "frozen_transfer_income_year": 2022,
        "agi_floor_usd": FLOOR, "2023_fitted_adjustments": {key: asdict(v) for key, v in fitted.items()},
        "by_income_year": {"2023": year23, "2022": year22},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("--state-output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.source_folder, args.state_output), indent=2, sort_keys=True, allow_nan=False))
