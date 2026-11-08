from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal
import os,sys,csv,io,unittest,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v07_calibration import *

class CBOCalibratedBridgeTests(unittest.TestCase):
 def test_complete_pin_count(self):self.assertEqual(len(pins()),18)
 def test_total_rows(self):self.assertEqual(sum(x['expected_csv_rows'] for x in pins()),97459)
 def test_pin_hash_looks_valid(self):
  for p in pins():
   self.assertRegex(p['git_blob_sha1'],r'^[a-f0-9]{40}$')
   self.assertIn('2026-02.csv',p['path'])
 def test_no_claim_local_raw_acquisition(self):
  d=json.loads((ROOT/'data/v07/cbo_2026_02_git_pins.json').read_text());self.assertEqual(d['local_originals_acquired'],0)
 def test_git_blob_hash(self):
  h=git_blob_sha1(b'hello\n');self.assertEqual(len(h),40)
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'source.csv';p.write_bytes(b'date,variable,value\nFY2036,x,1\n')
   sample={'path':'x','git_blob_sha1':git_blob_sha1(p.read_bytes()),'expected_csv_rows':1}
   self.assertTrue(validate_source(p,sample)['verified_original_bytes'])
 def test_source_tampering_fails(self):
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'source.csv';p.write_bytes(b'date,variable,value\nFY2036,x,1\n')
   sample={'path':'x','git_blob_sha1':git_blob_sha1(p.read_bytes()),'expected_csv_rows':1}
   p.write_bytes(b'date,variable,value\nFY2036,x,2\n')
   with self.assertRaises(SourceGateError):validate_source(p,sample)
 def test_csv_rowcount_mismatch_fails(self):
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'source.csv';p.write_bytes(b'date,variable,value\nFY2036,x,1\n')
   sample={'path':'x','git_blob_sha1':git_blob_sha1(p.read_bytes()),'expected_csv_rows':2}
   with self.assertRaises(SourceGateError):validate_source(p,sample)
 def test_csv_malformed_fails(self):
  with self.assertRaises(SourceGateError):parse_csv_bytes(b'date,variable,value\nFY2036,x,1,2\n')
 def test_duplicate_different_rejected(self):
  r=[{'date':'FY2036','variable':'tf_oasi','value':'1'}, {'date':'FY2036','variable':'tf_oasi','value':'10'}]
  self.assertEqual(len(duplicate_keys(r)),1)
  with self.assertRaises(SourceGateError):strict_value_pivot(r)
  with self.assertRaises(SourceGateError):strict_value_pivot(r,allow_identical=True)
 def test_duplicate_same_requires_permission(self):
  r=[{'date':'CY2036','variable':'tp_wedge_housing','value':'0.3'}]*2
  with self.assertRaises(SourceGateError):strict_value_pivot(r)
  self.assertEqual(strict_value_pivot(r,allow_identical=True)[('CY2036','tp_wedge_housing')],'0.3')
 def test_six_agi_groups_add(self):
  rows=six_rank_agi_margins()
  self.assertEqual(len(rows),6)
  self.assertEqual(sum(Decimal(x['returns_millions']) for x in rows),Decimal('180.5'))
  self.assertEqual(sum(Decimal(x['agi_billions']) for x in rows),Decimal('26787.8'))
 def test_top_one_agi(self):
  r=six_rank_agi_margins()[-1]
  self.assertEqual(Decimal(r['returns_millions']),Decimal('1.805'))
  self.assertEqual(Decimal(r['agi_billions']),Decimal('6161.194'))
 def test_jensen_lower_bound(self):
  v=jensen_top_group_floor(top_group_agi_bn='6161.194',top_group_returns_mn='1.805',per_return_threshold_usd='1000000',mechanical_rate='.05')
  self.assertEqual(v['mechanical_lower_base_bn'],'4356.194')
  self.assertEqual(v['unadjusted_lower_product_bn'],'217.80970')
 def test_jensen_is_not_our_surtax(self):
  v=jensen_top_group_floor(top_group_agi_bn='6161.194',top_group_returns_mn='1.805',per_return_threshold_usd='1000000',mechanical_rate='.05')
  self.assertIn('NOT_A_POLICY_SCORE',v['status'])
 def test_same_agi_different_liability(self):
  t=Decimal('1000000');a=[Decimal('800000'),Decimal('800000')];b=[Decimal('200000'),Decimal('1400000')]
  self.assertEqual(sum(a),sum(b))
  f=lambda arr:sum(max(x-t,Decimal(0)) for x in arr)
  self.assertNotEqual(f(a),f(b))
 def test_budget_2036_gap(self):
  v=verify_2036_budget('8300.755','11416.142','-3115.387','2144.336','-971.051','46712.1423975')
  self.assertEqual(v['gap_to_3pct_bn'],'1714.022728075')
 def test_bad_budget_fails(self):
  with self.assertRaises(SourceGateError):verify_2036_budget('8300.755','11416.142','-3115.000','2144.336','-971.051','46712.1423975')
 def test_spending_units_millions(self):
  x=[{'date':'FY2036','tin':'001','disc_or_mand':'Mandatory','category':'Medicare','budget_authority':'1000','outlays':'120000'}, {'date':'FY2036','tin':'002','disc_or_mand':'Discretionary','category':'Defense','budget_authority':'90000','outlays':'80000'}]
  self.assertEqual(check_spending_accounts(x,{'FY2036':'200'})['verified_fiscal_years'],1)
 def test_spending_mismatched_outlays_fails(self):
  x=[{'date':'FY2036','tin':'001','disc_or_mand':'Mandatory','category':'HI','budget_authority':'100','outlays':'1000'}]
  with self.assertRaises(SourceGateError):check_spending_accounts(x,{'FY2036':'2'})
if __name__=='__main__':unittest.main()
