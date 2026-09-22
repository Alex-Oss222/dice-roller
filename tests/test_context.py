"""Focused context must preserve obligations and provide honest retrieval paths."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from iron_engine.context import context_packet, history_packet, record_index_packet, record_packet
from iron_engine.engine import CampaignError, CampaignStore
from tests.fixtures import bind_head, correction, setup_payload, source, task
from tests.test_workflow import advance_payload, workflow_state, world_record


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")

    def initialize(self, state=None):
        return self.store.initialize(setup_payload(state or workflow_state()))

    def snapshot(self):
        return {path.name: path.read_bytes() for path in (self.store.path / "events").iterdir()}

    def test_narrative_budget_is_exact_and_omitted_prose_can_be_retrieved(self):
        self.initialize()
        narratives = ["Old test scene never requested. " * 30, "A middle test scene. " * 100, "Final test scene é. " * 100]
        accepted = []
        for narrative in narratives:
            accepted.append(self.store.advance(advance_payload(self.store, narrative=narrative)))
        before = self.snapshot()
        packet = context_packet(self.store, recent_turns=2, max_chars=75)
        self.assertEqual([2, 3], [scene["turn"] for scene in packet["recent_turns"]])
        self.assertEqual(75, sum(len(scene["narrative"]) for scene in packet["recent_turns"]))
        self.assertEqual(75, packet["narrative_budget"]["used_chars"])
        self.assertEqual(sum(map(len, narratives[1:])) - 75, packet["narrative_budget"]["omitted_chars"])
        self.assertEqual(3, packet["history_retrieval"]["resolved_turns"])
        self.assertEqual(2, packet["history_retrieval"]["returned_turns"])
        self.assertNotIn(narratives[0], json.dumps(packet))
        self.assertNotIn("events", packet)
        for scene in packet["recent_turns"]:
            self.assertTrue(scene["narrative_truncated"])
            retrieved = history_packet(self.store, scene["retrieve"]["turn"])
            self.assertEqual(narratives[scene["turn"] - 1], retrieved["accepted_input"]["narrative"])
            self.assertEqual(scene["event_hash"], retrieved["event_hash"])
        self.assertEqual(narratives[0], history_packet(self.store, 1)["accepted_input"]["narrative"])
        self.assertEqual(before, self.snapshot())

    def test_zero_narrative_budget_keeps_every_deadline_and_obligation(self):
        records = {f"due-{number}": world_record("project", title=f"Test deadline {number}", due=100000 + number)
                   for number in range(18)}
        records["blocked"] = world_record("thread", title="Blocked test obligation", status="blocked", due=100)
        state = workflow_state(records)
        state["obligations"] = ["A mandatory test commitment " + "with a long explanation " * 100]
        state["standing_orders"] = ["Stop for a consequential test decision"]
        state["tasks"] = [task(due=100000), task(due=200, status="blocked", task_id="blocked-task")]
        state["interrupted_plan"] = {"objective": "Continue the test week", "endpoint_seconds": 604800,
                                     "remaining_seconds": 604800, "stopping_conditions": ["New test decision"]}
        self.initialize(state)
        note = "Pending test stakes must survive a small context budget"
        self.store.checkpoint(bind_head(self.store, {"request_id": "context-note", "resume_note": note}))
        packet = context_packet(self.store, recent_turns=0, max_chars=0)
        mandatory = packet["mandatory"]
        self.assertEqual(state["obligations"], mandatory["obligations"])
        self.assertEqual(state["standing_orders"], mandatory["standing_orders"])
        self.assertEqual(state["tasks"], mandatory["active_tasks"])
        self.assertEqual(records, mandatory["due_world_records"])
        self.assertEqual(state["interrupted_plan"], mandatory["interrupted_plan"])
        self.assertEqual(note, mandatory["resume_note"])
        self.assertEqual(set(records), set(packet["selected_records"]))
        self.assertEqual([], packet["recent_turns"])
        self.assertEqual(0, packet["narrative_budget"]["used_chars"])
        self.assertIn("mandatory", packet["narrative_budget"]["scope"])

    def test_complete_index_does_not_dump_unselected_details_and_focus_follows_links(self):
        records = {
            "test-clerk": world_record(links=["test-thread"]),
            "test-witness": world_record(title="Invented test witness"),
            "test-thread": world_record("thread", participants=["test-clerk"], known_by=["test-witness"],
                links=["test-fact"], details={"receipt": "Complete detailed test receipt"}),
            "test-fact": world_record("fact", status="closed", links=["test-thread"],
                details={"evidence": "Closed facts still matter to the selected thread"}),
            "unrelated": world_record("person", title="Unrelated test person", details={"long_history": "UNSELECTED_DETAIL " * 1000}),
        }
        self.initialize(workflow_state(records))
        packet = context_packet(self.store, focus_ids=["test-thread"], max_chars=0)
        self.assertEqual({"test-clerk", "test-thread", "test-witness", "unrelated"},
                         {row["id"] for row in packet["active_record_index"]})
        self.assertEqual({"test-fact"}, {row["id"] for row in packet["closed_record_index"]})
        self.assertEqual({"test-clerk", "test-witness", "test-thread", "test-fact"}, set(packet["selected_records"]))
        for record_id, record in packet["selected_records"].items():
            self.assertEqual(records[record_id], record)
        self.assertNotIn("UNSELECTED_DETAIL", json.dumps(packet))
        row = next(row for row in packet["active_record_index"] if row["id"] == "unrelated")
        retrieved = record_packet(self.store, row["retrieve"]["record_id"])
        self.assertEqual(records["unrelated"], retrieved["record"])
        self.assertEqual(self.store.head(), retrieved["head"])

    def test_closed_history_has_honest_counts_and_complete_searchable_pagination(self):
        records = {f"closed-{number:02}": world_record("fact", status="closed", title=f"Closed test fact {number}",
                    details={"finding": "Unique Search Token" if number == 17 else "Ordinary closed test evidence"})
                   for number in range(27)}
        records["active"] = world_record("project", due=100000)
        records["blocked"] = world_record("thread", status="blocked", due=200000)
        self.initialize(workflow_state(records))
        packet = context_packet(self.store, max_chars=0)
        self.assertEqual(27, packet["closed_records"]["total"])
        self.assertEqual(10, packet["closed_records"]["returned"])
        self.assertEqual(17, packet["closed_records"]["remaining"])
        self.assertEqual(10, len(packet["closed_record_index"]))
        self.assertEqual({"active", "blocked"}, set(packet["mandatory"]["due_world_records"]))
        collected = []
        offset = 0
        while offset is not None:
            page = record_index_packet(self.store, status="inactive", offset=offset, limit=7)
            self.assertEqual(29, page["total_records"])
            self.assertEqual(27, page["matched_records"])
            self.assertLessEqual(len(page["records"]), 7)
            collected.extend(row["id"] for row in page["records"])
            offset = page["next_offset"]
        self.assertEqual([f"closed-{number:02}" for number in range(27)], collected)
        found = record_index_packet(self.store, query="unique search token", kind="fact", status="closed")
        self.assertEqual(["closed-17"], [row["id"] for row in found["records"]])
        self.assertEqual(records["closed-17"], record_packet(self.store, found["records"][0]["retrieve"]["record_id"])["record"])
        self.assertEqual({"active", "blocked"}, {row["id"] for row in record_index_packet(self.store, status="open")["records"]})

    def test_focus_finds_incoming_closed_constraints_without_loading_unrelated_archives(self):
        records = {f"archive-{number:02}": world_record("fact", status="closed") for number in range(15)}
        records.update({
            "heir": world_record(title="Invented surviving heir"),
            "witness": world_record(title="Invented witness"),
            "z-capture": world_record("divergence", status="closed", links=["heir"],
                summary="The heir remains a prisoner; the closed capture cannot be undone by canon.",
                known_by=["witness"], details={"constraint": "RETRIEVE_CAPTURE_DETAIL"}),
            "z-death": world_record("person", status="dead", links=["heir"],
                summary="The heir's predecessor died and cannot resume the command."),
            "z-fact": world_record("fact", status="closed", participants=["heir"],
                summary="The heir's sworn obligation survives the settled meeting."),
            "old-speech": world_record("thread", status="completed", participants=["heir"],
                details={"wording": "UNNEEDED_SPEECH"}),
            "heard-only": world_record("divergence", status="closed", known_by=["heir"],
                details={"distant_event": "UNRELATED_KNOWN_FACT"}),
            "unrelated": world_record("divergence", status="closed", links=["witness"],
                details={"full_history": "UNRELATED_ARCHIVE"}),
        })
        self.initialize(workflow_state(records))
        packet = context_packet(self.store, focus_ids=["heir"], recent_turns=0, max_chars=0)
        self.assertEqual({"heir"}, set(packet["selected_records"]))
        constraints = {row["id"]: row for row in packet["continuity_record_index"]}
        self.assertEqual({"z-capture", "z-death", "z-fact"}, set(constraints))
        self.assertEqual(["witness"], constraints["z-capture"]["known_by"])
        self.assertEqual(["heir"], constraints["z-capture"]["related_to"])
        self.assertIn("z-capture", packet["selection"]["details_not_loaded"])
        for omitted in ("RETRIEVE_CAPTURE_DETAIL", "UNNEEDED_SPEECH", "UNRELATED_KNOWN_FACT", "UNRELATED_ARCHIVE"):
            self.assertNotIn(omitted, json.dumps(packet))
        capture = record_packet(self.store, constraints["z-capture"]["retrieve"]["record_id"])
        self.assertEqual(records["z-capture"], capture["record"])
        self.assertEqual(packet["continuity_record_index"], record_packet(self.store, "world.heir")["continuity_record_index"])
        self.assertEqual([], context_packet(self.store, recent_turns=0)["continuity_record_index"])

    def test_outbound_loaded_constraints_are_not_duplicated_and_pc_focus_is_explicit(self):
        records = {
            "heir": world_record(links=["old-oath"]),
            "old-oath": world_record("fact", status="closed", participants=["heir", "pc"]),
        }
        self.initialize(workflow_state(records))
        packet = context_packet(self.store, focus_ids=["heir"])
        self.assertEqual({"heir", "old-oath"}, set(packet["selected_records"]))
        self.assertEqual([], packet["continuity_record_index"])
        pc_packet = context_packet(self.store, focus_ids=["pc.character"])
        self.assertEqual(["old-oath"], [row["id"] for row in pc_packet["continuity_record_index"]])
        self.assertEqual(pc_packet["continuity_record_index"], record_packet(self.store, "pc.character")["continuity_record_index"])

    def test_full_character_task_source_and_capability_retrieval_preserve_separation(self):
        state = workflow_state({"test-clerk": world_record(), "character": world_record(title="World record with a colliding name")})
        state["tasks"] = [task(due=100000)]
        self.initialize(state)
        self.store.add_research(bind_head(self.store, {"request_id": "context-source", "sources": [source()]}))
        requested = ["pc.character", "task.test-delivery", "research.test-source", "capability.accounts"]
        packet = context_packet(self.store, read_record_ids=requested)
        self.assertEqual(set(requested), set(packet["selected_details"]))
        self.assertEqual({}, packet["selected_records"])
        self.assertEqual(state["character"], record_packet(self.store, "pc.character")["record"])
        self.assertEqual(state["world"]["records"]["character"], record_packet(self.store, "world.character")["record"])
        self.assertEqual({"record_id": "pc.character"}, packet["character_detail_reference"])
        self.assertEqual(state["tasks"][0], record_packet(self.store, "task.test-delivery")["record"])
        self.assertEqual(source(), record_packet(self.store, "research.test-source")["record"])
        self.assertEqual(2, record_packet(self.store, "capability.accounts")["record"]["rating"])
        self.assertEqual([], packet["known_context"]["knowledge"])
        self.assertIn("do not grant PC knowledge", packet["knowledge_note"])
        self.assertEqual(record_packet(self.store, "test-clerk")["record"],
                         record_packet(self.store, "world.test-clerk")["record"])

    def test_accepted_opening_uses_the_prose_budget_and_remains_retrievable_as_turn_zero(self):
        opening = "An accepted test opening with precise wording. " * 10
        payload = setup_payload(workflow_state())
        payload["opening_narrative"] = opening
        accepted = self.store.initialize(payload)
        packet = context_packet(self.store, max_chars=20)
        self.assertEqual([], packet["recent_turns"])
        self.assertEqual(opening[:20], packet["opening_scene"]["narrative"])
        self.assertTrue(packet["opening_scene"]["narrative_truncated"])
        self.assertEqual(len(opening) - 20, packet["narrative_budget"]["omitted_chars"])
        self.assertEqual(accepted["hash"], packet["opening_reference"]["event_hash"])
        self.assertEqual(opening, history_packet(self.store, 0)["accepted_input"]["opening_narrative"])
        self.assertEqual(0, self.store.current()["turn"])

    def test_history_keeps_original_prose_and_reports_later_same_turn_correction(self):
        self.initialize()
        narrative = "Original accepted test account.\n\nIt remains exactly as written.  "
        accepted = self.store.advance(advance_payload(self.store, narrative=narrative))
        fix = self.store.correct(bind_head(self.store, correction()))
        self.store.advance(advance_payload(self.store, narrative="A later test scene."))
        packet = history_packet(self.store, 1)
        self.assertEqual(narrative, packet["accepted_input"]["narrative"])
        self.assertEqual(accepted["hash"], packet["event_hash"])
        self.assertEqual(self.store.head(), packet["head"])
        self.assertEqual(1, len(packet["later_same_turn_notes"]))
        self.assertEqual(fix["hash"], packet["later_same_turn_notes"][0]["event_hash"])
        self.assertEqual((0, 3600), (packet["start_seconds"], packet["end_seconds"]))
        self.assertNotIn("state", packet)

    def test_opening_revision_is_current_but_original_setup_and_corrections_remain_retrievable(self):
        payload = setup_payload(workflow_state())
        payload["opening_narrative"] = "Original opening retained as evidence."
        original = self.store.initialize(payload)
        original_bytes = (self.store.path / "events" / "000000.json").read_bytes()
        revised_character = deepcopy(payload["state"]["character"])
        revised_character["background"] = "Corrected invented starting background."
        self.store.correct(bind_head(self.store, correction(request_id="opening-first", resources_delta={},
            changes={"character": revised_character}, evidence={"character": "The player's starting background was miscopied."},
            reason="Correct the background and remove its unsupported opening detail before play.",
            opening_narrative="First corrected opening.")))
        revised_character["equipment"] = ["Corrected test ledger"]
        latest = self.store.correct(bind_head(self.store, correction(request_id="opening-second", resources_delta={},
            changes={"character": revised_character}, evidence={"character": "The player's starting ledger description was miscopied."},
            reason="Use the player's settled pre-play equipment and starting description.",
            opening_narrative="Final corrected opening.")))
        packet = context_packet(self.store, max_chars=10)
        self.assertEqual("Final corr", packet["opening_scene"]["narrative"])
        self.assertEqual(latest["hash"], packet["opening_reference"]["event_hash"])
        self.assertEqual(len("Final corrected opening.") - 10, packet["narrative_budget"]["omitted_chars"])
        history = history_packet(self.store, 0)
        self.assertEqual(original["hash"], history["event_hash"])
        self.assertEqual(payload["opening_narrative"], history["accepted_input"]["opening_narrative"])
        self.assertEqual("Final corrected opening.", history["effective_opening_narrative"])
        self.assertEqual(latest["hash"], history["opening_reference"]["event_hash"])
        self.assertEqual(2, len(history["later_same_turn_notes"]))
        self.assertEqual(original_bytes, (self.store.path / "events" / "000000.json").read_bytes())
        self.store.advance(advance_payload(self.store))
        later = context_packet(self.store)
        self.assertNotIn("opening_scene", later)
        self.assertEqual(latest["hash"], later["opening_reference"]["event_hash"])

    def test_packet_mutations_do_not_change_canonical_records(self):
        self.initialize(workflow_state({"test-clerk": world_record()}))
        before = self.snapshot()
        packet = context_packet(self.store, focus_ids=["test-clerk"])
        packet["character"]["name"] = "Changed only in the returned object"
        packet["selected_records"]["test-clerk"]["summary"] = "Changed only in the returned object"
        retrieved = record_packet(self.store, "test-clerk")
        retrieved["record"]["summary"] = "Another unsaved change"
        self.assertEqual(before, self.snapshot())

    def test_missing_records_invalid_limits_and_unconfigured_stores_fail_clearly(self):
        awaiting = context_packet(self.store)
        self.assertEqual("awaiting_setup", awaiting["status"])
        self.assertIsNone(awaiting["head"])
        self.assertNotIn("character", awaiting)
        with self.assertRaises(CampaignError):
            record_packet(self.store, "character")
        self.initialize()
        for kwargs in ({"max_chars": -1}, {"max_chars": True}, {"recent_turns": False},
                       {"focus_ids": ["missing"]}, {"focus_ids": "not-a-list"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(CampaignError):
                context_packet(self.store, **kwargs)
        with self.assertRaises(CampaignError):
            history_packet(self.store, 20)
        with self.assertRaises(CampaignError):
            history_packet(self.store, True)

    def test_all_retrieval_paths_validate_the_full_chain_before_returning_content(self):
        self.initialize(workflow_state({"test-clerk": world_record()}))
        self.store.advance(advance_payload(self.store))
        self.store.advance(advance_payload(self.store))
        (self.store.path / "events" / "000001.json").unlink()
        for call in (lambda: context_packet(self.store), lambda: record_packet(self.store, "test-clerk"),
                     lambda: history_packet(self.store, 2), lambda: record_index_packet(self.store)):
            with self.assertRaises(CampaignError):
                call()


if __name__ == "__main__":
    unittest.main()
