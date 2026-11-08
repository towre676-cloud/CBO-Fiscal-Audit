import unittest,csv,tempfile
from pathlib import Path
from decimal import Decimal
from fiscal_data.actuarial import ssa_rows,trustee_key,validate_solvent
class ActuarialTests(unittest.TestCase):
 def test_ssa_11years(self):self.assertEqual(len(ssa_rows()),11)
 def test_oasi_2032_negative(self):
  x=next(r for r in ssa_rows() if r['year']=='2032')
  self.assertEqual(Decimal(x['oasi_balance_pct']),Decimal('-3.05'))
 def test_oasi_2036_negative(self):
  x=next(r for r in ssa_rows() if r['year']=='2036')
  self.assertEqual(Decimal(x['oasi_balance_pct']),Decimal('-3.08'))
 def test_trustfund_separation(self):
  funds=trustee_key()
  self.assertEqual(funds['OASI']['year_of_reserve_depletion'],'2032')
  self.assertEqual(funds['HI']['quarter_of_reserve_depletion'],'Q2')
  self.assertEqual(funds['OASDI_illustrative_combined']['legal_status'],'NOT_LEGALLY_COMBINED')
  self.assertEqual(funds['DI']['year_of_reserve_depletion'],'')
 def test_combined_not_official_score(self):
  with self.assertRaisesRegex(ValueError,'UNSCORED'):validate_solvent('arithmetic proof')
 def test_unsupported_claim_rejected(self):
  with self.assertRaisesRegex(ValueError,'UNVERIFIED'):validate_solvent('yes',{'official_source_url':'https://www.ssa.gov','complete_projection':True})
 def test_balance_tamper_rejected(self):
  source=Path(__file__).resolve().parents[1]/'data/verified_tables/ssa_ivb1_rates_2026_2036.csv'
  with tempfile.TemporaryDirectory() as tmp:
   with source.open(newline='',encoding='utf-8') as stream:
    rows=list(csv.DictReader(stream))
   rows[0]['oasi_balance_pct']='55'
   dst=Path(tmp)/'bad.csv'
   with dst.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
   with self.assertRaisesRegex(ValueError,'balance'):ssa_rows(dst)
