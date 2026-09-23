"""Read-only focused context from validated records, with explicit retrieval.

The chain is checked by code, not copied into the GM's next prompt. A narrative
budget never removes obligations, deadlines, or the complete active record index.
"""

from __future__ import annotations

from copy import deepcopy
import json

from .engine import CampaignError, CampaignStore


TURN_KINDS = {"turn", "advance"}
OPEN_STATUSES = {"active", "blocked"}


def _count(value, label, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise CampaignError(f"{label} must be an integer of at least {minimum}")
    return value


def _ids(value, label):
    if value is None:
        return []
    if not isinstance(value, (list, tuple)) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise CampaignError(f"{label} must be a list of nonempty record IDs")
    return list(dict.fromkeys(value))


def _event_reference(store, event):
    return {"event_hash": event["hash"], "sequence": event["sequence"],
            "event_file": str(store.path / "events" / f"{event['sequence']:06d}.json")}


def _opening_event(events):
    """The latest accepted pre-play wording, retaining original setup evidence."""
    return next((event for event in reversed(events)
                 if event["kind"] in {"setup", "correction"}
                 and event["state"]["turn"] == 0
                 and "opening_narrative" in event["input"]), None)


def _record_index(record_id, record):
    return {"id": record_id, "kind": record["kind"], "title": record["title"],
            "status": record["status"], "summary": record["summary"],
            "due_seconds": record.get("due_seconds"), "known_by": list(record.get("known_by", [])),
            "links": list(record.get("links", [])), "retrieve": {"record_id": "world." + record_id}}


def _compact_record_index(record_id, record):
    return {"id": record_id, "kind": record["kind"], "title": record["title"],
            "status": record["status"], "retrieve": {"record_id": "world." + record_id}}


def _continuity_index(records, subjects, loaded=()):
    """Surface durable constraints pointing to this focus without archive loading.

    Links need not be reciprocal. A closed capture or death record can still
    constrain a person whose own record does not link back to it. Knowledge
    attribution alone is not relevance: knowing a fact must not load every fact
    the person has ever heard. Related summaries provide explicit retrieval;
    they do not recursively widen the focus or grant the PC knowledge.
    """
    subjects = set(subjects)
    loaded = set(loaded)
    result = []
    for record_id, record in sorted(records.items()):
        durable = record["kind"] in {"fact", "divergence"} or (
            record["kind"] == "person" and record["status"] == "dead")
        related = subjects.intersection(record.get("links", []) + record.get("participants", []))
        if durable and related and record_id not in loaded:
            result.append({**_record_index(record_id, record), "related_to": sorted(related)})
    return result


def record_index_packet(store: CampaignStore, query="", kind=None, status=None, offset=0, limit=25) -> dict:
    """Search current world records by text and filters, in stable ID order.

    The status aliases 'open' and 'inactive' select all active/blocked or closed
    statuses respectively; an exact status still selects only that status.
    """
    if not isinstance(query, str):
        raise CampaignError("query must be text")
    for label, value in (("kind", kind), ("status", status)):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise CampaignError(f"{label} must be a nonempty string when supplied")
    _count(offset, "offset")
    _count(limit, "limit", minimum=1)
    events = store.validate()
    if not events:
        return {"status": "awaiting_setup", "head": None, "turn": None, "total_records": 0,
                "matched_records": 0, "offset": offset, "limit": limit, "next_offset": None, "records": []}
    records = events[-1]["state"].get("world", {}).get("records", {})
    search = query.casefold()
    matching = []
    for record_id, record in sorted(records.items()):
        if kind is not None and record["kind"] != kind:
            continue
        if status == "open" and record["status"] not in OPEN_STATUSES:
            continue
        if status == "inactive" and record["status"] in OPEN_STATUSES:
            continue
        if status not in {None, "open", "inactive"} and record["status"] != status:
            continue
        if search and search not in (record_id + " " + json.dumps(record, ensure_ascii=False, sort_keys=True)).casefold():
            continue
        matching.append((record_id, record))
    page = matching[offset:offset + limit]
    return {"head": events[-1]["hash"], "turn": events[-1]["state"]["turn"],
            "query": query, "kind": kind, "status_filter": status,
            "total_records": len(records), "matched_records": len(matching),
            "offset": offset, "limit": limit,
            "next_offset": offset + len(page) if offset + len(page) < len(matching) else None,
            "records": [_record_index(key, record) for key, record in page],
            "source": _event_reference(store, events[-1])}


def _resolve_record(state, record_id):
    records = state.get("world", {}).get("records", {})
    if record_id == "pc.character":
        return "pc.character", state["character"]
    if record_id.startswith("world.") and record_id[6:] in records:
        return record_id[6:], records[record_id[6:]]
    for prefix, field in (("task.", "tasks"), ("research.", "research")):
        if record_id.startswith(prefix):
            for record in state[field]:
                if record["id"] == record_id[len(prefix):]:
                    return record_id, record
    if record_id.startswith("capability."):
        key = record_id[len("capability."):]
        if key in state["character"]["skills"]:
            return record_id, {"rating": state["character"]["skills"][key],
                               "record": state["character"].get("capabilities", {}).get(key)}
    if record_id in records:
        return record_id, records[record_id]
    if record_id == "character":
        return record_id, state["character"]
    raise CampaignError(f"Unknown record ID: {record_id}. Read the context index before choosing a record.")


def record_packet(store: CampaignStore, record_id: str) -> dict:
    """Return one complete current record with its exact current provenance."""
    _ids([record_id], "record_id")
    events = store.validate()
    if not events:
        raise CampaignError("Campaign is awaiting setup; no current records exist")
    state = events[-1]["state"]
    key, record = _resolve_record(state, record_id)
    records = state.get("world", {}).get("records", {})
    subjects = [key] if record is records.get(key) else ["pc"] if record is state["character"] else []
    return {"head": events[-1]["hash"], "turn": events[-1]["state"]["turn"],
            "record_id": key, "record": deepcopy(record),
            "continuity_record_index": _continuity_index(records, subjects, [key]),
            "source": _event_reference(store, events[-1]),
            "knowledge_note": "A player-safe record is not automatically knowledge possessed by the PC; inspect known_by."}


def history_packet(store: CampaignStore, turn: int) -> dict:
    """Retrieve one accepted turn and its same-turn OOC notes, not the chain."""
    _count(turn, "turn")
    events = store.validate()
    matching = [(index, event) for index, event in enumerate(events)
                if event["state"]["turn"] == turn
                and (event["kind"] in TURN_KINDS or turn == 0 and event["kind"] == "setup")]
    if not matching:
        raise CampaignError(f"No accepted turn {turn} exists")
    index, event = matching[0]
    notes = [{"kind": item["kind"], "input": deepcopy(item["input"]),
              **_event_reference(store, item)}
             for item in events[index + 1:]
             if item["state"]["turn"] == turn and item["kind"] not in TURN_KINDS]
    packet = {"head": events[-1]["hash"], "turn": turn,
            "start_seconds": events[index - 1]["state"]["time_seconds"] if index else event["state"]["time_seconds"],
            "end_seconds": event["state"]["time_seconds"], "kind": event["kind"],
            "accepted_input": deepcopy(event["input"]), "later_same_turn_notes": notes,
            **_event_reference(store, event)}
    if turn == 0:
        opening = _opening_event(events)
        if opening:
            packet["effective_opening_narrative"] = opening["input"]["opening_narrative"]
            packet["opening_reference"] = _event_reference(store, opening)
    return packet


def _capability_index(character, events):
    """Each rating with the reason behind it, so the GM selects abilities by meaning."""
    from .capabilities import capability_usage
    usage = capability_usage(events)
    records = character.get("capabilities", {})
    index = {}
    for key, rating in character["skills"].items():
        record = records.get(key, {})
        entry = {"rating": rating, "kind": record.get("kind", "skill")}
        if record.get("basis"):
            entry["basis"] = record["basis"]
        if usage.get(key):
            entry["use_turns"] = usage[key]
        index[key] = entry
    return index


def context_packet(store: CampaignStore, focus_ids=None, recent_turns=2, max_chars=12000,
                   read_record_ids=None) -> dict:
    """Return current essentials, complete indexes, selected closure, recent prose.

    max_chars is the combined recent-narrative character budget, not a total JSON
    ceiling. Mandatory state and explicitly requested records are never truncated.
    Every omitted narrative character is disclosed with exact turn retrieval refs.
    """
    requested = _ids(focus_ids, "focus_ids") + _ids(read_record_ids, "read_record_ids")
    _count(recent_turns, "recent_turns")
    _count(max_chars, "max_chars")
    events = store.validate()
    if not events:
        if requested:
            raise CampaignError("Campaign is awaiting setup; no focus records exist")
        return {"status": "awaiting_setup", "head": None, "turn": None,
                "starting_character_sheet": str(store.path.parent / "character-sheet.md"),
                "note": "Read the supplied starting character sheet and establish missing setup details. "
                        "No character state, opening scene, or resolved turn is initialized."}
    state = events[-1]["state"]
    records = state.get("world", {}).get("records", {})
    selected = {}
    selected_details = {}
    queue = list(dict.fromkeys(requested))
    # All unresolved dated records are mandatory even when outside the focus.
    due = {key: record for key, record in records.items()
           if record["status"] in OPEN_STATUSES and record.get("due_seconds") is not None}
    queue.extend("world." + key for key in sorted(due))
    while queue:
        key, record = _resolve_record(state, queue.pop(0))
        is_world_record = record is records.get(key)
        target = selected if is_world_record else selected_details
        if key in target:
            continue
        target[key] = deepcopy(record)
        if is_world_record:
            dependencies = list(record.get("links", [])) + list(record.get("participants", [])) + list(record.get("known_by", []))
            queue.extend("world." + link for link in dependencies if link in records and link not in selected)
    character = state["character"]
    continuity_subjects = set(selected)
    if "pc.character" in selected_details or "character" in selected_details:
        continuity_subjects.add("pc")
    continuity = _continuity_index(records, continuity_subjects, selected)
    closed_records = [(key, record) for key, record in sorted(records.items()) if record["status"] not in OPEN_STATUSES]
    packet = {
        "status": "ready" if state["alive"] else "character_dead",
        "head": events[-1]["hash"], "turn": state["turn"],
        "time_seconds": state["time_seconds"], "phase": state["phase"], "location": state["location"],
        "campaign": deepcopy(state["campaign"]),
        "character": {key: deepcopy(character[key]) for key in
                      ("name", "age", "status", "background", "aim", "skills", "condition", "conditions", "equipment")
                      if key in character},
        "character_detail_reference": {"record_id": "pc.character"},
        "disposition": deepcopy(character.get("profile", {}).get("disposition", {})),
        "capability_index": _capability_index(character, events),
        "capability_note": "Action first. Choose the governing ability by what its basis says the character "
                           "can actually do, not by its name; use_turns shows where it has already governed play.",
        "resources": deepcopy(state["resources"]), "alive": state["alive"], "death": deepcopy(state["death"]),
        "mandatory": {
            "obligations": deepcopy(state["obligations"]),
            "standing_orders": deepcopy(state["standing_orders"]),
            "interrupted_plan": deepcopy(state["interrupted_plan"]), "resume_note": state["resume_note"],
            "active_tasks": deepcopy([task for task in state["tasks"] if task["status"] in OPEN_STATUSES]),
            "due_world_records": deepcopy(due),
        },
        "known_context": {key: deepcopy(state[key]) for key in ("relationships", "knowledge", "assumptions")},
        "active_record_index": [_record_index(key, record) for key, record in sorted(records.items())
                                if record["status"] in OPEN_STATUSES],
        "closed_record_index": [_compact_record_index(key, record) for key, record in closed_records[:10]],
        "closed_records": {"total": len(closed_records), "returned": min(10, len(closed_records)),
                           "remaining": max(0, len(closed_records) - 10),
                           "retrieve": {"command": "records --status inactive --offset 10 --limit 25"}},
        "task_index": [{"id": task["id"], "status": task["status"], "due_seconds": task["due_seconds"],
                        "retrieve": {"record_id": "task." + task["id"]}} for task in state["tasks"]],
        "research_index": [{"id": source["id"], "claim": source["claim"], "type": source["type"],
                            "retrieve": {"record_id": "research." + source["id"]}} for source in state["research"]],
        "selected_records": selected,
        "selected_details": selected_details,
        "continuity_record_index": continuity,
        "selection": {"requested_ids": list(dict.fromkeys(requested)),
                      "expanded_through": ["links", "participants", "known_by", "all open dated records"],
                      "continuity_note": "Related facts, divergences and dead people remain binding after closure. "
                                         "Incoming links and participants supply summaries, not recursive archive loading. "
                                         "Retrieve their details before a dependent ruling. Focus or retrieve each relevant "
                                         "person or subject before using canonical assumptions about them.",
                      "details_not_loaded": sorted(({key for key, record in records.items()
                                                      if record["status"] in OPEN_STATUSES}
                                                     | {key for key, _ in closed_records[:10]}
                                                     | {row["id"] for row in continuity}) - set(selected)),
                      "note": "Indexed records retain their full details in the ledger. Retrieve them before a ruling that depends on those details."},
        "recent_turns": [],
        "narrative_budget": {"max_chars": max_chars, "used_chars": 0, "omitted_chars": 0,
                             "scope": "recent narrative text only; mandatory state and selected records are complete"},
        "source": _event_reference(store, events[-1]),
        "knowledge_note": "Research and world records do not grant PC knowledge; inspect attribution and known_by.",
    }
    resolved = [(index, event) for index, event in enumerate(events) if event["kind"] in TURN_KINDS]
    chosen = resolved[-recent_turns:] if recent_turns else []
    remaining = max_chars
    # Allocate to the newest scene first; preserve chronological presentation.
    for index, event in reversed(chosen):
        payload = event["input"]
        narrative = payload["narrative"]
        excerpt = narrative[:remaining]
        omitted = len(narrative) - len(excerpt)
        remaining -= len(excerpt)
        packet["recent_turns"].append({
            "turn": event["state"]["turn"], "start_seconds": events[index - 1]["state"]["time_seconds"],
            "end_seconds": event["state"]["time_seconds"], "objective": payload["objective"], "outcome": payload["outcome"],
            "next_decision": payload.get("next_decision"), "narrative": excerpt, "narrative_truncated": bool(omitted), "omitted_chars": omitted,
            "retrieve": {"turn": event["state"]["turn"]}, **_event_reference(store, event)})
        packet["narrative_budget"]["omitted_chars"] += omitted
    packet["recent_turns"].reverse()
    opening_event = _opening_event(events)
    opening = opening_event["input"]["opening_narrative"] if opening_event else None
    if opening:
        packet["opening_reference"] = {"turn": 0, **_event_reference(store, opening_event)}
        if not resolved and recent_turns:
            excerpt = opening[:remaining]
            omitted = len(opening) - len(excerpt)
            remaining -= len(excerpt)
            packet["opening_scene"] = {"narrative": excerpt, "narrative_truncated": bool(omitted),
                                       "omitted_chars": omitted, "retrieve": {"turn": 0},
                                       **_event_reference(store, opening_event)}
            packet["narrative_budget"]["omitted_chars"] += omitted
    packet["narrative_budget"]["used_chars"] = max_chars - remaining
    packet["history_retrieval"] = {"resolved_turns": len(resolved),
                                   "returned_turns": len(chosen), "command": "history --turn N",
                                   "note": "Retrieve older or truncated scenes before relying on their exact wording."}
    first_sequence = chosen[0][1]["sequence"] if chosen else events[-1]["sequence"]
    packet["recent_corrections"] = [{"turn": event["state"]["turn"], "reason": event["input"]["reason"],
                                     "changed_fields": sorted(event["input"]["changes"]),
                                     "resource_adjustments": deepcopy(event["input"]["resources_delta"]),
                                     "retrieve": {"turn": event["state"]["turn"]}, **_event_reference(store, event)}
                                    for event in events if event["kind"] == "correction"
                                    and event["sequence"] >= first_sequence]
    return packet
