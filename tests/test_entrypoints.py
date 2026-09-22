"""The player-facing start/continue flow publishes coherent local reading views."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from iron_engine.__main__ import main
from iron_engine.engine import CampaignError
from iron_engine.stories import Story, create_story, create_successor
from iron_engine.workflow import COVERAGE_FIELDS
from tests.fixtures import bind_head, setup_payload, starting_state, turn_payload


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("AGENTS.md", "iron_engine/engine.py", "rules/core.md",
                     "data/travel_distances.json", "references/books.md", "docs/research.md",
                     "docs/play_workflow.md", "docs/record_contract.md", "docs/travel.md",
                     "templates/advance.json", "templates/turn-output.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Invented shared test fixture only\n", encoding="utf-8")
        self.sheet = self.root / "supplied.md"
        self.sheet.write_text("# Invented supplied character\n", encoding="utf-8")

    def story(self, name="first", *, workflow=True):
        create_story(name, self.sheet, root=self.root)
        story = Story(name, root=self.root)
        state = starting_state()
        state["campaign"]["id"] = name
        if workflow:
            state["campaign"]["workflow_version"] = "1"
        payload = setup_payload(state)
        payload["opening_narrative"] = "An invented test clerk waits by the gate."
        (story.path / "opening.md").write_text(payload["opening_narrative"] + "\n", encoding="utf-8")
        (story.path / "setup.json").write_text(json.dumps(payload), encoding="utf-8")
        return story

    def cli(self, *arguments):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = main(list(arguments), root=self.root)
        return result, output.getvalue(), errors.getvalue()

    def input_file(self, payload):
        path = self.root / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def advance(self, story):
        return {
            "request_id": "test-advance", "expected_hash": story.store.head(), "expected_turn": 0,
            "objective": "Inspect the invented yard", "outcome": "Inspection is complete",
            "narrative": "The clerk checks the empty yard and shuts the gate.", "elapsed_seconds": 60,
            "operations": [], "authorization": {"objective": "Inspect the invented yard",
                "max_elapsed_seconds": 60, "stop_condition": "Stop after the inspection"},
            "adjudication": {"mode": "routine", "actor": "pc", "capability": None,
                "preparation": "Present at the yard", "opposition": "None established",
                "risk": "No meaningful uncertainty", "basis": "Routine visible inspection", "task_band": "routine"},
            "coverage": {key: {"status": "unchanged", "basis": "No change follows from this fixture inspection"}
                         for key in COVERAGE_FIELDS},
            "processed_tasks": {}, "review": None, "next_decision": "Choose the next invented test action.", "milestones": [],
        }

    @staticmethod
    def snapshot(path):
        return {str(item.relative_to(path)): item.read_bytes() for item in path.rglob("*") if item.is_file()}

    def test_start_rejects_opening_setup_mismatch_without_creating_events(self):
        story = self.story()
        (story.path / "opening.md").write_text("Different prepared opening.\n", encoding="utf-8")
        result = self.cli("--story", "first", "start")
        self.assertEqual(2, result[0], result)
        self.assertEqual([], story.validate())

    def test_start_accepts_preparation_once_and_later_resumes_without_reset(self):
        story = self.story()
        self.assertEqual([], story.validate())
        result = self.cli("--story", "first", "context")
        self.assertEqual(0, result[0], result)
        self.assertEqual("awaiting_setup", json.loads(result[1])["status"])
        first = self.cli("--story", "first", "start")
        self.assertEqual(0, first[0], first)
        self.assertEqual(0, json.loads(first[1])["turn"])
        self.assertIn("waits by the gate", (story.play_path / "latest.md").read_text())
        setup_events = story.validate()
        again = self.cli("--story", "first", "start")
        self.assertEqual(0, again[0], again)
        self.assertEqual(setup_events, story.validate())
        result = self.cli("--story", "first", "advance", self.input_file(self.advance(story)))
        self.assertEqual(0, result[0], result)
        events = story.validate()
        resumed = self.cli("--story", "first", "start")
        self.assertEqual(1, json.loads(resumed[1])["turn"])
        self.assertEqual(events, story.validate())

    def test_advance_refreshes_reading_pages_and_leaves_other_story_untouched(self):
        story = self.story()
        other = self.story("second")
        before = self.snapshot(other.path)
        story.start()
        payload = self.advance(story)
        result = self.cli("--story", "first", "advance", self.input_file(payload))
        self.assertEqual(0, result[0], result)
        for path in ("latest.md", "story.md", "turns/turn-000001.md"):
            self.assertIn(payload["narrative"], (story.play_path / path).read_text())
        context = self.cli("--story", "first", "context", "--recent", "1")
        self.assertEqual(0, context[0], context)
        self.assertEqual(story.store.head(), json.loads(context[1])["head"])
        history = self.cli("--story", "first", "history", "--turn", "1")
        self.assertEqual(payload, json.loads(history[1])["accepted_input"])
        self.assertEqual(before, self.snapshot(other.path))

    def test_failed_render_is_reported_as_saved_and_repair_does_not_replay(self):
        story = self.story()
        story.start()
        (story.play_path / "latest.md").write_text("Unmarked manual file\n", encoding="utf-8")
        result = self.cli("--story", "first", "advance", self.input_file(self.advance(story)))
        self.assertEqual(2, result[0], result)
        self.assertIn("Event accepted", result[2])
        accepted = story.validate()
        self.assertEqual(1, accepted[-1]["state"]["turn"])
        (story.play_path / "latest.md").unlink()
        repaired = self.cli("--story", "first", "render")
        self.assertEqual(0, repaired[0], repaired)
        self.assertEqual(accepted, story.validate())

    def test_successor_requires_death_and_preserves_world_without_granting_inheritance(self):
        predecessor = self.story(workflow=False)
        predecessor.start()
        with self.assertRaises(CampaignError):
            create_successor("next", self.sheet, "first", root=self.root)
        self.assertFalse((self.root / "stories" / "next").exists())
        death = bind_head(predecessor.store, turn_payload(seconds=60,
            changes={"alive": False, "death": {"cause": "Invented fatal fixture", "time_seconds": 60}},
            evidence={"alive": "Fatal fixture", "death": "Recorded at endpoint"}))
        predecessor.store.commit_turn(death)
        before = self.snapshot(predecessor.path)
        new_sheet = self.root / "new-character.md"
        new_sheet.write_text("# A different supplied successor\n", encoding="utf-8")
        result = self.cli("create-successor", "next", "--from-story", "first", "--character-sheet", str(new_sheet))
        self.assertEqual(0, result[0], result)
        successor = Story("next", root=self.root)
        self.assertEqual([], successor.validate())
        self.assertFalse((successor.path / "setup.json").exists())
        self.assertEqual(new_sheet.read_bytes(), successor.character_sheet_path.read_bytes())
        inherited = json.loads((successor.path / "notes" / "predecessor-world.json").read_text())
        self.assertEqual(predecessor.store.current(), inherited["state"])
        self.assertEqual(predecessor.store.head(), inherited["predecessor_hash"])
        self.assertEqual(before, self.snapshot(predecessor.path))


if __name__ == "__main__":
    unittest.main()
