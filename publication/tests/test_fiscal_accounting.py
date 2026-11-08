"""Exact published-source benchmark tests, plus adverse data-integrity checks."""
import csv
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path
from publication.fiscal_accounting import (
    annual_targets, read_inputs, BASELINE, GDP, PCE, EvidenceError, write_csv,
)

class FiscalPublicationTests(unittest.TestCase):
    def test_all_years_complete(self):
        rows=annual_targets()
        self.assertEqual([int(x['fy']) for x in rows],list(range(2027,2037)))

    def test_2036_three_percent_gap(self):
        row=annual_targets()[-1]
        self.assertEqual(D(row['three_percent_deficit_target_gap_bn']),D('1714.022728075'))

    def test_2036_debt_ratio_gap_not_same_as_deficit_gap(self):
        row=annual_targets()[-1]
        self.assertAlmostEqual(D(row['constant_prior_year_debt_ratio_gap_bn']),D('1042.8005081199414124'),places=10)
        self.assertNotEqual(row['constant_prior_year_debt_ratio_gap_bn'],row['three_percent_deficit_target_gap_bn'])

    def test_budget_and_debt_stock_flow_all_years(self):
        budget,economy,consumption=read_inputs()
        self.assertEqual(len(budget),11)
        self.assertEqual(len(economy),11)
        self.assertEqual(len(consumption),10)

    def test_2036_vat_is_hypothesis_only(self):
        row=annual_targets()[-1]
        self.assertEqual(D(row['cbo_total_pce_bn']),D('31989.63122405'))
        self.assertEqual(D(row['all_pce_gross_at_stylized_vat_rate_bn']),D('1599.4815612025'))
        self.assertEqual(D(row['all_pce_net_after_stylized_rebate_bn']),D('1279.58524896200'))
        self.assertIn('HYPOTHESIS',row['interpretation'])

    def test_zero_rate_no_vat_capacity(self):
        self.assertEqual(D(annual_targets(vat_rate='0')[-1]['all_pce_gross_at_stylized_vat_rate_bn']),0)

    def test_full_rebate_unavailable_alone_rate(self):
        self.assertEqual(annual_targets(illustration_rebate_fraction='1')[-1]['fixed_base_rate_needed_alone_at_rebate_fraction'],'undefined')

    def test_input_validation(self):
        for rate in ('-0.1','1.1','NaN','Infinity','anything'):
            with self.subTest(rate=rate),self.assertRaises(EvidenceError): annual_targets(vat_rate=rate)

    def test_tampered_budget_line_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'budget.csv'
            txt=BASELINE.read_text()
            path.write_text(txt.replace('2026,-1852.703','2026,-1851.703',1))
            with self.assertRaisesRegex(EvidenceError,'budget identity'):
                read_inputs(baseline=path)

    def test_tampered_debt_bridge_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'budget.csv'
            text=BASELINE.read_text().replace('2027,-1887.203','2027,-1887.204',1)
            path.write_text(text)
            with self.assertRaises(EvidenceError): read_inputs(baseline=path)

    def test_duplicate_pce_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pce.csv'
            lines=PCE.read_text().splitlines()
            p.write_text('\n'.join(lines+[lines[1]])+'\n')
            with self.assertRaisesRegex(EvidenceError,'Duplicate PCE year'):
                read_inputs(pce=p)

    def test_source_marker_pce_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pce.csv';p.write_text(PCE.read_text().replace('e0799d7972696a65823e5d90cf36486d21903520','badsha'))
            with self.assertRaisesRegex(EvidenceError,'Unrecognized CBO PCE source'):
                read_inputs(pce=p)

    def test_write_quoted_csv(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'targets.csv';write_csv(path)
            with path.open() as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),10)
            self.assertEqual(rows[-1]['fy'],'2036')

if __name__=='__main__': unittest.main()
