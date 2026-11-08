import unittest
from decimal import Decimal as D
from fiscal_data.v11_joint import joint_wage_vat,Unidentified,assert_not_national_score


def case(year=2028, wage='100000', magi='100000', filing='single', healthcare='0', tier='self_only'):
    return {'calendar_year':year,'filing_status':filing,'household_is_one_tax_unit':True,
       'baseline_tax_unit_magi_usd':magi,'official_oasdi_wage_base_usd':'190000',
       'persons':[{'id':'p1','employers':[{'id':'a','cash_wages_usd':wage,'covered_under_OASDI_and_HI':True,
                      'employer_health_cost_usd':healthcare,'coverage_tier':tier,'health_cost_includes_section125_pretax':True}]}],
       'baseline_income_tax_before_reform_usd':'5000',
       'income_tax_after_health_inclusion_before_other_sections_usd':'5000',
       'source_record_provenance':'SYNTHETIC_UNIT_TEST'}

class TestJointStatutory(unittest.TestCase):
    def test_wage_only_2028(self):
        r=joint_wage_vat(case())
        x=r['components']
        self.assertEqual(x['106_107_oasdi_employee_increment_usd'],D('100'))
        self.assertEqual(x['106_107_oasdi_employer_increment_usd'],D('100'))
        self.assertEqual(x['112_hi_employee_increment_usd'],D('125'))
        self.assertEqual(x['112_hi_employer_increment_usd'],D('125'))
        self.assertEqual(x['additional_medicare_existing_0_9pct_delta_usd'],0)
        self.assertEqual(r['identified_statutory_liability_subtotal_usd'],D('450'))
        self.assertIsNone(r['full_12_provision_result'])
    def test_surtax_and_itemized_health_interaction(self):
        c=case(wage='498000',magi='498000',healthcare='17000')
        c.update({'baseline_income_tax_before_reform_usd':'105000',
        'income_tax_after_health_inclusion_before_other_sections_usd':'106300',
        'post_health_income_tax_without_itemized_usd':'118000',
        'post_health_income_tax_with_itemized_usd':'106300',
        'post_health_allowed_itemized_usd':'35000'})
        x=joint_wage_vat(c)['components']
        self.assertEqual(x['104_health_wage_inclusion_usd'],D('4000'))
        self.assertEqual(x['102_income_surtax_usd'],D('40'))
        self.assertEqual(x['102_surtax_health_interaction_usd'],D('40'))
        self.assertEqual(x['103_itemized_limitation_usd'],D('1900'))
        self.assertEqual(x['104_income_tax_change_usd'],D('1300'))
        self.assertEqual(x['additional_medicare_existing_0_9pct_delta_usd'],D('36'))
        self.assertGreater(x['106_107_oasdi_employee_increment_usd'],D('0'))
        self.assertGreater(x['112_hi_employer_increment_usd'],D('0'))
    def test_person_spouses_not_one_high_earner(self):
        c=case(filing='mfj',wage='150000',magi='300000')
        c['persons'] += [{'id':'p2','employers':[{'id':'b','cash_wages_usd':'150000','covered_under_OASDI_and_HI':True}]}]
        r=joint_wage_vat(c)
        self.assertEqual(sum(p['new_high_band_usd'] for p in r['people']),D(0))
        c['persons']=[{'id':'p1','employers':[{'id':'a','cash_wages_usd':'300000','covered_under_OASDI_and_HI':True}]}]
        one=joint_wage_vat(c)
        self.assertEqual(sum(p['new_high_band_usd'] for p in one['people']),D('50000'))
    def test_employer_splitting_high_band_invariant(self):
        c=case(wage='300000',magi='300000')
        before=joint_wage_vat(c)
        c['persons'][0]['employers']=[{'id':'a','cash_wages_usd':'100000','covered_under_OASDI_and_HI':True},
                                     {'id':'b','cash_wages_usd':'200000','covered_under_OASDI_and_HI':True}]
        after=joint_wage_vat(c)
        self.assertEqual(before['people'][0]['new_high_band_usd'], after['people'][0]['new_high_band_usd'])
        self.assertEqual(sum(after['people'][0]['employer_high_band_allocations_usd']),D('50000'))
        # Current-law employer OASDI applies per employer: do NOT assume whole 
        # payroll burden is invariant to employer splitting.
        self.assertNotEqual(before['components']['106_107_oasdi_employer_increment_usd'],
                            after['components']['106_107_oasdi_employer_increment_usd'])
    def test_vat_credit_taper_2029(self):
        c=case(year=2029,wage='50000',magi='50000')
        c.update({'indexed_high_band_threshold_usd':'255000',
          'indexed_surtax_threshold_usd':'520000','indexed_itemized_magi_threshold_usd':'309000',
          'classified_final_taxable_consumption_usd':'30000','documented_hhs_poverty_guideline_usd':'20000'})
        r=joint_wage_vat(c)
        self.assertEqual(r['components']['101_vat_gross_usd'],D('1500'))
        self.assertEqual(r['components']['101_refundable_vat_credit_usd'],D('500'))
        self.assertEqual(r['components']['101_vat_net_usd'],D('1000'))
    def test_vat_credit_is_additional_5pct_marginal_taper(self):
        c=case(year=2029,wage='50000',magi='50000',healthcare='0')
        c.update({'indexed_high_band_threshold_usd':'255000',
          'indexed_surtax_threshold_usd':'520000','indexed_itemized_magi_threshold_usd':'309000',
          'indexed_health_caps_usd':{'self_only':'13200','family':'32000'},
          'classified_final_taxable_consumption_usd':'30000','documented_hhs_poverty_guideline_usd':'20000'})
        r1=joint_wage_vat(c)
        c['persons'][0]['employers'][0]['employer_health_cost_usd']='15200'
        r2=joint_wage_vat(c)
        self.assertEqual(r2['components']['104_health_wage_inclusion_usd'],D('2000'))
        self.assertEqual(r2['components']['101_refundable_vat_credit_usd'],D('400'))
        self.assertEqual(r2['components']['101_vat_net_usd']-r1['components']['101_vat_net_usd'],D('100'))
    def test_extra_medicare_existing_tax(self):
        c=case(wage='198000',magi='198000',healthcare='17000')
        x=joint_wage_vat(c)['components']
        self.assertEqual(x['104_health_wage_inclusion_usd'],D('4000'))
        self.assertEqual(x['additional_medicare_existing_0_9pct_delta_usd'],D('18'))
    def test_missing_future_index_rejected(self):
        c=case(year=2029)
        with self.assertRaisesRegex(Unidentified,'future indexed high earnings threshold'):joint_wage_vat(c)
    def test_future_health_cap_rejected(self):
        c=case(year=2029,healthcare='40000')
        with self.assertRaisesRegex(Unidentified,'indexed health exclusion cap'):joint_wage_vat(c)
    def test_multiple_tax_units_rejected(self):
        c=case();c['household_is_one_tax_unit']=False
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_seca_not_omitted(self):
        c=case();c['persons'][0]['self_employment_income_usd']='20000'
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_duplicate_person_rejected(self):
        c=case();c['persons'] += c['persons']
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_duplicate_employer_rejected(self):
        c=case();c['persons'][0]['employers'] += c['persons'][0]['employers']
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_missing_income_tax_not_priced(self):
        c=case(wage='500000',magi='500000')
        c.pop('income_tax_after_health_inclusion_before_other_sections_usd')
        out=joint_wage_vat(c)
        self.assertIsNone(out['components']['104_income_tax_change_usd'])
        self.assertIsNone(out['identified_statutory_liability_subtotal_usd'])
    def test_missing_itemized_inputs_not_assumed_zero(self):
        c=case(wage='500000',magi='500000')
        out=joint_wage_vat(c)
        self.assertIsNone(out['components']['103_itemized_limitation_usd'])
        self.assertIsNone(out['identified_statutory_liability_subtotal_usd'])
    def test_itemization_tax_mismatch_rejected(self):
        c=case(magi='500000')
        c.update({'post_health_income_tax_without_itemized_usd':'10000',
          'post_health_income_tax_with_itemized_usd':'9000','post_health_allowed_itemized_usd':'1000'})
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_unreconciled_national_score_rejected(self):
        with self.assertRaises(Unidentified):assert_not_national_score([])
    def test_nonfinite_rejected(self):
        c=case(wage='NaN')
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_negative_wage_rejected(self):
        c=case(wage='-1')
        with self.assertRaises(Unidentified):joint_wage_vat(c)
    def test_pre_vat_year_has_no_vat(self):
        out=joint_wage_vat(case())
        self.assertEqual(out['components']['101_vat_net_usd'],D(0))
    def test_tax_not_federal_cash(self):
        out=joint_wage_vat(case())
        self.assertIsNone(out['fiscal_cash_timing'])
        self.assertTrue(out['statutory_payer_not_economic_burden'])
    def test_rate_increment_after_2032(self):
        c=case(year=2036)
        c.update({'indexed_high_band_threshold_usd':'320000',
          'indexed_surtax_threshold_usd':'650000',
          'indexed_itemized_magi_threshold_usd':'390000',
          'classified_final_taxable_consumption_usd':'30000',
          'documented_hhs_poverty_guideline_usd':'25000'})
        out=joint_wage_vat(c)
        self.assertEqual(out['components']['106_107_oasdi_employee_increment_usd'],D('500'))
        self.assertEqual(out['components']['106_107_oasdi_employer_increment_usd'],D('500'))
    def test_2036_uses_provided_statutory_indices_not_invented(self):
        c=case(year=2036)
        c.update({'indexed_high_band_threshold_usd':'320000',
          'indexed_surtax_threshold_usd':'650000',
          'indexed_itemized_magi_threshold_usd':'390000',
          'classified_final_taxable_consumption_usd':'30000',
          'documented_hhs_poverty_guideline_usd':'25000'})
        out=joint_wage_vat(c)
        self.assertEqual(out['people'][0]['new_high_band_threshold_usd'],D('320000'))

    def test_oasdi_decomposition_exact_two_employers(self):
        c=case(wage='280000',magi='280000',healthcare='17000')
        c['persons'][0]['employers'] += [{'id':'b','cash_wages_usd':'25000','covered_under_OASDI_and_HI':True}]
        result=joint_wage_vat(c)
        p=result['people'][0]
        expected=result['components']['106_107_oasdi_employee_increment_usd']+result['components']['106_107_oasdi_employer_increment_usd']
        self.assertEqual(sum(p['oasdi_statutory_decomposition_usd'].values()),expected)
    def test_high_band_and_phaseup_interaction_2028(self):
        c=case(wage='300000',magi='300000')
        r=joint_wage_vat(c)
        d=r['people'][0]['oasdi_statutory_decomposition_usd']
        self.assertEqual(d['old_rate_new_high_band_tax_usd'],D('6200'))
        self.assertEqual(d['phaseup_on_new_high_band_interaction_usd'],D('100'))
    def test_fica_coverage_required(self):
        c=case()
        c['persons'][0]['employers'][0].pop('covered_under_OASDI_and_HI')
        with self.assertRaisesRegex(Unidentified,'FICA covered'):joint_wage_vat(c)
    def test_pretax_health_cost_definition_required(self):
        c=case(healthcare='30000')
        c['persons'][0]['employers'][0].pop('health_cost_includes_section125_pretax')
        with self.assertRaisesRegex(Unidentified,'Section 125'):joint_wage_vat(c)
    def test_more_than_two_people_refused(self):
        c=case(filing='mfj')
        c['persons'] += [{'id':z,'employers':[{'id':'w'+z,'cash_wages_usd':'1','covered_under_OASDI_and_HI':True}]} for z in ('b','c')]
        with self.assertRaisesRegex(Unidentified,'at most two'):joint_wage_vat(c)
    def test_single_with_two_people_refused(self):
        c=case()
        c['persons'] += [{'id':'b','employers':[{'id':'w','cash_wages_usd':'1','covered_under_OASDI_and_HI':True}]}]
        with self.assertRaisesRegex(Unidentified,'only MFJ'):joint_wage_vat(c)
    def test_2029_missing_taxable_consumption_refused(self):
        c=case(year=2029)
        c.update({'indexed_high_band_threshold_usd':'260000',
          'indexed_surtax_threshold_usd':'530000','indexed_itemized_magi_threshold_usd':'315000'})
        with self.assertRaisesRegex(Unidentified,'classified_final_taxable_consumption'):joint_wage_vat(c)
    def test_married_additional_medicare_income_threshold(self):
        c=case(filing='mfj',wage='240000',magi='260000',healthcare='17000',tier='self_only')
        c['persons'] += [{'id':'p2','employers':[{'id':'b','cash_wages_usd':'16000','covered_under_OASDI_and_HI':True}]}]
        r=joint_wage_vat(c)
        self.assertEqual(r['components']['additional_medicare_existing_0_9pct_delta_usd'],D('36'))
    def test_no_multiple_health_plans_silently_combined(self):
        c=case(healthcare='17000')
        c['persons'][0]['employers'] += [{'id':'b','cash_wages_usd':'20000','covered_under_OASDI_and_HI':True,
            'employer_health_cost_usd':'17000','coverage_tier':'self_only','health_cost_includes_section125_pretax':True}]
        with self.assertRaisesRegex(Unidentified,'multiple health plans'):joint_wage_vat(c)

if __name__=='__main__':unittest.main()
