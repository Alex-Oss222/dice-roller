"""Explicit authorization, compact edits, and persistent world records.

The validators check declared scope, references, arithmetic and coverage. They
cannot establish whether a GM's prose, research, causal judgment or claimed
authorization is true. Account notes are descriptive; no economy is simulated.
"""

import copy
import re

from .capabilities import SYSTEM
from .engine import OPEN_STATUSES, _canonical, _fail, _integer, _list, _object, _string


VERSION = "1"
JOURNEY_DISTANCE_KEYS = {"distance_this_turn", "distance_total", "distance_remaining", "travel_seconds_this_turn"}
# Markers that belong on the records pages, never inside accepted scene prose.
NARRATIVE_MARKERS = (
    re.compile(r"^\s*#{1,6}\s*(Ledger|Changes|Resolution record|Record review|Assessment)\b", re.M | re.I),
    re.compile(r"^\s*(Evidence|Basis|Actor|Task band|Primary capability|Supporting capability|Source event hash)\s*:", re.M),
    re.compile(r"\bCondition\s*:?\s*\d\s*/\s*9\b"),
    re.compile(r"\[\s*Tags?\b"),
    re.compile(r"\([^()\n]*\b[A-Z][A-Za-z/-]{2,}(?: [A-Za-z/-]+){0,3} [0-9]\b[^()\n]*\)"),
)
LONG_INTERVAL = 30 * 86400
WORLD_KINDS = {"person", "thread", "fact", "divergence", "project", "journey", "account_note"}
WORLD_STATUSES = {"active", "blocked", "completed", "failed", "expired", "abandoned", "closed", "dead"}
OPEN_WORLD_STATUSES = OPEN_STATUSES
RATING = re.compile(r"[0-9]\Z")
WORLD_FIELDS = {"kind", "title", "status", "summary", "participants", "links", "known_by", "due_seconds", "details", "evidence_turns"}
COVERAGE_FIELDS = {
    "character": ("character", "alive", "death"),
    "resources": ("resources",),
    "relationships": ("relationships",),
    "obligations": ("obligations",),
    "tasks": ("tasks",),
    "knowledge": ("knowledge",),
    "assumptions": ("assumptions",),
    "plans": ("phase", "location", "standing_orders", "interrupted_plan"),
    "world": ("world",),
}
ADVANCE_FIELDS = set("request_id expected_hash expected_turn objective outcome narrative elapsed_seconds "
                     "operations authorization adjudication coverage processed_tasks review milestones".split())
ADVANCE_OPTIONAL_FIELDS = {"next_decision"}
CAPABILITY_SET_FIELDS = {"development", "basis", "experience", "aptitude", "domain", "parent", "derivation", "anchors", "kind"}
LIST_FIELDS = {"relationships", "obligations", "knowledge", "assumptions", "standing_orders"}
MISSING = object()


def _references(value, label):
    entries = _list(value, label)
    seen = set()
    for item in entries:
        _string(item, label)
        if item in seen:
            _fail(f"{label} contains a duplicate reference: {item}")
        seen.add(item)
    return entries


def _evidence(value, turn, label, *, interval_only=False):
    entries = _list(value, label)
    if not entries:
        _fail(f"{label} requires at least one accepted turn reference")
    for entry in entries:
        _integer(entry, label, turn if interval_only else 0, turn)


def world_records(state):
    """Look up optional world state without inserting defaults."""
    return state.get("world", {"records": {}})["records"]


def validate_world(state):
    version = state["campaign"].get("workflow_version")
    if version is not None and version != VERSION:
        _fail("Unknown workflow_version; supported explicit version is '1'")
    if version == VERSION:
        if state["campaign"]["resolution_mode"] != "adjudicated":
            _fail("Workflow version 1 requires adjudicated resolution")
        for task in state["tasks"]:
            if task["id"].startswith("world."):
                _fail("Task IDs beginning 'world.' are reserved for world-record deadline references")
    if "world" not in state:
        return
    if version != VERSION:
        _fail("Typed world records require campaign.workflow_version '1'")
    _object(state["world"], "world", {"records"})
    records = _object(state["world"]["records"], "world.records")
    for record_id, record in records.items():
        _string(record_id, "world record ID")
        if record_id in {"pc", "public"}:
            _fail("World record IDs 'pc' and 'public' are reserved references")
        _object(record, f"world.records.{record_id}", WORLD_FIELDS)
        for field in ("kind", "title", "status", "summary"):
            _string(record[field], f"world.{record_id}.{field}")
        if record["kind"] not in WORLD_KINDS:
            _fail(f"Unknown world record kind: {record['kind']}")
        if record["status"] not in WORLD_STATUSES:
            _fail(f"Unknown world record status: {record['status']}")
        for field in ("participants", "links", "known_by"):
            _references(record[field], f"world.{record_id}.{field}")
        for key, value in _object(record["details"], f"world.{record_id}.details").items():
            _string(key, "world detail key")
            _string(value, f"world.{record_id}.details.{key}")
            if record["kind"] == "journey" and key.startswith(("distance", "travel_seconds")) and key not in JOURNEY_DISTANCE_KEYS:
                _fail(f"Journey {record_id} uses an unknown progress key {key}; use {sorted(JOURNEY_DISTANCE_KEYS)}")
            if record["kind"] == "person" and RATING.fullmatch(value) and f"{key} basis" not in record["details"]:
                _fail(f"Person {record_id} rates {key} without a '{key} basis' detail explaining it")
        _evidence(record["evidence_turns"], state["turn"], f"world.{record_id}.evidence_turns")
        due = record["due_seconds"]
        if due is not None:
            _integer(due, f"world.{record_id}.due_seconds", 0)
            if record["status"] in OPEN_WORLD_STATUSES and due <= state["time_seconds"]:
                _fail(f"Open world record {record_id} is overdue; settle or explicitly reschedule it")
    for record_id, record in records.items():
        for target in record["links"]:
            if target not in records:
                _fail(f"World record {record_id} links to missing record {target}")
        for field in ("participants", "known_by"):
            reserved = {"pc", "public"} if field == "known_by" else {"pc"}
            for target in record[field]:
                if target not in reserved and (target not in records or records[target]["kind"] != "person"):
                    _fail(f"World {field} reference {target} must identify a person or an allowed reserved reference")


def retain_world(before, after):
    """Records close in place; a replacement cannot silently discard their IDs."""
    if "world" not in before:
        return
    if "world" not in after:
        _fail("World state cannot be removed once recorded")
    _object(after["world"], "world", {"records"})
    new = _object(after["world"]["records"], "world.records")
    missing = set(world_records(before)) - set(new)
    if missing:
        _fail(f"World record IDs cannot be deleted; settle them instead: {sorted(missing)}")


def validate_world_deadlines(before, after, processed):
    for record_id, record in world_records(before).items():
        if (record["status"] in OPEN_WORLD_STATUSES and record["due_seconds"] is not None
                and record["due_seconds"] <= after["time_seconds"]):
            if f"world.{record_id}" not in processed:
                _fail(f"Deadline crossed without processing world record {record_id}")
            updated = world_records(after)[record_id]
            if updated["status"] in OPEN_WORLD_STATUSES:
                if (updated["due_seconds"] is None or updated["due_seconds"] <= after["time_seconds"]
                        or not updated["details"].get("deadline_reason", "").strip()):
                    _fail(f"Rescheduled world record {record_id} needs a future deadline and details.deadline_reason")


def _path(value):
    path = _list(value, "operation.path")
    if not path:
        _fail("Operation paths cannot be empty")
    for part in path:
        _string(part, "operation path component")
    return path


def _set_allowed(path):
    if len(path) == 1:
        return path[0] in {"phase", "location", "interrupted_plan"}
    if path[0] != "character":
        return False
    if len(path) == 2:
        return path[1] in {"name", "age", "status", "background", "aim", "condition", "profile"}
    if len(path) == 3 and path[1] == "condition":
        return path[2] in {"rating", "tags", "basis"}
    if len(path) == 3 and path[1] in {"skills", "capabilities"}:
        return True
    if len(path) == 4 and path[1] == "capabilities":
        return path[3] in CAPABILITY_SET_FIELDS
    return len(path) in {3, 4} and path[1] == "profile"


def _list_allowed(path, adding):
    if len(path) == 1:
        return path[0] in LIST_FIELDS
    if len(path) == 2:
        return path[0] == "character" and path[1] in {"conditions", "equipment"}
    if len(path) == 3:
        return path[:2] == ["character", "condition"] and path[2] == "tags" or path == ["character", "profile", "languages"]
    if len(path) == 4 and path[:2] == ["character", "capabilities"]:
        return path[3] == "evidence_turns" or adding and path[3] == "training"
    return False


def _parent(state, path):
    parent = state
    for component in path[:-1]:
        if not isinstance(parent, dict) or component not in parent or not isinstance(parent[component], dict):
            _fail("Operation parent is missing or is not an object; establish an allowed parent explicitly")
        parent = parent[component]
    return parent, path[-1]


def _expected(actual, expected):
    if actual is MISSING:
        if expected is not None:
            _fail("New entries require expected null")
    elif _canonical(actual) != _canonical(expected):
        _fail("Operation expected value differs from the currently recorded value")


def _authorization(payload):
    authorization = _object(payload["authorization"], "authorization", {"objective", "max_elapsed_seconds", "stop_condition"})
    _string(authorization["objective"], "authorization.objective")
    _string(authorization["stop_condition"], "authorization.stop_condition")
    _integer(authorization["max_elapsed_seconds"], "authorization.max_elapsed_seconds", 1)
    if authorization["objective"] != payload["objective"]:
        _fail("The submitted objective must match its declared authorization")
    if payload["elapsed_seconds"] > authorization["max_elapsed_seconds"]:
        _fail("Elapsed time exceeds the declared authorization; an unfinished plan is not additional permission")


def _adjudication_capability(before, actor, source, capabilities, reference, label, *, supporting=False):
    fields = {"source", "key", "role"} if supporting else {"source", "key"}
    _object(reference, label, fields)
    _string(reference["source"], f"{label}.source")
    key = _string(reference["key"], f"{label}.key")
    if supporting:
        _string(reference["role"], f"{label}.role")
    if reference["source"] != source or key not in capabilities:
        _fail("The relevant capability source must belong to the actor and exist before this action")
    if actor != "pc" and not RATING.fullmatch(str(capabilities[key])):
        _fail(f"Person detail {key} is not a 0 to 9 rating; adjudicate from a rated ability")
    if actor == "pc" and before["campaign"].get("capability_system") == SYSTEM:
        metadata = before["character"]["capabilities"][key]
        if metadata["kind"] == "domain":
            _fail("Blood & Gold adjudication must use a specific subskill, specialty, or derived ability; a broad domain cannot substitute for the action skill")
    return reference["source"], key


def _adjudication(before, payload):
    base_fields = {"mode", "actor", "capability", "preparation", "opposition", "risk", "basis", "task_band"}
    record = _object(payload["adjudication"], "adjudication",
                     base_fields | (set(payload["adjudication"]) & {"supporting_capabilities"}))
    for field in ("mode", "actor", "preparation", "opposition", "risk", "basis", "task_band"):
        _string(record[field], f"adjudication.{field}")
    if record["mode"] not in {"routine", "uncertain"}:
        _fail("Adjudication mode must be routine or uncertain")
    if record["task_band"] not in {"routine", "ordinary", "demanding", "hard", "extreme"}:
        _fail("Unknown adjudication task_band")
    if (record["mode"] == "routine") != (record["task_band"] == "routine"):
        _fail("Routine mode uses the routine band; uncertain acts require another explicit band")
    actor = record["actor"]
    if actor == "pc":
        source = "character.skills"
        capabilities = before["character"]["skills"]
    else:
        person = world_records(before).get(actor)
        if person is None or person["kind"] != "person":
            _fail("The adjudicated actor must be the PC or a previously recorded person")
        source = f"world.records.{actor}.details"
        capabilities = person["details"]

    seen = set()
    reference = record["capability"]
    if reference is None:
        if record["mode"] == "uncertain":
            _fail("An uncertain act needs a relevant capability from the established record")
    else:
        seen.add(_adjudication_capability(
            before, actor, source, capabilities, reference, "adjudication.capability"))

    supporting = _list(record.get("supporting_capabilities", []), "adjudication.supporting_capabilities")
    for index, support in enumerate(supporting):
        identity = _adjudication_capability(
            before, actor, source, capabilities, support,
            f"adjudication.supporting_capabilities[{index}]", supporting=True)
        if identity in seen:
            _fail("Adjudication capabilities cannot duplicate the primary capability or another supporting capability")
        seen.add(identity)

def lint_narrative(text):
    """Refuse mechanics inside the scene; the records pages carry them instead."""
    for pattern in NARRATIVE_MARKERS:
        match = pattern.search(text)
        if match is not None:
            _fail(f"Narrative contains mechanical text that belongs in the records, not the scene: {match.group(0).strip()!r}")


def _consequential(before, result, operations):
    """Death, a worsened Condition or a new divergence needs a named governing ability."""
    if any(operation.get("op") == "death" for operation in operations):
        return "a death"
    old_condition, new_condition = before["character"].get("condition"), result["character"].get("condition")
    if old_condition is not None and new_condition is not None and new_condition["rating"] < old_condition["rating"]:
        return "a lowered Condition"
    old_records, new_records = world_records(before), world_records(result)
    for record_id, record in new_records.items():
        if record["kind"] == "divergence" and old_records.get(record_id) != record:
            return f"divergence record {record_id}"
    return None


def _milestones(payload):
    milestones = _list(payload["milestones"], "milestones")
    previous = 0
    for milestone in milestones:
        _object(milestone, "interval milestone", {"elapsed_seconds", "basis", "evidence_turns"})
        _integer(milestone["elapsed_seconds"], "milestone.elapsed_seconds", 1, payload["elapsed_seconds"])
        if milestone["elapsed_seconds"] <= previous:
            _fail("Interval milestones must be in strictly increasing elapsed-time order")
        previous = milestone["elapsed_seconds"]
        _string(milestone["basis"], "milestone.basis")
        _evidence(milestone["evidence_turns"], payload["expected_turn"] + 1, "milestone.evidence_turns", interval_only=True)
    if payload["elapsed_seconds"] >= LONG_INTERVAL:
        if len(milestones) < 2 or previous != payload["elapsed_seconds"]:
            _fail("Intervals of 30 days or more require at least two ordered milestones, including the ending time")


def _coverage(before, after, coverage):
    _object(coverage, "coverage", set(COVERAGE_FIELDS))
    for category, fields in COVERAGE_FIELDS.items():
        entry = _object(coverage[category], f"coverage.{category}", {"status", "basis"})
        _string(entry["basis"], f"coverage.{category}.basis")
        _string(entry["status"], f"coverage.{category}.status")
        expected = "changed" if any(_canonical(before.get(field)) != _canonical(after.get(field)) for field in fields) else "unchanged"
        if entry["status"] != expected:
            _fail(f"coverage.{category}.status must match the actual resulting state: {expected}")


def expand_advance(before, payload):
    """Project accepted compact input to the existing validated turn interface.

    This function is pure and can be reused by reading views. It validates the
    workflow declarations and edits; the caller still runs ordinary turn/state,
    development, deadline, death, review and stale-hash validation afterward.
    """
    _object(payload, "advance input", ADVANCE_FIELDS | (set(payload) & ADVANCE_OPTIONAL_FIELDS))
    if before["campaign"].get("workflow_version") != VERSION:
        _fail("advance requires campaign.workflow_version '1'; legacy campaigns retain their turn interface")
    if before["campaign"]["resolution_mode"] != "adjudicated":
        _fail("The compact advance workflow requires adjudicated resolution")
    _integer(payload["expected_turn"], "expected_turn", 0)
    _integer(payload["elapsed_seconds"], "elapsed_seconds", 1)
    for field in ("objective", "outcome", "narrative"):
        _string(payload[field], field)
    lint_narrative(payload["narrative"])
    if payload.get("next_decision") is not None:
        _string(payload["next_decision"], "next_decision")
    _authorization(payload)
    _adjudication(before, payload)
    _milestones(payload)
    result = copy.deepcopy(before)
    reasons = {}

    def reason(field, basis):
        reasons.setdefault(field, []).append(basis)

    for operation in _list(payload["operations"], "operations"):
        _object(operation, "operation")
        kind = _string(operation.get("op"), "operation.op")
        basis = _string(operation.get("basis"), "operation.basis")
        if kind == "set":
            _object(operation, "set operation", {"op", "path", "expected", "value", "basis"})
            path = _path(operation["path"])
            if not _set_allowed(path):
                _fail("This path is not an allowed compact set target")
            parent, key = _parent(result, path)
            _expected(parent.get(key, MISSING), operation["expected"])
            parent[key] = copy.deepcopy(operation["value"])
            reason(path[0], basis)
        elif kind in {"list_add", "list_remove"}:
            _object(operation, "list operation", {"op", "path", "expected", "value", "basis"})
            path = _path(operation["path"])
            adding = kind == "list_add"
            if not _list_allowed(path, adding):
                _fail("This path is not an allowed compact list target")
            parent, key = _parent(result, path)
            entries = _list(parent.get(key), "operation target")
            found = [index for index, value in enumerate(entries) if _canonical(value) == _canonical(operation["value"])]
            if type(operation["expected"]) is not bool or operation["expected"] != bool(found):
                _fail("List operation expected must match current item membership")
            if adding:
                if found:
                    _fail("list_add cannot duplicate an existing item")
                entries.append(copy.deepcopy(operation["value"]))
            else:
                if len(found) != 1:
                    _fail("list_remove requires exactly one existing matching item")
                entries.pop(found[0])
            reason(path[0], basis)
        elif kind == "resource_establish":
            _object(operation, "resource establishment", {"op", "unit", "expected", "value", "basis"})
            unit = _string(operation["unit"], "resource unit")
            if operation["expected"] is not None or unit in result["resources"]:
                _fail("resource_establish requires expected null and a previously absent unit")
            _integer(operation["value"], "established resource value", 0)
            result["resources"][unit] = operation["value"]
            reason(f"resources.{unit}", basis)
        elif kind == "resource_adjust":
            _object(operation, "resource operation", {"op", "unit", "expected", "delta", "basis"})
            unit = _string(operation["unit"], "resource unit")
            if unit not in result["resources"]:
                _fail("resource_adjust requires an established resource unit")
            _integer(operation["expected"], "resource expected", 0)
            _integer(operation["delta"], "resource delta")
            _expected(result["resources"][unit], operation["expected"])
            result["resources"][unit] += operation["delta"]
            if result["resources"][unit] < 0:
                _fail("An intermediate resource adjustment cannot overdraw the recorded balance")
            reason(f"resources.{unit}", basis)
        elif kind in {"task_upsert", "world_upsert"}:
            _object(operation, "record operation", {"op", "id", "expected", "value", "basis"})
            record_id = _string(operation["id"], "record ID")
            value = _object(operation["value"], "record value")
            if kind == "task_upsert":
                if value.get("id") != record_id:
                    _fail("A task upsert cannot rename its stable ID")
                matches = [index for index, task in enumerate(result["tasks"]) if task["id"] == record_id]
                previous = result["tasks"][matches[0]] if matches else MISSING
                _expected(previous, operation["expected"])
                if matches:
                    result["tasks"][matches[0]] = copy.deepcopy(value)
                else:
                    result["tasks"].append(copy.deepcopy(value))
                reason("tasks", basis)
            else:
                records = result.setdefault("world", {"records": {}})["records"]
                _expected(records.get(record_id, MISSING), operation["expected"])
                records[record_id] = copy.deepcopy(value)
                reason("world", basis)
        elif kind == "death":
            _object(operation, "death operation", {"op", "expected_alive", "cause", "basis"})
            if operation["expected_alive"] is not True or not result["alive"]:
                _fail("Death can only be recorded once from an explicitly living state")
            _string(operation["cause"], "death cause")
            result["alive"] = False
            result["death"] = {"cause": operation["cause"], "time_seconds": before["time_seconds"] + payload["elapsed_seconds"]}
            reason("alive", basis)
            reason("death", basis)
        else:
            _fail(f"Unknown compact operation: {kind}")
    if not result["alive"] and payload.get("next_decision") is not None:
        _fail("A dead character cannot have a pending next decision")
    consequence = _consequential(before, result, payload["operations"])
    if consequence is not None and payload["adjudication"]["capability"] is None:
        _fail(f"This advance records {consequence}; name the governing capability in adjudication instead of routine mode with none")
    _coverage(before, result, payload["coverage"])
    changes, deltas, evidence = {}, {}, {}
    for field, bases in reasons.items():
        if field.startswith("resources."):
            unit = field[len("resources."):]
            delta = result["resources"][unit] - before["resources"].get(unit, 0)
            if delta or unit not in before["resources"]:
                deltas[unit] = delta
                evidence[field] = "; ".join(bases)
        elif _canonical(before.get(field)) != _canonical(result.get(field)):
            changes[field] = result[field]
            evidence[field] = "; ".join(bases)
    return {**{field: payload[field] for field in ("request_id", "expected_hash", "expected_turn", "elapsed_seconds",
                                                  "objective", "outcome", "narrative", "processed_tasks", "review")},
            "resources_delta": deltas, "changes": changes, "evidence": evidence, "checks": []}
