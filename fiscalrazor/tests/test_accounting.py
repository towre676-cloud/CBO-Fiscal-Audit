import unittest
from decimal import Decimal
from copy import deepcopy
from fiscal_data.accounting import read_budget,verify_budget,read_actual,target_gap_2036,read_direct_gdp

class AccountingTests(unittest.TestCase):
 def test_11_years(self):self.assertEqual(len(verify_budget()),11)
 def test_231_selected_numeric_cells(self):self.assertEqual(sum(len(row) for row in read_budget().values()),231)
 def test_static_gap(self):
  x=target_gap_2036()
  self.assertEqual(x['gap_bn'],Decimal('1714.022728075'))
 def test_2026_actual(self):
  a=read_actual(); self.assertEqual(Decimal(a['outlays_bn'])-Decimal(a['receipts_bn']),Decimal('1992.473'))
 def test_actual_vs_forecast(self):
  self.assertEqual(Decimal(read_actual()['deficit_bn'])+read_budget()[2026]['proj_deficit_total'],Decimal('139.770'))
 def test_deficit_tamper_rejected(self):
  b=read_budget();b[2036]['proj_deficit_total']+=Decimal(1)
  with self.assertRaisesRegex(ValueError,'deficit'):verify_budget(b)
 def test_receipts_tamper_rejected(self):
  b=read_budget();b[2036]['proj_rev_total']+=Decimal(1)
  with self.assertRaisesRegex(ValueError,'outlays'):verify_budget(b)
 def test_debt_tamper_rejected(self):
  b=read_budget();b[2034]['proj_debt_held_by_public']+=Decimal(3)
  with self.assertRaisesRegex(ValueError,'debt'):verify_budget(b)
 def test_negative_target_rejected(self):
  with self.assertRaises(ValueError):target_gap_2036(Decimal(-2))
 def test_discretionary_double_count_rejected(self):
  b=read_budget();b[2036]['proj_disc_defense']+=Decimal(100)
  with self.assertRaisesRegex(ValueError,'defense'):verify_budget(b)
 def test_subset_double_count_rejected(self):
  b=read_budget();b[2036]['proj_mand_medicare']+=Decimal(2000)
  with self.assertRaisesRegex(ValueError,'subcomponents'):verify_budget(b)

 def test_gdp_source_direct_not_debt_ratio(self):
  self.assertEqual(read_direct_gdp()[2036],Decimal('46712.1423975'))
  self.assertEqual(target_gap_2036()['source_basis'],'CBO_2026_02_DIRECT_FY_GDP_AND_BUDGET_STATIC_NOT_UPDATED_LAW')
 def test_gdp_tamper_rejected(self):
  import tempfile,pathlib
  p=pathlib.Path(tempfile.mkdtemp())/'bad.csv'
  p.write_text('fiscal_year,nominal_gdp_bn\n'+''.join(f'{y},1\n' for y in range(2026,2037)))
  with self.assertRaisesRegex(ValueError,'GDP does not reconcile'):
   target_gap_2036(gdp_path=p)
