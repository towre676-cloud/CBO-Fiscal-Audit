import unittest,json,csv,sys,io
from pathlib import Path
from decimal import Decimal as D, ROUND_HALF_UP
from fiscal_data.v06_law import EXPECTED_IDS, scenario,baseline_gap,defense_caps,validate_spec
from fiscal_data.v06_frontier import PAIRS
ROOT=Path(__file__).resolve().parents[1]
def rows(path):return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))

class EvidenceArtifacts(unittest.TestCase):
 def test_legislation_sections(self):
  txt=(ROOT/'legislation/ILLUSTRATIVE_FISCAL_REFORM_ACT_2027.md').read_text()
  for s in range(101,113):self.assertIn(f'Section {s}',txt)
 def test_research_program_preserved(self):self.assertTrue((ROOT/'research/OUR_RESEARCH_PROGRAM.md').is_file())
 def test_budget_year_matrix_not_zero(self):
  p=rows(ROOT/'data/v06/provision_year_120_UNSCORED_TEMPLATE.csv')
  self.assertEqual(len(p),120);self.assertTrue(all(x['status']=='UNSCORED_NOT_ZERO' and x['primary_balance_effect_bn']=='' for x in p))
 def test_interactions_not_zero(self):
  p=rows(ROOT/'data/v06/interaction_year_90_UNSCORED_TEMPLATE.csv')
  self.assertEqual(len(p),90);self.assertTrue(all(x['net_primary_balance_effect_bn']=='' for x in p))
 def test_pairs_all_66(self):self.assertEqual(len(rows(ROOT/'data/v06/all_policy_pairs_66.csv')),66)
 def test_ownership_unique(self):
  a=rows(ROOT/'data/v06/provision_cash_and_fund_ownership.csv')
  self.assertEqual([p['provision_id'] for p in a],list(EXPECTED_IDS))
 def test_ba_caps_exact_round(self):
  for x in rows(ROOT/'data/v06/defense_ba_cap_locked.csv'):
   expected=(D(x['cbo_2026_02_defense_base_BA_bn'])*D('.95')).quantize(D('.001'),rounding=ROUND_HALF_UP)
   self.assertEqual(D(x['draft_95pct_nominal_cap_bn']),expected)
 def test_source_status_normalized(self):
  status=json.loads((ROOT/'results/v06/source_gate.json').read_text());self.assertEqual(status['sources'],status['materialized_originals']+status['not_acquired_direct']+status['landing_or_API_only'])
 def test_no_actual_distribution(self):
  s=json.loads((ROOT/'results/v06/research_status.json').read_text());self.assertEqual(s['real_national_household_incidence'],'NOT_COMPUTED_NO_MICRODATA')
 def test_workbench_has_12_and_warning(self):
  text=(ROOT/'policy_workbench_v06.html').read_text();self.assertEqual(text.count('<details>'),12);self.assertIn('not a predicted real household burden',text.lower())
 def test_2036_static_identity(self):
  x=baseline_gap()[-1];self.assertEqual(D(x['static_improvement_required_bn']),D(x['baseline_deficit_bn'])-D(x['max_deficit_3pct_bn']))

if __name__=='__main__':unittest.main()
