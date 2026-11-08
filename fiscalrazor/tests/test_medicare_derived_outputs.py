"""Cross-source regression checks for published CMS table transcription.

A passing test does NOT imply the original expanded CMS archive was acquired.
"""
from pathlib import Path
import csv
import json
import unittest
from decimal import Decimal as D
from fiscal_data.medicare_cash import validate_hi,validate_smi,uniform_incremental_hi_inflow_floor
from fiscal_data.accounting import read_budget

BASE=Path(__file__).resolve().parents[1]

class DerivedMedicareChecks(unittest.TestCase):
    def test_calendaryear_gross_baseline_totals(self):
        hi=validate_hi()
        smi=validate_smi()['SMI']
        # The report's individual account numbers are real reported values,
        # while the additive totals are newly computed checks.
        self.assertEqual(hi[0]['expenditures_bn']+smi[0]['expenditures_bn'],D('1210.0'))
        self.assertEqual(hi[-1]['expenditures_bn']+smi[-1]['expenditures_bn'],D('2543.1'))

    def test_noncomparability_with_cbo_fiscalyear_net(self):
        smi=validate_smi()['SMI']
        hi=validate_hi()
        g=hi[-1]['expenditures_bn']+smi[-1]['expenditures_bn']
        net=read_budget()[2035]['proj_mand_medicare']
        self.assertEqual(g-net,D('388.207'))
        report=json.loads((BASE/'results'/'medicare_2026_funding_analysis.json').read_text())
        self.assertTrue(report['cbo_medicare_comparison_caution']['accounting_status'].startswith('NONCOMPARABLE'))

    def test_exact_fixed_yearend_funding_floor(self):
        r=uniform_incremental_hi_inflow_floor()
        self.assertEqual(r['annual_increment_bn']*D(9),D('296.5'))
        self.assertTrue(all(v>=0 for v in r['year_end_path_bn'].values()))

    def test_no_false_original_raw_source_status(self):
        status=json.loads((BASE/'results'/'verification_status.json').read_text())
        self.assertEqual(status['raw_dataset_acquisition']['fully_downloaded'],0)
        self.assertEqual(status['official_combined_score'],'NOT_AVAILABLE')
        self.assertEqual(status['household_reform_incidence'],'NOT_COMPUTABLE_NO_RAW_HOUSEHOLD_AND_REFORM_RECORDS')
