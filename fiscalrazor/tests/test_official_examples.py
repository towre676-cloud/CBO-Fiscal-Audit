import unittest, csv, tempfile
from pathlib import Path
from decimal import Decimal
from fiscal_data.official_examples import ssa_option_rows,actuarial_reference_2035_e25,jct_teaching_example,joint_ssa_estimate,joint_jct_estimate
class OfficialExampleTests(unittest.TestCase):
 def test_ssa_full_coverage(self):self.assertEqual(len(ssa_option_rows()),11)
 def test_ssa_2036_anchors(self):
  r=ssa_option_rows()[-1]
  self.assertEqual((r['E2_5_delta_annual_balance_pct_payroll'],r['E1_10_delta_annual_balance_pct_payroll'],r['B1_2_delta_annual_balance_pct_payroll']),('2.53','0.86','0.01'))
 def test_ssa_2035_dollars_screen(self):self.assertEqual(actuarial_reference_2035_e25(),Decimal('415.4472'))
 def test_payroll_vintage_mismatch_rejected(self):
  with self.assertRaisesRegex(ValueError,'Unknown payroll'):actuarial_reference_2035_e25(Decimal('18000'))
 def test_jct_illustration_subtotal(self):
  r=jct_teaching_example()
  self.assertEqual(r['teaching_example_net_bn'],Decimal('180'))
  self.assertEqual(sum(Decimal(x['ten_year_effect_bn']) for x in r['rows'][1:]),Decimal('-170'))
  self.assertEqual(r['status'],'JCT_ILLUSTRATIVE_NOT_OFFICIAL_SCORE')
 def test_joint_ssa_not_permitted(self):
  with self.assertRaisesRegex(ValueError,'UNSCORED'):joint_ssa_estimate()
 def test_joint_jct_not_permitted(self):
  with self.assertRaisesRegex(ValueError,'UNSCORED'):joint_jct_estimate()
 def test_ssa_missing_year_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'partial.csv'
   p.write_text('calendar_year,E2_5_delta_annual_balance_pct_payroll,E1_10_delta_annual_balance_pct_payroll,B1_2_delta_annual_balance_pct_payroll\n2036,2.53,0.86,0.01\n')
   with self.assertRaisesRegex(ValueError,'Incomplete'):ssa_option_rows(p)
