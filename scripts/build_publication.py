#!/usr/bin/env python3
"""Rebuild publication-safe mechanical benchmark table from retained CBO excerpts."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from publication.fiscal_accounting import write_csv

def main():
    out=ROOT/'publication/results/cbo_2026_frozen_fiscal_stability_benchmarks.csv'
    rows=write_csv(out)
    print(json.dumps({'dataset':'CBO_FEB_2026_FROZEN_EXCERPTS','rows':len(rows),
                      'csv':str(out.relative_to(ROOT)),
                      'fy2036_deficit_target_gap_bn':rows[-1]['three_percent_deficit_target_gap_bn'],
                      'fy2036_debt_ratio_stasis_gap_bn':rows[-1]['constant_prior_year_debt_ratio_gap_bn'],
                      'status':'NOT_OFFICIAL_SCORE'},indent=2))
if __name__=='__main__':main()
