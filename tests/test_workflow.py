"""Compact advances preserve explicit authorization, evidence, and world records.

All people, claims, outcomes, and assets are invented test fixtures.
"""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from iron_engine.engine import CampaignError, CampaignStore
from tests.fixtures import bind_head, correction, setup_payload, starting_state, task, turn_payload


CATEGORIES = ("character", "resources", "relationships", "obligations", "tasks", "knowledge", "assumptions", "plans", "world")


def world_record(kind="person", title="Invented test clerk", due=None, **overrides):
    record = {
        "kind": kind, "title": title, "status": "active", "summary": "Explicit test facts, not published canon",
        "participants": [], "links": [], "known_by": ["pc"], "due_seconds": due,
        "details": {"accounts": "3", "accounts basis": "Established test bookkeeping experience"}, "evidence_turns": [0],
    }
    record.update(deepcopy(overrides))
    return record


def workflow_state(records=None):
    state = starting_state()
    state["campaign"]["workflow_version"] = "1"
    state["world"] = {"records": deepcopy(records or {})}
    return state


def blood_gold_workflow_state():
    state = workflow_state()
    state["campaign"]["capability_system"] = "blood_and_gold_0_9"
    state["campaign"]["permitted_books"] = ["Invented test source with no published plot facts"]
    state["character"]["skills"] = {
        "learning": 3, "accounts": 3, "reading": 3, "arithmetic": 3,
    }

    def trainable():
        return {
            "kind": "subskill",
            "basis": "Invented specific test ability",
            "evidence_turns": [0],
            "development": 0,
            "aptitude": {"level": "ordinary", "applied_to": "development"},
            "experience": "Invented test experience",
            "training": [],
            "domain": "learning",
        }

    state["character"]["capabilities"] = {
        "learning": {
            "kind": "domain",
            "basis": "Invented weighted summary for this test",
            "evidence_turns": [0],
            "anchors": {"accounts": 40, "reading": 30, "arithmetic": 30},
        },
        "accounts": trainable(),
        "reading": trainable(),
        "arithmetic": trainable(),
    }
    return state


def advance_payload(store, seconds=3600, operations=None, changed=(), **overrides):
    state = store.current()
    payload = turn_payload(state["turn"], seconds=seconds)
    for key in ("resources_delta", "changes", "evidence", "checks"):
        del payload[key]
    payload.update({
        "operations": deepcopy(operations or []),
        "authorization": {"objective": payload["objective"], "max_elapsed_seconds": seconds,
                          "stop_condition": "Stop before any unapproved consequential choice"},
        "adjudication": {"mode": "routine", "actor": "pc", "capability": None,
                         "supporting_capabilities": [],
                         "preparation": "The necessary test ledger is present", "opposition": "None established",
                         "risk": "No material uncertainty in this routine test action",
                         "basis": "Routine test work follows the established record", "task_band": "routine"},
        "coverage": {category: {"status": "changed" if category in changed else "unchanged",
                                "basis": f"Explicit review of {category} for this test interval"}
                     for category in CATEGORIES},
        "next_decision": None, "milestones": [],
    })
    payload.update(deepcopy(overrides))
    return bind_head(store, payload)


def set_op(path, expected, value):
    return {"op": "set", "path": path, "expected": deepcopy(expected), "value": deepcopy(value),
            "basis": "Documented test facts support this particular change"}


def resource_op(expected=8, delta=-2):
    return {"op": "resource_adjust", "unit": "silver_stags", "expected": expected, "delta": delta,
            "basis": "The test clerk pays the recorded charge"}


def world_op(record_id, expected, value):
    return {"op": "world_upsert", "id": record_id, "expected": deepcopy(expected), "value": deepcopy(value),
            "basis": "The accepted test event establishes this world record"}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CampaignStore(self.root / "campaign")

    def initialize(self, state=None, **setup_fields):
        payload = setup_payload(state or workflow_state())
        payload.update(setup_fields)
        return self.store.initialize(payload)

    def reject(self, payload, method=None):
        before = self.store.validate()
        with self.assertRaises(CampaignError):
            (method or self.store.advance)(payload)
        self.assertEqual(before, self.store.validate())

    def test_next_decision_is_saved_for_resume_and_validated(self):
        self.initialize()
        first = self.store.advance(advance_payload(
            self.store, next_decision="Choose whether to continue the invented test work."))
        self.assertEqual("Choose whether to continue the invented test work.", first["state"]["resume_note"])
        self.reject(advance_payload(self.store, next_decision=" "))
        self.reject(advance_payload(self.store, next_decision=True))
        second = self.store.advance(advance_payload(self.store, next_decision=None))
        self.assertIsNone(second["state"]["resume_note"])

    def test_compact_advance_replays_and_exact_retry_does_not_double_charge(self):
        self.initialize()
        payload = advance_payload(self.store, operations=[resource_op()], changed=("resources",))
        accepted = self.store.advance(payload)
        self.assertEqual("advance", accepted["kind"])
        self.assertEqual(payload, accepted["input"])
        self.assertEqual(6, accepted["state"]["resources"]["silver_stags"])
        self.assertNotIn("changes", accepted["input"])
        self.store.advance(advance_payload(self.store))
        self.assertEqual(accepted, self.store.advance(deepcopy(payload)))
        self.assertEqual(2, self.store.current()["turn"])
        self.assertEqual(6, self.store.current()["resources"]["silver_stags"])
        save = self.root / "compact.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "restored")
        restored.restore_save(save)
        self.assertEqual(self.store.validate(), restored.validate())
        altered_retry = deepcopy(payload)
        altered_retry["outcome"] = "Different outcome under the same request ID"
        self.reject(altered_retry)

    def test_same_turn_correction_invalidates_old_compact_draft(self):
        self.initialize()
        payload = advance_payload(self.store, operations=[resource_op()], changed=("resources",))
        self.store.correct(bind_head(self.store, correction()))
        self.assertEqual(0, self.store.current()["turn"])
        self.reject(payload)
        self.assertEqual(9, self.store.current()["resources"]["silver_stags"])

    def test_operations_preserve_unmentioned_character_fields_and_compare_expected_values(self):
        self.initialize()
        original = self.store.current()["character"]
        self.reject(advance_payload(self.store, operations=[set_op(["character", "aim"], "Wrong old aim", "A new test aim")],
                                    changed=("character",)))
        self.store.advance(advance_payload(self.store,
            operations=[set_op(["character", "aim"], original["aim"], "A new test aim")], changed=("character",)))
        expected = deepcopy(original)
        expected["aim"] = "A new test aim"
        self.assertEqual(expected, self.store.current()["character"])
        self.reject(advance_payload(self.store, operations=[resource_op(expected=7)], changed=("resources",)))

    def test_boolean_cannot_hide_as_an_unchanged_integer_during_compact_expansion(self):
        state = workflow_state()
        state["character"]["skills"]["accounts"] = 1
        self.initialize(state)
        operation = set_op(["character", "skills", "accounts"], 1, True)
        for changed in ((), ("character",)):
            with self.subTest(coverage=changed):
                self.reject(advance_payload(self.store, operations=[operation], changed=changed))
        self.assertIs(type(self.store.current()["character"]["skills"]["accounts"]), int)

    def test_establishing_zero_records_a_known_balance_and_supports_adjustment_and_replay(self):
        state = workflow_state()
        state["resources"] = {}
        self.initialize(state)
        self.reject(advance_payload(self.store, operations=[resource_op(expected=0, delta=0)]))
        self.assertEqual({}, self.store.current()["resources"])
        establish = {"op": "resource_establish", "unit": "silver_stags", "expected": None, "value": 0,
                     "basis": "The test account is inspected and confirms a zero balance"}
        payload = advance_payload(self.store, operations=[establish], changed=("resources",))
        accepted = self.store.advance(payload)
        self.assertEqual({"silver_stags": 0}, self.store.current()["resources"])
        self.assertEqual(accepted, self.store.advance(deepcopy(payload)))
        self.store.advance(advance_payload(self.store, operations=[resource_op(expected=0, delta=3)], changed=("resources",)))
        same_advance = [
            {"op": "resource_establish", "unit": "test_coppers", "expected": None, "value": 0,
             "basis": "The test account establishes a previously unrecorded unit"},
            {"op": "resource_adjust", "unit": "test_coppers", "expected": 0, "delta": 2,
             "basis": "Two test coppers are then received during the same interval"},
        ]
        self.store.advance(advance_payload(self.store, operations=same_advance, changed=("resources",)))
        self.assertEqual({"silver_stags": 3, "test_coppers": 2}, self.store.current()["resources"])
        save = self.root / "established-resources.json"
        self.store.export_save(save)
        restored = CampaignStore(self.root / "restored-resources")
        restored.restore_save(save)
        self.assertEqual(self.store.validate(), restored.validate())

    def test_resource_establishment_rejects_negative_boolean_and_nonnull_expected_balances(self):
        state = workflow_state()
        state["resources"] = {}
        self.initialize(state)
        base = {"op": "resource_establish", "unit": "silver_stags", "expected": None, "value": 2,
                "basis": "An explicit test count establishes the amount"}
        for overrides in ({"value": -1}, {"value": True}, {"value": 1.5}, {"expected": 0}, {"basis": " "}):
            with self.subTest(overrides=overrides):
                self.reject(advance_payload(self.store, operations=[{**base, **overrides}], changed=("resources",)))
        self.assertEqual({}, self.store.current()["resources"])

    def test_establishment_cannot_rewrite_an_existing_resource_unit(self):
        self.initialize()
        for value in (0, 8, 9):
            operation = {"op": "resource_establish", "unit": "silver_stags", "expected": None, "value": value,
                         "basis": "Attempt to establish a unit that already has a known balance"}
            with self.subTest(value=value):
                self.reject(advance_payload(self.store, operations=[operation], changed=("resources",)))
        self.assertEqual(8, self.store.current()["resources"]["silver_stags"])

    def test_protected_roots_metadata_and_unknown_operation_fields_cannot_be_set(self):
        self.initialize()
        state = self.store.current()
        self.reject(bind_head(self.store, turn_payload()), self.store.commit_turn)
        for path, expected, value in [
            (["campaign", "workflow_version"], "1", "2"), (["campaign", "id"], state["campaign"]["id"], "another-story"),
            (["time_seconds"], 0, 900000), (["turn"], 0, 99), (["alive"], True, False),
            (["resources"], state["resources"], {}), (["tasks"], [], []), (["world"], state["world"], {"records": {}}),
            (["world", "records", "test-clerk"], None, world_record()), (["resume_note"], None, "An unsolicited note"),
            (["research"], [], []), (["character", "missing_parent", "name"], None, "Cannot create missing parent"),
        ]:
            with self.subTest(path=path):
                self.reject(advance_payload(self.store, operations=[set_op(path, expected, value)]))
        unknown = resource_op()
        unknown["secret_override"] = True
        self.reject(advance_payload(self.store, operations=[unknown], changed=("resources",)))

    def test_list_membership_is_explicit_and_cannot_duplicate_or_remove_missing_fact(self):
        self.initialize()
        add = {"op": "list_add", "path": ["knowledge"], "expected": False,
               "value": "The test clerk has acknowledged receipt", "basis": "The PC hears the acknowledgment"}
        self.store.advance(advance_payload(self.store, operations=[add], changed=("knowledge",)))
        self.reject(advance_payload(self.store, operations=[add], changed=("knowledge",)))
        wrong_remove = {**add, "op": "list_remove", "expected": True, "value": "A fact never acquired"}
        self.reject(advance_payload(self.store, operations=[wrong_remove], changed=("knowledge",)))
        remove = {**add, "op": "list_remove", "expected": True, "basis": "Correct the mistaken in-world interpretation"}
        self.store.advance(advance_payload(self.store, operations=[remove], changed=("knowledge",)))
        self.assertEqual([], self.store.current()["knowledge"])

    def test_coverage_must_describe_actual_changes_and_cover_all_categories(self):
        self.initialize()
        self.reject(advance_payload(self.store, operations=[resource_op()]))
        self.reject(advance_payload(self.store, changed=("character",)))
        missing = advance_payload(self.store)
        del missing["coverage"]["world"]
        self.reject(missing)
        empty_basis = advance_payload(self.store)
        empty_basis["coverage"]["knowledge"]["basis"] = " "
        self.reject(empty_basis)
        self.store.advance(advance_payload(self.store, operations=[resource_op()], changed=("resources",)))

    def test_time_cannot_exceed_player_authorization_or_mismatch_its_objective(self):
        self.initialize()
        for field, value in [("max_elapsed_seconds", 3599), ("max_elapsed_seconds", True),
                             ("objective", "An unrelated objective"), ("stop_condition", "")]:
            payload = advance_payload(self.store)
            payload["authorization"][field] = value
            with self.subTest(field=field, value=value):
                self.reject(payload)
        partial = advance_payload(self.store, seconds=7200)
        partial["authorization"]["max_elapsed_seconds"] = 7 * 86400
        self.store.advance(partial)
        self.assertEqual(7200, self.store.current()["time_seconds"])

    def test_long_interval_requires_ordered_milestones_covering_the_endpoint(self):
        self.initialize()
        month = 30 * 86400
        mid = {"elapsed_seconds": month // 2, "basis": "The middle test interval is assessed", "evidence_turns": [1]}
        end = {"elapsed_seconds": month, "basis": "The ending test interval is assessed", "evidence_turns": [1]}
        for milestones in ([], [end], [end, mid], [mid, {**end, "elapsed_seconds": month - 1}],
                           [mid, {**end, "elapsed_seconds": month + 1}], [mid, {**end, "evidence_turns": [0]}]):
            with self.subTest(milestones=milestones):
                self.reject(advance_payload(self.store, seconds=month, milestones=milestones))
        self.store.advance(advance_payload(self.store, seconds=month, milestones=[mid, end]))
        self.assertEqual(month, self.store.current()["time_seconds"])
        self.assertEqual(1, self.store.current()["turn"])

    def test_world_links_participants_and_evidence_must_resolve(self):
        records = {"test-clerk": world_record(), "test-thread": world_record("thread", participants=["pc", "test-clerk"],
                    links=["test-clerk"], known_by=["public", "test-clerk"])}
        self.initialize(workflow_state(records))
        for invalid in [world_record("thread", links=["missing-record"]),
                        world_record("thread", participants=["test-thread"]),
                        world_record("thread", known_by=["missing-person"]),
                        world_record("thread", evidence_turns=[99])]:
            with self.subTest(record=invalid):
                self.reject(advance_payload(self.store, operations=[world_op("new-thread", None, invalid)], changed=("world",)))
        valid = world_record("fact", title="Test receipt fact", links=["test-thread"], participants=["test-clerk"],
                             evidence_turns=[1])
        self.store.advance(advance_payload(self.store, operations=[world_op("receipt-fact", None, valid)], changed=("world",)))
        self.assertEqual(valid, self.store.current()["world"]["records"]["receipt-fact"])
        self.assertEqual([], self.store.current()["knowledge"])

    def test_world_deadline_requires_explanation_and_settlement_at_exact_endpoint(self):
        record = world_record("project", due=7200, title="Invented test delivery")
        self.initialize(workflow_state({"test-delivery": record}))
        self.reject(advance_payload(self.store, seconds=7200))
        settled = {**record, "status": "completed", "summary": "The test delivery was received", "evidence_turns": [0, 1]}
        operations = [world_op("test-delivery", record, settled)]
        self.reject(advance_payload(self.store, seconds=7200, operations=operations, changed=("world",)))
        self.store.advance(advance_payload(self.store, seconds=7200, operations=operations, changed=("world",),
            processed_tasks={"world.test-delivery": "The test receipt confirms completion"}))
        self.assertEqual("completed", self.store.current()["world"]["records"]["test-delivery"]["status"])

    def test_rescheduled_world_deadline_requires_specific_reason_and_future_time(self):
        record = world_record("journey", due=7200, title="Invented test journey")
        self.initialize(workflow_state({"test-journey": record}))
        revised = {**record, "due_seconds": 10800, "summary": "Test travel is delayed", "evidence_turns": [0, 1]}
        payload = advance_payload(self.store, seconds=7200, operations=[world_op("test-journey", record, revised)],
            changed=("world",), processed_tasks={"world.test-journey": "A test delay is established"})
        self.reject(payload)
        revised["details"] = {"deadline_reason": "A documented test obstruction requires another hour"}
        self.store.advance(advance_payload(self.store, seconds=7200, operations=[world_op("test-journey", record, revised)],
            changed=("world",), processed_tasks={"world.test-journey": "A test delay is established"}))
        self.assertEqual(10800, self.store.current()["world"]["records"]["test-journey"]["due_seconds"])

    def test_world_ids_cannot_be_deleted_by_turn_or_correction(self):
        self.initialize(workflow_state({"test-clerk": world_record()}))
        erased = {"records": {}}
        self.reject(bind_head(self.store, turn_payload(changes={"world": erased}, evidence={"world": "Attempted deletion"})),
                    self.store.commit_turn)
        self.reject(bind_head(self.store, correction(changes={"world": erased}, resources_delta={},
                    evidence={"world": "Attempted deletion"})), self.store.correct)

    def test_blocked_world_record_cannot_hide_a_due_obligation(self):
        original = world_record("project", title="Blocked test delivery", due=7200)
        self.initialize(workflow_state({"test-delivery": original}))
        processed = {"world.test-delivery": "A test obstruction prevents completion"}
        for due in (7200, None, 10800):
            blocked = {**original, "status": "blocked", "due_seconds": due,
                       "summary": "The delivery is obstructed", "evidence_turns": [0, 1]}
            with self.subTest(due=due):
                self.reject(advance_payload(self.store, seconds=7200,
                    operations=[world_op("test-delivery", original, blocked)], changed=("world",), processed_tasks=processed))
        blocked["details"] = {"deadline_reason": "Reassess the documented obstruction in one hour"}
        self.store.advance(advance_payload(self.store, seconds=7200,
            operations=[world_op("test-delivery", original, blocked)], changed=("world",), processed_tasks=processed))
        self.reject(advance_payload(self.store, seconds=3600))
        completed = {**blocked, "status": "completed", "summary": "The test obstruction is removed and delivery completes",
                     "evidence_turns": [0, 1, 2]}
        self.store.advance(advance_payload(self.store, seconds=3600,
            operations=[world_op("test-delivery", blocked, completed)], changed=("world",),
            processed_tasks={"world.test-delivery": "The test clerk acknowledges receipt"}))
        self.assertEqual("completed", self.store.current()["world"]["records"]["test-delivery"]["status"])

    def test_tasks_still_require_settlement_when_using_compact_operations(self):
        state = workflow_state()
        state["tasks"] = [task(due=3600)]
        self.initialize(state)
        completed = task(due=3600, status="completed", note="The test delivery is acknowledged")
        operation = {"op": "task_upsert", "id": completed["id"], "expected": state["tasks"][0], "value": completed,
                     "basis": "The test clerk receives the delivery"}
        self.reject(advance_payload(self.store, operations=[operation], changed=("tasks",)))
        self.store.advance(advance_payload(self.store, operations=[operation], changed=("tasks",),
            processed_tasks={completed["id"]: "Receipt establishes completion"}))
        self.assertEqual([completed], self.store.current()["tasks"])

    def test_uncertain_adjudication_requires_preexisting_actor_and_capability(self):
        self.initialize(workflow_state({"test-clerk": world_record()}))
        valid = advance_payload(self.store)
        valid["adjudication"].update(mode="uncertain", capability={"source": "character.skills", "key": "accounts"},
                                     risk="The count could remain unresolved", task_band="demanding")
        missing_actor = deepcopy(valid)
        missing_actor["adjudication"]["actor"] = "unknown-person"
        self.reject(missing_actor)
        missing_skill = deepcopy(valid)
        missing_skill["adjudication"]["capability"]["key"] = "unrecorded-test-skill"
        self.reject(missing_skill)
        created_this_turn = deepcopy(missing_skill)
        created_this_turn["operations"] = [set_op(["character", "skills", "unrecorded-test-skill"], None, 2)]
        created_this_turn["coverage"]["character"]["status"] = "changed"
        self.reject(created_this_turn)
        no_basis = deepcopy(valid)
        no_basis["adjudication"]["basis"] = " "
        self.reject(no_basis)
        borrowed = deepcopy(valid)
        borrowed["adjudication"]["capability"] = {"source": "world.records.test-clerk.details", "key": "accounts"}
        self.reject(borrowed)
        npc_borrowed = deepcopy(valid)
        npc_borrowed["adjudication"]["actor"] = "test-clerk"
        self.reject(npc_borrowed)
        self.store.advance(valid)
        npc = advance_payload(self.store)
        npc["adjudication"] = deepcopy(valid["adjudication"])
        npc["adjudication"].update(actor="test-clerk",
            capability={"source": "world.records.test-clerk.details", "key": "accounts"})
        self.store.advance(npc)

    def test_supporting_capabilities_are_preexisting_actor_owned_distinct_and_role_labeled(self):
        self.initialize()
        valid = advance_payload(self.store)
        valid["adjudication"]["supporting_capabilities"] = [{
            "source": "character.skills",
            "key": "accounts",
            "role": "Tracks the established figures while the routine inspection is performed",
        }]
        self.store.advance(valid)

        cases = []
        wrong_source = advance_payload(self.store)
        wrong_source["adjudication"]["supporting_capabilities"] = [{
            "source": "world.records.test-clerk.details", "key": "accounts", "role": "Borrow an NPC ability",
        }]
        cases.append(wrong_source)

        missing = advance_payload(self.store)
        missing["adjudication"]["supporting_capabilities"] = [{
            "source": "character.skills", "key": "unrecorded-test-skill", "role": "Use a missing ability",
        }]
        cases.append(missing)

        blank_role = advance_payload(self.store)
        blank_role["adjudication"]["supporting_capabilities"] = [{
            "source": "character.skills", "key": "accounts", "role": " ",
        }]
        cases.append(blank_role)

        duplicate = advance_payload(self.store)
        duplicate["adjudication"]["supporting_capabilities"] = [
            {"source": "character.skills", "key": "accounts", "role": "First use"},
            {"source": "character.skills", "key": "accounts", "role": "Second use"},
        ]
        cases.append(duplicate)

        primary_duplicate = advance_payload(self.store)
        primary_duplicate["adjudication"].update(
            mode="uncertain",
            capability={"source": "character.skills", "key": "accounts"},
            supporting_capabilities=[{
                "source": "character.skills", "key": "accounts", "role": "Duplicate the primary ability",
            }],
            risk="The invented count could remain unresolved",
            task_band="demanding",
        )
        cases.append(primary_duplicate)

        for payload in cases:
            with self.subTest(payload=payload["adjudication"]):
                self.reject(payload)

    def test_blood_and_gold_adjudication_uses_specific_abilities_not_broad_domains(self):
        self.initialize(blood_gold_workflow_state())

        broad_primary = advance_payload(self.store)
        broad_primary["adjudication"].update(
            mode="uncertain",
            capability={"source": "character.skills", "key": "learning"},
            risk="The invented problem may remain unresolved",
            task_band="demanding",
        )
        self.reject(broad_primary)

        broad_support = advance_payload(self.store)
        broad_support["adjudication"]["supporting_capabilities"] = [{
            "source": "character.skills",
            "key": "learning",
            "role": "Attempt to substitute a broad domain for a specific action skill",
        }]
        self.reject(broad_support)

        valid = advance_payload(self.store)
        valid["adjudication"].update(
            mode="uncertain",
            capability={"source": "character.skills", "key": "accounts"},
            supporting_capabilities=[{
                "source": "character.skills",
                "key": "reading",
                "role": "Reads the specific entries needed to support the accounting task",
            }],
            risk="The invented account could remain unresolved",
            task_band="demanding",
        )
        self.store.advance(valid)

    def test_established_capability_does_not_protect_pc_from_a_supported_fatal_result(self):
        state = workflow_state()
        state["character"]["skills"]["accounts"] = 5
        self.initialize(state)
        payload = advance_payload(self.store, seconds=60,
            operations=[{"op": "death", "expected_alive": True, "cause": "Invented fatal test collapse",
                         "basis": "The test structure fails; bookkeeping expertise offers no protection"}], changed=("character",))
        payload["adjudication"].update(mode="uncertain", capability={"source": "character.skills", "key": "accounts"},
            opposition="The test structure is unstable", risk="Collapse can be fatal", task_band="extreme",
            basis="Established bookkeeping ability does not prevent this unrelated physical consequence")
        accepted = self.store.advance(payload)
        self.assertFalse(accepted["state"]["alive"])
        self.assertEqual(5, accepted["state"]["character"]["skills"]["accounts"])
        self.reject(advance_payload(self.store))

    def test_tenth_compact_turn_requires_review_in_the_same_event(self):
        self.initialize()
        for _ in range(9):
            self.store.advance(advance_payload(self.store))
        self.reject(advance_payload(self.store, review=None))
        event = self.store.advance(advance_payload(self.store))
        self.assertEqual(10, event["state"]["turn"])
        self.assertEqual(10, event["input"]["review"]["to_turn"])

    def test_setup_opening_is_accepted_prose_without_advancing_time_or_turn(self):
        opening = "The test clerk opens the account.\n\nNo delivery has arrived.  "
        event = self.initialize(opening_narrative=opening)
        self.assertEqual(opening, event["input"]["opening_narrative"])
        self.assertEqual((0, 0), (event["state"]["turn"], event["state"]["time_seconds"]))

    def test_legacy_history_remains_strict_and_byte_compatible(self):
        first = self.store.initialize(setup_payload())
        self.assertEqual("42571dfca2ac917d1f9ecc4f5e8fe13e2c730e8b09cced762ec0f2ec86fe3068", first["hash"])
        self.reject(advance_payload(self.store))
        mixed = bind_head(self.store, turn_payload())
        mixed["operations"] = []
        self.reject(mixed, self.store.commit_turn)
        second = self.store.commit_turn(bind_head(self.store, turn_payload()))
        self.assertEqual("090529a498c0d238b69a8bf87edb50e7efa01757fec36ab389c3242ae28d1017", second["hash"])
        self.assertNotIn("world", self.store.current())
        self.assertNotIn("workflow_version", self.store.current()["campaign"])

    def test_unsupported_workflow_metadata_cannot_create_an_unplayable_campaign(self):
        real_dice = workflow_state()
        real_dice["campaign"]["resolution_mode"] = "real_dice"
        unknown_version = workflow_state()
        unknown_version["campaign"]["workflow_version"] = "2"
        for number, state in enumerate((real_dice, unknown_version)):
            with self.subTest(state=state["campaign"]):
                store = CampaignStore(self.root / f"unsupported-{number}")
                with self.assertRaises(CampaignError):
                    store.initialize(setup_payload(state))
                self.assertEqual([], store.validate())


if __name__ == "__main__":
    unittest.main()


class GuardTests(unittest.TestCase):
    """Consequential results name an ability; scenes carry no mechanics; ratings rise one step at a time."""

    setUp = WorkflowTests.setUp
    initialize = WorkflowTests.initialize
    reject = WorkflowTests.reject

    def test_narrative_rejects_mechanical_markers_and_accepts_plain_prose(self):
        self.initialize()
        for text in ("He rides out (Riding 6, Tactics 5).", "Condition: 8/9 Hale.", "[Tag: Wounded]",
                     "The scene ends.\n\n### Ledger\n\n- accounts 2 -> 3", "The clerk nods.\nEvidence: he rode."):
            self.reject(advance_payload(self.store, narrative=text))
        accepted = self.store.advance(advance_payload(self.store,
            narrative="He rides out at first light; the road is dry.\n\n### The mill\n\nThe wheel is fixed by noon."))
        self.assertEqual(1, accepted["state"]["turn"])

    def test_death_lowered_condition_or_divergence_cannot_be_routine_with_no_capability(self):
        state = workflow_state()
        state["character"]["condition"] = {"rating": 8, "tags": ["Hale"], "basis": "Invented healthy test start"}
        self.initialize(state)
        death = advance_payload(self.store, seconds=60, changed=("character",),
            operations=[{"op": "death", "expected_alive": True, "cause": "Invented fatal test collapse",
                         "basis": "The test structure fails"}])
        self.reject(death)
        worse = advance_payload(self.store, changed=("character",),
            operations=[set_op(["character", "condition", "rating"], 8, 6)])
        self.reject(worse)
        divergence = world_record("divergence", title="Invented test departure",
                                  summary="The test ledger is burned instead of audited", evidence_turns=[0, 1])
        self.reject(advance_payload(self.store, changed=("world",), operations=[world_op("test-departure", None, divergence)]))
        named = advance_payload(self.store, changed=("world",), operations=[world_op("test-departure", None, divergence)])
        named["adjudication"].update(mode="uncertain", task_band="ordinary",
                                     capability={"source": "character.skills", "key": "accounts"})
        self.assertEqual(1, self.store.advance(named)["state"]["turn"])

    def test_journey_progress_keys_are_canonical(self):
        bad = world_record("journey", title="Invented test road", summary="Not yet departed",
                           details={"distance_travelled": "0 miles"})
        with self.assertRaises(CampaignError):
            self.initialize(workflow_state({"test-road": bad}))
        good = world_record("journey", title="Invented test road", summary="Not yet departed",
                            details={"distance_total": "0 miles", "route": "Test yard to test ford"})
        self.initialize(workflow_state({"test-road": good}))

    def test_rating_rises_at_most_one_step_per_event(self):
        self.initialize(blood_gold_workflow_state())
        state = self.store.current()
        record = deepcopy(state["character"]["capabilities"]["accounts"])
        period = {"id": "test-period-1", "start_seconds": 0, "end_seconds": 3600, "development": 30,
                  "activity": "Invented sustained test instruction", "basis": "Invented test evidence", "evidence_turns": [1]}
        two_steps = deepcopy(record)
        two_steps["training"] = [period]
        two_steps["development"] = 30 - 12 - 14
        payload = advance_payload(self.store, changed=("character",), operations=[
            set_op(["character", "capabilities", "accounts"], record, two_steps),
            set_op(["character", "skills", "accounts"], 3, 5)])
        self.reject(payload)
        one_step = deepcopy(record)
        one_step["training"] = [period]
        one_step["development"] = 30 - 12
        payload = advance_payload(self.store, changed=("character",), operations=[
            set_op(["character", "capabilities", "accounts"], record, one_step),
            set_op(["character", "skills", "accounts"], 3, 4)])
        self.assertEqual(4, self.store.advance(payload)["state"]["character"]["skills"]["accounts"])
