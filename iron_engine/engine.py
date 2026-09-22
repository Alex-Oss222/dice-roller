"""Validate and persist player-safe campaign results, never invent them.

The event chain is authoritative. Each read checks hashes and replays submitted
inputs; each write publishes a complete file without overwriting another writer.
Hashes detect inconsistency, not an attacker rewriting the entire local chain.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any


class CampaignError(ValueError):
    """Invalid campaign data, damaged history, or unsafe filesystem operation."""


STATE_FIELDS = set("campaign turn time_seconds phase location character resources "
                   "relationships obligations tasks knowledge assumptions research "
                   "standing_orders interrupted_plan alive death resume_note".split())
CHANGE_FIELDS = set("phase location character relationships obligations tasks knowledge "
                    "assumptions standing_orders interrupted_plan alive death".split())
REVIEW_FIELDS = set("results decisions capabilities position gm_consistency next_constraint".split())
TASK_STATUSES = {"active", "completed", "blocked", "failed", "expired", "abandoned"}
SOURCE_TYPES = {"canon", "secondary", "author", "historical_analogy", "campaign_assumption"}
EVENT_FIELDS = set("schema_version sequence kind request_id input previous_hash state hash".split())


def _fail(message: str) -> None:
    raise CampaignError(message)


def _object(value: Any, label: str, keys: set[str] | None = None) -> dict:
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        _fail(f"{label} must be an object with string keys")
    if keys is not None and set(value) != keys:
        missing, unknown = sorted(keys - set(value)), sorted(set(value) - keys)
        _fail(f"{label}: missing fields {missing}; unknown fields {unknown}")
    return value


def _string(value: Any, label: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        _fail(f"{label} must be {'a' if empty else 'a nonempty'} string")
    # Unpaired surrogates cannot be encoded to our canonical UTF-8 format.
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise CampaignError(f"{label} must be valid UTF-8 text") from exc
    return value


def _integer(value: Any, label: str, minimum: int | None = None,
             maximum: int | None = None) -> int:
    if type(value) is not int:
        _fail(f"{label} must be an integer, not a boolean or float")
    if minimum is not None and value < minimum:
        _fail(f"{label} must be at least {minimum}")
    if maximum is not None and value > maximum:
        _fail(f"{label} must be at most {maximum}")
    return value


def _list(value: Any, label: str) -> list:
    if not isinstance(value, list):
        _fail(f"{label} must be a list")
    return value


def _strings(value: Any, label: str) -> None:
    for item in _list(value, label):
        _string(item, label)


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise CampaignError(f"Data is not canonical JSON: {exc}") from exc


def _clone_json(value: Any, depth: int = 0) -> Any:
    """Reject Python-only values and ambiguous dict keys before copying input."""
    if depth > 40:
        _fail("JSON nesting exceeds 40 levels")
    if value is None or type(value) in (str, int, bool):
        if isinstance(value, str):
            _string(value, "JSON text", empty=True)
        return value
    if type(value) is float:
        _fail("Floating-point values are not accepted in ledger commands")
    if isinstance(value, list):
        return [_clone_json(item, depth + 1) for item in value]
    if isinstance(value, dict):
        _object(value, "JSON object")
        return {_string(key, "JSON key", empty=True): _clone_json(item, depth + 1)
                for key, item in value.items()}
    _fail("Commands must contain only JSON objects, arrays, strings, integers, booleans, and null")


def _hash(envelope: dict) -> str:
    return hashlib.sha256(_canonical({k: v for k, v in envelope.items() if k != "hash"})).hexdigest()


def _source(value: Any) -> None:
    _object(value, "research source", set("id claim source type scope confidence limitations".split()))
    for key, item in value.items():
        _string(item, f"source.{key}")
    if value["type"] not in SOURCE_TYPES:
        _fail("Unknown research source type")
    if value["type"] == "campaign_assumption" and value["source"] != "campaign convention":
        _fail("Campaign assumptions must use source 'campaign convention'")


def _state(value: Any) -> None:
    _object(value, "state", STATE_FIELDS)
    campaign = _object(value["campaign"], "campaign", set(
        "id title era region spoiler_cutoff day_zero_anchor rules_version resolution_mode".split()))
    for key, item in campaign.items():
        _string(item, f"campaign.{key}")
    if campaign["resolution_mode"] not in {"adjudicated", "real_dice"}:
        _fail("resolution_mode must be adjudicated or real_dice")
    for key in ("turn", "time_seconds"):
        _integer(value[key], key, 0)
    for key in ("phase", "location"):
        _string(value[key], key)
    character = _object(value["character"], "character", set(
        "name age status background aim skills conditions equipment".split()))
    for key in ("name", "status", "background", "aim"):
        _string(character[key], f"character.{key}")
    _integer(character["age"], "character.age", 0)
    for key, rating in _object(character["skills"], "character.skills").items():
        _string(key, "skill name")
        _integer(rating, f"skill {key}", 0, 5)
    for key in ("conditions", "equipment"):
        _strings(character[key], f"character.{key}")
    for key, amount in _object(value["resources"], "resources").items():
        _string(key, "resource unit")
        _integer(amount, f"resources.{key}", 0)
    for key in ("relationships", "obligations", "knowledge", "assumptions", "standing_orders"):
        _strings(value[key], key)
    if value["resume_note"] is not None:
        _string(value["resume_note"], "resume_note")
    task_ids = set()
    for task in _list(value["tasks"], "tasks"):
        _object(task, "task", {"id", "description", "status", "due_seconds", "note"})
        for key in ("id", "description", "status"):
            _string(task[key], f"task.{key}")
        _string(task["note"], "task.note", empty=True)
        if task["id"] in task_ids:
            _fail(f"Duplicate task ID: {task['id']}")
        task_ids.add(task["id"])
        if task["status"] not in TASK_STATUSES:
            _fail(f"Unknown task status: {task['status']}")
        if task["due_seconds"] is not None:
            _integer(task["due_seconds"], "task.due_seconds", 0)
            if task["status"] == "active" and task["due_seconds"] <= value["time_seconds"]:
                _fail(f"Active task {task['id']} is overdue; settle it or record a future deadline")
    source_ids = set()
    for source in _list(value["research"], "research"):
        _source(source)
        if source["id"] in source_ids:
            _fail(f"Duplicate research ID: {source['id']}")
        source_ids.add(source["id"])
    plan = value["interrupted_plan"]
    if plan is not None:
        _object(plan, "interrupted_plan", {
            "objective", "endpoint_seconds", "remaining_seconds", "stopping_conditions"})
        _string(plan["objective"], "interrupted_plan.objective")
        _strings(plan["stopping_conditions"], "stopping_conditions")
        if plan["endpoint_seconds"] is None and plan["remaining_seconds"] is None:
            _fail("An interrupted plan needs an endpoint or remaining duration")
        for key in ("endpoint_seconds", "remaining_seconds"):
            if plan[key] is not None:
                _integer(plan[key], f"interrupted_plan.{key}", 0)
    if type(value["alive"]) is not bool:
        _fail("alive must be a boolean")
    if value["alive"]:
        if value["death"] is not None:
            _fail("A living character must have death null")
    else:
        death = _object(value["death"], "death", {"cause", "time_seconds"})
        _string(death["cause"], "death.cause")
        _integer(death["time_seconds"], "death.time_seconds", 0)
        if death["time_seconds"] != value["time_seconds"]:
            _fail("Death time must equal the final campaign time")


def _changes(state: dict, payload: dict, *, correction: bool) -> dict:
    changes = _object(payload["changes"], "changes")
    allowed = CHANGE_FIELDS - ({"alive", "death"} if correction else set())
    if not set(changes) <= allowed:
        _fail(f"Fields cannot be replaced: {sorted(set(changes) - allowed)}")
    delta = _object(payload["resources_delta"], "resources_delta")
    evidence = _object(payload["evidence"], "evidence")
    expected_evidence = set(changes) | {f"resources.{key}" for key in delta}
    if set(evidence) != expected_evidence:
        _fail("evidence must explain exactly each changes field and resources.UNIT adjustment")
    for key, explanation in evidence.items():
        _string(explanation, f"evidence.{key}")
    result = copy.deepcopy(state)
    result.update(copy.deepcopy(changes))
    for unit, adjustment in delta.items():
        _string(unit, "resource unit")
        _integer(adjustment, f"resources_delta.{unit}")
        if unit not in result["resources"] and not correction:
            _fail(f"Unknown resource unit {unit}; establish it in setup or correction")
        result["resources"][unit] = result["resources"].get(unit, 0) + adjustment
        if result["resources"][unit] < 0:
            _fail(f"Insufficient resources: {unit}")
    old_ids = {task["id"] for task in state["tasks"]}
    new_ids = set()
    for task in _list(result["tasks"], "tasks"):
        _object(task, "task", {"id", "description", "status", "due_seconds", "note"})
        new_ids.add(_string(task["id"], "task.id"))
    if old_ids - new_ids:
        _fail(f"Existing tasks cannot be deleted: {sorted(old_ids - new_ids)}")
    return result


def _checks(checks: Any, mode: str) -> None:
    _list(checks, "checks")
    if mode == "adjudicated" and checks:
        _fail("Adjudicated campaigns require checks to be empty")
    for check in checks:
        _object(check, "check", set("source roll skill modifier target total margin objective stakes".split()))
        if check["source"] not in ("player", "tool"):
            _fail("Check source must be player or tool")
        _integer(check["roll"], "check.roll", 1, 20)
        _integer(check["skill"], "check.skill", 0, 5)
        _integer(check["modifier"], "check.modifier", -4, 4)
        for key in ("target", "total", "margin"):
            _integer(check[key], f"check.{key}")
        for key in ("objective", "stakes"):
            _string(check[key], f"check.{key}")
        if check["total"] != check["roll"] + check["skill"] + check["modifier"]:
            _fail("Check total does not match roll + skill + modifier")
        if check["margin"] != check["total"] - check["target"]:
            _fail("Check margin does not match total - target")


def _review(review: Any, turn: int) -> None:
    if turn % 10:
        if review is not None:
            _fail("A stored review is allowed only on every tenth turn")
        return
    _object(review, "review", {"from_turn", "to_turn", "findings"})
    first = turn - 9
    for key, expected in (("from_turn", first), ("to_turn", turn)):
        _integer(review[key], f"review.{key}")
        if review[key] != expected:
            _fail(f"review.{key} must be {expected}")
    for name, finding in _object(review["findings"], "review.findings", REVIEW_FIELDS).items():
        _object(finding, f"review.{name}", {"assessment", "evidence_turns"})
        _string(finding["assessment"], f"review.{name}.assessment")
        references = _list(finding["evidence_turns"], "evidence_turns")
        if not references:
            _fail(f"Review finding {name} needs evidence from this ten-turn window")
        for reference in references:
            _integer(reference, "evidence_turn", first, turn)


def _apply(kind: str, payload: dict, before: dict | None, previous_hash: str | None = None) -> dict:
    if kind == "setup":
        _object(payload, "setup input", {"request_id", "state"})
        if before is not None:
            _fail("A campaign can only be initialized once")
        state = copy.deepcopy(payload["state"])
        _state(state)
        if (state["turn"] != 0 or not state["alive"] or state["death"] is not None
                or state["resume_note"] is not None):
            _fail("Setup must be turn 0 with a living character, death null, and resume_note null")
        return state
    if before is None:
        _fail("The campaign must be initialized first")
    expected_hash = _string(payload.get("expected_hash"), "expected_hash")
    if expected_hash != previous_hash:
        _fail("Stale expected_hash: inspect the latest event before preparing a new command")
    if kind == "checkpoint":
        _object(payload, "checkpoint input", {"request_id", "expected_hash", "resume_note"})
        if payload["resume_note"] is not None:
            _string(payload["resume_note"], "resume_note")
        state = copy.deepcopy(before)
        state["resume_note"] = payload["resume_note"]
        return state
    if kind == "research":
        _object(payload, "research input", {"request_id", "expected_hash", "sources"})
        state = copy.deepcopy(before)
        sources = _list(payload["sources"], "sources")
        if not sources:
            _fail("Provide at least one research source")
        state["research"].extend(copy.deepcopy(sources))
        _state(state)
        return state
    if kind == "correction":
        _object(payload, "correction input", {
            "request_id", "expected_hash", "reason", "changes", "resources_delta", "evidence"})
        _string(payload["reason"], "correction.reason")
        if not payload["changes"] and not payload["resources_delta"]:
            _fail("A correction must change at least one field or resource unit")
        state = _changes(before, payload, correction=True)
        _state(state)
        return state
    if kind != "turn":
        _fail(f"Unknown event kind: {kind}")
    _object(payload, "turn input", set(
        "request_id expected_hash expected_turn elapsed_seconds objective outcome narrative resources_delta "
        "changes evidence processed_tasks checks review".split()))
    if not before["alive"]:
        _fail("Death is final; no further turns can be committed")
    _integer(payload["expected_turn"], "expected_turn", 0)
    if payload["expected_turn"] != before["turn"]:
        _fail(f"Stale turn: expected {payload['expected_turn']}, current turn is {before['turn']}")
    _integer(payload["elapsed_seconds"], "elapsed_seconds", 1)
    for key in ("objective", "outcome", "narrative"):
        _string(payload[key], key)
    state = _changes(before, payload, correction=False)
    state["turn"] = before["turn"] + 1
    state["time_seconds"] = before["time_seconds"] + payload["elapsed_seconds"]
    state["resume_note"] = None
    processed = _object(payload["processed_tasks"], "processed_tasks")
    previous_tasks = {task["id"]: task for task in before["tasks"]}
    for task_id, explanation in processed.items():
        _string(explanation, f"processed_tasks.{task_id}")
        if task_id not in previous_tasks:
            _fail(f"processed_tasks contains an unknown previous task ID: {task_id}")
    _state(state)
    resulting_tasks = {task["id"]: task for task in state["tasks"]}
    for task_id, task in previous_tasks.items():
        if (task["status"] == "active" and task["due_seconds"] is not None
                and task["due_seconds"] <= state["time_seconds"]):
            if task_id not in processed:
                _fail(f"Deadline crossed without processing task {task_id}")
            updated = resulting_tasks[task_id]
            if updated["status"] == "active":
                if (updated["due_seconds"] is None or updated["due_seconds"] <= state["time_seconds"]
                        or not updated["note"].strip()):
                    _fail(f"Rescheduled task {task_id} needs a future deadline and explanatory note")
    _checks(payload["checks"], state["campaign"]["resolution_mode"])
    _review(payload["review"], state["turn"])
    return state


def _validate_events(events: Any) -> list[dict]:
    _list(events, "events")
    state, previous_hash = None, None
    requests = set()
    for sequence, event in enumerate(events):
        _object(event, "event", EVENT_FIELDS)
        _integer(event["schema_version"], "schema_version", 1, 1)
        _integer(event["sequence"], "sequence", 0)
        if event["sequence"] != sequence:
            _fail(f"Event sequence gap at {sequence}")
        _string(event["kind"], "event.kind")
        request_id = _string(event["request_id"], "request_id")
        if request_id in requests:
            _fail(f"Duplicate request ID in history: {request_id}")
        requests.add(request_id)
        payload = _object(event["input"], "event.input")
        if payload.get("request_id") != request_id:
            _fail("Envelope and command request IDs differ")
        if event["previous_hash"] != previous_hash:
            _fail(f"Broken previous hash at event {sequence}")
        if not isinstance(event["hash"], str) or event["hash"] != _hash(event):
            _fail(f"Hash mismatch at event {sequence}")
        state = _apply(event["kind"], payload, state, previous_hash)
        if _canonical(state) != _canonical(event["state"]):
            _fail(f"State does not match replayed command at event {sequence}")
        previous_hash = event["hash"]
    return events


def _safe_path(path: str | os.PathLike) -> Path:
    try:
        text = _string(os.fspath(path), "ledger path")
        if "\x00" in text:
            _fail("Ledger paths cannot contain null characters")
        candidate = Path(text).expanduser()
        if ".." in candidate.parts:
            _fail("Parent traversal '..' is not allowed in ledger paths")
        candidate = candidate.absolute()
        for parent in reversed((candidate, *candidate.parents)):
            if parent.is_symlink():
                _fail(f"Symbolic links are not allowed in ledger paths: {parent}")
        return candidate
    except (OSError, TypeError, ValueError) as exc:
        if isinstance(exc, CampaignError):
            raise
        raise CampaignError(f"Invalid ledger path: {exc}") from exc


def _pairs(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: str | os.PathLike) -> Any:
    """Read strict JSON from a regular file, refusing symbolic links."""
    path = _safe_path(path)
    descriptor = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(path, flags)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            _fail(f"Expected a regular JSON file: {path}")
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            descriptor = None
            value = json.load(stream, object_pairs_hook=_pairs,
                              parse_constant=lambda token: _fail(f"Invalid JSON number: {token}"))
        return _clone_json(value)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, CampaignError):
            raise
        raise CampaignError(f"Could not read JSON {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _sync_directory(path: Path) -> None:
    # Directory fsync is supported on Unix; not every OS/filesystem offers it.
    if os.name != "posix":
        return
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish(path: Path, data: bytes, temporary_parent: Path) -> None:
    """Flush bytes before an exclusive link makes the complete file visible."""
    path, temporary_parent = _safe_path(path), _safe_path(temporary_parent)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=temporary_parent, prefix=".iron-engine-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # This operation either publishes once or fails if the name already exists.
        _safe_path(path)
        os.link(temporary, path)
        _sync_directory(path.parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class CampaignStore:
    """One local, player-safe campaign with an append-only validated event log."""

    def __init__(self, path: str | os.PathLike = "campaign") -> None:
        self.path = _safe_path(path)

    def validate(self) -> list[dict]:
        try:
            path = _safe_path(self.path)
            if not path.exists():
                return []
            if not path.is_dir():
                _fail("Campaign store must be a directory")
            children = list(path.iterdir())
            if not children:
                return []
            if len(children) != 1 or children[0].name != "events":
                _fail("Campaign store may contain only its events directory")
            directory = _safe_path(path / "events")
            if not directory.is_dir():
                _fail("events must be a directory")
            files = sorted(directory.iterdir(), key=lambda item: item.name)
            events = []
            for sequence, file in enumerate(files):
                if file.name != f"{sequence:06d}.json":
                    _fail(f"Unexpected or missing event file at sequence {sequence}: {file.name}")
                events.append(read_json(file))
            return _validate_events(events)
        except OSError as exc:
            raise CampaignError(f"Could not validate campaign: {exc}") from exc

    def current(self) -> dict:
        events = self.validate()
        if not events:
            _fail("Campaign is awaiting setup; initialize before requesting a character sheet")
        return copy.deepcopy(events[-1]["state"])

    def head(self) -> str:
        events = self.validate()
        if not events:
            _fail("Campaign is awaiting setup; there is no current event hash")
        return events[-1]["hash"]

    @staticmethod
    def _existing(events: list[dict], kind: str, payload: dict) -> dict | None:
        for event in events:
            if event["request_id"] == payload["request_id"]:
                if event["kind"] != kind or _canonical(event["input"]) != _canonical(payload):
                    _fail("request_id was already used for different input")
                return copy.deepcopy(event)
        return None

    def _commit(self, kind: str, payload: Any) -> dict:
        payload = _clone_json(payload)
        _object(payload, "command input")
        _string(payload.get("request_id"), "request_id")
        events = self.validate()
        existing = self._existing(events, kind, payload)
        if existing is not None:
            return existing
        state = _apply(kind, payload, events[-1]["state"] if events else None,
                       events[-1]["hash"] if events else None)
        event = {"schema_version": 1, "sequence": len(events), "kind": kind,
                 "request_id": payload["request_id"], "input": payload,
                 "previous_hash": events[-1]["hash"] if events else None, "state": state}
        event["hash"] = _hash(event)
        try:
            _safe_path(self.path).mkdir(parents=True, exist_ok=True)
            directory = _safe_path(self.path / "events")
            directory.mkdir(exist_ok=True)
            _publish(directory / f"{len(events):06d}.json", _canonical(event) + b"\n", self.path.parent)
            return copy.deepcopy(event)
        except FileExistsError as exc:
            existing = self._existing(self.validate(), kind, payload)
            if existing is not None:
                return existing
            raise CampaignError("A concurrent write won; inspect current state and submit a new request") from exc
        except OSError as exc:
            raise CampaignError(f"Could not publish event: {exc}") from exc

    def initialize(self, payload: dict) -> dict:
        return self._commit("setup", payload)

    def commit_turn(self, payload: dict) -> dict:
        return self._commit("turn", payload)

    def add_research(self, payload: dict) -> dict:
        return self._commit("research", payload)

    def correct(self, payload: dict) -> dict:
        return self._commit("correction", payload)

    def checkpoint(self, payload: dict) -> dict:
        return self._commit("checkpoint", payload)

    def export_save(self, path: str | os.PathLike) -> Path:
        events = self.validate()
        if not events:
            _fail("Cannot export a campaign awaiting setup")
        output = _safe_path(path)
        if output == self.path or self.path in output.parents:
            _fail("Save files must be outside the campaign event store")
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _publish(output, _canonical({"schema_version": 1, "events": events}) + b"\n", output.parent)
            return output
        except FileExistsError as exc:
            raise CampaignError("Save destination already exists; choose a new filename") from exc
        except OSError as exc:
            raise CampaignError(f"Could not export save: {exc}") from exc

    def restore_save(self, input_path: str | os.PathLike) -> dict:
        bundle = read_json(input_path)
        _object(bundle, "save", {"schema_version", "events"})
        _integer(bundle["schema_version"], "save.schema_version", 1, 1)
        events = _validate_events(bundle["events"])
        if not events:
            _fail("Save has no setup event")
        if self.validate():
            _fail("Restore requires an empty campaign store")
        # Validate everything first, then prepare the entire history off to the side.
        # Rename publishes a directory as one operation; it refuses a populated
        # destination. A competing initializer's event therefore cannot be lost.
        staging = None
        try:
            _safe_path(self.path).mkdir(parents=True, exist_ok=True)
            target = _safe_path(self.path / "events")
            if target.exists() and any(target.iterdir()):
                _fail("Restore requires an empty campaign store")
            staging = Path(tempfile.mkdtemp(dir=self.path.parent, prefix=".iron-restore-"))
            for event in events:
                destination = staging / f"{event['sequence']:06d}.json"
                with destination.open("xb") as stream:
                    stream.write(_canonical(event) + b"\n")
                    stream.flush()
                    os.fsync(stream.fileno())
            _sync_directory(staging)
            _safe_path(target)
            os.rename(staging, target)
            staging = None
            _sync_directory(self.path)
            return copy.deepcopy(events[-1]["state"])
        except OSError as exc:
            raise CampaignError(f"Could not restore save into an empty store: {exc}") from exc
        finally:
            if staging is not None:
                for child in staging.iterdir():
                    child.unlink()
                staging.rmdir()


def character_sheet(state: dict) -> str:
    """Render the entire current public state without maintaining a second copy."""
    character = state["character"]
    days, remainder = divmod(state["time_seconds"], 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    lines = [f"{state['campaign']['title']}",
             f"Turn {state['turn']} | Day {days}, {hours:02}:{minutes:02}:{seconds:02}",
             f"{state['phase']} | {state['location']}",
             f"{character['name']} | age {character['age']} | {character['status']}",
             f"Alive: {'yes' if state['alive'] else 'no'}",
             f"Background: {character['background']}", f"Aim: {character['aim']}"]
    for label, entries in (("Skills", character["skills"]), ("Resources (each key is its own unit)", state["resources"])):
        lines.append(f"{label}: " + (", ".join(f"{key}={value}" for key, value in sorted(entries.items())) or "none"))
    for label, entries in (("Conditions", character["conditions"]), ("Equipment", character["equipment"]),
                           *((key.replace("_", " ").capitalize(), state[key]) for key in
                             ("relationships", "obligations", "knowledge", "assumptions", "standing_orders"))):
        lines.append(f"{label}: " + ("; ".join(entries) or "none"))
    lines.append("Tasks:")
    for task in state["tasks"]:
        due = "none" if task["due_seconds"] is None else str(task["due_seconds"]) + " seconds after Day 0 midnight"
        lines.append(f"  {task['id']} [{task['status']}] {task['description']} | due: {due} | {task['note']}")
    if not state["tasks"]:
        lines.append("  none")
    lines.append("Interrupted plan: " + json.dumps(state["interrupted_plan"], ensure_ascii=False))
    lines.append("Resume note: " + (state["resume_note"] or "none"))
    lines.append("Death: " + json.dumps(state["death"], ensure_ascii=False))
    lines.append("Campaign settings: " + json.dumps(state["campaign"], ensure_ascii=False, sort_keys=True))
    lines.append("Research:")
    for source in state["research"]:
        lines.append("  " + json.dumps(source, ensure_ascii=False, sort_keys=True))
    if not state["research"]:
        lines.append("  none")
    return "\n".join(lines)
