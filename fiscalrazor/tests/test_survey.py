import csv,tempfile,unittest
from decimal import Decimal as D
from pathlib import Path
from fiscal_data.survey import census_asec_sdr,load_asec_replicate_estimates

class SDRTests(unittest.TestCase):
    def test_160_census_factor(self):
        r=census_asec_sdr('10',[D('11')]*160)
        self.assertEqual(r['variance'],D(4))
        self.assertEqual(r['sampling_standard_error'],D(2))
    def test_zero_variance(self):
        self.assertEqual(census_asec_sdr('25',[D(25)]*160)['variance'],0)
    def test_one_replicate_missing_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'EXACTLY_160'):
            census_asec_sdr(10,[D(10)]*159)
    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'NON_FINITE'):
            census_asec_sdr(10,[float('nan')]*160)
    def test_replicate_csv_reordered_ok(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'rep.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['replicate_index','estimate'])
                for i in range(160,0,-1):w.writerow([i,100+i])
            self.assertEqual(load_asec_replicate_estimates(p),[D(100+i) for i in range(1,161)])
    def test_duplicate_index_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'rep.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['replicate_index','estimate'])
                for i in range(160):w.writerow([i or 1,100])
            with self.assertRaisesRegex(ValueError,'DUPLICATE_OR_OUT_OF_RANGE'):
                load_asec_replicate_estimates(p)
    def test_invalid_index_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'rep.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['replicate_index','estimate'])
                for i in range(1,161):w.writerow([i if i!=80 else 999,100])
            with self.assertRaisesRegex(ValueError,'DUPLICATE_OR_OUT_OF_RANGE'):
                load_asec_replicate_estimates(p)
    def test_negative_estimate_valid(self):
        r=census_asec_sdr('-10',[D(-10)]*160)
        self.assertEqual(r['variance'],0)
