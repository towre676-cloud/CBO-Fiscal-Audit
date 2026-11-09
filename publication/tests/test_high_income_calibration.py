import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from calibrate_high_income import FLOOR, checked_fit, fine_margins, margins
from replay_same_year_tax_units import cps_cells, cps_returns


class CalibrationTests(unittest.TestCase):
    def test_count_only_preserves_mean(self):
        sample = [(200_000, 2), (500_000, 3)]
        count, agi = margins(checked_fit(sample, 20, 9_000_000, "count_only").apply(sample))
        self.assertAlmostEqual(count, 20)
        self.assertAlmostEqual(agi / count, 380_000)

    def test_matching_both_moments_by_distinct_mechanisms(self):
        sample = [(200_000, 2), (500_000, 3)]
        tilt = checked_fit(sample, 10, 4_500_000, "tilt").apply(sample)
        stretch = checked_fit(sample, 10, 4_500_000, "stretch").apply(sample)
        for calibrated in (tilt, stretch):
            count, agi = margins(calibrated)
            self.assertAlmostEqual(count, 10)
            self.assertAlmostEqual(agi, 4_500_000)
        self.assertAlmostEqual(tilt[0][1], 5 / 3)
        self.assertEqual([x for x, _ in tilt], [200_000, 500_000])
        self.assertEqual(stretch[0], (200_000, 4.0))
        self.assertAlmostEqual(stretch[1][0], 200_000 + 250_000 / 0.6)
        self.assertAlmostEqual(stretch[1][1], 6)

    def test_tilt_abstains_outside_positive_weight_support(self):
        for target in (200_000, 500_000, 800_000):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "observed CPS support"):
                checked_fit([(200_000, 2), (500_000, 3)], 10, 10 * target, "tilt")
        with self.assertRaisesRegex(ValueError, "missing sample support"):
            checked_fit([], 10, 4_000_000, "stretch")

    def test_tilt_can_lower_the_conditional_mean(self):
        sample = [(200_000, 2), (500_000, 3)]
        self.assertLess(checked_fit(sample, 10, 2_500_000, "tilt").tilt_per_million, 0)

    def test_exact_thresholds_enter_the_higher_band(self):
        fine = fine_margins([(FLOOR, 4), (499_999, 2), (500_000, 1), (1_000_000, 3)])
        self.assertEqual([fine[x]["returns"] for x in (FLOOR, 500_000, 1_000_000)], [6, 1, 3])

    def test_shared_extractor_counts_joint_and_dependent_returns_once(self):
        households = "H_SEQ,H_HHTYPE,HRHTYPE,GESTFIPS,HSUP_WGT,H_NUMPER\n1,1,1,6,100,6\n"
        people = (
            "PH_SEQ,TAX_ID,A_LINENO,A_SPOUSE,FILESTAT,DEP_STAT,AGI,MARSUPWT\n"
            "1,1,1,2,1,0,300000,110\n"
            "1,1,2,1,1,0,0,120\n"
            "1,1,3,0,5,1,25000,130\n"
            "1,2,4,5,1,0,400000,100\n"
            "1,2,5,0,1,0,0,100\n"
            "1,3,6,0,6,0,0,100\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("hhpub24.csv", households)
                archive.writestr("pppub24.csv", people)
            returns, diag, homes, units = cps_returns(path)
            cells, old_diag, _, _ = cps_cells(path)
        self.assertEqual([(row.kind, row.agi) for row in returns], [("principal", 300_000), ("dependent", 25_000)])
        self.assertEqual((homes, units), (1, 3))
        self.assertEqual(diag["joint_with_different_person_weights"], 1)
        self.assertEqual(diag["unresolved_or_nonfiler_units"], 2)
        self.assertEqual(cells[6, 6]["person_count"], 110)
        self.assertEqual(cells[6, 2]["household_count"], 100)
        self.assertEqual(old_diag["dependent_positive_agi_sample_returns"], 1)


class PublishedCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / "publication" / "results"
        cls.result = json.loads((folder / "cps_irs_high_income.json").read_text())
        cls.original = json.loads((folder / "cps_irs_2023_calibration.json").read_text())
        with (folder / "cps_irs_high_income_states.csv").open(newline="") as stream:
            cls.states = list(csv.DictReader(stream))

    def test_new_2023_baseline_reconciles_to_every_preserved_national_band(self):
        for stub, original in self.original["by_positive_agi_stub"].items():
            replay = self.result["by_income_year"]["2023"]["composition_by_agi_stub"][stub]
            self.assertEqual(replay["cps_returns_and_agi_usd"], [
                original["cps_person_weighted_returns"], original["cps_person_weighted_agi_usd"]
            ])
            self.assertEqual(replay["irs_returns_and_agi_usd"], [original["irs_returns"], original["irs_agi_usd"]])

    def test_fitted_and_transfer_results_remain_separate(self):
        for year, data in self.result["by_income_year"].items():
            count, agi = data["composition_by_agi_stub"]["6"]["irs_returns_and_agi_usd"]
            states = [row for row in self.states if row["income_year"] == year]
            self.assertEqual(len({row["state_fips"] for row in states}), 51)
            for method in ("stretch", "tilt"):
                estimate = data["distribution"][method]
                if year == "2023":
                    self.assertAlmostEqual(estimate["returns"] / count, 1)
                    self.assertAlmostEqual(estimate["agi_usd"] / agi, 1)
                    for row in states:
                        self.assertEqual(row[f"local_{method}_status"], "matched")
                        self.assertAlmostEqual(float(row[f"local_{method}_agi_usd"]) / float(row["irs_agi_usd"]), 1)
                else:
                    self.assertTrue(all(not row[f"local_{method}_status"] for row in states))
                    self.assertLess(estimate["agi_usd"], agi)

    def test_unmodeled_far_tail_is_visible_in_independent_benchmark(self):
        data = self.result["by_income_year"]["2023"]
        self.assertEqual(data["irs_national_soi_fine_bands_not_fit"]["all"]["10000000"]["returns"], 30_382)
        for method in ("raw", "tilt", "stretch"):
            self.assertEqual(data["distribution"][method]["fine_bands"]["10000000"]["returns"], 0)
