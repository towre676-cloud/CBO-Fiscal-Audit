import unittest,sys
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data import v10_potential as v

class TestV10RealPotential(unittest.TestCase):
    def test_legal(self):self.assertEqual(len(v.legal_spec()['policies']),12)
    def test_baseline_gap_2036(self):self.assertEqual(v.target_gap(2036)['static_gap_to_3pct_bn'],D('1714.022728075'))
    def test_baseline_gap_2034(self):self.assertEqual(v.target_gap(2034)['static_gap_to_3pct_bn'],D('1517.30031742275'))
    def test_no_2025_gap(self):
        with self.assertRaises(v.EvidenceBoundary):v.target_gap(2025)
    def test_10_years_available(self):self.assertEqual(len([v.target_gap(y) for y in range(2027,2037)]),10)
    def test_analogues_complete(self):self.assertEqual(len(v.analogues()),12)
    def test_analogue_selected_fy_only(self):
        with self.assertRaises(v.EvidenceBoundary):v.analogue_comparison(2036)
    def test_analogue_no_missing_as_zero(self):self.assertEqual(sum(r['official_analogue_bn'] is None for r in v.analogue_comparison()),3)
    def test_no_analogue_is_own_law(self):self.assertTrue(all(r['our_law_score']=='UNSCORED' for r in v.analogue_comparison()))
    def test_cannot_add_analogues(self):
        with self.assertRaises(v.EvidenceBoundary):v.cannot_combine_comparators(v.analogue_comparison())
    def test_analogue_vat(self):self.assertEqual(v.analogue_comparison()[0]['official_analogue_bn'],D('290'))
    def test_analogue_high_wage(self):self.assertEqual(v.analogue_comparison()[5]['official_analogue_bn'],D('192'))
    def test_ssa_years(self):self.assertEqual(len(v.ssa_annual_balance_equivalents()),11)
    def test_ssa_2036_e25(self):self.assertEqual(v.ssa_annual_balance_equivalents()[-1]['E2_5_balance_dollar_equiv_bn'],D('433.2625'))
    def test_ssa_2034_e25(self):self.assertEqual(v.ssa_annual_balance_equivalents()[-3]['E2_5_balance_dollar_equiv_bn'],D('400.7773'))
    def test_ssa_2036_base_mechanical(self):self.assertEqual(v.ssa_annual_balance_equivalents()[-1]['our_107_1pp_base_oasdi_mechanical_bn'],D('171.25'))
    def test_hi_all_cases(self):self.assertEqual(len(v.hi_scenarios()),33)
    def test_hi_no_new_tax_in_2027(self):self.assertTrue(all(r['new_mechanical_hi_tax_bn']==0 for r in v.hi_scenarios() if r['calendar_year']<2028))
    def test_hi_new_tax_rate_2028(self):self.assertTrue(all(r['draft112_extra_combined_hi_rate_pp']==D('.25') for r in v.hi_scenarios() if r['calendar_year']==2028))
    def test_hi_new_tax_rate_2030(self):self.assertTrue(all(r['draft112_extra_combined_hi_rate_pp']==D('.75') for r in v.hi_scenarios() if r['calendar_year']>=2030))
    def test_hi_intermediate_2035_positive(self):
        row=next(r for r in v.hi_scenarios() if r['calendar_year']==2035 and r['scenario']=='intermediate')
        self.assertGreater(row['frozen_baseline_year_end_assets_bn'],D('650'))
        self.assertLess(row['frozen_baseline_year_end_assets_bn'],D('660'))
    def test_hi_high_2033_negative(self):
        r=next(r for r in v.hi_scenarios() if r['calendar_year']==2033 and r['scenario']=='high_cost')
        self.assertLess(r['frozen_baseline_year_end_assets_bn'],0)
    def test_hi_high_2032_positive(self):
        r=next(r for r in v.hi_scenarios() if r['calendar_year']==2032 and r['scenario']=='high_cost')
        self.assertGreater(r['frozen_baseline_year_end_assets_bn'],0)
    def test_hi_low_2035_positive(self):
        r=next(r for r in v.hi_scenarios() if r['calendar_year']==2035 and r['scenario']=='low_cost')
        self.assertGreater(r['frozen_baseline_year_end_assets_bn'],D('1800'))
    def test_hi_threshold_positive(self):self.assertTrue(all(x['min_scalar_for_100pct_yearend_reserve_in_2035_only']>0 for x in v.hi_thresholds()))
    def test_hi_high_threshold_greater(self):
        s={r['scenario']:r for r in v.hi_thresholds()}
        self.assertGreater(s['high_cost']['min_scalar_for_100pct_yearend_reserve_in_2035_only'],s['intermediate']['min_scalar_for_100pct_yearend_reserve_in_2035_only'])
    def test_static_all_pce_2034(self):self.assertGreater(v.mechanical_consumption_benchmark()['upper_static_gross_5pct_all_pce_bn'],D('1400'))
    def test_no_national_score(self):
        with self.assertRaises(v.EvidenceBoundary):v.refuse_national_score()
    def test_not_legal_vat_base(self):self.assertIn('FULL_PCE',v.mechanical_consumption_benchmark()['NOT_AN_ESTIMATE_OF_OUR_VAT'])
    def test_2034_not_2036_analogue(self):self.assertEqual({r['comparator_fy'] for r in v.analogue_comparison()},{2034})
    def test_not_fiscal_ssa(self):self.assertTrue(all('NOT_FY_CASH' in r['score_status'] for r in v.ssa_annual_balance_equivalents()))

if __name__=='__main__':unittest.main()

class TestV10ExactHouseholdMath(unittest.TestCase):
    def test_household_9_thresholds(self):self.assertEqual(len(v.vat_household_thresholds_by_poverty_multiple()),9)
    def test_household_full_credit_below_2p(self):
        self.assertTrue(all(r['rebate_as_share_of_HHS_guideline']==D('.05') for r in v.vat_household_thresholds_by_poverty_multiple() if r['annual_MAGI_over_HHS_guideline']<=2))
    def test_household_credit_zero_above_3p(self):
        self.assertTrue(all(r['rebate_as_share_of_HHS_guideline']==0 for r in v.vat_household_thresholds_by_poverty_multiple() if r['annual_MAGI_over_HHS_guideline']>=3))
    def test_household_break_even_2point5p(self):
        r=next(r for r in v.vat_household_thresholds_by_poverty_multiple() if r['annual_MAGI_over_HHS_guideline']==D('2.5'))
        self.assertEqual(r['taxable_consumption_over_guideline_at_net_VAT_zero'],D('.5'))
    def test_low_income_1p_consumption_1point25p_net_loss(self):
        r=next(r for r in v.vat_household_thresholds_by_poverty_multiple() if r['annual_MAGI_over_HHS_guideline']==D('1.5'))
        self.assertEqual(r['tax_on_C_equal_1_25P_less_rebate_over_P'],D('.0125'))
    def test_2034_vat_all_pce_not_enough(self):self.assertGreater(v.vat_fixed_base_capacity(2034)['uncovered_gap_even_with_all_pce_taxed_and_no_rebates_bn'],D('30'))
    def test_2036_vat_all_pce_not_enough(self):self.assertGreater(v.vat_fixed_base_capacity(2036)['uncovered_gap_even_with_all_pce_taxed_and_no_rebates_bn'],D('110'))

class TestV10CBOQuantifiedSurtaxAndDefense(unittest.TestCase):
    def test_2028_top1_count(self):self.assertEqual(v.drafted_surtax_cy2028_top1_mechanical_lower_bound()['top1_returns_million'],D('1.721'))
    def test_2028_top1_AGI(self):self.assertEqual(v.drafted_surtax_cy2028_top1_mechanical_lower_bound()['top1_AGI_total_bn'],D('4597.1292'))
    def test_2028_top1_threshold(self):self.assertEqual(v.drafted_surtax_cy2028_top1_mechanical_lower_bound()['top1_aggregate_threshold_equivalent_bn'],D('1721'))
    def test_2028_mechanical_liability_lower_bound(self):self.assertEqual(v.drafted_surtax_cy2028_top1_mechanical_lower_bound()['nonbehavioral_top1_MAGI_surtax_liability_lower_bound_bn'],D('57.522584'))
    def test_scope_never_net_revenue(self):self.assertIn('NOT_TAX_REVENUE',v.drafted_surtax_cy2028_top1_mechanical_lower_bound()['status'])
    def test_defense_9(self):self.assertEqual(len(v.defense_budget_authority_reduction_path()),9)
    def test_defense_2034_BA(self):
        r=next(x for x in v.defense_budget_authority_reduction_path() if x['fy']==2034)
        self.assertEqual(r['mechanical_base_BA_delta_bn'],D('54.267'))
        self.assertIsNone(r['fiscal_year_outlay_delta_bn'])
    def test_defense_2036_BA(self):
        r=next(x for x in v.defense_budget_authority_reduction_path() if x['fy']==2036)
        self.assertEqual(r['mechanical_base_BA_delta_bn'],D('56.826'))
