import unittest
import tempfile
import csv
from pathlib import Path
from decimal import Decimal as D
from src import fiscalrazor as fr

class PublishedAnchorTests(unittest.TestCase):
 def test_budget_accounts_all_years(self): self.assertEqual([],fr.audit_baseline())
 def test_baseline_year_count(self): self.assertEqual(11,len(fr.baseline_rows()))
 def test_published_2036_exact(self):
  r=fr.baseline_rows()[-1]
  self.assertEqual('2036',r['year'])
  self.assertEqual(D('-3115.387'),D(r['deficit_billion']))
  self.assertEqual(D('2144.336'),D(r['net_interest_billion']))
  self.assertEqual(D('56152.391'),D(r['debt_public_billion']))
 def test_2036_policy_gap_not_score(self):
  t=fr.target_2036()
  self.assertEqual(D('1714.02'),D(t['required_reduction_before_policy_feedback_billion']))
  self.assertIn('NOT_A_POLICY_SCORE',t['status'])
  self.assertEqual(D('46712.1423975'), D(t['nominal_gdp_billion']))
  self.assertEqual(D('1401.36'), D(t['target_deficit_3pct_gdp_billion']))
 def test_jct_worked_example(self): self.assertEqual([],fr.audit_jct())
 def test_ssa_anchors(self): self.assertEqual([],fr.audit_ssa())
 def test_nonadditive_trust_fund_options(self):
  r=fr.ssa_option_series('B1.2_progressive_price_indexing_2033_30th_pct')
  self.assertEqual(D('0.01'),dict(r)[2036])
 def test_policy_gate_stays_closed(self):
  s=fr.score_status()
  self.assertEqual(0,s['scored'])
  self.assertEqual('NOT_ESTABLISHED',s['combined_score'])
 def test_source_registry(self):
  import json
  entries=json.loads((fr.ROOT/'data/public_source_registry.json').read_text())
  self.assertGreaterEqual(len(entries),30)
  self.assertTrue(all(e['url'].startswith('https://') for e in entries))
  self.assertEqual(len(entries),len(set(e['id'] for e in entries)))
 def test_check_official_rejects_incomplete_dummy(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/'not_cbo.csv'
   p.write_text('date,variable,value\nFY2036,proj_rev_total,8300.755\n')
   problems=fr.full_cbo_csv_check(p)
   self.assertGreater(len(problems),20)
 def test_check_official_detects_tampering(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/'tampered.csv'
   p.write_text('date,variable,value\nFY2036,proj_deficit_total,-9999\n')
   problems=fr.full_cbo_csv_check(p)
   self.assertTrue(any('transcribed' in v for v in problems))

if __name__ == '__main__':unittest.main()

class ScoreGateTests(unittest.TestCase):
 def test_empty_files_are_not_scores(self):
  from src.score_gate import audit_candidate
  result=audit_candidate(fr.ROOT/'data/policy_effects_TEMPLATE.csv',fr.ROOT/'data/joint_interactions_TEMPLATE.csv')
  self.assertFalse(result['gate_passed'])
  self.assertIn('NOT_ESTABLISHED',result['combined_federal_net_savings'])
  self.assertTrue(any('provision-year' in s for s in result['problems']))
 def test_ledger_requires_reviewed_provenance(self):
  from src.score_gate import audit_candidate
  with tempfile.TemporaryDirectory() as d:
   impact=Path(d)/'impacts.csv'
   interaction=Path(d)/'interactions.csv'
   impact.write_text((fr.ROOT/'data/policy_effects_TEMPLATE.csv').read_text()+
     'corporate_tax_rate,2036,corporate-income-tax,300,0,https://example.com,,not_reviewed,2026-02,federal_fy_nominal_billions_cash\n')
   interaction.write_text((fr.ROOT/'data/joint_interactions_TEMPLATE.csv').read_text())
   result=audit_candidate(impact,interaction)
   self.assertFalse(result['gate_passed'])
   self.assertTrue(any('provenance' in x or 'not independently reviewed' in x for x in result['problems']))

class SSACrossSourceMathTests(unittest.TestCase):
 def test_2035_ssa_derived_high_earnings(self):
  from src.ssa_derived import approximate_ssa_cy2035_balance_change
  r=approximate_ssa_cy2035_balance_change('E2.5_high_earner_tax_250k_no_benefit_credit')
  self.assertEqual('415.4472',r['derived_annual_actuarial_balance_improvement_billion'])
  self.assertIn('NOT_FY_CASH',r['status'])
  self.assertEqual(D('0.82430'),D(r['pct_rounding_only_uncertainty_bound_billion']))

class CBOVintageDiscoveryTests(unittest.TestCase):
 def test_discover_vintage_from_real_catalog_schema(self):
  from scripts.fetch_cbo_catalog_all import catalog_entries
  data={'datasets':[{'identifier':'one','distribution':[
    {'vintage':'2026-02','downloadURL':'data/budget/a/annual_fy_2026-02.csv','mediaType':'text/csv','file_type':'annual_fy'},
    {'vintage':'2024-06','downloadURL':'data/budget/a/annual_fy_2024-06.csv'},
    {'vintage':'2026-02','downloadURL':'../secrets.csv'},
    {'vintage':'2026-02','downloadURL':'https://evil.test/malware.csv'},
  ]}]}
  rows=catalog_entries(data,'2026-02')
  self.assertEqual(1,len(rows))
  self.assertIn('annual_fy_2026-02.csv',rows[0]['relative_path'])


class CBONominalGDPTests(unittest.TestCase):
 def test_gdp_year_range_and_ratio(self):
  self.assertEqual(11,len(fr.gdp_rows()))
  self.assertEqual([],fr.audit_baseline())
 def test_full_gdp_source_parsing(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'full.csv'
   with path.open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['date','variable','value'])
    for r in fr.gdp_rows():writer.writerow(['FY'+r['year'],'gdp',r['nominal_gdp_billion']])
   self.assertEqual([],fr.full_cbo_gdp_csv_check(path))
   path.write_text(path.read_text().replace('FY2036,gdp,46712.1423975','FY2036,gdp,1'))
   self.assertTrue(any('FY2036' in e for e in fr.full_cbo_gdp_csv_check(path)))
 def test_all_years_have_3pct_gap(self):
  path=fr.fiscal_year_gap_path()
  self.assertEqual(11,len(path))
  self.assertEqual('1714.02',path[-1]['gap_to_target_billion'])
  self.assertEqual('BASELINE_ARITHMETIC_ONLY_NOT_A_POLICY_SCORE',path[-1]['status'])
