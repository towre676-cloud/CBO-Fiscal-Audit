#!/usr/bin/env python3
"""Replay bounded or isolated mechanics for draft §§107, 108, 111, and 112."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
from hashlib import file_digest
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from replay_trustee_baselines import CMS_SHA256, cms_csv, decimal_cell, read_html, row_cells

ROOT = Path(__file__).resolve().parents[1]
D = Decimal
SSA_PAYROLL_URL = "https://www.ssa.gov/oact/tr/2026/lr6g1.html"
B12_URL = "https://www.ssa.gov/OACT/solvency/provisions/tables/table_run153.html"
CBO_SOURCE = "data/budget/ten_year_budget/annual_fy_2026-02.csv"
YEARS = set(range(2026, 2101))


def ssa_payroll(path):
    active = False
    result = {}
    for tr in read_html(path).find_all("tr"):
        row = row_cells(tr)
        if row == ["Intermediate:"]:
            active = True
        elif active and row and row[0].lower().startswith("low-cost"):
            break
        if active and len(row) == 13 and row[0].isdigit() and int(row[0]) in YEARS:
            year = int(row[0])
            if year in result:
                raise ValueError("Duplicate SSA taxable payroll year")
            result[year] = decimal_cell(row[6])
    if result.keys() != YEARS or min(result.values()) <= 0:
        raise ValueError(f"Incomplete or invalid SSA intermediate payroll: missing {YEARS - result.keys()}, extra {result.keys() - YEARS}")
    return result


def ssa_b12(path):
    annual = {}
    summary = set()
    for tr in read_html(path).find_all("tr"):
        row = row_cells(tr)
        if len(row) != 10:
            continue
        if row[0] == "2026-2100":
            summary.add(tuple(row))
        elif row[0].isdigit() and int(row[0]) in YEARS:
            year = int(row[0])
            if year in annual:
                raise ValueError("Duplicate SSA B1.2 annual row")
            values = [decimal_cell(row[i]) for i in (1, 2, 3, 7, 8, 9)]
            if abs(values[1] - values[0] - values[2]) > D(".01") or abs(values[4] - values[3] - values[5]) > D(".01"):
                raise ValueError("SSA B1.2 balance identity exceeds displayed precision")
            annual[year] = values
    if annual.keys() != YEARS or len(summary) != 1:
        raise ValueError("Incomplete SSA B1.2 annual series or summary")
    summary_row, = summary
    if any(value for year in range(2026, 2033) for value in annual[year][3:]):
        raise ValueError("B1.2 has a reported effect before the eligible cohort")
    return {
        "source": B12_URL,
        "summary_years": summary_row[0],
        "ssa_proposal_75_year_actuarial_balance": summary_row[3],
        "ssa_improvement_vs_current_law_percentage_points": summary_row[9].rstrip("%"),
        "ssa_combined_reserve_depletion_year": int(summary_row[5]),
        "columns_pct_current_law_taxable_payroll": ["cost", "income", "balance",
                                                    "delta_cost", "delta_income", "delta_balance"],
        "annual": annual,
    }


def payroll_mechanics(payroll, cms_path):
    with cms_path.open("rb") as handle:
        if file_digest(handle, "sha256").hexdigest() != CMS_SHA256:
            raise ValueError("Unexpected CMS expanded archive")
    with ZipFile(cms_path) as archive:
        hi_payroll = cms_csv(archive, "Ratio of HI Taxable Payroll to GDP", 2026, 2100, (1,))
        hi_rates = cms_csv(archive, "HI Cost and Income Rates", 2026, 2100, (3,))
    if min(row[0] for row in hi_payroll.values()) <= 0:
        raise ValueError("Invalid HI taxable payroll")
    result = {}
    for year in sorted(YEARS):
        oasdi_rate = D(".002") * max(0, min(5, year - 2027))
        hi_rate = D(".0025") * max(0, min(3, year - 2027))
        hi_base = hi_payroll[year][0] / 1000
        result[year] = [payroll[year], oasdi_rate * 100, payroll[year] * oasdi_rate,
                        hi_base, hi_rate * 100, hi_base * hi_rate, hi_rates[year][0] + 100 * hi_rate]
    return {
        "ssa_payroll_source": SSA_PAYROLL_URL,
        "columns": ["oasdi_payroll_bn", "section107_rate_points", "section107_base_only_bn",
                    "hi_payroll_bn", "section112_rate_points", "section112_static_bn",
                    "hi_balance_rate_plus_section112_points"],
        "hi_negative_years_after_full_phase_in": [y for y, row in result.items() if y >= 2030 and row[-1] < 0],
        "annual": result,
    }


def defense(source_root):
    # Reuse the publication-layer source catalog and raw publisher checks.
    sys.path.insert(0, str(ROOT / "fiscalrazor" / "src"))
    from fiscal_data.v06_law import defense_caps
    from fiscal_data.v07_calibration import parse_csv_bytes, pins, strict_value_pivot, validate_source
    path = source_root / CBO_SOURCE
    pin, = [pin for pin in pins() if pin["path"] == CBO_SOURCE]
    receipt = validate_source(path, pin)
    pivot = strict_value_pivot(parse_csv_bytes(path.read_bytes()))
    caps = defense_caps()
    differences = {}
    for year, cap in sorted(caps.items()):
        baseline = D(pivot[f"FY{year}", "proj_disc_defense_base_ba_timing_adj"])
        if (baseline * D(".95")).quantize(D(".001"), rounding=ROUND_HALF_UP) != cap:
            raise ValueError(f"Draft cap is not 95% of original CBO authority in FY{year}")
        differences[year] = baseline - cap
    # Two illustrative gross spendout kernels. No estimated outlay-rate parameters.
    kernels = {"faster": (D(".65"), D(".25"), D(".10")),
               "slower": (D(".25"), D(".35"), D(".25"), D(".15"))}
    outlays = {name: {year: sum(differences.get(year - lag, D(0)) * weight
                               for lag, weight in enumerate(kernel)) for year in differences}
               for name, kernel in kernels.items()}
    return {"source_git_blob_sha1": receipt["git_blob_sha1"], "budget_authority_difference_bn": differences,
            "total_budget_authority_difference_bn": sum(differences.values()),
            "illustrative_spendout_weights": kernels, "illustrative_gross_outlay_difference_bn": outlays,
            "illustrative_fy2028_2036_total_bn": {k: sum(values.values()) for k, values in outlays.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, help="SSA HTML files and CMS ZIP")
    parser.add_argument("cbo_source_root", type=Path)
    args = parser.parse_args()
    result = {"classification": "ISOLATED_POLICY_MECHANICS_AND_PUBLISHED_ACTUARIAL_COMPARATOR",
              "section107_and_section112": payroll_mechanics(ssa_payroll(args.sources / "payroll_ssa.html"),
                                                             args.sources / "cms.zip"),
              "section108_comparator": ssa_b12(args.sources / "ssa_b12.html"),
              "section111": defense(args.cbo_source_root)}
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
