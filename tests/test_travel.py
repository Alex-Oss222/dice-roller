"""Source fidelity, explicit assumptions, and read-only travel behavior."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from iron_engine.travel import DEFAULT_CATALOG, TravelCatalog, TravelError, estimate, load_catalog, lookup


class TravelTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def test_snapshot_counts_and_source_cell_are_preserved(self):
        self.assertEqual({"road": 276, "sea": 91, "raven": 210}, self.catalog.summary["route_counts"])
        self.assertEqual(7, len(self.catalog.profiles))
        road = lookup("road", "Castle Black", "Winterfell", catalog=self.catalog)
        raven = lookup("raven", "Castle Black", "Winterfell", catalog=self.catalog)
        self.assertEqual(680, road["distance_miles"])
        self.assertEqual(640, raven["distance_miles"])
        self.assertEqual("B6", road["source"]["cell"])
        self.assertEqual(1, road["source"]["gid"])
        self.assertTrue(road["source"]["url"].endswith("#gid=1&range=B6"))
        self.assertEqual(5, raven["source"]["gid"])

    def test_direction_case_and_whitespace_do_not_change_source(self):
        reverse = self.catalog.lookup(" ROAD ", "  winterfell\n", "castle   BLACK")
        direct = self.catalog.lookup("road", "Castle Black", "Winterfell")
        self.assertEqual(direct["source"], reverse["source"])
        self.assertEqual(direct["distance_miles"], reverse["distance_miles"])
        self.assertEqual("Winterfell", reverse["origin"])

    def test_only_documented_aliases_are_accepted(self):
        for alias, canonical in self.catalog.summary["aliases"].items():
            self.assertEqual(self.catalog.lookup("road", canonical, "Castle Black"),
                             self.catalog.lookup("road", alias.upper(), "Castle Black"))
        with self.assertRaisesRegex(TravelError, "Unknown road location"):
            self.catalog.lookup("road", "Winterfel", "Castle Black")

    def test_missing_route_is_not_inferred_from_other_cells(self):
        raw = json.loads(DEFAULT_CATALOG.read_text())
        raw["routes"] = [r for r in raw["routes"] if not (r["mode"] == "road" and r["source"]["cell"] == "B6")]
        reduced = TravelCatalog(raw)
        with self.assertRaisesRegex(TravelError, "No supplied road route"):
            reduced.lookup("road", "Castle Black", "Winterfell")
        with self.assertRaises(TravelError):
            self.catalog.lookup("road", "Castle Black", "Castle Black")

    def test_modes_do_not_share_distances_or_invent_ports(self):
        with self.assertRaises(TravelError):
            self.catalog.lookup("sea", "Winterfell", "Castle Black")
        with self.assertRaises(TravelError):
            self.catalog.lookup("air", "Winterfell", "Castle Black")
        sea = self.catalog.lookup("sea", "White Harbor", "Eastwatch-by-the-Sea")
        self.assertEqual(2130, sea["distance_miles"])

    def test_explicit_rate_rest_and_speed_multiplier_have_defined_meanings(self):
        result = estimate("road", "Castle Black", "Winterfell", rate_mpd=20,
                          multiplier=0.5, rest_days=2, catalog=self.catalog)
        self.assertEqual(20, result["rate_mpd"])
        self.assertEqual(10, result["effective_rate_mpd"])
        self.assertEqual(68, result["moving_days"])
        self.assertEqual(70 * 86400, result["elapsed_seconds"])
        self.assertEqual(2, result["rest_days"])
        self.assertIsNone(result["rate_source"])
        json.dumps(result, allow_nan=False)

    def test_rounding_is_upward_and_exact_at_whole_second_boundaries(self):
        whole = self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=30)
        fraction = self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=7)
        self.assertEqual(1958400, whole["elapsed_seconds"])
        self.assertEqual(8393143, fraction["elapsed_seconds"])

    def test_missing_or_nonfinite_invalid_rates_are_rejected(self):
        for rate in [None, 0, -1, float("nan"), float("inf"), -float("inf"), True, "20"]:
            with self.subTest(rate=rate), self.assertRaises(TravelError):
                self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=rate)
        for key in ["multiplier", "rest_days"]:
            invalid = [-1, float("nan"), float("inf"), True, "2"]
            if key == "multiplier":
                invalid.append(0)
            for value in invalid:
                with self.subTest(key=key, value=value), self.assertRaises(TravelError):
                    self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=20, **{key: value})

    def test_extreme_arithmetic_cannot_emit_infinity_or_zero_rate(self):
        for rate, multiplier in [(1e308, 1e308), (5e-324, 5e-324)]:
            with self.assertRaises(TravelError):
                self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=rate, multiplier=multiplier)

    def test_road_profile_is_explicit_and_average_is_its_only_default(self):
        result = self.catalog.estimate("road", "Castle Black", "Winterfell", profile="small_party_riding")
        self.assertEqual(24, result["rate_mpd"])
        self.assertEqual("average", result["pace"])
        self.assertEqual("'Road travel speed rates'!A9:E9", result["rate_source"]["source_range"])
        self.assertFalse(result["requires_endurance_assumption"])
        for extras in [{"pace": "average"}, {"profile": "unknown"},
                       {"profile": "small_party_riding", "pace": "sprint"},
                       {"profile": "small_party_riding", "rate_mpd": 20}]:
            with self.subTest(extras=extras), self.assertRaises(TravelError):
                self.catalog.estimate("road", "Castle Black", "Winterfell", **extras)

    def test_sea_and_raven_require_explicit_rates(self):
        routes = [("sea", "White Harbor", "Eastwatch-by-the-Sea"),
                  ("raven", "Castle Black", "Winterfell")]
        for route in routes:
            with self.subTest(route=route):
                with self.assertRaises(TravelError):
                    self.catalog.estimate(*route)
                with self.assertRaises(TravelError):
                    self.catalog.estimate(*route, profile="small_party_riding")
                result = self.catalog.estimate(*route, rate_mpd=100)
                self.assertEqual(result["distance_miles"] / 100, result["moving_days"])
                self.assertIn("explicit campaign convention", result["units"]["basis"])

    def test_no_implicit_unit_conversion(self):
        raw = json.loads(DEFAULT_CATALOG.read_text())
        raw["units"]["distance"] = "kilometers"
        with self.assertRaisesRegex(TravelError, "no implicit unit conversion"):
            TravelCatalog(raw)
        result = self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=24)
        self.assertEqual(680, result["distance_miles"])
        self.assertEqual(24, result["effective_rate_mpd"])

    def test_long_fast_journey_prominently_flags_endurance(self):
        result = self.catalog.estimate("road", "Castle Black", "Winterfell",
                                       profile="small_party_riding", pace="fast_conditioned")
        self.assertEqual(50, result["rate_mpd"])
        self.assertGreater(result["moving_days"], 3)
        self.assertTrue(result["requires_endurance_assumption"])
        self.assertTrue(result["warnings"][0].startswith("ENDURANCE:"))
        acknowledged = self.catalog.estimate("road", "Castle Black", "Winterfell",
                        profile="small_party_riding", pace="fast_conditioned",
                        endurance_assumption="A supported relay with replacement mounts is available.")
        self.assertFalse(acknowledged["requires_endurance_assumption"])
        self.assertTrue(acknowledged["warnings"])
        self.assertIn("replacement mounts", acknowledged["endurance_assumption"])
        with self.assertRaises(TravelError):
            self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=20, endurance_assumption=" ")

    def test_short_fast_journey_does_not_trigger_three_day_warning(self):
        result = self.catalog.estimate("road", "The Trident", "Lord Harroway's Town",
                                       profile="small_party_riding", pace="fast_conditioned")
        self.assertEqual(2, result["moving_days"])
        self.assertFalse(result["requires_endurance_assumption"])

    def test_returned_records_cannot_mutate_catalog_or_other_results(self):
        original = self.catalog.lookup("road", "Castle Black", "Winterfell")
        altered = self.catalog.lookup("road", "Castle Black", "Winterfell")
        altered["source"]["cell"] = "Z999"
        altered["assumptions"].append("injected")
        altered["units"]["basis"] = "injected"
        profiles = self.catalog.profiles
        profiles[0]["rates_miles_per_day"]["average"] = 9999
        summary = self.catalog.summary
        summary["aliases"]["New"] = "Winterfell"
        self.assertEqual(original, self.catalog.lookup("road", "Castle Black", "Winterfell"))
        self.assertEqual(13, self.catalog.profiles[0]["rates_miles_per_day"]["average"])
        self.assertNotIn("New", self.catalog.summary["aliases"])
        raw = json.loads(DEFAULT_CATALOG.read_text())
        isolated = TravelCatalog(raw)
        raw["routes"][0]["distance_miles"] = 1
        self.assertEqual(680, isolated.lookup("road", "Castle Black", "Winterfell")["distance_miles"])

    def test_helper_writes_no_files_or_campaign_state(self):
        from iron_engine.engine import CampaignStore
        from tests.fixtures import setup_payload
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = CampaignStore(root / "campaign")
            store.initialize(setup_payload())
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            events_before = deepcopy(store.validate())
            with patch.object(CampaignStore, "__init__", side_effect=AssertionError("Travel must not open campaign store")):
                self.catalog.estimate("road", "Castle Black", "Winterfell", rate_mpd=20)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(events_before, store.validate())

    def test_invalid_catalog_is_reported_as_travel_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            with self.assertRaises(TravelError):
                load_catalog(path)
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(TravelError):
                load_catalog(path)
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(TravelError):
                load_catalog(path)

    def test_cli_road_profile_works_without_creating_a_store(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "not-created"
            run = subprocess.run([sys.executable, "-m", "iron_engine", "--store", str(store), "travel",
                                  "--mode", "road", "--from", "Castle Black", "--to", "Winterfell",
                                  "--profile", "small_party_riding", "--speed-multiplier", "0.5", "--rest-days", "2"],
                                 cwd=DEFAULT_CATALOG.parent.parent, capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(12, result["effective_rate_mpd"])
            self.assertEqual(5068800, result["elapsed_seconds"])
            self.assertFalse(store.exists())

    def test_cli_sea_explicit_rate(self):
        run = subprocess.run([sys.executable, "-m", "iron_engine", "travel", "--mode", "sea",
                              "--from", "White Harbor", "--to", "Eastwatch-by-the-Sea", "--rate-mpd", "100"],
                             cwd=DEFAULT_CATALOG.parent.parent, capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(2130, result["distance_miles"])
        self.assertEqual(21.3, result["moving_days"])

    def test_cli_rejects_nan_without_a_traceback(self):
        run = subprocess.run([sys.executable, "-m", "iron_engine", "travel", "--mode", "road",
                              "--from", "Castle Black", "--to", "Winterfell", "--rate-mpd", "nan"],
                             cwd=DEFAULT_CATALOG.parent.parent, capture_output=True, text=True)
        self.assertEqual(2, run.returncode)
        self.assertIn("finite", run.stderr)
        self.assertNotIn("Traceback", run.stderr)
        self.assertEqual("", run.stdout)


if __name__ == "__main__":
    unittest.main()
