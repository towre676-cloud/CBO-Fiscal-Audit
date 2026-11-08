import unittest
from decimal import Decimal
from fiscal_data.fiscalization import CASH,LIABILITY,fiscal_year,fiscalize_cash_months,hypothetical_monthly_liability_allocation,verify_budget_change_row
D=Decimal
class FiscalTests(unittest.TestCase):
    def test_fiscal_boundary(self):
        self.assertEqual(fiscal_year('2030-09'),2030)
        self.assertEqual(fiscal_year('2030-10'),2031)
        self.assertEqual(fiscal_year('2026-01'),2026)
    def test_invalid_month(self):
        for x in ('2026-13','26-01','2026-00','2026/01','abcd-10'):
            with self.assertRaises(ValueError):fiscal_year(x)
    def test_fy_cash_reconciliation(self):
        r=[{'cash_month':'2030-09','amount_bn':'13.1','account':'HI','basis':CASH},
           {'cash_month':'2030-10','amount_bn':'-5.3','account':'HI','basis':CASH},
           {'cash_month':'2031-01','amount_bn':'7.2','account':'HI','basis':CASH}]
        x=fiscalize_cash_months(r)
        self.assertEqual(x[(2030,'HI')],D('13.1'))
        self.assertEqual(x[(2031,'HI')],D('1.9'))
        self.assertEqual(sum(x.values()),D(15))
    def test_reject_liability_as_cash(self):
        with self.assertRaises(ValueError):fiscalize_cash_months([{'cash_month':'2027-09','amount_bn':10,'account':'income_tax','basis':LIABILITY}])
    def test_cash_account_required(self):
        with self.assertRaises(ValueError):fiscalize_cash_months([{'cash_month':'2027-03','amount_bn':10,'basis':CASH}])
    def test_cash_duplicate_account_month(self):
        row={'cash_month':'2027-03','amount_bn':10,'basis':CASH,'account':'B'}
        with self.assertRaises(ValueError):fiscalize_cash_months([row,row])
    def test_no_implicit_cy_to_fy_revenue(self):
        weights={2027:{m:D("0.08") for m in range(1,13)}}
        weights[2027][12]=D("0.12")
        r=hypothetical_monthly_liability_allocation({2027:D(120)},weights)
        self.assertEqual(len(r),12)
        self.assertEqual(sum(x['allocated_liability_bn'] for x in r),D(120))
        self.assertTrue(all(x['basis']==LIABILITY for x in r))
        with self.assertRaises(ValueError):fiscalize_cash_months(r)
    def test_yearly_liability_needs_all_timing_weights(self):
        with self.assertRaises(ValueError):hypothetical_monthly_liability_allocation({2027:100},{2027:{1:D(1)}})
    def test_wrong_monthly_sum(self):
        with self.assertRaises(ValueError):hypothetical_monthly_liability_allocation({2027:100},{2027:{m:D('.1') for m in range(1,13)}})
    def test_budget_bridge_math(self):
        v=verify_budget_change_row({'fy':2036,'delta_receipts_bn':'25.1','delta_noninterest_outlays_bn':'-5','delta_net_interest_bn':'-3',
                                    'delta_debt_other_financing_bn':'1','source_kind':'independently_modeled_hypothesis'})
        self.assertEqual(v['delta_primary_balance_bn'],D('30.1'))
        self.assertEqual(v['delta_total_balance_bn'],D('33.1'))
        self.assertEqual(v['delta_debt_financing_bn'],D('-32.1'))
    def test_unsupported_official_claim(self):
        with self.assertRaises(ValueError):verify_budget_change_row({'fy':2036,'delta_receipts_bn':0,'delta_noninterest_outlays_bn':0,'delta_net_interest_bn':0,
                                    'delta_debt_other_financing_bn':0,'source_kind':'official_joint_score'})
    def test_missing_interest_rejected(self):
        with self.assertRaises(ValueError):verify_budget_change_row({'fy':2036,'delta_receipts_bn':10,'delta_noninterest_outlays_bn':2,
                                    'delta_debt_other_financing_bn':0,'source_kind':'independently_modeled_hypothesis'})
