"""Cross-agency anchors and adverse input tests; all locally runnable."""
import unittest
from decimal import Decimal as D
from src.primary_bridges import (ssa_cash_audit,cms_hi_audit,bea_pce_audit,evidence_audit,
    ssa_dollar_equivalents,cms_hi_perturbation,pce_mechanical_reference,series)
from src.fiscalization import fiscalize_calendar_cash,rate_to_fy_exercise
from src.spendout import budget_authority_to_outlays
from src.distribution import Household,household_vat_effect,weighted_distribution,population_quality_gate
from scripts.check_ssa_live import normal_number, match_source_html

class PublicTables(unittest.TestCase):
    def test_cross_source_ssa(self): self.assertEqual([],ssa_cash_audit())
    def test_cms_hi_fund(self): self.assertEqual([],cms_hi_audit())
    def test_bea_pce_hierarchy(self): self.assertEqual([],bea_pce_audit())
    def test_new_gate_stays_not_official(self):
        e=evidence_audit();self.assertTrue(e['verified_internal_arithmetic']);self.assertFalse(e['source_byte_validation']);self.assertEqual('NOT_ESTABLISHED',e['official_combined_policy_score'])
    def test_high_earner_2027_and_2036(self):
        s=ssa_dollar_equivalents('E2.5_high_earner_tax_250k_no_benefit_credit')
        self.assertEqual(D('225.7136'),D(s[1]['derived_nominal_annual_balance_change_billion']))
        self.assertEqual(D('415.4472'),D(s[9]['derived_nominal_annual_balance_change_billion']))
        self.assertEqual(D('433.2625'),D(s[10]['derived_nominal_annual_balance_change_billion']))
        self.assertIn('not FY federal receipts',s[10]['measure'])
    def test_2032_and_2033_hi_depletion(self):
        a=series('cms_trustees_2026_hi_operations_cy.csv')
        self.assertEqual(D('28.1'),D(a[2032]['end_reserves_billion']))
        self.assertEqual(D('-56.9'),D(a[2033]['end_reserves_billion']))
        self.assertIn('hypothetical',a[2035]['projection_status'])
    def test_medcare_whatif_no_false_score(self):
        r=cms_hi_perturbation(extra_annual_noninterest_income={2027:10,2028:10})
        yr={x['calendar_year']:x for x in r['rows']}
        self.assertEqual(D('261.4'),D(yr[2027]['illustrative_reserves_billion']))
        self.assertEqual(D('250.1'),D(yr[2028]['illustrative_reserves_billion']))
        self.assertEqual('NOT_ESTABLISHED',r['federal_FY_score'])
    def test_medpac_non_additive(self):
        from src.primary_bridges import medpac_ma_audit
        import json
        from src.fiscalrazor import ROOT
        self.assertEqual([],medpac_ma_audit())
        a=json.loads((ROOT/"data/medpac_2026_ma_calibration.json").read_text())
        self.assertEqual(76,a["excess_ma_payments"])
        self.assertEqual(11,a["higher_part_b_premium_contributions_associated_with_ma_billion"])
    def test_pce_mechanical_reference_not_score(self):
        r=pce_mechanical_reference();self.assertEqual('1043.5075',r['all_pce_times_rate_billion_NOT_SCORE']);self.assertEqual('NOT_ESTABLISHED',r['net_vat_revenue'])
        q=pce_mechanical_reference(.05,.5,.9);self.assertEqual('469.5784',q['mechanical_gross_billion'])
    def test_nonexistent_option_rejected(self):
        with self.assertRaises(ValueError):ssa_dollar_equivalents('FAKE')
    def test_evidence_has_published_2026(self):
        vals=series('ssa_trustees_2026_economic_cy.csv')
        self.assertEqual(D('17125'),D(vals[2036]['oasdi_taxable_payroll_billion']))

class TimingAndDefense(unittest.TestCase):
    def test_uniform_fy_oct_prev_plus_jan_sept(self):
        cy={2026:D(120),2027:D(240)}
        self.assertEqual({2027:D(210)},fiscalize_calendar_cash(cy,first_fy=2027,last_fy=2027))
    def test_missing_cy_not_zero(self):
        with self.assertRaisesRegex(ValueError,'Missing'):fiscalize_calendar_cash({2027:100},first_fy=2027,last_fy=2027)
    def test_bad_month_weights_not_accepted(self):
        with self.assertRaises(ValueError):fiscalize_calendar_cash({2026:10,2027:20},months={1:1},first_fy=2027,last_fy=2027)
    def test_ssa_timing_exercise_prohibits_fy_score(self):
        a=rate_to_fy_exercise(ssa_dollar_equivalents('E2.5_high_earner_tax_250k_no_benefit_credit'))
        self.assertEqual('428.8087',a[-1]['pure_timing_exercise_billion'])
        self.assertIn('NOT_VALID',a[-1]['status'])
    def test_spendout_conserves_and_shifts(self):
        r=budget_authority_to_outlays({2028:100},{0:.2,1:.5,2:.3},through_year=2029)
        self.assertEqual(D('20'),r['outlay_reductions_billion'][2028]);self.assertEqual(D('50'),r['outlay_reductions_billion'][2029]);self.assertEqual(D('30'),r['post_horizon_unspent_billion'])
    def test_spendout_rejects_missing_lag(self):
        with self.assertRaises(ValueError):budget_authority_to_outlays({2028:100},{0:.5})
    def test_spendout_rejects_negative(self):
        with self.assertRaises(ValueError):budget_authority_to_outlays({2028:-2},{0:1})

class Distributional(unittest.TestCase):
    def setUp(self):
        self.households=[Household('low',D(10),D(20000),D(14000),1,2),Household('high',D(90),D(100000),D(40000),2,0)]
    def test_rebate_math(self):
        a=household_vat_effect(self.households,D('.05'),adult_rebate=300,child_rebate=150)
        self.assertEqual(D('100'),a[0]['net_vat_burden']);self.assertEqual(D('1400'),a[1]['net_vat_burden'])
    def test_deciles_conserve_weights(self):
        a=household_vat_effect(self.households,D('.05'))
        dec=weighted_distribution(a)
        self.assertEqual(10,len(dec));self.assertTrue(all(D(r['weighted_population'])==D(10) for r in dec))
        self.assertEqual(D('700'),D(dec[0]['average_gross_vat']))
    def test_reject_duplicate_household(self):
        with self.assertRaises(ValueError):household_vat_effect(self.households+[self.households[0]],.05)
    def test_national_claim_gate_does_not_pass_synthetic(self):
        self.assertFalse(population_quality_gate([],real_sample=False)['passed'])
        self.assertFalse(population_quality_gate([1],real_sample=True,pce_coverage_ratio=1)['passed'])

class VerificationParser(unittest.TestCase):
    def test_numeric_normalization(self):self.assertEqual(D('-321.3'),normal_number('−$321.3'))
    def test_html_source_verifier_good_and_tampered(self):
        # Temporary same-format regression fixture, NOT proof of original HTML access.
        from unittest.mock import patch
        import tempfile,csv
        from pathlib import Path
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)/'v.csv'
            r.write_text('calendar_year,a,b\n2026,100,200\n2027,110,210\n')
            page='''<html><table><tr><td>2026</td><td>100</td><td>200</td></tr><tr><td>2027</td><td>110</td><td>210</td></tr></table></html>'''
            with patch('scripts.check_ssa_live.ROOT',Path(t)):
                (Path(t)/'data').mkdir();r.rename(Path(t)/'data'/'v.csv')
                self.assertEqual([],match_source_html(page,'v.csv',['a','b']))
                self.assertTrue(match_source_html(page.replace('210','300'),'v.csv',['a','b']))

if __name__=='__main__': unittest.main()

class PayrollOverlap(unittest.TestCase):
    def test_2027_250k_no_extra_benefit(self):
        from src.payroll_interactions import worker_oasdi_overlap
        r=worker_oasdi_overlap(300000,192300,250000,increase_applies_high_earnings=True,combined_rate_increase='.01')
        self.assertEqual(D('500'),D(r['mechanical_interaction']))
        self.assertEqual(D('6200'),D(r['high_earnings_only_increment']))
        self.assertEqual(D('1923'),D(r['rate_increase_only_increment']))
        self.assertEqual(D('8623'),D(r['joint_tax_increment']))
    def test_donut_hole_closes_when_max_over_threshold(self):
        from src.payroll_interactions import worker_oasdi_overlap
        r=worker_oasdi_overlap(300000,270000,250000)
        self.assertEqual(D('30000'),D(r['new_high_wage_tax_base']))
        self.assertEqual(D('3720'),D(r['high_earnings_only_increment']))
    def test_exclusive_rate_has_no_mechanical_overlap(self):
        from src.payroll_interactions import worker_oasdi_overlap
        r=worker_oasdi_overlap(300000,192300,250000,combined_rate_increase='.01',increase_applies_high_earnings=False)
        self.assertEqual(D('0'),D(r['mechanical_interaction']))

class UnifiedVsTrustFund(unittest.TestCase):
    def test_internal_transfers_not_federal_savings(self):
        from src.cross_account import CashEffect,reconcile_cash_ledger
        rows=[CashEffect(2027,'a','tax','external_receipt',D(40),account='OASI'),
              CashEffect(2027,'b','provider savings','external_outlay',D(-20),account='HI'),
              CashEffect(2027,'c','financing','intragovernmental_transfer',D(30),source_fund='GENERAL',destination_fund='HI'),
              CashEffect(2027,'d','interest accounting','trust_fund_interest_credit',D(5),source_fund='GENERAL',destination_fund='OASI')]
        out=reconcile_cash_ledger(rows,2027,2027)
        s=out['years'][0];self.assertEqual(D(60),D(s['delta_unified_primary_balance_billion']))
        self.assertEqual(D(45),D(s['by_fund_balance_change_billion']['OASI']))
        self.assertEqual(D(50),D(s['by_fund_balance_change_billion']['HI']))
        self.assertEqual(D(-35),D(s['by_fund_balance_change_billion']['GENERAL']))
        self.assertEqual('NOT_ESTABLISHED',out['unified_policy_score'])
    def test_duplicate_account_in_cross_ledger_fails(self):
        from src.cross_account import CashEffect,reconcile_cash_ledger
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            reconcile_cash_ledger([CashEffect(2027,'tax-A','a','external_receipt',D(1)),
                        CashEffect(2027,'tax-A','b','external_receipt',D(1))],2027,2027)
    def test_transfer_not_misclassified_as_external(self):
        from src.cross_account import CashEffect,reconcile_cash_ledger
        with self.assertRaisesRegex(ValueError,'distinct'):
            reconcile_cash_ledger([CashEffect(2027,'move','a','intragovernmental_transfer',D(2),source_fund='HI',destination_fund='HI')],2027,2027)
    def test_non_finite_external_rejected(self):
        from src.cross_account import CashEffect,reconcile_cash_ledger
        with self.assertRaisesRegex(ValueError,'Non-finite'):
            reconcile_cash_ledger([CashEffect(2027,'bad','a','external_receipt',D('NaN'))],2027,2027)

class SourceRegisterTests(unittest.TestCase):
    def test_registry_links_and_identifiers(self):
        import json
        from src.fiscalrazor import ROOT
        rows=json.loads((ROOT/'data/public_source_registry.json').read_text())
        ids=[r['id'] for r in rows]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(ids),50)
        self.assertTrue(all(r['url'].startswith('https://') for r in rows))

class CryptographicEvidenceGate(unittest.TestCase):
    def test_unbacked_receipt_not_accepted(self):
        from src.receipt_validation import validate_replay_receipt
        row={'source_url':'https://www.cbo.gov/','reproduction_receipt':'receipts/FAKE.json'}
        self.assertTrue(validate_replay_receipt(row))
    def test_receipt_path_traversal_not_accepted(self):
        from src.receipt_validation import validate_replay_receipt
        row={'source_url':'https://www.cbo.gov/','reproduction_receipt':'../README.md'}
        self.assertTrue(validate_replay_receipt(row))
    def test_receipt_fingerprint_mutation_detected(self):
        from src.receipt_validation import row_fingerprint
        a={'source_url':'https://www.cbo.gov/','provision_id':'a','fiscal_year':'2027','delta_receipts_billion':'1','reproduction_receipt':'receipts/a.json','review_status':'independently_reproduced_and_reviewed'}
        b=dict(a,delta_receipts_billion='2')
        self.assertNotEqual(row_fingerprint(a),row_fingerprint(b))
