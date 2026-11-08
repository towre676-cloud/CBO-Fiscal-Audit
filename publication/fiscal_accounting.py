"""Exact, source-excerpt-based fiscal targets. Independent research; not an agency score.

Inputs are source-attributed excerpts committed under fiscalrazor/data. Their Git SHA
metadata points to original CBO files; Git metadata alone is NOT a local original-byte
verification. All monetary output in billions of nominal dollars.
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "fiscalrazor" / "data" / "verified_tables"
BASELINE = BASE / "cbo_budget_fy2026_2036_21_series.csv"
GDP = BASE / "cbo_gdp_fy2026_2036_official.csv"
PCE = ROOT / "fiscalrazor" / "data" / "v09" / "cbo_fy_pce_2027_2036_source_excerpt.csv"
PCE_SOURCE_GIT_SHA1 = "e0799d7972696a65823e5d90cf36486d21903520"

class EvidenceError(ValueError):
    """A supplied source excerpt is malformed, inconsistent, or missing."""


def decimal_value(raw: str) -> Decimal:
    try:
        number = Decimal(raw)
    except (InvalidOperation, TypeError) as exc:
        raise EvidenceError(f"Non-numeric datum: {raw!r}") from exc
    if not number.is_finite():
        raise EvidenceError(f"Non-finite datum: {raw!r}")
    return number


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise EvidenceError(f"Missing source excerpt: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_inputs(baseline: Path = BASELINE, gdp: Path = GDP, pce: Path = PCE):
    budget = {}
    for row in _rows(baseline):
        try:
            year = int(row["fy"])
        except (KeyError, ValueError) as exc:
            raise EvidenceError("Invalid budget year") from exc
        if year in budget:
            raise EvidenceError(f"Duplicate budget year: {year}")
        budget[year] = {key: decimal_value(value) for key, value in row.items() if key != "fy"}
    economy = {}
    for row in _rows(gdp):
        year = int(row["fiscal_year"])
        if year in economy:
            raise EvidenceError(f"Duplicate GDP year: {year}")
        economy[year] = decimal_value(row["nominal_gdp_bn"])
    consumption = {}
    for row in _rows(pce):
        year = int(row["fiscal_year"])
        if year in consumption:
            raise EvidenceError(f"Duplicate PCE year: {year}")
        if row["source_variable"] != "pce" or row["source_git_blob_sha1"] != PCE_SOURCE_GIT_SHA1:
            raise EvidenceError(f"Unrecognized CBO PCE source marker in {year}")
        consumption[year] = decimal_value(row["pce_nominal_billions"])
    if set(budget) != set(range(2026, 2037)) or set(economy) != set(budget):
        raise EvidenceError("Budget and GDP years must be complete FY2026-FY2036")
    if set(consumption) != set(range(2027, 2037)):
        raise EvidenceError("PCE years must be complete FY2027-FY2036")
    for year, b in budget.items():
        receipts = b["proj_rev_total"]
        outlays = b["proj_outlays_total"]
        signed_deficit = b["proj_deficit_total"]
        interest = b["proj_outlays_net_interest"]
        primary = b["proj_primary_deficit"]
        if receipts - outlays != signed_deficit or primary - interest != signed_deficit:
            raise EvidenceError(f"CBO budget identity fails for FY{year}")
        if economy[year] <= 0 or b["proj_debt_held_by_public"] <= 0:
            raise EvidenceError("GDP and debt must be positive")
        # CBO reports rounded debt-to-GDP percentages, so never use them as input.
        reported = b["proj_debt_held_by_public_gdp_share"]
        exact_share = Decimal(100) * b["proj_debt_held_by_public"] / economy[year]
        if abs(exact_share - reported) > Decimal("0.002"):
            raise EvidenceError(f"Debt/GDP ratio outside source rounding for FY{year}")
        if year >= 2027:
            debt_flow = b["proj_debt_held_by_public"] - budget[year-1]["proj_debt_held_by_public"]
            expected_flow = -signed_deficit + b["proj_debt_change_other_financing"]
            if abs(debt_flow - expected_flow) > Decimal("0.000001"):
                raise EvidenceError(f"CBO debt stock-flow bridge fails for FY{year}")
    return budget, economy, consumption


def _fmt(value: Decimal) -> str:
    return format(value, 'f')


def annual_targets(*, vat_rate="0.05", illustration_rebate_fraction="0.20",
                   baseline: Path = BASELINE, gdp: Path = GDP, pce: Path = PCE):
    """Reference calculations at fixed CBO inputs, no macro, behavior, or tax-base estimate.

    The rebate fraction is an ILLUSTRATION only; the proposed Act's §101 instead
    defines an income/poverty-guideline household credit. Do not confuse them.
    """
    rate = decimal_value(vat_rate)
    rebate = decimal_value(illustration_rebate_fraction)
    if not (Decimal(0) <= rate <= Decimal(1)) or not (Decimal(0) <= rebate <= Decimal(1)):
        raise EvidenceError("VAT and rebate parameters must each lie in [0,1]")
    b, g, c = read_inputs(baseline, gdp, pce)
    result = []
    for year in range(2027, 2037):
        year_b = b[year]
        deficit = -year_b["proj_deficit_total"]
        debt = year_b["proj_debt_held_by_public"]
        debt_last = b[year-1]["proj_debt_held_by_public"]
        # Static improvement in one year's debt held by public, not 75-year stability.
        debt_limit = debt_last * g[year] / g[year-1]
        debt_gap = max(Decimal(0), debt-debt_limit)
        deficit_gap = max(Decimal(0), deficit - Decimal('0.03')*g[year])
        vat_gross = c[year] * rate
        vat_after_illustrative_rebate = vat_gross*(Decimal(1)-rebate)
        result.append({
            "fy":str(year),
            "cbo_nominal_gdp_bn":_fmt(g[year]),
            "cbo_public_debt_bn":_fmt(debt),
            "cbo_total_deficit_bn":_fmt(deficit),
            "cbo_primary_deficit_bn":_fmt(-year_b['proj_primary_deficit']),
            "cbo_net_interest_bn":_fmt(year_b['proj_outlays_net_interest']),
            "cbo_other_financing_bn":_fmt(year_b['proj_debt_change_other_financing']),
            "three_percent_deficit_target_gap_bn":_fmt(deficit_gap),
            "constant_prior_year_debt_ratio_gap_bn":_fmt(debt_gap),
            "cbo_total_pce_bn":_fmt(c[year]),
            "all_pce_gross_at_stylized_vat_rate_bn":_fmt(vat_gross),
            "all_pce_net_after_stylized_rebate_bn":_fmt(vat_after_illustrative_rebate),
            "remaining_gap_after_stylized_vat_bn":_fmt(deficit_gap-vat_after_illustrative_rebate),
            "fixed_base_rate_needed_alone_at_rebate_fraction":_fmt(deficit_gap/(c[year]*(Decimal(1)-rebate))) if rebate<1 else "undefined",
            "interpretation":"FROZEN_CBO_BASELINE_AND_ALL_PCE_HYPOTHESIS_NOT_JOINT_POLICY_SCORE",
        })
    return result


def write_csv(path: Path, **options):
    rows=annual_targets(**options)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    return rows
