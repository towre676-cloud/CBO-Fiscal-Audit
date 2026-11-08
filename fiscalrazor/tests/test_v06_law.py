import unittest
from decimal import Decimal as D
from datetime import date
from fiscal_data.v06_law import (validate_spec,scenario,policies,EXPECTED_IDS,dec,fiscal_year,phase_extra_rate,hi_extra_each_side,
 hi_mechanical_new_tax,high_threshold,payroll_decomposition,surtax_2028,itemized_cap_additional_tax_2028,
 employer_health_inclusion_2028,vat_rebate_assessment,corporate_mechanical_2028,defense_caps,admit_national_score,
 baseline_gap, MissingEvidence,BadSpecification)
from fiscal_data.v06_frontier import robust_target_status,EffectBound,PAIRS

class LegalParameters(unittest.TestCase):
 def test_count(self): self.assertTrue(validate_spec());self.assertEqual(len(scenario()['policies']),12)
 def test_ids(self):self.assertEqual(tuple(policies()),EXPECTED_IDS)
 def test_sections(self):self.assertEqual([int(p['section']) for p in scenario()['policies']],list(range(101,113)))
 def test_all_unscored(self):self.assertTrue(all(p['official_score'] is None and p['model_estimate'] is None for p in scenario()['policies']))
 def test_first_effect_2028(self):self.assertEqual(phase_extra_rate(2027),D(0));self.assertEqual(phase_extra_rate(2028),D('.001'))
 def test_phase_2032(self):self.assertEqual(phase_extra_rate(2032),D('.005'));self.assertEqual(phase_extra_rate(2036),D('.005'))
 def test_phase_2029(self):self.assertEqual(phase_extra_rate(2029),D('.002'))
 def test_hi_2027(self):self.assertEqual(hi_mechanical_new_tax(1_000_000,2027),0)
 def test_hi_2028(self):self.assertEqual(hi_mechanical_new_tax(1_000_000,2028),D('2500'))
 def test_hi_2030(self):self.assertEqual(hi_mechanical_new_tax(1_000_000,2030),D('7500'))
 def test_hi_2036(self):self.assertEqual(hi_mechanical_new_tax(1_000_000,2036),D('7500'))
 def test_hi_not_capped(self):self.assertEqual(hi_mechanical_new_tax(2_000_000,2031),2*hi_mechanical_new_tax(1_000_000,2031))
 def test_oasdi_no_high_before_2028(self):self.assertEqual(payroll_decomposition(350000,2027,192300)['increment'],0)
 def test_high_2028(self):self.assertEqual(high_threshold(2028,192300),D(250000))
 def test_high_avoid_overlap(self):self.assertEqual(high_threshold(2028,260000),D(260000))
 def test_high_2029_requires_AWI(self):
  with self.assertRaises(MissingEvidence):high_threshold(2029,195000)
 def test_high_2029_index(self):self.assertEqual(high_threshold(2029,195000,awi_2026=60000,awi_lagged=60600),D(253000))
 def test_oasdi_increment_2028(self):self.assertEqual(payroll_decomposition(350000,2028,192300)['increment'],D('12984.600'))
 def test_oasdi_no_double_tax_when_wage_cap_large(self):self.assertEqual(payroll_decomposition(270000,2028,270000)['taxable_high'],0)
 def test_oasdi_interaction(self):
  p=payroll_decomposition(350000,2028,192300)
  self.assertEqual(p['increment'],p['high_band']+p['base_rate']+p['interaction'])
  self.assertEqual(p['interaction'],D('200'))
 def test_statutory_surtax(self):self.assertEqual(surtax_2028(1200000,'mfj'),D('4000'))
 def test_surtax_below(self):self.assertEqual(surtax_2028(900000,'mfj'),0)
 def test_itemized_benefit_limit(self):self.assertEqual(itemized_cap_additional_tax_2028(900000,'mfj',50000,18500,0),D('4500'))
 def test_itemized_below_threshold(self):self.assertEqual(itemized_cap_additional_tax_2028(400000,'mfj',50000,18500,0),0)
 def test_itemized_no_penalty_when_benefit_low(self):self.assertEqual(itemized_cap_additional_tax_2028(900000,'mfj',50000,10000,0),0)
 def test_health_single(self):self.assertEqual(employer_health_inclusion_2028(20000,'self_only'),D('7000'))
 def test_health_family(self):self.assertEqual(employer_health_inclusion_2028(32000,'family'),D('1000'))
 def test_vat_lowincome(self):
  p=vat_rebate_assessment(20000,20000,20000);self.assertEqual(p['net_before_behavior'],0)
 def test_vat_non_filer_credit(self):
  p=vat_rebate_assessment(0,20000,0);self.assertEqual(p['refundable_credit'],D('1000'))
 def test_vat_highincome(self):
  p=vat_rebate_assessment(100000,20000,20000);self.assertEqual(p['refundable_credit'],0)
 def test_vat_credit_taper(self):
  p=vat_rebate_assessment(50000,20000,20000);self.assertEqual(p['refundable_credit'],D('500'))
 def test_corporate_rate(self):self.assertEqual(corporate_mechanical_2028(1000000),D('10000'))
 def test_corploss_rejected(self):
  with self.assertRaises(BadSpecification):corporate_mechanical_2028(-100)
 def test_negative_rejected(self):
  with self.assertRaises(BadSpecification):payroll_decomposition(-1,2028,200000)
 def test_fiscalization_dates(self):self.assertEqual(fiscal_year(date(2028,10,1)),2029);self.assertEqual(fiscal_year(date(2028,9,30)),2028)
 def test_ba_caps(self):self.assertEqual(defense_caps()[2036],D('1079.686'));self.assertEqual(len(defense_caps()),9)
 def test_gap(self):self.assertEqual(D(baseline_gap()[-1]['static_improvement_required_bn']),D('1714.022728075'))
 def test_primary_surplus(self):self.assertEqual(D(baseline_gap()[-1]['if_net_interest_fixed_target_primary_balance_bn']),D('742.971728075'))
 def test_annual_gap_nonzero(self):self.assertEqual(len(baseline_gap()),10);self.assertTrue(all(D(p['static_improvement_required_bn'])>0 for p in baseline_gap()))
 def test_joint_gate_rejects_empty(self):
  with self.assertRaises(MissingEvidence):admit_national_score([],[])
 def test_joint_gate_rejects_unsupported_zeros(self):
  rows=[dict(provision=i,fy=y,net_primary_balance_change_bn='0') for i in EXPECTED_IDS for y in range(2027,2037)]
  with self.assertRaises(MissingEvidence):admit_national_score(rows,[])
 def test_decimal_nan_rejected(self):
  with self.assertRaises(BadSpecification):dec('NaN')
 def test_frontier_requires_all(self):self.assertEqual(robust_target_status(2036,{}, {})['status'],'NOT_DETERMINABLE')
 def test_bound_requires_provenance(self):
  with self.assertRaises(MissingEvidence):EffectBound(D(0),D(1),'', '', 'MODELED', True)
 def test_bound_rejects_inverted(self):
  with self.assertRaises(ValueError):EffectBound(D(2),D(1),'http://x','0'*64,'MODELED',True)
 def test_pair_count(self):self.assertEqual(len(PAIRS),9)

if __name__=='__main__': unittest.main()

class MultiEmployerResearch(unittest.TestCase):
 def test_split_invariance(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  self.assertEqual(sum(a([350000],250000)),sum(a([175000,175000],250000)))
 def test_pro_rata_2_employers(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  self.assertEqual(a([180000,180000],250000),[D('55000'),D('55000')])
 def test_seca_aggregate(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  p=a([200000,100000,50000],250000)
  self.assertEqual(sum(p),D('100000'))
  self.assertEqual(p[0]*D('.062')*2+p[1]*D('.062')*2+p[2]*D('.124'),D('12400'))
 def test_no_excess_when_under(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  self.assertEqual(a([100000,150000],250000),[0,0])
 def test_reject_negative(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  with self.assertRaises(BadSpecification):a([100000,-1],250000)
 def test_employer_health_interaction(self):
  from fiscal_data.v06_law import high_band_proportional_allocation as a
  with_health=200000+employer_health_inclusion_2028(65000,'family')
  self.assertEqual(sum(a([with_health,100000],250000)),D('84000'))

class DebtRatioResearch(unittest.TestCase):
 def test_one_year_2036(self):
  from fiscal_data.v06_frontier import one_year_debt_ratio_stability
  x=one_year_debt_ratio_stability()[-1]
  self.assertEqual(D(x['frozen_one_year_debt_ratio_improvement_required_bn']).quantize(D('.001')),D('1042.801'))
 def test_other_financing_retained(self):
  from fiscal_data.v06_frontier import one_year_debt_ratio_stability
  x=one_year_debt_ratio_stability()[-1]
  self.assertEqual(D(x['other_financing_adjustment_bn']),D('-66.219'))
 def test_all_ten_years(self):
  from fiscal_data.v06_frontier import one_year_debt_ratio_stability
  x=one_year_debt_ratio_stability()
  self.assertEqual(len(x),10)
  self.assertEqual(x[0]['fy'],2027)
