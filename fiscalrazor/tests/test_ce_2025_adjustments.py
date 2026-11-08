import unittest
from decimal import Decimal
from fiscal_data.ce_2025_adjustments import interview_mo_scope,interview_2025_expenditure,diary_2025_weights
D=Decimal
class CETests(unittest.TestCase):
    def test_interview_changed_scope(self):
        for (year,month),want in [((2025,8),'3.5'),((2025,9),'5.5'),((2025,12),'5.5'),((2026,1),'3.5')]:
            self.assertEqual(interview_mo_scope(year,month,3),D(want))
    def test_unaffected_scope(self):self.assertEqual(interview_mo_scope(2025,7,3),D(3))
    def test_interview_expense_reference_months(self):
        for m,mult in [(7,'1.5'),(8,'3'),(9,'3'),(10,'1.5'),(11,'1')]:
            self.assertEqual(interview_2025_expenditure(2025,m,10)['corrected_expenditure'],D(10)*D(mult))
    def test_interview_no_wrong_year_adjustments(self):
        for year in (2024,2026):self.assertEqual(interview_2025_expenditure(year,8,10)['corrected_expenditure'],D(10))
    def test_interview_already_adjusted_rejected(self):
        with self.assertRaises(ValueError):interview_2025_expenditure(2025,8,10,already_adjusted=True)
    def test_diary_sept_dec_replicates(self):
        for m in (9,12):
            r=diary_2025_weights(2025,m,100,[i for i in range(1,45)])
            self.assertEqual(r['FINLWT21'],D(200))
            self.assertEqual(r['WTREP01_WTREP44'][-1],D(88))
            self.assertEqual(r['multiplier'],D(2))
    def test_diary_unaffected_month(self):
        self.assertEqual(diary_2025_weights(2025,8,100,[1]*44)['FINLWT21'],D(100))
    def test_diary_wrong_year_not_adjusted(self):
        self.assertEqual(diary_2025_weights(2026,9,100,[1]*44)['FINLWT21'],D(100))
    def test_diary_wrong_replicates_rejected(self):
        with self.assertRaises(ValueError):diary_2025_weights(2025,9,100,[1]*43)
    def test_diary_double_adjustment_rejected(self):
        with self.assertRaises(ValueError):diary_2025_weights(2025,9,100,[1]*44,already_adjusted=True)
