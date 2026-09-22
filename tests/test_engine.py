"""Behavioral tests for the campaign ledger's accounting and audit boundaries."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from iron_engine.engine import CampaignError, CampaignStore
from tests.fixtures import bind_head, correction, review_for, setup_payload, source, starting_state, task, turn_payload


def canonical_hash(event):
    unsigned = {key: value for key, value in event.items() if key != "hash"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")

    def initialize(self, state=None):
        return self.store.initialize(setup_payload(state))

    def turn(self, *args, store=None, **kwargs):
        # Bind when the draft is created; retries submit the original draft unchanged.
        return bind_head(store or self.store, turn_payload(*args, **kwargs))

    def correction(self, **kwargs):
        return bind_head(self.store, correction(**kwargs))

    def command(self, payload):
        return bind_head(self.store, payload)

    def assert_rejected_without_change(self, operation, payload):
        before = self.store.validate()
        with self.assertRaises(CampaignError):
            operation(payload)
        self.assertEqual(before, self.store.validate())

    def advance(self, count):
        for number in range(count):
            self.store.commit_turn(self.turn(number))

    def test_unconfigured_store_is_not_a_campaign(self):
        self.assertEqual([], self.store.validate())
        with self.assertRaises(CampaignError):
            self.store.current()
        with self.assertRaises(CampaignError):
            self.store.commit_turn(turn_payload(expected_hash="0" * 64))

    def test_setup_is_turn_zero_and_round_trips_every_explicit_field(self):
        state = starting_state()
        event = self.initialize(state)
        self.assertEqual(state, self.store.current())
        self.assertEqual(0, event["sequence"])
        self.assertEqual("setup", event["kind"])
        self.assertIsNone(event["previous_hash"])
        self.assertEqual(canonical_hash(event), event["hash"])
        self.assertEqual([event], self.store.validate())

    def test_independent_turn_duration_and_complete_sheet_update(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["conditions"] = ["Test ankle sprain"]
        self.store.commit_turn(self.turn(seconds=7200, changes={"character": character},
            evidence={"character": "A documented fall caused the test sprain"}))
        self.store.commit_turn(self.turn(1, seconds=3 * 86400))
        state = self.store.current()
        self.assertEqual(2, state["turn"])
        self.assertEqual(7200 + 3 * 86400, state["time_seconds"])
        self.assertEqual(character, state["character"])

    def test_exact_retry_returns_original_event_even_after_later_turn(self):
        setup = self.initialize()
        payload = self.turn(resources_delta={"silver_stags": -2},
            evidence={"resources.silver_stags": "Paid the documented test lodging charge"})
        original = self.store.commit_turn(payload)
        self.store.commit_turn(self.turn(1))
        self.assertEqual(original, self.store.commit_turn(deepcopy(payload)))
        self.assertEqual(setup, self.store.initialize(setup_payload()))
        self.assertEqual(3, len(self.store.validate()))
        self.assertEqual(6, self.store.current()["resources"]["silver_stags"])

    def test_request_id_cannot_be_reused_for_changed_input_or_other_command(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(seconds=7200))
        self.assert_rejected_without_change(self.store.add_research,
            self.command({"request_id": "test-turn-1", "sources": [source()]}))

    def test_stale_turn_is_rejected_without_charging_resources(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(request_id="stale-request", resources_delta={"silver_stags": -1},
                evidence={"resources.silver_stags": "Test charge"}))

    def test_stale_head_cannot_erase_same_turn_corrections(self):
        self.initialize()
        old_character = deepcopy(self.store.current()["character"])
        old_character["equipment"].append("Test receipt")
        draft = self.turn(changes={"character": old_character},
            evidence={"character": "The clerk gives the character a test receipt"})
        correction_draft = self.correction(request_id="later-correction")
        research_draft = self.command({"request_id": "later-research", "sources": [source()]})
        checkpoint_draft = self.command({"request_id": "later-checkpoint", "resume_note": "An old pending decision"})
        old_hash = draft["expected_hash"]
        corrected_character = deepcopy(self.store.current()["character"])
        corrected_character["conditions"] = ["Previously omitted test sprain"]
        self.store.correct(self.correction(changes={"character": corrected_character}, resources_delta={},
            evidence={"character": "Restore the sprain omitted from setup"}))
        self.assertEqual(0, self.store.current()["turn"])
        self.assertNotEqual(old_hash, self.store.head())
        for operation, payload in [(self.store.commit_turn, draft), (self.store.correct, correction_draft),
            (self.store.add_research, research_draft), (self.store.checkpoint, checkpoint_draft)]:
            with self.subTest(operation=operation.__name__):
                self.assert_rejected_without_change(operation, payload)
        self.assertEqual(corrected_character, self.store.current()["character"])

    def test_every_nonsetup_write_requires_expected_hash(self):
        self.initialize()
        cases = [
            (self.store.commit_turn, self.turn()),
            (self.store.correct, self.correction()),
            (self.store.add_research, self.command({"request_id": "test-research", "sources": [source()]})),
            (self.store.checkpoint, self.command({"request_id": "test-checkpoint", "resume_note": "Test pending choice"})),
        ]
        for operation, payload in cases:
            del payload["expected_hash"]
            with self.subTest(operation=operation.__name__):
                self.assert_rejected_without_change(operation, payload)

    def test_resources_account_exactly_and_cannot_overdraft_or_invent_units(self):
        self.initialize()
        self.store.commit_turn(self.turn(resources_delta={"silver_stags": -8, "ration_days": 2},
            evidence={"resources.silver_stags": "Spent all eight test stags", "resources.ration_days": "Received two test rations"}))
        self.assertEqual({"silver_stags": 0, "ration_days": 9}, self.store.current()["resources"])
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(1, resources_delta={"silver_stags": -1}, evidence={"resources.silver_stags": "Cannot afford this"}))
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(1, resources_delta={"gold_dragons": 1}, evidence={"resources.gold_dragons": "Unconfigured unit"}))

    def test_correction_introduces_a_unit_without_advancing_time_or_turn(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        before = self.store.current()
        payload = self.correction(resources_delta={"test_coppers": 0}, evidence={"resources.test_coppers": "Explicitly introduce this test accounting unit"})
        event = self.store.correct(payload)
        after = self.store.current()
        self.assertEqual((before["turn"], before["time_seconds"]), (after["turn"], after["time_seconds"]))
        self.assertEqual(0, after["resources"]["test_coppers"])
        self.assertEqual(event, self.store.correct(payload))
        self.store.commit_turn(self.turn(1, resources_delta={"test_coppers": 3},
            evidence={"resources.test_coppers": "Received three test coppers"}))
        self.assertEqual(3, self.store.current()["resources"]["test_coppers"])

    def test_opening_correction_preserves_setup_and_replays_without_advancing(self):
        setup = setup_payload()
        setup["opening_narrative"] = "The test clerk has the incorrectly recorded account."
        original = self.store.initialize(setup)
        before = self.store.current()
        payload = self.correction(opening_narrative="The test clerk sets the corrected account on the table.")
        accepted = self.store.correct(payload)
        reloaded = CampaignStore(self.root / "campaign")
        self.assertEqual([original, accepted], reloaded.validate())
        self.assertEqual(original, reloaded.validate()[0])
        self.assertEqual(payload, accepted["input"])
        self.assertEqual((before["turn"], before["time_seconds"]),
                         (reloaded.current()["turn"], reloaded.current()["time_seconds"]))
        self.assertEqual(accepted, reloaded.correct(payload))
        self.assertNotIn("opening_narrative", reloaded.current())

    def test_legacy_correction_does_not_gain_an_opening_field(self):
        self.initialize()
        payload = self.correction()
        accepted = self.store.correct(payload)
        self.assertEqual(payload, accepted["input"])
        self.assertNotIn("opening_narrative", accepted["input"])
        self.assertEqual(canonical_hash(accepted), accepted["hash"])
        self.assertEqual(accepted, self.store.validate()[-1])

    def test_opening_correction_requires_nonempty_text_reason_and_record_change(self):
        self.initialize()
        for invalid in ("", " \n ", None, 0, []):
            with self.subTest(opening_narrative=invalid):
                self.assert_rejected_without_change(self.store.correct,
                    self.correction(opening_narrative=invalid))
        self.assert_rejected_without_change(self.store.correct,
            self.correction(opening_narrative="The corrected opening.", reason=" "))
        self.assert_rejected_without_change(self.store.correct,
            self.correction(opening_narrative="The corrected opening.", changes={},
                resources_delta={}, evidence={}))

    def test_opening_correction_is_blocked_after_first_resolved_turn(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        self.assert_rejected_without_change(self.store.correct,
            self.correction(opening_narrative="A replacement opening after play has begun."))
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(1, opening_narrative="A replacement opening in a resolved turn."))

    def test_evidence_is_required_for_every_change_and_delta(self):
        self.initialize()
        for payload in [
            self.turn(changes={"location": "Test mill"}),
            self.turn(resources_delta={"silver_stags": -1}),
            self.turn(changes={"location": "Test mill"}, evidence={"location": "  "}),
            self.turn(evidence={"resources.silver_stags": "Invented evidence with no delta"}),
        ]:
            with self.subTest(payload=payload):
                self.assert_rejected_without_change(self.store.commit_turn, payload)

    def test_due_task_stops_unresolved_advance_at_exact_deadline(self):
        state = starting_state()
        state["tasks"] = [task()]
        self.initialize(state)
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(seconds=7200))
        self.store.commit_turn(self.turn(seconds=7199))
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(1, seconds=1))

    def test_due_task_requires_both_result_and_retained_settled_task(self):
        state = starting_state()
        state["tasks"] = [task()]
        self.initialize(state)
        settled = task(status="completed", note="Test receipt signed")
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(seconds=7200, changes={"tasks": [settled]}, evidence={"tasks": "Test receipt signed"}))
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(seconds=7200, processed_tasks={"test-delivery": "Claimed complete"}))
        self.store.commit_turn(self.turn(seconds=7200, changes={"tasks": [settled]},
            evidence={"tasks": "Test receipt signed"}, processed_tasks={"test-delivery": "Receipt confirms delivery"}))
        self.assertEqual("completed", self.store.current()["tasks"][0]["status"])

    def test_due_task_can_be_blocked_or_rescheduled_with_explanation(self):
        for status, due in [("blocked", 7200), ("active", 10800)]:
            with self.subTest(status=status):
                store = CampaignStore(self.root / status)
                state = starting_state()
                state["tasks"] = [task()]
                store.initialize(setup_payload(state))
                revised = task(due=due, status=status, note="Test carrier delayed; next inspection scheduled")
                store.commit_turn(self.turn(store=store, seconds=7200, changes={"tasks": [revised]},
                    evidence={"tasks": "The carrier reported a test delay"},
                    processed_tasks={"test-delivery": "Delay established at the deadline"}))
                self.assertEqual(revised, store.current()["tasks"][0])

    def test_task_ids_cannot_disappear_and_new_task_cannot_already_be_overdue(self):
        state = starting_state()
        state["tasks"] = [task(due=20000)]
        self.initialize(state)
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(changes={"tasks": []}, evidence={"tasks": "Would silently lose the obligation"}))
        self.assert_rejected_without_change(self.store.commit_turn,
            self.turn(changes={"tasks": [task(due=20000), task(due=1000, task_id="new-task")]},
                evidence={"tasks": "Attempt to create overdue task"}))

    def test_interrupted_plan_preserves_unspent_time_across_save(self):
        self.initialize()
        plan = {"objective": "Complete a test week of practice", "endpoint_seconds": 604800,
            "remaining_seconds": 432000, "stopping_conditions": ["New consequential decision"]}
        self.store.commit_turn(self.turn(seconds=172800, changes={"interrupted_plan": plan},
            evidence={"interrupted_plan": "A consequential decision interrupts day two of seven"}))
        self.assertEqual(plan, self.store.current()["interrupted_plan"])
        self.assertEqual(172800, self.store.current()["time_seconds"])
        save = self.root / "interrupted.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "restored-plan")
        restored.restore_save(save)
        self.assertEqual(plan, restored.current()["interrupted_plan"])

    def test_tenth_turn_requires_review_in_same_event_and_retry_is_free(self):
        self.initialize()
        self.advance(9)
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(9, review=None))
        payload = self.turn(9)
        event = self.store.commit_turn(payload)
        self.assertEqual(10, event["state"]["turn"])
        self.assertEqual(review_for(10), event["input"]["review"])
        self.assertEqual(event, self.store.commit_turn(payload))
        self.assertEqual(11, len(self.store.validate()))

    def test_reviews_cannot_be_early_incomplete_or_cite_outside_window(self):
        self.initialize()
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(review=review_for(10)))
        self.advance(9)
        bad_reviews = []
        missing = review_for(10)
        del missing["findings"]["gm_consistency"]
        bad_reviews.append(missing)
        outside = review_for(10)
        outside["findings"]["results"]["evidence_turns"] = [0]
        bad_reviews.append(outside)
        future = review_for(10)
        future["findings"]["decisions"]["evidence_turns"] = [11]
        bad_reviews.append(future)
        wrong_window = review_for(10)
        wrong_window["from_turn"] = 2
        bad_reviews.append(wrong_window)
        for review in bad_reviews:
            with self.subTest(review=review):
                self.assert_rejected_without_change(self.store.commit_turn, self.turn(9, review=review))

    def test_research_does_not_grant_pc_knowledge_or_consume_time(self):
        self.initialize()
        self.advance(9)
        before = self.store.current()
        payload = self.command({"request_id": "test-research", "sources": [source()]})
        research = self.store.add_research(payload)
        after = self.store.current()
        self.assertEqual(9, after["turn"])
        self.assertEqual(before["time_seconds"], after["time_seconds"])
        self.assertEqual(before["knowledge"], after["knowledge"])
        self.assertEqual([source()], after["research"])
        self.assertEqual(research, self.store.add_research(payload))
        self.assert_rejected_without_change(self.store.add_research,
            self.command({"request_id": "other-research", "sources": [source()]}))
        self.store.correct(self.correction())
        self.assertEqual(9, self.store.current()["turn"])
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(9, review=None))
        self.store.commit_turn(self.turn(9))
        self.assertEqual(10, self.store.current()["turn"])

    def test_checkpoint_preserves_pending_stakes_without_advancing_and_clears_on_turn(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        payload = self.command({"request_id": "pending-test-check", "resume_note": "Pending test check: failure delays delivery; no roll has occurred."})
        before = self.store.current()
        saved = self.store.checkpoint(payload)
        self.assertEqual(saved, self.store.checkpoint(payload))
        after = self.store.current()
        self.assertEqual((before["turn"], before["time_seconds"]), (after["turn"], after["time_seconds"]))
        self.assertEqual(payload["resume_note"], after["resume_note"])
        self.assert_rejected_without_change(self.store.checkpoint,
            self.command({"request_id": "pending-test-check", "resume_note": "Changed stakes under a reused ID"}))
        save = self.root / "checkpoint-save.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "checkpoint-restored")
        restored.restore_save(save)
        self.assertEqual(payload["resume_note"], restored.current()["resume_note"])
        restored.commit_turn(self.turn(1, store=restored))
        self.assertIsNone(restored.current()["resume_note"])

    def test_dice_arithmetic_is_checked_and_adjudicated_mode_rejects_rolls(self):
        check = {"source": "player", "roll": 12, "skill": 2, "modifier": -1,
            "target": 14, "total": 13, "margin": -1,
            "objective": "Test the delivery count", "stakes": "Failure leaves the discrepancy unresolved"}
        self.initialize()
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(checks=[check]))
        real = CampaignStore(self.root / "real-dice")
        real.initialize(setup_payload(starting_state("real_dice")))
        for field, value in [("total", 14), ("margin", 1), ("roll", 21), ("skill", 6), ("modifier", -5)]:
            bad = deepcopy(check)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(CampaignError):
                real.commit_turn(self.turn(store=real, checks=[bad]))
            self.assertEqual(0, real.current()["turn"])
        real.commit_turn(self.turn(store=real, checks=[check]))
        real.commit_turn(self.turn(1, store=real, checks=[]))
        self.assertEqual(2, real.current()["turn"])

    def test_death_closes_new_turns_and_cannot_be_reversed_by_correction(self):
        self.initialize()
        payload = self.turn(seconds=60, changes={"alive": False, "death": {"cause": "Invented fatal test injury", "time_seconds": 60}},
            evidence={"alive": "The test injury is fatal", "death": "Death occurs at the turn endpoint"})
        death = self.store.commit_turn(payload)
        self.assertFalse(self.store.current()["alive"])
        self.assertEqual(death, self.store.commit_turn(payload))
        self.assert_rejected_without_change(self.store.commit_turn, self.turn(1))
        self.assert_rejected_without_change(self.store.correct,
            self.correction(changes={"alive": True, "death": None}, resources_delta={},
                evidence={"alive": "Attempted resurrection", "death": "Attempted removal"}))

    def test_death_time_and_alive_flag_must_agree(self):
        self.initialize()
        for changes in [{"alive": False}, {"death": {"cause": "Test", "time_seconds": 3600}},
            {"alive": False, "death": {"cause": "Test", "time_seconds": 0}}]:
            with self.subTest(changes=changes):
                self.assert_rejected_without_change(self.store.commit_turn,
                    self.turn(changes=changes, evidence={key: "Test evidence" for key in changes}))

    def test_unknown_fields_and_unauthorized_state_replacements_fail_closed(self):
        self.initialize()
        for payload in [self.turn(elasped_seconds=60), self.turn(changes={"turn": 99}, evidence={"turn": "Forbidden"}),
            self.turn(changes={"campaign": starting_state()["campaign"]}, evidence={"campaign": "Forbidden"}),
            self.turn(changes={"research": [source()]}, evidence={"research": "Wrong command"})]:
            with self.subTest(payload=payload):
                self.assert_rejected_without_change(self.store.commit_turn, payload)

    def test_bool_nan_and_nonobject_inputs_are_not_silently_coerced(self):
        self.initialize()
        for payload in [self.turn(elapsed_seconds=True), self.turn(expected_turn=False),
            self.turn(elapsed_seconds=1.5), self.turn(elapsed_seconds=0),
            self.turn(resources_delta={"silver_stags": True}, evidence={"resources.silver_stags": "Invalid boolean"}),
            self.turn(resources_delta={"silver_stags": float("nan")}, evidence={"resources.silver_stags": "Invalid NaN"}),
            [], None, "not an object"]:
            with self.subTest(payload=payload):
                self.assert_rejected_without_change(self.store.commit_turn, payload)

    def test_setup_rejects_missing_unknown_mistyped_and_overdue_fields(self):
        states = []
        missing = starting_state()
        del missing["campaign"]["spoiler_cutoff"]
        states.append(missing)
        unknown = starting_state()
        unknown["character"]["mana"] = 5
        states.append(unknown)
        boolean = starting_state()
        boolean["character"]["age"] = True
        states.append(boolean)
        invalid_number = starting_state()
        invalid_number["resources"]["silver_stags"] = float("inf")
        states.append(invalid_number)
        overdue = starting_state()
        overdue["tasks"] = [task(due=0)]
        states.append(overdue)
        for index, state in enumerate(states):
            with self.subTest(index=index):
                store = CampaignStore(self.root / f"invalid-setup-{index}")
                with self.assertRaises(CampaignError):
                    store.initialize(setup_payload(state))
                self.assertEqual([], store.validate())

    def test_missing_middle_event_and_hash_corruption_fail_closed(self):
        self.initialize()
        self.advance(2)
        next_turn = self.turn(2)
        path = self.root / "campaign" / "events" / "000001.json"
        original = path.read_bytes()
        path.unlink()
        with self.assertRaises(CampaignError):
            self.store.current()
        with self.assertRaises(CampaignError):
            self.store.commit_turn(next_turn)
        path.write_bytes(original)
        event = json.loads(original)
        event["state"]["resources"]["silver_stags"] = 999
        path.write_text(json.dumps(event), encoding="utf-8")
        with self.assertRaises(CampaignError):
            self.store.validate()

    def test_save_restores_complete_history_and_refuses_overwrite(self):
        self.initialize()
        self.advance(10)
        self.store.add_research(self.command({"request_id": "research-before-save", "sources": [source()]}))
        save = self.root / "save.json"
        self.store.export_save(save)
        original = save.read_bytes()
        restored = CampaignStore(self.root / "restored")
        restored.restore_save(save)
        self.assertEqual(self.store.validate(), restored.validate())
        self.assertEqual(self.store.current(), restored.current())
        with self.assertRaises(CampaignError):
            restored.restore_save(save)
        with self.assertRaises(CampaignError):
            self.store.export_save(save)
        self.assertEqual(original, save.read_bytes())

    def test_restore_replays_inputs_even_if_tampered_state_has_valid_hash(self):
        self.initialize()
        self.store.commit_turn(self.turn())
        save = self.root / "tampered-save.json"
        self.store.export_save(save)
        data = json.loads(save.read_text(encoding="utf-8"))
        event = data["events"][-1]
        event["state"]["resources"]["silver_stags"] = 500
        event["hash"] = canonical_hash(event)
        save.write_text(json.dumps(data), encoding="utf-8")
        restored = CampaignStore(self.root / "reject-tampering")
        with self.assertRaises(CampaignError):
            restored.restore_save(save)
        self.assertEqual([], restored.validate())

    def test_restore_into_nonempty_target_and_symlink_target_are_rejected(self):
        self.initialize()
        save = self.root / "save.json"
        self.store.export_save(save)
        target = self.root / "nonempty"
        target.mkdir()
        marker = target / "keep.txt"
        marker.write_text("Keep this file", encoding="utf-8")
        with self.assertRaises(CampaignError):
            CampaignStore(target).restore_save(save)
        self.assertEqual("Keep this file", marker.read_text(encoding="utf-8"))
        linked = self.root / "linked"
        linked.symlink_to(target, target_is_directory=True)
        with self.assertRaises(CampaignError):
            CampaignStore(linked).restore_save(save)

    def test_failed_atomic_publish_preserves_previous_event(self):
        self.initialize()
        before = self.store.validate()
        with patch("os.link", side_effect=OSError("Injected test link failure")):
            with self.assertRaises(CampaignError):
                self.store.commit_turn(self.turn())
        self.assertEqual(before, self.store.validate())
        self.store.commit_turn(self.turn())
        self.assertEqual(1, self.store.current()["turn"])

    def test_concurrent_writers_cannot_overwrite_or_double_charge_one_turn(self):
        self.initialize()
        gate = threading.Barrier(2)
        def attempt(number):
            contender = CampaignStore(self.root / "campaign")
            payload = self.turn(store=contender, request_id=f"concurrent-{number}",
                resources_delta={"silver_stags": -1}, evidence={"resources.silver_stags": "One test charge"})
            gate.wait(timeout=5)
            try:
                return contender.commit_turn(payload)
            except CampaignError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, [1, 2]))
        self.assertEqual(1, sum(result is not None for result in results))
        self.assertEqual(2, len(self.store.validate()))
        self.assertEqual(1, self.store.current()["turn"])
        self.assertEqual(7, self.store.current()["resources"]["silver_stags"])


if __name__ == "__main__":
    unittest.main()
