import unittest,tempfile,itertools
from decimal import Decimal
from fiscal_data.research_v08 import annual_objectives,evidence_completion,interval_target,NEEDS,ALL_PAIR_INTERACTIONS
from fiscal_data.primary_ingest_v08 import OriginalSourceError
from fiscal_data.v06_law import EXPECTED_IDS
ZERO_PAIRS={pair:(0,0) for pair in ALL_PAIR_INTERACTIONS}

class TestResearchV08(unittest.TestCase):
 def test_ten_year_objectives(self):
  a=annual_objectives();self.assertEqual(len(a),10)
  self.assertEqual(a[-1]['three_percent_gap_bn'],'1714.022728075')
 def test_debt_ratio_one_year_target(self):
  a=annual_objectives()
  self.assertAlmostEqual(float(a[-1]['one_year_debt_ratio_improvement_bn']),1042.80050811994,places=7)
 def test_debt_ratio_and_3pct_not_same(self):
  a=annual_objectives()[-1]
  self.assertNotEqual(a['one_year_debt_ratio_improvement_bn'],a['three_percent_gap_bn'])
 def test_twelve_policy_requirements_complete(self):
  self.assertEqual(set(NEEDS),set(EXPECTED_IDS))
 def test_12_policy_evidence_blocked_when_raw_missing(self):
  with tempfile.TemporaryDirectory() as td:
   x=evidence_completion(td)
   self.assertEqual(len(x),12)
   self.assertTrue(all(r['raw_input_gate']=='BLOCKED_ORIGINAL_DATA' for r in x))
 def test_interval_no_missing_provision_allowed(self):
  with self.assertRaisesRegex(OriginalSourceError,'TWELVE'):
   interval_target({},ZERO_PAIRS,2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
 def test_interval_no_missing_interactions_allowed(self):
  with self.assertRaisesRegex(OriginalSourceError,'SIXTY_SIX'):
   interval_target({i:(0,0) for i in EXPECTED_IDS},{},2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
 def test_interval_interest_cannot_be_assumed_zero(self):
  with self.assertRaisesRegex(OriginalSourceError,'INTEREST'):
   interval_target({i:(0,0) for i in EXPECTED_IDS},ZERO_PAIRS,2036,higher_order_residual_bounds=(0,0))
 def test_interval_upper_below_target(self):
  a=interval_target({i:(0,10) for i in EXPECTED_IDS},ZERO_PAIRS,2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
  self.assertEqual(a['logical_result'],'CONDITIONALLY_REJECT_TARGET')
 def test_interval_lower_above_target(self):
  a=interval_target({i:(180,190) for i in EXPECTED_IDS},ZERO_PAIRS,2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
  self.assertEqual(a['logical_result'],'CONDITIONALLY_GUARANTEE_TARGET')
 def test_interval_indeterminate(self):
  a=interval_target({i:(0,200) for i in EXPECTED_IDS},ZERO_PAIRS,2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
  self.assertEqual(a['logical_result'],'CONDITIONALLY_INDETERMINATE')
 def test_invalid_interval_rejected(self):
  with self.assertRaisesRegex(OriginalSourceError,'INVALID_INTERVAL'):
   interval_target({i:(10,0) for i in EXPECTED_IDS},ZERO_PAIRS,2036,interest_bounds=(0,0),higher_order_residual_bounds=(0,0))
