"""Player sheets keep current abilities legible without turning into an audit."""

import copy
import json
from pathlib import Path
import unittest

from iron_engine.character_view import render_character_sheet


class CharacterViewTests(unittest.TestCase):
    def test_current_sheet_reflects_new_ratings_and_current_development_cost(self):
        path = Path(__file__).resolve().parents[1] / "stories/story-001/setup.json"
        state = copy.deepcopy(json.loads(path.read_text())["state"])
        state["character"]["skills"]["Mediation"] = 7
        state["character"]["capabilities"]["Mediation"]["development"] = 2
        state["character"]["background"] = "A mediator who learned through household disputes."
        state["resources"] = {"silver stags": 0}
        before = copy.deepcopy(state)
        sheet = render_character_sheet(state)
        self.assertIn("| Mediation | 7 | 2 / 20 |", sheet)
        self.assertIn(state["character"]["background"], sheet)
        self.assertIn("silver stags: 0", sheet)
        self.assertIn("| Condition | 8 — Hale |", sheet)
        self.assertNotIn("Anchors:", sheet)
        self.assertNotIn("evidence turns:", sheet)
        self.assertNotIn("Condition tags:", sheet)
        self.assertEqual(before, state)


if __name__ == "__main__":
    unittest.main()
