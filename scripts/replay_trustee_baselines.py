#!/usr/bin/env python3
"""Reconcile the 2026 SSA and CMS trustee baselines by fund and calendar year."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from hashlib import file_digest, sha256
from io import TextIOWrapper
import json
from pathlib import Path
from zipfile import ZipFile

from bs4 import BeautifulSoup

SSA_SHORT = "https://www.ssa.gov/oact/tr/2026/IV_A_SRest.html"
SSA_LONG = "https://www.ssa.gov/oact/tr/2026/lr6g3.html"
CMS_ZIP = "https://www.cms.gov/files/zip/2026-expanded-supplementary-tables-figures.zip"
CMS_SHA256 = "67675b3375a4db8f678d67ef078dca15cfe43831600fd499e1bec2651f2ed15b"
D = Decimal


def row_cells(row):
    return [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"], recursive=False)]


def decimal_cell(value):
    return D(value.replace("$", "").replace(",", ""))


def read_html(path):
    return BeautifulSoup(path.read_bytes(), "html.parser")


def ssa_operations(soup, table_number):
    captions = [tag for tag in soup.find_all("div", class_="TableTitle")
                if tag.get_text(" ", strip=True).startswith(f"Table {table_number}.—")]
    if len(captions) != 1:
        raise ValueError(f"Missing or duplicated SSA caption {table_number}")
    table = captions[0].find_previous("table")
    if table.find("table") or len(table.find_all("tr")) < 30:
        raise ValueError(f"Unexpected SSA operations table {table_number}")
    result = {}
    for tr in table.find_all("tr"):
        row = row_cells(tr)
        if row and row[0].startswith("Low-cost"):
            break
        if len(row) < 15 or not row[1].isdigit() or not 2025 <= int(row[1]) <= 2035:
            continue
        year = int(row[1])
        cells = [row[i] for i in (2, 8, 13, 14)]
        if year in result:
            raise ValueError(f"Duplicate SSA operations year in {table_number}")
        result[year] = tuple(None if cell == "g" else decimal_cell(cell) for cell in cells)
    if set(result) != set(range(2025, 2036)):
        raise ValueError(f"Incomplete SSA operations years for {table_number}")
    return result


def ssa_long_run(soup):
    active = False
    result = {}
    for tr in soup.find_all("tr"):
        row = row_cells(tr)
        if row == ["Intermediate:"]:
            active = True
        elif active and row and row[0].lower().startswith("low-cost"):
            break
        if active and len(row) == 19 and row[0].isdigit():
            year = int(row[0])
            if year in result:
                raise ValueError("Duplicate SSA long-range year")
            # Footnote b places the value between -0.5 and +0.5 billion.
            result[year] = tuple(D(0) if row[i] == "b" else decimal_cell(row[i]) for i in (2, 4, 6, 8, 10, 12, 14, 16, 18))
    if set(result) != set(range(2026, 2101)):
        raise ValueError("Incomplete SSA long-range years")
    return result


def cms_csv(archive, filename, first, last, cols):
    result = {}
    with archive.open(f"CSV/{filename}.csv") as stream:
        rows = csv.reader(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
        for row in rows:
            if row and row[0].strip().isdigit():
                year = int(row[0])
                if first <= year <= last:
                    if year in result:
                        raise ValueError(f"Duplicate CMS year for {filename}")
                    result[year] = tuple(decimal_cell(row[i]) for i in cols)
    if set(result) != set(range(first, last + 1)):
        raise ValueError(f"Incomplete CMS years for {filename}")
    return result


def reconcile_operations(rows, tolerance):
    cash = []
    reserves = []
    for year, (income, cost, change, end) in rows.items():
        if income is None or change is None or end is None:
            continue
        cash.append(abs(income - cost - change))
        if year - 1 in rows and rows[year - 1][3] is not None:
            reserves.append(abs(rows[year - 1][3] + change - end))
    if not cash or not reserves or max(cash + reserves) > tolerance:
        raise ValueError("Trust fund cash or reserve reconciliation exceeds source precision")
    return {
        "cash_identities_checked": len(cash),
        "reserve_identities_checked": len(reserves),
        "max_cash_residual_billions": str(max(cash)),
        "max_reserve_residual_billions": str(max(reserves)),
        "annual": rows,
    }


def replay(source_dir):
    with (source_dir / "cms.zip").open("rb") as handle:
        if file_digest(handle, "sha256").hexdigest() != CMS_SHA256:
            raise ValueError("CMS ZIP differs from the pinned acquisition")
    with ZipFile(source_dir / "cms.zip") as cms:
        hi_ops = cms_csv(cms, "Operations of the Hospital Insurance (HI) Trust Fund For Calendar Years",
                         2025, 2035, (8, 11, 12, 13))
        hi_rates = cms_csv(cms, "HI Cost and Income Rates", 2026, 2100, (2, 1, 3))
    hi_ops = {year: tuple(value / 1000 for value in row) for year, row in hi_ops.items()}
    short = read_html(source_dir / "ssa.html")
    oasi_ops = ssa_operations(short, "IV.A1")
    di_ops = ssa_operations(short, "IV.A2")
    ssa_annual = ssa_long_run(read_html(source_dir / "ssa_long.html"))
    for year, row in ssa_annual.items():
        if any(abs(row[i] - row[i+1] - row[i+2]) > 1 for i in (0, 3, 6)):
            raise ValueError(f"SSA long-range balance fails source rounding in {year}")
        if any(abs(row[i] + row[i+3] - row[i+6]) > 1 for i in range(3)):
            raise ValueError(f"Separate SSA funds do not reconcile to combined source in {year}")
    for year, (income, cost, balance) in hi_rates.items():
        if abs(income - cost - balance) > D(".01"):
            raise ValueError(f"CMS HI rate balance fails source rounding in {year}")

    result = {
        "classification": "SEPARATE_AGENCY_BASELINES_NO_POST_REFORM_SOLVENCY",
        "source_urls": [SSA_SHORT, SSA_LONG, CMS_ZIP],
        "cms_archive_sha256": CMS_SHA256,
        "ssa_long_run_rounded_zero_footnotes": {"2096": ["DI_balance"]},
        "operations_columns_billions": ["income", "cost", "net_change", "end_reserve"],
        "operations": {
            "OASI": reconcile_operations(oasi_ops, D(".1")),
            "DI": reconcile_operations(di_ops, D(".1")),
            "HI": reconcile_operations(hi_ops, D(".001")),
        },
        "ssa_annual_nominal_billions": {
            "columns": [f"{fund}_{measure}" for fund in ("OASI", "DI", "OASDI")
                        for measure in ("noninterest_income", "scheduled_cost", "balance")],
            "annual": ssa_annual,
        },
        "hi_annual_pct_taxable_payroll": {"columns": ["income", "cost", "balance"], "annual": hi_rates},
    }
    ssa_payload = json.dumps([oasi_ops, di_ops, ssa_annual], sort_keys=True, default=str)
    result["ssa_selected_table_content_sha256"] = sha256(ssa_payload.encode()).hexdigest()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(args.source_dir), indent=2, sort_keys=True, default=str) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
