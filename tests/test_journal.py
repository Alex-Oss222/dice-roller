"""Reading views preserve canonical prose and never become campaign state."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import re
import tempfile
import unittest

from iron_engine.__main__ import main
from iron_engine.engine import CampaignError, CampaignStore
from iron_engine.journal import FILENAMES, render_campaign
from tests.fixtures import bind_head, correction, setup_payload, source, starting_state, task, turn_payload
from tests.test_workflow import advance_payload, resource_op, workflow_state, world_record


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")
        self.output = self.root / "play"

    def initialize(self, state=None):
        self.store.initialize(setup_payload(state))

    def turn(self, number=0, **kwargs):
        return self.store.commit_turn(bind_head(self.store, turn_payload(number, **kwargs)))

    def snapshot(self):
        return {path.name: path.read_bytes() for path in (self.store.path / "events").iterdir()}

    def read(self, name):
        return (self.output / name).read_text(encoding="utf-8")

    def test_story_preserves_exact_prose_actual_turns_and_fictional_interval(self):
        state = starting_state()
        state["time_seconds"] = 43200
        self.initialize(state)
        self.store.add_research(bind_head(self.store, {"request_id": "journal-source", "sources": [source()]}))
        narrative = 'The test clerk counts eleven sacks.\n\n"I wrote twelve," he says.\nThe account remains open.  '
        first = self.turn(seconds=7200, narrative=narrative)
        self.store.correct(bind_head(self.store, correction()))
        second = self.turn(1, seconds=3 * 86400, narrative="The carrier returns three days later.")
        before = self.snapshot()
        render_campaign(self.store, self.output)
        story = self.read("story.md")
        self.assertIn(narrative, story)
        self.assertEqual(["1", "2"], re.findall(r"^## Turn (\d+)$", story, re.MULTILINE))
        self.assertIn("Day 0, 12:00:00 to Day 0, 14:00:00", story)
        self.assertIn("Day 0, 14:00:00 to Day 3, 14:00:00", story)
        self.assertIn("Phase: Test household service", story)
        self.assertIn("OOC record note: correction at Turn 1", story)
        self.assertIn("duplicate recorded charge", story)
        self.assertIn("resulting balance: 9", story)
        self.assertLess(story.index(narrative), story.index("OOC record note"))
        self.assertLess(story.index("OOC record note"), story.index("## Turn 2"))
        self.assertNotIn(source()["claim"], story)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(2, self.store.current()["turn"])
        self.assertEqual(2, first["sequence"])
        for name in FILENAMES:
            self.assertIn(second["hash"], self.read(name))

    def test_resume_preserves_pending_stakes_and_unspent_plan(self):
        state = starting_state()
        state["obligations"] = ["Report the test shortage"]
        state["tasks"] = [task(due=900000)]
        self.initialize(state)
        plan = {"objective": "Complete the test week", "endpoint_seconds": 604800,
                "remaining_seconds": 432000, "stopping_conditions": ["A consequential decision"]}
        self.turn(seconds=172800, changes={"interrupted_plan": plan},
                  evidence={"interrupted_plan": "Stop on day two, preserving five days"})
        pending = "Fixed test check: target 14; skill 2; failure delays delivery. No roll yet."
        self.store.checkpoint(bind_head(self.store, {"request_id": "journal-pending", "resume_note": pending}))
        before = self.snapshot()
        render_campaign(self.store, self.output)
        resume = self.read("resume.md")
        self.assertIn(pending, resume)
        self.assertIn("5 days, 0 hours, 0 minutes, 0 seconds", resume)
        self.assertIn("Day 7, 00:00:00", resume)
        self.assertIn("Report the test shortage", resume)
        self.assertIn("test-delivery [active]", resume)
        self.assertIn("context command validates the entire", resume)
        self.assertIn("Retrieve relevant records and older turns on demand", resume)
        self.assertIn("rules/iron_engine.md", resume)
        self.assertIn("Aim: Check the test account", resume)
        self.assertIn(pending, self.read("character-sheet.md"))
        self.assertEqual(before, self.snapshot())

    def test_turn_ledger_reports_actual_costs_condition_and_other_material_changes(self):
        state = starting_state()
        state["character"]["condition"] = {
            "rating": 8, "tags": ["Rested"], "basis": "The initial test assessment establishes ordinary good health"
        }
        self.initialize(state)
        character = self.store.current()["character"]
        character["condition"] = {
            "rating": 6, "tags": ["Test ankle restriction", "Short of sleep"],
            "basis": "The combined test effects restrict current function."
        }
        character["equipment"].append("Test bandage")
        narrative = 'The clerk pays two stags.\n\nThe carrier signs the test receipt.  '
        self.turn(narrative=narrative, resources_delta={"silver_stags": -2, "ration_days": 0},
                  changes={"character": character, "knowledge": ["The test ford is closed"]},
                  evidence={"resources.silver_stags": "Two stags paid for the recorded test supply",
                            "resources.ration_days": "No ration expenditure",
                            "character": "The recorded strain limits walking; a bandage was supplied",
                            "knowledge": "The test carrier reports the closed ford"})
        events_before = self.snapshot()
        render_campaign(self.store, self.output)
        story = self.read("story.md")
        self.assertIn(narrative, story)
        self.assertLess(story.index(narrative), story.index("### Ledger"))
        self.assertIn("silver_stags: 8 → 6 (-2)", story)
        self.assertIn("Two stags paid for the recorded test supply", story)
        self.assertNotIn("- ration_days:", story)
        self.assertIn("Condition: 8/9 Hale (Healthy) → 6/9 Worn (Strained)", story)
        self.assertIn("Test ankle restriction; Short of sleep", story)
        self.assertEqual(1, story.count(character["condition"]["basis"]))
        self.assertIn("Character (equipment): updated", story)
        self.assertIn("Knowledge: updated. Evidence: The test carrier reports the closed ford", story)
        self.assertNotIn('"skills":', story)
        self.assertEqual(events_before, self.snapshot())

    def test_time_only_and_unchanged_replacements_do_not_create_a_ledger(self):
        self.initialize()
        self.turn(seconds=3600)
        state = self.store.current()
        self.turn(1, seconds=7200, resources_delta={"silver_stags": 0},
                  changes={"character": state["character"], "phase": state["phase"], "location": state["location"]},
                  evidence={"resources.silver_stags": "No expenditure", "character": "The assessment is unchanged",
                            "phase": "Service continues", "location": "The character remains at the same yard"})
        render_campaign(self.store, self.output)
        story = self.read("story.md")
        self.assertNotIn("### Ledger", story)
        self.assertEqual(["1", "2"], re.findall(r"^## Turn (\d+)$", story, re.MULTILINE))

    def test_workflow_turn_matches_shared_presentation_and_decision_index(self):
        self.store.initialize(setup_payload(workflow_state()))
        accepted = self.store.advance(advance_payload(
            self.store, next_decision="Choose whether to continue the invented account review."))
        render_campaign(self.store, self.output)
        turn = self.read("turns/turn-000001.md")
        self.assertIn("| Field | Current |", turn)
        self.assertIn("| Name | Test Adult |", turn)
        self.assertIn("| Age | 30 |", turn)
        self.assertIn("| Condition | 8/9 Hale (Healthy) |", turn)
        self.assertRegex(turn, r"## Turn 1 \\| Day 0, ")
        self.assertIn("### Next\n\nChoose whether to continue the invented account review.", turn)
        self.assertEqual("Choose whether to continue the invented account review.",
                         accepted["state"]["resume_note"])
        decisions = self.read("decisions.md")
        self.assertIn("## Turn 1", decisions)
        self.assertIn("Objective:", decisions)
        self.assertIn("Outcome:", decisions)
        self.assertIn("Pending next decision: Choose whether to continue the invented account review.", decisions)

    def test_new_resource_is_shown_as_unrecorded_even_when_its_established_balance_is_zero(self):
        for amount in (0, 3):
            with self.subTest(amount=amount):
                state = workflow_state()
                state["resources"] = {}
                store = CampaignStore(self.root / f"established-{amount}")
                store.initialize(setup_payload(state))
                establish = {"op": "resource_establish", "unit": "silver_stags", "expected": None, "value": amount,
                             "basis": "The test account is inspected and its previously unrecorded amount is established"}
                store.advance(advance_payload(store, operations=[establish], changed=("resources",)))
                output = self.root / f"play-{amount}"
                render_campaign(store, output)
                story = (output / "story.md").read_text(encoding="utf-8")
                self.assertIn(f"silver_stags: unrecorded → {amount}", story)
                self.assertNotIn(f"silver_stags: 0 → {amount}", story)
                self.assertIn(establish["basis"], story)
                store.advance(advance_payload(store, operations=[resource_op(expected=amount, delta=0)]))
                render_campaign(store, output)
                self.assertNotIn("### Ledger", (output / "latest.md").read_text(encoding="utf-8"))

    def test_condition_only_ledger_has_no_character_dump_and_survives_later_correction(self):
        state = starting_state()
        state["character"]["condition"] = {"rating": 8, "tags": ["Rested"], "basis": "Initial test assessment"}
        self.initialize(state)
        character = self.store.current()["character"]
        character["condition"] = {"rating": 6, "tags": ["Test exertion"], "basis": "The accepted test exertion limits function"}
        narrative = "The clerk finishes the inventory.\n\nThe account is closed."
        self.turn(narrative=narrative, changes={"character": character},
                  evidence={"character": "The turn records the observed effects of test exertion"})
        character["condition"] = {"rating": 7, "tags": ["Test exertion"], "basis": "Correct the clerical rating entry"}
        self.store.correct(bind_head(self.store, correction(changes={"character": character}, resources_delta={},
            evidence={"character": "The recorded test rating was copied incorrectly"})))
        render_campaign(self.store, self.output)
        story = self.read("story.md")
        original_turn, correction_note = story.split("### OOC record note", 1)
        self.assertIn(narrative, original_turn)
        self.assertIn("8/9 Hale (Healthy) → 6/9 Worn (Strained)", original_turn)
        self.assertNotIn("Character (", original_turn)
        self.assertNotIn('"skills":', original_turn)
        self.assertNotIn("7/9", original_turn)
        self.assertIn("copied incorrectly", correction_note)
        self.assertEqual(7, self.store.current()["character"]["condition"]["rating"])

    def test_same_head_render_is_byte_identical_and_does_not_rewrite_files(self):
        self.initialize()
        self.turn()
        render_campaign(self.store, self.output)
        before = {path.relative_to(self.output).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                  for path in self.output.rglob("*.md")}
        render_campaign(self.store, self.output)
        after = {path.relative_to(self.output).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                 for path in self.output.rglob("*.md")}
        self.assertEqual(before, after)
        self.assertEqual({"story.md", "character-sheet.md", "resume.md", "README.md", "latest.md", "threads.md", "world.md", "decisions.md", "turns"},
                         {path.name for path in self.output.iterdir()})

    def test_compact_turn_history_is_byte_stable_after_later_corrections_and_turns(self):
        self.store.initialize(setup_payload(workflow_state()))
        narrative = "The test clerk pays the carrier.\n\nThe receipt remains on the account.  "
        accepted = self.store.advance(advance_payload(self.store, narrative=narrative,
            operations=[resource_op()], changed=("resources",)))
        render_campaign(self.store, self.output)
        historical = self.output / "turns" / "turn-000001.md"
        first_bytes = historical.read_bytes()
        first_time = historical.stat().st_mtime_ns
        self.assertIn(narrative.encode("utf-8"), first_bytes)
        self.assertIn(accepted["hash"].encode("ascii"), first_bytes)
        self.assertIn("silver_stags: 8 → 6 (-2)", first_bytes.decode("utf-8"))
        correction_event = self.store.correct(bind_head(self.store, correction()))
        render_campaign(self.store, self.output)
        self.assertEqual(first_bytes, historical.read_bytes())
        self.assertEqual(first_time, historical.stat().st_mtime_ns)
        latest = self.read("latest.md")
        self.assertIn(narrative, latest)
        self.assertIn("OOC record note", latest)
        self.assertIn(correction_event["hash"], latest)
        next_event = self.store.advance(advance_payload(self.store, narrative="The second test scene begins."))
        render_campaign(self.store, self.output)
        self.assertEqual(first_bytes, historical.read_bytes())
        self.assertEqual(first_time, historical.stat().st_mtime_ns)
        self.assertNotIn(next_event["hash"].encode("ascii"), historical.read_bytes())
        self.assertIn("The second test scene begins.", self.read("latest.md"))
        self.assertIn("turns/turn-000001.md", self.read("README.md"))
        self.assertIn("turns/turn-000002.md", self.read("README.md"))

    def test_recorded_opening_is_rendered_verbatim_without_creating_a_first_turn(self):
        opening = "The test clerk opens the ledger.\n\nNothing has yet been charged.  "
        payload = setup_payload(workflow_state())
        payload["opening_narrative"] = opening
        self.store.initialize(payload)
        render_campaign(self.store, self.output)
        self.assertIn(opening, self.read("story.md"))
        self.assertIn(opening, self.read("latest.md"))
        self.assertIn("Opening: Turn 0", self.read("story.md"))
        self.assertNotIn("## Turn 1", self.read("story.md"))
        self.assertFalse((self.output / "turns" / "turn-000001.md").exists())
        self.assertEqual(0, self.store.current()["turn"])

    def test_world_and_thread_views_preserve_closed_records_and_knowledge_attribution(self):
        records = {"test-clerk": world_record(),
                   "open-thread": world_record("thread", title="Unresolved test account", participants=["test-clerk"],
                       due=100000, known_by=["test-clerk"]),
                   "closed-thread": world_record("thread", title="Settled test account", status="closed",
                       summary="The closed test account remains in history")}
        self.store.initialize(setup_payload(workflow_state(records)))
        render_campaign(self.store, self.output)
        world = self.read("world.md")
        threads = self.read("threads.md")
        for record_id in records:
            self.assertIn(record_id, world)
        self.assertIn("Unresolved test account", threads)
        self.assertIn("Settled test account", threads)
        self.assertIn("Known by: test-clerk", world)
        self.assertEqual([], self.store.current()["knowledge"])

    def test_ten_turn_review_is_readable_and_separate_from_accepted_prose(self):
        self.initialize()
        for number in range(10):
            self.turn(number)
        render_campaign(self.store, self.output)
        story = self.read("story.md")
        self.assertIn("### OOC assessment: turns 1 to 10", story)
        self.assertIn("#### Gm consistency", story)
        self.assertIn("#### Next constraint", story)
        self.assertIn("routine work is recorded; ability remains uncertain", story)
        self.assertIn("Evidence turns: 1, 10.", story)
        self.assertLess(story.index("## Turn 10"), story.index("### OOC assessment"))
        self.assertEqual([str(number) for number in range(1, 11)],
                         re.findall(r"^## Turn (\d+)$", story, re.MULTILINE))

    def test_new_head_refreshes_owned_views_and_preserves_unrelated_files(self):
        self.initialize()
        render_campaign(self.store, self.output)
        old_head = self.store.head()
        unrelated = self.output / "notes.txt"
        unrelated.write_text("Unrelated player notes", encoding="utf-8")
        accepted = self.turn()
        render_campaign(self.store, self.output)
        for name in FILENAMES:
            self.assertIn(accepted["hash"], self.read(name))
            self.assertNotIn(old_head, self.read(name))
        self.assertEqual("Unrelated player notes", unrelated.read_text(encoding="utf-8"))

    def test_awaiting_setup_renders_no_character_or_invented_story(self):
        render_campaign(self.store, self.output)
        for name in FILENAMES:
            self.assertIn("Awaiting setup", self.read(name))
            self.assertIn("source-event-hash:awaiting-setup", self.read(name))
            self.assertNotIn("Test Adult", self.read(name))
            self.assertNotIn("## Turn 1", self.read(name))
        self.assertFalse(self.store.path.exists())

    def test_render_refuses_store_directories_and_preserves_event_bytes(self):
        self.initialize()
        before = self.snapshot()
        other = CampaignStore(self.root / "other-campaign")
        other.initialize(setup_payload())
        for output in (self.store.path, self.store.path / "events", self.store.path / "nested",
                       self.store.path / "events" / "nested", self.root / "another" / "events", other.path):
            with self.subTest(output=output), self.assertRaises(CampaignError):
                render_campaign(self.store, output)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(0, other.current()["turn"])

    def test_hostile_reserved_file_prevents_all_view_writes(self):
        self.initialize()
        self.output.mkdir()
        protected = self.output / "character-sheet.md"
        protected.write_text("Player-authored material, preserve exactly.", encoding="utf-8")
        with self.assertRaises(CampaignError):
            render_campaign(self.store, self.output)
        self.assertEqual("Player-authored material, preserve exactly.", protected.read_text(encoding="utf-8"))
        self.assertFalse((self.output / "story.md").exists())
        self.assertFalse((self.output / "resume.md").exists())

    def test_output_symlinks_and_hardlinked_files_are_rejected(self):
        self.initialize()
        self.output.mkdir()
        protected = self.root / "player-notes.md"
        protected.write_text("Player notes", encoding="utf-8")
        destination = self.output / "story.md"
        destination.symlink_to(protected)
        with self.assertRaises(CampaignError):
            render_campaign(self.store, self.output)
        self.assertEqual("Player notes", protected.read_text(encoding="utf-8"))
        destination.unlink()
        linked_dir = self.root / "linked-play"
        linked_dir.symlink_to(self.output, target_is_directory=True)
        with self.assertRaises(CampaignError):
            render_campaign(self.store, linked_dir)
        render_campaign(self.store, self.output)
        (self.root / "linked-story.md").hardlink_to(destination)
        with self.assertRaises(CampaignError):
            render_campaign(self.store, self.output)

    def test_corrupted_chain_is_rejected_before_touching_existing_views(self):
        self.initialize()
        self.turn()
        render_campaign(self.store, self.output)
        before = {name: (self.output / name).read_bytes() for name in FILENAMES}
        event = self.store.path / "events" / "000001.json"
        data = json.loads(event.read_text(encoding="utf-8"))
        data["input"]["narrative"] = "Altered without a valid event hash"
        event.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(CampaignError):
            render_campaign(self.store, self.output)
        self.assertEqual(before, {name: (self.output / name).read_bytes() for name in FILENAMES})

    def test_dead_character_resume_does_not_invite_more_turns(self):
        self.initialize()
        self.turn(seconds=60, changes={"alive": False, "death": {"cause": "Test fatal injury", "time_seconds": 60}},
                  evidence={"alive": "Fatal test result", "death": "Test death at interval endpoint"})
        render_campaign(self.store, self.output)
        self.assertIn("Do not advance this character or reverse the death", self.read("resume.md"))
        self.assertIn("Test fatal injury", self.read("resume.md"))

    def test_cli_render_preserves_existing_commands(self):
        self.initialize()
        with redirect_stdout(StringIO()) as output, redirect_stderr(StringIO()):
            result = main(["--store", str(self.store.path), "render", "--output", str(self.output)])
        self.assertEqual(0, result)
        self.assertIn("story.md", output.getvalue())
        with redirect_stdout(StringIO()) as head:
            result = main(["--store", str(self.store.path), "head"])
        self.assertEqual(0, result)
        self.assertEqual(self.store.head(), head.getvalue().strip())


if __name__ == "__main__":
    unittest.main()
