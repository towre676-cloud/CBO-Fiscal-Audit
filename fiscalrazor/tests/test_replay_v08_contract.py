"""Cross-source admission and annual-fiscal objective tests. Synthetic fixtures only where noted."""
from __future__ import annotations
import csv, tempfile, unittest
from pathlib import Path
from decimal import Decimal as D
from fiscal_data.primary_ingest_v08 import status,source_specs,OriginalSourceError
from fiscal_data.research_v08 import annual_objectives,evidence_completion,ALL_PAIR_INTERACTIONS,NEEDS
from fiscal_data.v06_law import EXPECTED_IDS

class TestV08Contract(unittest.TestCase):
 def test_18_immutable_cbo_source_descriptions(self):
  specs=source_specs()
  cbo=[s for k,s in specs.items() if k.startswith('cbo_')]
  self.assertEqual(len(cbo),18)
  self.assertEqual(sum(x['expected_csv_rows'] for x in cbo),97459)
  self.assertTrue(all(len(x['expected_git_blob_sha1'])==40 for x in cbo))
 def test_2027_through_2036_objectives_all_numeric_and_distinct(self):
  rows=annual_objectives()
  self.assertEqual([r['fy'] for r in rows],list(range(2027,2037)))
  for r in rows:
   deficit=D(r['baseline_deficit_bn']);interest=D(r['baseline_interest_bn'])
   primary=D(r['baseline_primary_deficit_bn']);gdp=D(r['nominal_gdp_bn'])
   self.assertEqual(deficit,primary+interest)
   self.assertEqual(D(r['three_percent_deficit_limit_bn']),gdp*D('0.03'))
  self.assertEqual(D(rows[-1]['three_percent_gap_bn']),D('1714.022728075'))
 def test_3_pct_gap_not_a_claimed_package_effect(self):
  self.assertIn('NOT_PACKAGE_SCORE',annual_objectives()[-1]['classification'])
 def test_66_pairwise_covers_each_provision_once_each_other(self):
  self.assertEqual(len(ALL_PAIR_INTERACTIONS),66)
  self.assertEqual(len(set(ALL_PAIR_INTERACTIONS)),66)
  counts={i:sum(i in p for p in ALL_PAIR_INTERACTIONS) for i in EXPECTED_IDS}
  self.assertEqual(set(counts.values()),{11})
 def test_evidence_before_policy_modeling_is_blocked(self):
  with tempfile.TemporaryDirectory() as td:
   gates=evidence_completion(td)
   self.assertEqual(len(gates),12)
   self.assertTrue(all(g['raw_input_gate']=='BLOCKED_ORIGINAL_DATA' for g in gates))
   self.assertTrue(all(g['national_policy_score']=='NOT_ESTABLISHED' for g in gates))
 def test_cbo_account_original_needed_for_defense_provision(self):
  self.assertIn('cbo_17',NEEDS['defense_budget'])
 def test_irs_and_cps_universes_remain_different(self):
  s=source_specs()
  self.assertNotEqual(s['irs_soi_2023_zip_agi']['unit'],s['cps_asec_2026_csv']['unit'])

if __name__=='__main__':unittest.main()
