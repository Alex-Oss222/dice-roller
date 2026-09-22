"""Capability records retain their evidence and cannot manufacture advancement.

Every character, training period, and place below is an invented test fixture.
"""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from iron_engine.engine import CampaignError, CampaignStore
from tests.fixtures import bind_head, setup_payload, starting_state, turn_payload


SYSTEM = "blood_and_gold_0_9"


def established(domain="learning", development=0, kind="subskill", parent=None):
    record = {
        "kind": kind,
        "basis": "Explicit invented training background for this test only",
        "evidence_turns": [0],
        "development": development,
        "aptitude": {"level": "ordinary", "applied_to": "development"},
        "experience": "Invented relevant experience, not a universal time requirement",
        "training": [],
    }
    record["parent" if kind == "specialty" else "domain"] = parent if kind == "specialty" else domain
    return record


def capability_state(rating=3, development=11):
    state = starting_state()
    state["campaign"]["capability_system"] = SYSTEM
    state["campaign"]["permitted_books"] = ["Invented test source; no published plot facts"]
    state["character"]["skills"] = {
        "learning": rating, "accounts": rating, "reading": rating, "arithmetic": rating,
    }
    state["character"]["capabilities"] = {
        "learning": {
            "kind": "domain",
            "basis": "Three established test abilities support this summary",
            "evidence_turns": [0],
            "anchors": {"accounts": 40, "reading": 30, "arithmetic": 30},
        },
        "accounts": established(development=development),
        "reading": established(),
        "arithmetic": established(),
    }
    return state


def derived(exposure="plausible"):
    return {
        "kind": "derived", "domain": "learning",
        "basis": "Limited transfer of established test abilities, not demonstrated mastery",
        "evidence_turns": [0],
        "derivation": {
            "related": {"accounts": 30, "reading": 30},
            "exposure": exposure,
            "basis": "Only the stated test exposure is assumed",
        },
    }


def training(period_id="practice-1", start=0, end=3600, development=2, turn=1):
    return {
        "id": period_id, "start_seconds": start, "end_seconds": end,
        "development": development,
        "activity": "Invented deliberate test exercise",
        "basis": "Explicit test award, not a claim that this duration normally earns points",
        "evidence_turns": [turn],
    }


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")
        self.rejected_cases = 0

    def initialize(self, state=None):
        return self.store.initialize(setup_payload(state or capability_state()))

    def draft(self, character, seconds=3600, **overrides):
        state = self.store.current()
        payload = turn_payload(
            turn=state["turn"], seconds=seconds,
            changes={"character": character},
            evidence={"character": "Documented test training and capability assessment"},
            **overrides,
        )
        return bind_head(self.store, payload)

    def reject_state(self, state):
        self.rejected_cases += 1
        store = CampaignStore(self.root / f"rejected-{self.rejected_cases}")
        with self.assertRaises(CampaignError):
            store.initialize(setup_payload(state))
        self.assertEqual([], store.validate())

    def reject_turn(self, character, seconds=3600):
        before = self.store.validate()
        with self.assertRaises(CampaignError):
            self.store.commit_turn(self.draft(character, seconds))
        self.assertEqual(before, self.store.validate())

    def test_legacy_hashes_and_replay_remain_byte_compatible(self):
        state = starting_state()
        first = self.store.initialize(setup_payload(state))
        second = self.store.commit_turn(bind_head(self.store, turn_payload()))
        self.assertEqual("42571dfca2ac917d1f9ecc4f5e8fe13e2c730e8b09cced762ec0f2ec86fe3068", first["hash"])
        self.assertEqual("090529a498c0d238b69a8bf87edb50e7efa01757fec36ab389c3242ae28d1017", second["hash"])
        self.assertEqual(state, first["state"])
        self.assertNotIn("capability_system", self.store.current()["campaign"])
        self.assertNotIn("capabilities", self.store.current()["character"])
        path = self.root / "legacy.json"
        self.store.export_save(path)
        restored = CampaignStore(self.root / "legacy-restored")
        restored.restore_save(path)
        self.assertEqual([first, second], restored.validate())

    def test_full_scale_requires_explicit_adjudicated_system(self):
        for rating in (0, 9):
            with self.subTest(accepted_rating=rating):
                store = CampaignStore(self.root / f"valid-{rating}")
                state = capability_state(rating=rating, development=0)
                store.initialize(setup_payload(state))
                self.assertEqual(state, store.current())
        legacy = starting_state()
        legacy["character"]["skills"]["accounts"] = 6
        self.reject_state(legacy)
        wrong_mode = capability_state()
        wrong_mode["campaign"]["resolution_mode"] = "real_dice"
        self.reject_state(wrong_mode)
        wrong_system = capability_state()
        wrong_system["campaign"]["capability_system"] = "unrecognized_scale"
        self.reject_state(wrong_system)
        missing_opt_in = capability_state()
        del missing_opt_in["campaign"]["capability_system"]
        self.reject_state(missing_opt_in)
        missing_books = capability_state()
        del missing_books["campaign"]["permitted_books"]
        self.reject_state(missing_books)

    def test_rating_and_metadata_keys_cannot_diverge(self):
        for mutation in ("missing_record", "extra_record", "missing_map", "rating_ten"):
            with self.subTest(mutation=mutation):
                state = capability_state()
                if mutation == "missing_record":
                    del state["character"]["capabilities"]["reading"]
                elif mutation == "extra_record":
                    state["character"]["capabilities"]["unrated"] = established()
                elif mutation == "missing_map":
                    del state["character"]["capabilities"]
                else:
                    state["character"]["skills"]["reading"] = 10
                self.reject_state(state)

    def test_domain_rounds_half_up_and_rejects_invented_summary(self):
        state = capability_state()
        state["character"]["skills"].update(learning=4, accounts=4, reading=4, arithmetic=2)
        state["character"]["capabilities"]["learning"]["anchors"] = {
            "accounts": 40, "reading": 35, "arithmetic": 25,
        }
        self.initialize(state)
        self.assertEqual(4, self.store.current()["character"]["skills"]["learning"])
        state["character"]["skills"]["learning"] = 3
        self.reject_state(state)

    def test_domain_anchors_enforce_count_weights_and_established_membership(self):
        for mutation in ("sum_99", "weight_41", "six_anchors", "wrong_domain", "derived", "specialty"):
            with self.subTest(mutation=mutation):
                state = capability_state()
                records = state["character"]["capabilities"]
                anchors = records["learning"]["anchors"]
                if mutation == "sum_99":
                    anchors["arithmetic"] = 29
                elif mutation == "weight_41":
                    anchors.update(accounts=41, arithmetic=29)
                elif mutation == "six_anchors":
                    for name in ("extra_a", "extra_b", "extra_c"):
                        records[name] = established()
                        state["character"]["skills"][name] = 3
                    records["learning"]["anchors"] = {
                        "accounts": 20, "reading": 20, "arithmetic": 20,
                        "extra_a": 20, "extra_b": 10, "extra_c": 10,
                    }
                elif mutation == "wrong_domain":
                    records["accounts"]["domain"] = "unrecorded_domain"
                elif mutation == "derived":
                    records["accounts"] = derived("expected")
                    records["accounts"]["derivation"]["related"] = {"reading": 30, "arithmetic": 30}
                else:
                    records["accounts"] = established(kind="specialty", parent="reading")
                self.reject_state(state)

    def test_derived_ceiling_allows_cautious_lower_rating(self):
        # 40% domain 3 + 60% related 3 - plausible exposure 1 gives a ceiling of 2.
        for rating in (0, 2):
            with self.subTest(rating=rating):
                state = capability_state()
                state["character"]["skills"]["bookkeeping"] = rating
                state["character"]["capabilities"]["bookkeeping"] = derived()
                store = CampaignStore(self.root / f"derived-{rating}")
                store.initialize(setup_payload(state))
                self.assertEqual(rating, store.current()["character"]["skills"]["bookkeeping"])
        state["character"]["skills"]["bookkeeping"] = 3
        self.reject_state(state)

    def test_derived_records_cannot_chain_or_accumulate_development(self):
        for mutation in ("chain", "unknown_related", "wrong_weight", "development"):
            with self.subTest(mutation=mutation):
                state = capability_state()
                skills = state["character"]["skills"]
                records = state["character"]["capabilities"]
                skills.update(bookkeeping=2, copying=2)
                records.update(bookkeeping=derived(), copying=derived())
                if mutation == "chain":
                    records["copying"]["derivation"]["related"] = {"bookkeeping": 60}
                elif mutation == "unknown_related":
                    records["copying"]["derivation"]["related"] = {"unrecorded": 60}
                elif mutation == "wrong_weight":
                    records["copying"]["derivation"]["related"] = {"accounts": 59}
                else:
                    records["copying"]["development"] = 1
                self.reject_state(state)

    def test_specialty_requires_an_established_subskill_parent(self):
        state = capability_state()
        state["character"]["skills"]["fine_accounts"] = 2
        state["character"]["capabilities"]["fine_accounts"] = established(kind="specialty", parent="accounts")
        self.initialize(state)
        for parent in ("learning", "fine_accounts", "missing"):
            with self.subTest(parent=parent):
                bad = deepcopy(state)
                bad["character"]["capabilities"]["fine_accounts"]["parent"] = parent
                self.reject_state(bad)

    def test_advancement_consumes_threshold_and_preserves_carryover(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["skills"]["accounts"] = 4
        character["capabilities"]["accounts"]["training"] = [training()]
        character["capabilities"]["accounts"]["development"] = 1
        draft = self.draft(character)
        accepted = self.store.commit_turn(draft)
        self.assertEqual(character, self.store.current()["character"])
        self.assertEqual(accepted, self.store.commit_turn(draft))
        self.assertEqual(1, self.store.current()["turn"])
        self.assertEqual(1, self.store.current()["character"]["capabilities"]["accounts"]["development"])

    def test_development_must_reconcile_with_awards_and_consumed_thresholds(self):
        self.initialize()
        for case in ("free_development", "free_rating", "unconsumed_threshold", "dropped_carry"):
            with self.subTest(case=case):
                character = deepcopy(self.store.current()["character"])
                account = character["capabilities"]["accounts"]
                if case == "free_development":
                    account["development"] = 12
                elif case == "free_rating":
                    character["skills"]["accounts"] = 4
                else:
                    character["skills"]["accounts"] = 4
                    account["training"] = [training()]
                    account["development"] = 13 if case == "unconsumed_threshold" else 0
                self.reject_turn(character)

    def test_aptitude_discount_is_applied_once_to_selected_requirement(self):
        for applied_to, remaining in (("development", 1), ("experience", 0)):
            with self.subTest(applied_to=applied_to):
                state = capability_state(rating=5, development=14)
                state["character"]["capabilities"]["accounts"]["aptitude"] = {
                    "level": "strong", "applied_to": applied_to,
                }
                self.store = CampaignStore(self.root / f"aptitude-{applied_to}")
                self.initialize(state)
                character = deepcopy(self.store.current()["character"])
                character["skills"]["accounts"] = 6
                character["capabilities"]["accounts"]["training"] = [training()]
                character["capabilities"]["accounts"]["development"] = remaining
                self.store.commit_turn(self.draft(character))
                self.assertEqual(remaining, self.store.current()["character"]["capabilities"]["accounts"]["development"])

    def test_terminal_rank_requires_full_threshold_and_retires_only_surplus(self):
        self.initialize(capability_state(rating=8, development=29))
        character = deepcopy(self.store.current()["character"])
        character["skills"]["accounts"] = 9
        character["capabilities"]["accounts"]["development"] = 0
        self.reject_turn(character)  # 29 points cannot pay the 30-point threshold.
        character["capabilities"]["accounts"]["training"] = [training(development=2)]
        self.store.commit_turn(self.draft(character))
        account = self.store.current()["character"]["capabilities"]["accounts"]
        self.assertEqual(0, account["development"])
        self.assertEqual([training(development=2)], account["training"])
        self.assertEqual(9, self.store.current()["character"]["skills"]["accounts"])

    def test_training_periods_cannot_overlap_repeat_ids_or_reach_future(self):
        self.initialize()
        for case in ("overlap", "duplicate_id", "future", "reversed"):
            with self.subTest(case=case):
                character = deepcopy(self.store.current()["character"])
                periods = [training(end=1800, development=1)]
                if case == "overlap":
                    periods.append(training("practice-2", start=1799, development=1))
                elif case == "duplicate_id":
                    periods.append(training(start=1800, development=1))
                elif case == "future":
                    periods = [training(end=3601, development=1)]
                else:
                    periods = [training(start=100, end=99, development=1)]
                character["capabilities"]["accounts"].update(
                    training=periods, development=11 + sum(period["development"] for period in periods),
                )
                self.reject_turn(character)

    def test_recorded_training_cannot_be_removed_rewritten_or_recredited(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["capabilities"]["accounts"].update(training=[training()], development=13)
        self.store.commit_turn(self.draft(character))
        for case in ("remove", "rewrite", "recredit"):
            with self.subTest(case=case):
                changed = deepcopy(character)
                account = changed["capabilities"]["accounts"]
                if case == "remove":
                    account.update(training=[], development=11)
                elif case == "rewrite":
                    account["training"][0]["basis"] = "Changed prior justification"
                else:
                    account["development"] = 15
                self.reject_turn(changed)

    def test_setup_does_not_backfill_live_training_or_future_turn_evidence(self):
        state = capability_state()
        state["time_seconds"] = 3600
        state["character"]["capabilities"]["accounts"]["training"] = [training(turn=0)]
        self.reject_state(state)
        state = capability_state()
        state["character"]["capabilities"]["accounts"]["evidence_turns"] = [1]
        self.reject_state(state)

    def test_new_trainable_cannot_appear_with_a_free_positive_rating(self):
        self.initialize()
        character = deepcopy(self.store.current()["character"])
        character["skills"]["copying"] = 1
        character["capabilities"]["copying"] = established()
        self.reject_turn(character)
        character["skills"]["copying"] = 0
        character["capabilities"]["copying"].update(training=[training(development=1)], development=1)
        self.store.commit_turn(self.draft(character))
        self.assertEqual(0, self.store.current()["character"]["skills"]["copying"])

    def test_derived_reclassification_cannot_create_rating_or_development(self):
        state = capability_state()
        state["character"]["skills"]["copying"] = 2
        state["character"]["capabilities"]["copying"] = derived()
        self.initialize(state)
        for rating, development in ((3, 0), (2, 1)):
            with self.subTest(rating=rating, development=development):
                character = deepcopy(self.store.current()["character"])
                character["skills"]["copying"] = rating
                character["capabilities"]["copying"] = established(development=development)
                self.reject_turn(character)
        character = deepcopy(self.store.current()["character"])
        character["capabilities"]["copying"] = established()
        self.store.commit_turn(self.draft(character))
        self.assertEqual(2, self.store.current()["character"]["skills"]["copying"])

    def test_established_reclassification_preserves_development_and_rating(self):
        state = capability_state()
        state["character"]["skills"]["copying"] = 2
        state["character"]["capabilities"]["copying"] = established(development=7)
        self.initialize(state)
        for rating, development in ((3, 7), (2, 0)):
            with self.subTest(rating=rating, development=development):
                character = deepcopy(self.store.current()["character"])
                character["skills"]["copying"] = rating
                character["capabilities"]["copying"] = established(kind="specialty", parent="reading", development=development)
                self.reject_turn(character)
        character = deepcopy(self.store.current()["character"])
        character["capabilities"]["copying"] = established(kind="specialty", parent="reading", development=7)
        self.store.commit_turn(self.draft(character))
        self.assertEqual(7, self.store.current()["character"]["capabilities"]["copying"]["development"])

    def test_complete_capabilities_and_pending_choice_survive_save_restore(self):
        state = capability_state()
        state["character"]["profile"] = {
            "identity": {"culture": "Invented test culture"},
            "background_details": {"education": "Test instruction documented at setup"},
            "natural_attributes": {"endurance": "No unusual capacity established"},
            "languages": [{
                "language": "Invented test language", "spoken": "Familiar",
                "read": "Trained", "written": "Familiar", "capability": "reading",
                "basis": "Explicit test education, not inherited rank",
            }],
        }
        self.initialize(state)
        character = deepcopy(self.store.current()["character"])
        character["capabilities"]["accounts"].update(training=[training()], development=13)
        self.store.commit_turn(self.draft(character))
        note = "The player must choose whether to resume the interrupted test training."
        self.store.checkpoint(bind_head(self.store, {"request_id": "pending-choice", "resume_note": note}))
        saved = self.root / "capabilities-save.json"
        self.store.export_save(saved)
        restored = CampaignStore(self.root / "restored")
        restored.restore_save(saved)
        self.assertEqual(self.store.validate(), restored.validate())
        self.assertEqual(character, restored.current()["character"])
        self.assertEqual(SYSTEM, restored.current()["campaign"]["capability_system"])
        self.assertEqual(note, restored.current()["resume_note"])


if __name__ == "__main__":
    unittest.main()
