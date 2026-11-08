import unittest
from fiscal_data.reconciliation import events,additive_annual_revision
class ReconciliationTests(unittest.TestCase):
 def test_events_registered(self): self.assertGreaterEqual(len(events()),2)
 def test_billion_tariff_update_not_forcibly_allocated(self):
  self.assertEqual(events()[0]['total_bn'],'900')
  with self.assertRaisesRegex(ValueError,'NO_ANNUAL_RECONCILIATION_PROFILE'):additive_annual_revision(events(),2030)
 def test_2026_actual_only_not_annual_revision(self):
  with self.assertRaisesRegex(ValueError,'NO_ANNUAL'):additive_annual_revision(events(),2026)
