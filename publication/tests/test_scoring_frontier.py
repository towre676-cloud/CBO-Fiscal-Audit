import unittest
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from replay_bls_ce_2025 import scope
from replay_trustee_baselines import reconcile_operations
from replay_vat_credit_scenarios import credit_cents, filer_agi


class ScoringFrontierTests(unittest.TestCase):
    def test_credit_caps_and_phaseout_endpoints(self):
        guideline = 20_000
        self.assertEqual(
            [credit_cents(i, guideline) for i in (-5_000, 40_000, 50_000, 60_000, 90_000)],
            [100_000, 100_000, 50_000, 0, 0],
        )

    def test_dependent_filers_do_not_inflate_principal_joint_agi(self):
        rows = [(1, 2, 1, 0, 70_000), (2, 1, 1, 0, 0), (3, 0, 5, 1, 5_000)]
        self.assertEqual(filer_agi(rows), 70_000)
        self.assertIsNone(filer_agi([(1, 0, 6, 0, 0)]))
        self.assertIsNone(filer_agi([(1, 0, 1, 0, 70_000)]))

    def test_ce_boundary_and_adjusted_interview_months(self):
        self.assertEqual([scope("251x", 1), scope("251x", 3), scope("261", 2)], [0, 2, 2])
        self.assertEqual([scope("253", 8), scope("253", 9), scope("254", 12), scope("261", 1)],
                         [3.5, 5.5, 5.5, 3.5])

    def test_trust_fund_reserve_identity_detects_broken_bridge(self):
        rows = {2025: (20, 10, 10, 60), 2026: (20, 30, -10, 51)}
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            reconcile_operations(rows, Decimal(".1"))
        rows[2026] = (20, 30, -10, 50)
        self.assertEqual(reconcile_operations(rows, Decimal(".1"))["reserve_identities_checked"], 1)
