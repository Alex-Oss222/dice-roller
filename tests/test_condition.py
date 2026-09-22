"""Condition is an explicit judgment, separate from ability and elapsed time.

Every character, cause, and treatment below is an invented test fixture.
"""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from iron_engine.engine import CampaignError, CampaignStore, character_sheet
from iron_engine.journal import render_campaign
from tests.fixtures import bind_head, correction, setup_payload, starting_state, turn_payload
from tests.test_capabilities import capability_state


def explicit_condition(rating=6, tags=None, basis="Combined assessment of the documented test causes, not a per-tag deduction"):
    return {"rating": rating, "tags": tags if tags is not None else ["Test ankle restriction", "Short of sleep"], "basis": basis}


class ConditionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")

    def initialize(self, condition=None, state=None):
        state = deepcopy(state or starting_state())
        state["character"]["condition"] = explicit_condition() if condition is None else deepcopy(condition)
        return self.store.initialize(setup_payload(state))

    def draft(self, character=None, **kwargs):
        state = self.store.current()
        fields = {} if character is None else {"character": deepcopy(character)}
        evidence = {} if character is None else {"character": "Documented test condition assessment"}
        payload = turn_payload(state["turn"], changes=fields, evidence=evidence, **kwargs)
        return bind_head(self.store, payload)

    def correct_character(self, character, **kwargs):
        return bind_head(self.store, correction(changes={"character": deepcopy(character)}, resources_delta={},
            evidence={"character": "Repair an incorrectly recorded test condition assessment"}, **kwargs))

    def reject_without_mutation(self, operation, payload):
        before = self.store.validate()
        with self.assertRaises(CampaignError):
            operation(payload)
        self.assertEqual(before, self.store.validate())

    def test_live_rating_extremes_and_custom_multiple_causes_are_explicit(self):
        for rating in (1, 9):
            with self.subTest(rating=rating):
                state = starting_state()
                state["character"]["condition"] = explicit_condition(rating,
                    tags=["Invented travel fatigue", "Invented treated wound", "Invented poor nutrition"])
                store = CampaignStore(self.root / f"rating-{rating}")
                store.initialize(setup_payload(state))
                self.assertEqual(state["character"]["condition"], store.current()["character"]["condition"])
                self.assertEqual(state["character"]["skills"], store.current()["character"]["skills"])

    def test_invalid_rating_type_shape_and_empty_descriptors_are_rejected(self):
        invalid = [
            explicit_condition(-1), explicit_condition(10), explicit_condition(True), explicit_condition(1.5),
            explicit_condition("6"), explicit_condition(float("nan")), explicit_condition(tags=[]),
            explicit_condition(tags=[""]), explicit_condition(tags=["  "]), explicit_condition(tags=["Test cause", 3]),
            explicit_condition(tags="Test cause"), explicit_condition(basis=" "),
            {"rating": 6, "tags": ["Test cause"]},
            {"rating": 6, "tags": ["Test cause"], "basis": "Test", "penalty": 2},
            None, [], "Not a structured condition",
        ]
        for number, value in enumerate(invalid):
            with self.subTest(value=value):
                state = starting_state()
                state["character"]["condition"] = value
                store = CampaignStore(self.root / f"invalid-{number}")
                with self.assertRaises(CampaignError):
                    store.initialize(setup_payload(state))
                self.assertEqual([], store.validate())

    def test_elapsed_time_neither_recovers_condition_nor_deducts_for_each_tag(self):
        condition = explicit_condition(7,
            tags=["Test splint", "Test sleep debt", "Test missed meal", "Test strain"],
            basis="Overall function is explicitly assessed at seven; this is not nine minus the tag count")
        self.initialize(condition)
        skills = deepcopy(self.store.current()["character"]["skills"])
        self.store.commit_turn(self.draft(seconds=7 * 86400))
        self.assertEqual(condition, self.store.current()["character"]["condition"])
        self.assertEqual(skills, self.store.current()["character"]["skills"])

    def test_condition_change_requires_complete_character_and_causal_evidence(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["condition"] = explicit_condition(8, tags=["Rested after test convalescence"],
            basis="The documented test examination supports improved function")
        missing_evidence = self.draft(character)
        missing_evidence["evidence"] = {}
        self.reject_without_mutation(self.store.commit_turn, missing_evidence)
        self.reject_without_mutation(self.store.commit_turn, self.draft({"condition": character["condition"]}))
        accepted = self.store.commit_turn(self.draft(character, seconds=2 * 86400))
        self.assertEqual(character, self.store.current()["character"])
        self.assertEqual(1, accepted["state"]["turn"])
        self.assertEqual(2 * 86400, accepted["state"]["time_seconds"])

    def test_condition_can_be_added_to_legacy_state_but_not_removed_later(self):
        self.store.initialize(setup_payload())
        character = deepcopy(self.store.current()["character"])
        character["condition"] = explicit_condition(9, tags=["Rested", "Adequately nourished"],
            basis="The test character's condition is now explicitly recorded")
        self.store.commit_turn(self.draft(character))
        del character["condition"]
        self.reject_without_mutation(self.store.commit_turn, self.draft(character))
        self.reject_without_mutation(self.store.correct, self.correct_character(character))

    def test_correction_repairs_rating_without_time_or_capability_changes(self):
        self.initialize(state=capability_state())
        before = self.store.current()
        character = deepcopy(before["character"])
        character["condition"] = explicit_condition(9, tags=["Rested", "Adequately nourished"],
            basis="A documented clerical error assigned the wrong test rating")
        corrected = self.store.correct(self.correct_character(character))
        after = self.store.current()
        self.assertEqual(character["condition"], after["character"]["condition"])
        self.assertEqual(before["character"]["skills"], after["character"]["skills"])
        self.assertEqual(before["character"]["capabilities"], after["character"]["capabilities"])
        self.assertEqual((before["turn"], before["time_seconds"]), (after["turn"], after["time_seconds"]))
        self.assertEqual("correction", corrected["kind"])

    def test_zero_requires_death_and_death_requires_zero_when_condition_recorded(self):
        living_zero = starting_state()
        living_zero["character"]["condition"] = explicit_condition(0, tags=["Test fatal injury"])
        with self.assertRaises(CampaignError):
            self.store.initialize(setup_payload(living_zero))
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["condition"] = explicit_condition(0, tags=["Test fatal injury"], basis="The invented test injury is fatal")
        self.reject_without_mutation(self.store.commit_turn, self.draft(character))
        death_changes = {"alive": False, "death": {"cause": "Test fatal injury", "time_seconds": 60}}
        death_evidence = {"alive": "Fatal test result", "death": "Death at the interval endpoint"}
        unsupported = bind_head(self.store, turn_payload(seconds=60, changes=death_changes, evidence=death_evidence))
        self.reject_without_mutation(self.store.commit_turn, unsupported)
        death_changes["character"] = character
        death_evidence["character"] = "Condition zero records the same fatal result"
        self.store.commit_turn(bind_head(self.store, turn_payload(seconds=60, changes=death_changes, evidence=death_evidence)))
        self.assertFalse(self.store.current()["alive"])
        self.assertEqual(0, self.store.current()["character"]["condition"]["rating"])

    def test_correction_cannot_raise_or_remove_condition_after_death(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["condition"] = explicit_condition(0, tags=["Test fatal injury"], basis="Fatal test result")
        self.store.commit_turn(bind_head(self.store, turn_payload(seconds=60,
            changes={"character": character, "alive": False, "death": {"cause": "Test fatal injury", "time_seconds": 60}},
            evidence={"character": "Fatal test result", "alive": "Fatal test result", "death": "Fatal test result"})))
        revived = deepcopy(character)
        revived["condition"]["rating"] = 1
        self.reject_without_mutation(self.store.correct, self.correct_character(revived))
        omitted = deepcopy(character)
        del omitted["condition"]
        self.reject_without_mutation(self.store.correct, self.correct_character(omitted))
        self.reject_without_mutation(self.store.commit_turn, self.draft())

    def test_legacy_hashes_and_restore_have_no_injected_condition(self):
        state = starting_state()
        setup = self.store.initialize(setup_payload(state))
        accepted = self.store.commit_turn(bind_head(self.store, turn_payload()))
        self.assertEqual("42571dfca2ac917d1f9ecc4f5e8fe13e2c730e8b09cced762ec0f2ec86fe3068", setup["hash"])
        self.assertEqual("090529a498c0d238b69a8bf87edb50e7efa01757fec36ab389c3242ae28d1017", accepted["hash"])
        self.assertNotIn("condition", self.store.current()["character"])
        save = self.root / "legacy-save.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "legacy-restored")
        restored.restore_save(save)
        self.assertEqual(self.store.validate(), restored.validate())
        self.assertNotIn("condition", restored.current()["character"])

    def test_condition_survives_export_restore_and_is_readable_with_its_basis(self):
        condition = explicit_condition(6, tags=["Test ankle restriction", "Short of sleep"],
            basis="Combined documented effects restrict the test character's current function")
        self.initialize(condition)
        self.store.commit_turn(self.draft())
        save = self.root / "condition-save.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "condition-restored")
        restored.restore_save(save)
        self.assertEqual(self.store.validate(), restored.validate())
        self.assertEqual(condition, restored.current()["character"]["condition"])
        sheet = character_sheet(restored.current())
        self.assertIn("Condition", sheet)
        self.assertIn("6/9", sheet)
        self.assertIn(condition["basis"], sheet)
        for tag in condition["tags"]:
            self.assertIn(tag, sheet)
        output = self.root / "play"
        render_campaign(restored, output)
        readable_sheet = (output / "character-sheet.md").read_text(encoding="utf-8")
        self.assertIn(condition["basis"], readable_sheet)
        story = (output / "story.md").read_text(encoding="utf-8")
        self.assertIn("Condition", story)
        self.assertIn("| Condition | 6 |", story)
        self.assertNotIn(condition["basis"], story)
        for tag in condition["tags"]:
            self.assertNotIn(tag, story)
        resume = (output / "resume.md").read_text(encoding="utf-8")
        self.assertIn("6/9", resume)
        self.assertIn(condition["basis"], resume)


if __name__ == "__main__":
    unittest.main()
