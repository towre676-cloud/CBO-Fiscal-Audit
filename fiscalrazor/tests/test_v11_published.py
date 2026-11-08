import unittest
from decimal import Decimal as D
from fiscal_data.v11_published import (
 ce_quintile_exposure,ce_vs_bea_2025_coverage_diagnostic,
 ssa_mechanical_rate_phaseup,vat_pce_fiscal_gap,hi_rounding_sensitivity,
 high_cost_min_scale_rounding)

class TestPublishedAggregates(unittest.TestCase):
    def test_bls_2025_quintile_count(self):
        a=ce_quintile_exposure()
        self.assertEqual(len(a),5)
        self.assertEqual(sum(int(x['published_consumer_units_thousands']) for x in a),137995)
    def test_bls_first_last_means(self):
        r=ce_quintile_exposure()
        self.assertEqual(r[0]['published_mean_all_expenditures_usd'],D('37935'))
        self.assertEqual(r[-1]['published_mean_pretax_income_usd'],D('286188'))
    def test_bls_burden_ratio_diagnostic_not_net_tax(self):
        r=ce_quintile_exposure()
        self.assertGreater(r[0]['tax_on_group_mean_spending_divided_by_group_mean_income_pct'],D('5'))
        self.assertLess(r[-1]['tax_on_group_mean_spending_divided_by_group_mean_income_pct'],D('1.5'))
        self.assertTrue(all(x['national_household_incidence']=='NOT_IDENTIFIED' for x in r))
    def test_zero_and_one_taxable_fraction(self):
        lo=ce_quintile_exposure(0)
        hi=ce_quintile_exposure(1)
        self.assertEqual(sum(x['hypothetical_weighted_group_exposure_bn'] for x in lo),0)
        self.assertEqual(hi[0]['hypothetical_annual_tax_on_group_mean_spending_usd'],D('1896.75'))
    def test_bad_fraction_rejected(self):
        with self.assertRaises(ValueError):ce_quintile_exposure(D('1.1'))
    def test_bea_concept_bridge_real_means(self):
        x=ce_vs_bea_2025_coverage_diagnostic()
        self.assertEqual(x['BLS_quintile_mean_times_consumer_units_bn'],D('11303.542001'))
        self.assertEqual(x['BEA_annual_PCE_bn'],D('20870.15'))
        self.assertAlmostEqual(float(x['ratio_BLS_expanded_survey_to_BEA_PCE']),.54161288,7)
    def test_ssa_2036_phaseup_base_only(self):
        x=ssa_mechanical_rate_phaseup()
        self.assertEqual(len(x),10)
        self.assertEqual(x[-1]['constant_base_additional_OASDI_tax_liability_bn'],D('171.25'))
        self.assertEqual(x[0]['constant_base_additional_OASDI_tax_liability_bn'],D('0'))
    def test_ssa_2028_and_2032(self):
        x={r['calendar_year']:r for r in ssa_mechanical_rate_phaseup()}
        self.assertEqual(x[2028]['constant_base_additional_OASDI_tax_liability_bn'],D('24.132'))
        self.assertEqual(x[2032]['constant_base_additional_OASDI_tax_liability_bn'],D('145.41'))
    def test_separate_ssa_calendar_and_cbo_fiscal(self):
        s=ssa_mechanical_rate_phaseup(); f=vat_pce_fiscal_gap()
        self.assertTrue(all('calendar_year' in x and 'fiscal_year' not in x for x in s))
        self.assertTrue(all('fiscal_year' in x and 'calendar_year' not in x for x in f))
        self.assertTrue(all(x['FY_cash_or_interest_effect']=='NOT_CALCULATED' for x in s))
    def test_cbo_2036_pce(self):
        x=vat_pce_fiscal_gap()[-1]
        self.assertEqual(x['CBO_FY_PCE_total_bn'],D('31989.63122405'))
        self.assertEqual(x['FY_3pct_deficit_static_target_gap_bn'],D('1714.022728075'))
        self.assertEqual(x['actual_VAT_effect'],'NOT_IDENTIFIED')
    def test_cms_rounding_contains_reported_nominal_model(self):
        x=hi_rounding_sensitivity()
        self.assertEqual(len(x),33)
        from fiscal_data.v10_potential import hi_scenarios
        old={(r['calendar_year'],r['scenario']):r for r in hi_scenarios()}
        for r in x:
            k=(r['calendar_year'],r['scenario'])
            z=old[k]['frozen_baseline_year_end_assets_bn']
            self.assertLessEqual(r['frozen_assets_after_tax_lower_rounding_bn'],z)
            self.assertGreaterEqual(r['frozen_assets_after_tax_upper_rounding_bn'],z)
    def test_hi_high_cost_more_than_one(self):
        x=high_cost_min_scale_rounding()
        self.assertGreater(x['min_scalar_for_nonnegative_2028_2035_yearend_high_cost_optimistic_rounding'],1)
        self.assertLess(x['min_scalar_for_nonnegative_2028_2035_yearend_high_cost_conservative_rounding'],2)
        self.assertLess(x['min_scalar_for_nonnegative_2028_2035_yearend_high_cost_optimistic_rounding'],x['min_scalar_for_nonnegative_2028_2035_yearend_high_cost_conservative_rounding'])
    def test_hi_2035_high_cost_always_negative_with_original_rate(self):
        x=[r for r in hi_rounding_sensitivity() if r['calendar_year']==2035 and r['scenario']=='high_cost'][0]
        self.assertLess(x['frozen_assets_after_tax_upper_rounding_bn'],0)
    def test_scenario_includes_zero_extra_2027(self):
        x=[r for r in hi_rounding_sensitivity() if r['calendar_year']==2027 and r['scenario']=='intermediate'][0]
        self.assertEqual(x['cumulative_extra_HI_tax_upper_rounding_bn'],0)

    def test_all_policy_sections_report_unscored(self):
        from pathlib import Path
        import csv
        p=Path(__file__).resolve().parents[1]/'data/v11/joint_policy_readiness.csv'
        with p.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
        self.assertEqual([int(r['section']) for r in rows],list(range(101,113)))
        self.assertTrue(all(r['national_policy_2027_2036_cash_score']=='UNSCORED' for r in rows))
    def test_BLS_mean_counts_rounded_not_137994(self):
        groups=ce_quintile_exposure()
        self.assertEqual(sum(int(r['published_consumer_units_thousands']) for r in groups),137995)
        # Published all-CU count is 137,994 thousand: one thousand units
        # difference results from source rounding, not duplicate sample units.
        self.assertEqual(sum(int(r['published_consumer_units_thousands']) for r in groups)-137994,1)

if __name__=='__main__':unittest.main()
