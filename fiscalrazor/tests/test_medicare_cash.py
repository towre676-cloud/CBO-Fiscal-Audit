import unittest
from decimal import Decimal
from pathlib import Path
import tempfile,csv
from fiscal_data.medicare_cash import validate_hi,validate_smi,uniform_incremental_hi_inflow_floor,end_of_2034_balance_needed_for_2035_full_reserve,refuse_smi_to_hi_transfer,HI,SMI
D=Decimal

class MedicareTests(unittest.TestCase):
    def test_hi_complete(self):self.assertEqual(len(validate_hi()),11)
    def test_smi_accounts_complete(self):self.assertEqual(sum(len(x) for x in validate_smi().values()),33)
    def test_hi_reported_2033_is_hypothetical(self):
        r=validate_hi()[8];self.assertEqual(r['calendar_year'],2033)
        self.assertEqual(r['status'],'hypothetical_after_depletion')
    def test_binding_minimum_inflow(self):
        v=uniform_incremental_hi_inflow_floor()
        self.assertEqual(v['binding_calendar_year'],2035)
        self.assertEqual(v['annual_increment_bn'],D('296.5')/D(9))
        self.assertEqual(v['year_end_path_bn'][2035],D(0))
        self.assertTrue(all(k>=0 for k in v['year_end_path_bn'].values()))
    def test_2033_scenario_reserves_positive(self):
        r=uniform_incremental_hi_inflow_floor()
        self.assertGreater(r['year_end_path_bn'][2033],0)
    def test_any_less_than_floor_misses_2035(self):
        q=uniform_incremental_hi_inflow_floor()['annual_increment_bn']-D('.01')
        self.assertLess(D('-296.5')+q*9,0)
    def test_no_post_horizon(self):
        for st,end in ((2028,2035),(2027,2036)):
            with self.assertRaises(ValueError):uniform_incremental_hi_inflow_floor(st,end)
    def test_full_reserve_2035(self):
        self.assertEqual(end_of_2034_balance_needed_for_2035_full_reserve(),D('130.725'))
    def test_smi_cannot_be_reassigned_as_hi(self):
        for name in ('B','D','SMI'):
            with self.assertRaises(ValueError):refuse_smi_to_hi_transfer(4,name)
    def test_corrupted_2033_hi_stock_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'tampered.csv'
            txt=HI.read_text().replace('2033,690.0,775.1,-85.0,-56.9','2033,690.0,775.1,-85.0,42.1')
            p.write_text(txt)
            with self.assertRaises(ValueError):validate_hi(p)
    def test_corrupted_smi_additivity_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'tampered.csv'
            txt=SMI.read_text().replace('SMI,2035,1689.8','SMI,2035,2000.8')
            p.write_text(txt)
            with self.assertRaises(ValueError):validate_smi(p)
    def test_rounding_tolerance_not_exact_parity(self):
        for r in validate_hi():
            self.assertLessEqual(abs(r['income_bn']-r['expenditures_bn']-r['change_in_fund_bn']),D('0.151'))
