"""Story selection isolates state, generated views, saves, and baseline choices."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from iron_engine.__main__ import main
from iron_engine.engine import CampaignError, CampaignStore
from iron_engine.stories import Story, create_story
from tests.fixtures import bind_head, setup_payload, starting_state, turn_payload


class StoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # These files represent a complete tiny shared baseline. They are test
        # data only; executable imports still use the actual tested package.
        self.shared = {
            "AGENTS.md": "Shared instructions, with no selected protagonist.\n",
            "iron_engine/engine.py": "# Shared test baseline engine version\n",
            "rules/core.md": "# Shared test rules\n",
            "data/travel_distances.json": '{"test_fixture": true}\n',
            "references/books.md": "# Shared source policy, no story-specific facts\n",
            "docs/research.md": "# Shared research procedure\n",
        }
        for relative, content in self.shared.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.sheet = self.root / "incoming" / "character.md"
        self.sheet.parent.mkdir()
        self.sheet.write_text("# Character preparation\n\nName: TBD\nBackground: TBD\n", encoding="utf-8")
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()

    def cli(self, *args, root=None):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            try:
                status = main(list(args), root=root or self.root)
            except SystemExit as exc:
                status = exc.code
        return status, output.getvalue(), errors.getvalue()

    def write_input(self, name, payload):
        path = self.inputs / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def create(self, story_id):
        create_story(story_id, self.sheet, root=self.root)
        return Story(story_id, root=self.root)

    def initialize(self, story_id):
        story = self.create(story_id)
        state = starting_state()
        state["campaign"]["id"] = story_id
        state["campaign"]["title"] = f"Invented {story_id} fixture"
        path = self.write_input(f"{story_id}-setup.json", setup_payload(state))
        result = self.cli("--story", story_id, "init", path)
        self.assertEqual(0, result[0], result)
        return story

    @staticmethod
    def snapshot(path):
        return {str(child.relative_to(path)): child.read_bytes()
                for child in path.rglob("*") if child.is_file() and not child.is_symlink()}

    def shared_snapshot(self):
        return {relative: (self.root / relative).read_bytes() for relative in self.shared}

    def test_creation_copies_character_preparation_without_starting_a_story(self):
        before = self.shared_snapshot()
        result = self.cli("create-story", "story-1", "--character-sheet", str(self.sheet))
        self.assertEqual(0, result[0], result)
        story = Story("story-1", root=self.root)
        self.assertEqual([], story.validate())
        self.assertFalse((story.store.path / "events").exists())
        self.assertEqual(self.sheet.read_bytes(), (story.path / "character-sheet.md").read_bytes())
        manifest = json.loads((story.path / "story.json").read_text(encoding="utf-8"))
        self.assertEqual("story-1", manifest["story_id"])
        self.assertEqual(hashlib.sha256(self.sheet.read_bytes()).hexdigest(), manifest["character_sheet_sha256"])
        for name in ("story.md", "character-sheet.md", "resume.md"):
            text = (story.play_path / name).read_text(encoding="utf-8")
            self.assertIn("Awaiting setup", text)
            self.assertNotIn("Test Adult", text)
            self.assertNotIn("## Turn 1", text)
        self.assertEqual(before, self.shared_snapshot())

    def test_turn_render_and_save_leave_other_story_and_shared_files_unchanged(self):
        first = self.initialize("story-1")
        second = self.initialize("story-2")
        other_before = self.snapshot(second.path)
        shared_before = self.shared_snapshot()
        narrative = "The test clerk records Story 1's result and closes the account."
        payload = bind_head(first.store, turn_payload(
            narrative=narrative,
            changes={"assumptions": ["The invented local route is closed only in Story 1."]},
            evidence={"assumptions": "A local test event establishes this story-specific fact"},
        ))
        path = self.write_input("story-1-turn.json", payload)
        for arguments in (("turn", path), ("render",), ("save", "checkpoint.json")):
            result = self.cli("--story", "story-1", *arguments)
            self.assertEqual(0, result[0], result)
        self.assertEqual(1, first.store.current()["turn"])
        self.assertEqual(0, second.store.current()["turn"])
        self.assertIn(narrative, (first.play_path / "story.md").read_text(encoding="utf-8"))
        saved = json.loads((first.path / "saves" / "checkpoint.json").read_text(encoding="utf-8"))
        self.assertEqual(first.validate(), saved["campaign_save"]["events"])
        self.assertEqual(other_before, self.snapshot(second.path))
        self.assertEqual(shared_before, self.shared_snapshot())
        self.assertFalse((self.root / "campaign").exists())
        self.assertFalse((self.root / "play").exists())

    def test_state_commands_never_infer_the_only_story_or_use_global_defaults(self):
        self.create("story-1")
        setup = self.write_input("setup.json", setup_payload())
        before = self.snapshot(self.root / "stories")
        for arguments in (("status",), ("validate",), ("head",), ("render",),
                          ("init", setup), ("save", "unspecified.json"), ("restore", setup)):
            with self.subTest(command=arguments[0]):
                result = self.cli(*arguments)
                self.assertEqual(2, result[0], result)
        self.assertEqual(before, self.snapshot(self.root / "stories"))
        self.assertFalse((self.root / "campaign").exists())
        self.assertFalse((self.root / "play").exists())
        self.assertFalse((self.root / "unspecified.json").exists())

    def test_invalid_ids_and_reusing_story_directory_are_refused(self):
        story = self.create("story-1")
        before = self.snapshot(story.path)
        for story_id in ("../story-2", "nested/story", ".", "", str(self.root / "absolute")):
            with self.subTest(story_id=story_id), self.assertRaises(CampaignError):
                create_story(story_id, self.sheet, root=self.root)
        with self.assertRaises(CampaignError):
            create_story("story-1", self.sheet, root=self.root)
        self.assertEqual(before, self.snapshot(story.path))

    def test_story_and_source_symlinks_do_not_redirect_creation_or_access(self):
        story = self.create("story-1")
        before = self.snapshot(story.path)
        linked_story = self.root / "stories" / "story-link"
        linked_story.symlink_to(story.path, target_is_directory=True)
        with self.assertRaises(CampaignError):
            Story("story-link", root=self.root).validate()
        with self.assertRaises(CampaignError):
            create_story("story-link", self.sheet, root=self.root)
        linked_sheet = self.root / "incoming" / "linked.md"
        linked_sheet.symlink_to(self.sheet)
        with self.assertRaises(CampaignError):
            create_story("linked-input", linked_sheet, root=self.root)
        self.assertEqual(before, self.snapshot(story.path))
        self.assertFalse((self.root / "stories" / "linked-input").exists())

    def test_selected_story_cannot_write_views_or_saves_into_another_story(self):
        first = self.initialize("story-1")
        second = self.initialize("story-2")
        before = self.snapshot(second.path)
        for arguments in (("render", "--output", str(second.play_path)),
                          ("save", str(second.path / "saves" / "wrong.json")),
                          ("save", "../story-2/wrong.json")):
            with self.subTest(arguments=arguments):
                result = self.cli("--story", "story-1", *arguments)
                self.assertEqual(2, result[0], result)
        self.assertEqual(before, self.snapshot(second.path))
        self.assertEqual(0, first.store.current()["turn"])
        result = self.cli("--story", "story-1", "--store", str(second.store.path), "status")
        self.assertEqual(2, result[0], result)

    def test_setup_and_restore_must_match_the_selected_story_identity(self):
        first = self.initialize("story-1")
        second = self.create("story-2")
        before = self.snapshot(second.path)
        wrong_state = starting_state()
        wrong_state["campaign"]["id"] = "story-1"
        path = self.write_input("wrong-identity.json", setup_payload(wrong_state))
        result = self.cli("--story", "story-2", "init", path)
        self.assertEqual(2, result[0], result)
        result = self.cli("--story", "story-1", "save", "transfer.json")
        self.assertEqual(0, result[0], result)
        result = self.cli("--story", "story-2", "restore", str(first.path / "saves" / "transfer.json"))
        self.assertEqual(2, result[0], result)
        self.assertEqual([], second.validate())
        self.assertEqual(before, self.snapshot(second.path))

    def test_manifest_identity_mismatch_does_not_load_another_story(self):
        story = self.initialize("story-1")
        records = self.snapshot(story.store.path)
        manifest_path = story.path / "story.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["story_id"] = "story-2"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.cli("--story", "story-1", "status")
        self.assertEqual(2, result[0], result)
        self.assertEqual(records, self.snapshot(story.store.path))

    def test_story_save_restores_matching_baseline_and_rejects_unmatched_provenance(self):
        first = self.initialize("story-1")
        result = self.cli("--story", "story-1", "save", "portable.json")
        self.assertEqual(0, result[0], result)
        saved_path = first.path / "saves" / "portable.json"
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        manifest = json.loads((first.path / "story.json").read_text(encoding="utf-8"))
        self.assertEqual({"story_save_version", "story_id", "shared_files", "campaign_save"}, set(saved))
        self.assertEqual(1, saved["story_save_version"])
        self.assertEqual("story-1", saved["story_id"])
        self.assertEqual(manifest["shared_files"], saved["shared_files"])
        destination = self.root / "matching-project"
        for relative in self.shared:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((self.root / relative).read_bytes())
        create_story("story-1", self.sheet, root=destination)
        restored = Story("story-1", root=destination)
        before = self.snapshot(restored.path)
        for case in ("foreign_story", "different_baseline", "legacy_without_pin"):
            with self.subTest(case=case):
                candidate = json.loads(json.dumps(saved))
                if case == "foreign_story":
                    candidate["story_id"] = "story-2"
                elif case == "different_baseline":
                    candidate["shared_files"]["rules/core.md"] = "0" * 64
                else:
                    candidate = candidate["campaign_save"]
                path = self.write_input(f"restore-{case}.json", candidate)
                result = self.cli("--story", "story-1", "restore", path, root=destination)
                self.assertEqual(2, result[0], result)
                self.assertEqual(before, self.snapshot(restored.path))
        result = self.cli("--story", "story-1", "restore", str(saved_path), root=destination)
        self.assertEqual(0, result[0], result)
        self.assertEqual(first.validate(), restored.validate())
        self.assertEqual(manifest["shared_files"],
                         json.loads((restored.path / "story.json").read_text(encoding="utf-8"))["shared_files"])

    def test_shared_drift_blocks_new_results_but_preserves_readable_history(self):
        first = self.initialize("story-1")
        second = self.initialize("story-2")
        other_before = self.snapshot(second.path)
        records_before = self.snapshot(first.store.path)
        rules = self.root / "rules" / "core.md"
        rules.write_text("# Changed shared rules awaiting an explicit upgrade decision\n", encoding="utf-8")
        mismatches = Story("story-1", root=self.root).baseline_mismatches()
        self.assertTrue(mismatches)
        payload = bind_head(first.store, turn_payload())
        path = self.write_input("drift-turn.json", payload)
        result = self.cli("--story", "story-1", "turn", path)
        self.assertEqual(2, result[0], result)
        for arguments in (("status",), ("validate",), ("head",), ("render",), ("save", "after-drift.json")):
            with self.subTest(command=arguments[0]):
                result = self.cli("--story", "story-1", *arguments)
                self.assertEqual(0, result[0], result)
        self.assertEqual(records_before, self.snapshot(first.store.path))
        self.assertEqual(other_before, self.snapshot(second.path))
        self.assertEqual(0, first.store.current()["turn"])
        self.assertTrue((first.path / "saves" / "after-drift.json").exists())
        saved = json.loads((first.path / "saves" / "after-drift.json").read_text(encoding="utf-8"))
        pinned = json.loads((first.path / "story.json").read_text(encoding="utf-8"))["shared_files"]
        self.assertEqual(pinned, saved["shared_files"])

    def test_pin_detects_added_and_missing_shared_files_before_initialization(self):
        story = self.create("story-1")
        manifest = json.loads((story.path / "story.json").read_text(encoding="utf-8"))
        self.assertEqual(set(self.shared), set(manifest["shared_files"]))
        for relative in self.shared:
            self.assertEqual(hashlib.sha256((self.root / relative).read_bytes()).hexdigest(),
                             manifest["shared_files"][relative])
        state = starting_state()
        state["campaign"]["id"] = "story-1"
        path = self.write_input("pinned-setup.json", setup_payload(state))
        extra = self.root / "rules" / "added.md"
        extra.write_text("# New shared rule\n", encoding="utf-8")
        self.assertTrue(Story("story-1", root=self.root).baseline_mismatches())
        self.assertEqual(2, self.cli("--story", "story-1", "init", path)[0])
        extra.unlink()
        original = (self.root / "references" / "books.md").read_bytes()
        (self.root / "references" / "books.md").unlink()
        self.assertTrue(Story("story-1", root=self.root).baseline_mismatches())
        self.assertEqual(2, self.cli("--story", "story-1", "init", path)[0])
        (self.root / "references" / "books.md").write_bytes(original)
        self.assertEqual([], Story("story-1", root=self.root).baseline_mismatches())
        self.assertEqual([], story.validate())

    def test_draft_edits_never_replace_the_saved_character(self):
        story = self.initialize("story-1")
        events = story.validate()
        (story.path / "character-sheet.md").write_text("# Later draft\nName: Somebody Else\n", encoding="utf-8")
        self.assertEqual([], Story("story-1", root=self.root).baseline_mismatches())
        result = self.cli("--story", "story-1", "render")
        self.assertEqual(0, result[0], result)
        self.assertEqual(events, story.validate())
        self.assertEqual("Test Adult", story.store.current()["character"]["name"])
        self.assertNotIn("Somebody Else", (story.play_path / "character-sheet.md").read_text(encoding="utf-8"))

    def test_explicit_legacy_store_works_but_render_requires_explicit_output(self):
        store_path = self.root / "legacy-campaign"
        input_path = self.write_input("legacy-setup.json", setup_payload())
        result = self.cli("--store", str(store_path), "init", input_path)
        self.assertEqual(0, result[0], result)
        self.assertEqual(0, self.cli("--store", str(store_path), "status")[0])
        self.assertEqual(2, self.cli("--store", str(store_path), "render")[0])
        output = self.root / "legacy-play"
        result = self.cli("--store", str(store_path), "render", "--output", str(output))
        self.assertEqual(0, result[0], result)
        self.assertTrue((output / "character-sheet.md").exists())
        save_path = self.root / "legacy-save.json"
        result = self.cli("--store", str(store_path), "save", str(save_path))
        self.assertEqual(0, result[0], result)
        self.assertEqual({"schema_version", "events"}, set(json.loads(save_path.read_text(encoding="utf-8"))))
        restored_path = self.root / "legacy-restored"
        result = self.cli("--store", str(restored_path), "restore", str(save_path))
        self.assertEqual(0, result[0], result)
        self.assertEqual(CampaignStore(store_path).validate(), CampaignStore(restored_path).validate())
        self.assertFalse((self.root / "play").exists())
        self.assertFalse((self.root / "campaign").exists())


if __name__ == "__main__":
    unittest.main()
