from pathlib import Path
import csv,unittest
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[2]
class SourceAccountReceiptTests(unittest.TestCase):
 def setUp(self):
  with (ROOT/'results/v07/cbo_spending_connector_verified_2026_2036.csv').open() as f:self.rows=list(csv.DictReader(f))
  with (ROOT/'data/verified_tables/cbo_budget_fy2026_2036_21_series.csv').open() as f:self.base={int(x['fy']):x for x in csv.DictReader(f)}
 def test_all_11_years(self):
  self.assertEqual({int(x['fy']) for x in self.rows},set(range(2026,2037)))
 def test_each_year_account_number(self):
  self.assertEqual(sum(int(x['account_rows']) for x in self.rows),21769)
  self.assertTrue(all(int(x['account_rows'])==1979 for x in self.rows))
 def test_outlays_all_11_years_match_cbo(self):
  for x in self.rows:
   y=int(x['fy']);self.assertEqual(D(x['outlays_million'])/1000,D(self.base[y]['proj_outlays_total']))
 def test_defense_outlays_all_11_years_match_cbo(self):
  for x in self.rows:
   y=int(x['fy']);self.assertEqual(D(x['defense_outlays_million'])/1000,D(self.base[y]['proj_disc_defense']))
 def test_ba_not_same_as_outlay(self):
  fy2036=next(x for x in self.rows if x['fy']=='2036')
  self.assertEqual(fy2036['defense_budget_authority_million'],'1136537')
  self.assertEqual(fy2036['defense_outlays_million'],'1100000')
  self.assertNotEqual(fy2036['defense_budget_authority_million'],fy2036['defense_outlays_million'])
if __name__=='__main__':unittest.main()
