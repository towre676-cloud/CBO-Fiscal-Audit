import unittest,csv,tempfile
from pathlib import Path
from decimal import Decimal
from fiscal_data.distribution import load_records,weighted_decile_fragments,analyze,summarize_subpopulations
D=Decimal
class DistributionTests(unittest.TestCase):
 def setUp(self):
  self.records=[]
  for i in range(1,101):
   self.records.append({'household_id':str(i),'weight':D(i%5+1),'market_income':D(i*1000),'base_federal_tax':D(100),'reform_federal_tax':D(102),
                        'base_transfers':D(300),'reform_transfers':D(302),'people':D(2),'children':D(i%2),'seniors':D(0),'disabled':D(0)})
 def test_exact_10_pct_each_decile(self):
  x=weighted_decile_fragments(self.records); total=sum(r['weight'] for r in self.records)
  for decile in x:self.assertEqual(sum((w for _,w in decile),D(0)),total/D(10))
 def test_zero_net_benefit(self):
  d=analyze(self.records)
  self.assertTrue(all(r['average_disposable_change']==0 for r in d))
 def test_no_double_weight(self):
  self.assertEqual(sum(r['weight'] for r in self.records),sum(r['weight'] for r in analyze(self.records)))
 def test_subgroup_counts(self):
  rows=summarize_subpopulations(self.records)
  self.assertEqual(rows[0]['group'],'all')
  self.assertEqual(rows[2]['weighted_households'],D(0))
 def test_reject_missing_tax_fields(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'bad.csv';p.write_text('household_id,weight,market_income\n1,1,30000\n')
   with self.assertRaisesRegex(ValueError,'Missing required'):load_records(p)
 def test_reject_duplicate_household(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'dupe.csv'
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(self.records[0]));w.writeheader();w.writerow(self.records[0]);w.writerow(self.records[0])
   with self.assertRaisesRegex(ValueError,'duplicate'):load_records(p)
 def test_tied_income_mass_conserved(self):
  for x in self.records:x['market_income']=D(0)
  q=weighted_decile_fragments(self.records)
  self.assertEqual(sum((w for sub in q for _,w in sub),D(0)),sum((r['weight'] for r in self.records),D(0)))
 def test_partial_tax_refund_allowed(self):
  self.records[0]['reform_federal_tax']=-D(10)
  self.assertTrue(analyze(self.records)[0]['average_disposable_change']>0)
