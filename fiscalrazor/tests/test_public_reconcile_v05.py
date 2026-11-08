"""Cross-artifact reconciliation, not official-source-byte verification."""
import unittest
from decimal import Decimal
from fiscal_data.reconcile_public import (
    reconcile_gdp,reconcile_cbo,reconcile_ssa,reconcile_cms_hi,
    static_gap,expanded_unique_resources,run_comparison)

class CrossSessionReconciliation(unittest.TestCase):
    def test_direct_cbo_gdp_agrees_all_11_fy(self):self.assertEqual(reconcile_gdp(),11)
    def test_cbo_seven_indicators_match_each_fy(self):self.assertEqual(reconcile_cbo(),77)
    def test_all_33_ssa_option_years_match(self):self.assertEqual(reconcile_ssa(),33)
    def test_all_11_cms_hi_years_and_five_fields_match(self):self.assertEqual(reconcile_cms_hi(),55)
    def test_exact_static_target_gap(self):
        self.assertEqual(Decimal(static_gap()['FY2036_gap_bn']),Decimal('1714.022728075'))
    def test_source_registry_not_counted_as_unique_datasets(self):
        reg=expanded_unique_resources();self.assertEqual(reg['our_entries'],51)
        self.assertEqual(reg['other_entries'],56)
        self.assertLess(reg['distinct_normalized_endpoint_paths'],107)
        self.assertIn('not a count',reg['note'])
    def test_scoring_status_fail_closed(self):
        r=run_comparison()
        self.assertEqual(r['total_compared'],176)
        self.assertFalse(r['external_original_archive_bytes_acquired'])
        self.assertEqual(r['joint_fiscal_score'],'UNSCORED')
        self.assertEqual(r['household_distribution'],'NOT_ESTABLISHED')
        self.assertEqual(r['official_CBO_JCT_SSA_CMS_combined_score'],'NOT_ESTABLISHED')

if __name__=='__main__':unittest.main()
