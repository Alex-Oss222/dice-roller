"""Deterministic, disposable reading views of the validated campaign event chain."""

import json
import os
from pathlib import Path
import stat
import tempfile

from .engine import CampaignError, CampaignStore
from .character_view import render_character_sheet
from .condition import condition_summary


FILENAMES = ("story.md", "character-sheet.md", "resume.md")
CURRENT_FILENAMES = FILENAMES + ("README.md", "latest.md", "threads.md", "world.md", "decisions.md", "changes.md")
TURN_KINDS = {"turn", "advance"}


def _marker(filename: str) -> str:
    return f"<!-- iron-engine-generated:{filename}:v1 -->"


def _time(seconds: int) -> str:
    day, rest = divmod(seconds, 86400)
    hour, rest = divmod(rest, 3600)
    minute, second = divmod(rest, 60)
    return f"Day {day}, {hour:02}:{minute:02}:{second:02}"


def _duration(seconds: int) -> str:
    day, rest = divmod(seconds, 86400)
    hour, rest = divmod(rest, 3600)
    minute, second = divmod(rest, 60)
    return f"{day} days, {hour} hours, {minute} minutes, {second} seconds"


def _value(value) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _header(filename: str, title: str, head: str, records: str, *, historical=False) -> str:
    reference = ("This page records one accepted event. Check [the latest view](../latest.md) for the current head and later corrections."
                 if historical else "Compare with the ledger's current `head` to detect a stale view.")
    return (
        f"{_marker(filename)}\n"
        f"<!-- source-event-hash:{head} -->\n\n"
        f"# {title}\n\n"
        "Generated reading view. The immutable event chain is authoritative; regenerate this file instead of editing it.\n\n"
        f"Source event hash: `{head}`. {reference}\n\n"
        f"Canonical records, relative to this directory: `{records}`.\n\n"
    )


def _story_header(filename: str, head: str) -> str:
    """Keep ownership and freshness information out of the reading experience."""
    return f"{_marker(filename)}\n<!-- source-event-hash:{head} -->\n\n"


def _changed_values(label: str, before, after) -> list[str]:
    """Describe only changed leaves, without repeating an entire character sheet."""
    if before == after:
        return []
    if isinstance(before, dict) and isinstance(after, dict):
        lines = []
        for key in sorted(set(before) | set(after)):
            detail = f"{label} / {key.replace('_', ' ')}"
            if key not in before:
                lines.append(f"- {detail}: established as {_value(after[key])}.")
            elif key not in after:
                lines.append(f"- {detail}: removed ({_value(before[key])}).")
            else:
                lines.extend(_changed_values(detail, before[key], after[key]))
        return lines
    if isinstance(before, list) and isinstance(after, list):
        removed = [item for item in before if item not in after]
        added = [item for item in after if item not in before]
        if removed or added:
            return ([f"- {label}: removed {_value(item)}." for item in removed] +
                    [f"- {label}: added {_value(item)}." for item in added])
    return [f"- {label}: {_value(before)} → {_value(after)}."]


def _turn_ledger(before: dict, after: dict, payload: dict) -> str:
    """A changed-only reading view, derived from the accepted event and evidence."""
    lines = []
    evidence = payload.get("evidence", {})
    if "operations" in payload:
        from .workflow import expand_advance
        return _turn_ledger(before, after, expand_advance(before, payload))
    changes = payload.get("changes", {})
    resource_changes = payload.get("resources_delta", {})
    for unit, delta in sorted(resource_changes.items()):
        basis = evidence.get('resources.' + unit, evidence.get('resources', 'See accepted operations.'))
        if unit not in before["resources"] and unit in after["resources"]:
            lines.append(f"- {unit}: unrecorded → {after['resources'][unit]}. Evidence: {basis}")
            continue
        opening, closing = before["resources"].get(unit, 0), after["resources"].get(unit, 0)
        if delta and opening != closing:
            lines.append(f"- {unit}: {opening} → {closing} ({delta:+d}). "
                         f"Evidence: {basis}")
    for field in sorted(changes):
        if before.get(field) == after.get(field):
            continue
        basis = evidence.get(field, "See accepted operations and adjudication.")
        if field == "character":
            old_character, character = before[field], after[field]
            if old_character.get("condition") != character.get("condition"):
                condition = character["condition"]
                lines.append(f"- Condition: {condition_summary(old_character)} → {condition_summary(character)}. "
                             f"Tags: {'; '.join(condition['tags'])}. Basis: {condition['basis']} "
                             f"Evidence: {basis}")
            changed_keys = sorted(key for key in set(old_character) | set(character)
                                  if key != "condition" and old_character.get(key) != character.get(key))
            for key in changed_keys:
                lines.extend(_changed_values(f"Character / {key.replace('_', ' ')}",
                                             old_character.get(key), character.get(key)))
            if changed_keys:
                lines.append(f"  Evidence: {basis}")
            continue
        if field == "world":
            old_records = before.get("world", {}).get("records", {})
            new_records = after.get("world", {}).get("records", {})
            for record_id in sorted(set(old_records) | set(new_records)):
                if old_records.get(record_id) != new_records.get(record_id):
                    record = new_records.get(record_id, {})
                    lines.append(f"- World record {record_id} [{record.get('status', 'not recorded')}]: "
                                 f"{record.get('title', record.get('summary', 'updated'))}. Evidence: "
                                 f"{evidence.get('world.records.' + record_id, basis)}")
                    lines.extend(_changed_values(f"World / {record_id}", old_records.get(record_id, {}), record))
            continue
        label = field.replace("_", " ").capitalize()
        if field in {"location", "phase"}:
            change = f"{before[field]} → {after[field]}"
        elif field == "alive":
            label, change = "Life status", "living" if after[field] else "dead"
        elif field == "death":
            change = f"{after[field]['cause']} at {_time(after[field]['time_seconds'])}"
        else:
            lines.extend(_changed_values(label, before.get(field), after.get(field)))
            lines.append(f"  Evidence: {basis}")
            continue
        lines.append(f"- {label}: {change}. Evidence: {basis}")
    return "### Changes\n\n" + "\n".join(lines) if lines else ""


def _turn_scene(event: dict, before: dict) -> str:
    state, payload = event["state"], event["input"]
    condition = state["character"].get("condition")
    condition_rating = condition["rating"] if condition is not None else "Not established"
    summary = (
        "| Field | Current |\n"
        "| --- | --- |\n"
        f"| Name | {_cell(state['character']['name'])} |\n"
        f"| Age | {state['character']['age']} |\n"
        f"| Condition | {condition_rating} |\n"
        f"| Location | {_cell(state['location'])} |"
    )
    segments = [
        summary + "\n\n"
        f"## Turn {state['turn']} | {_time(state['time_seconds'])} | {state['location']} | "
        f"Elapsed: {_duration(payload['elapsed_seconds'])}\n\n"
        + payload["narrative"]
    ]
    next_decision = payload.get("next_decision")
    if next_decision:
        segments.append("### Next\n\n" + next_decision)
    return "\n\n".join(segments)


def _correction_note(event: dict, before: dict) -> str:
    state, payload = event["state"], event["input"]
    lines = [f"### OOC record note: correction at Turn {state['turn']}",
             f"Event {event['sequence']}; {_time(state['time_seconds'])}. No fictional time elapsed.",
             f"Source event hash: `{event['hash']}`.",
             f"Reason: {payload['reason']}",
             "This corrects the recorded state. Earlier accepted story text is preserved."]
    for field, value in sorted(payload["changes"].items()):
        lines.extend(_changed_values(field.replace("_", " ").capitalize(), before.get(field), value))
        lines.append(f"Evidence: {payload['evidence'][field]}")
    for unit, delta in sorted(payload["resources_delta"].items()):
        lines.append(f"- Resource adjustment, {unit}: {delta:+d}; resulting balance: {state['resources'][unit]}. "
                     f"Evidence: {payload['evidence']['resources.' + unit]}")
    if "opening_narrative" in payload:
        lines.append("- Opening presentation revised before the first resolved turn. The original setup event is retained.")
    return "\n\n".join(lines)


def _opening_event(events: list[dict]) -> dict | None:
    return next((event for event in reversed(events) if event["kind"] in {"setup", "correction"}
                 and event["input"].get("opening_narrative")), None)


def _opening(events: list[dict]) -> str:
    event = _opening_event(events)
    narrative = event["input"]["opening_narrative"] if event is not None else None
    return "## Opening: Turn 0\n\n" + narrative if narrative else (
        "Setup is recorded at Turn 0. No opening narrative was supplied."
    )


def _story(events: list[dict]) -> str:
    if not events:
        return ("Awaiting setup. No character state has been initialized and no turns have been saved in the ledger. "
                "A supplied starting character sheet may exist in the selected story's root folder.\n")
    segments = []
    if _opening_event(events) is not None:
        segments.append(_opening(events))
    if not segments and not any(event["kind"] in TURN_KINDS for event in events):
        segments.append(_opening(events))
    for index, event in enumerate(events):
        if event["kind"] in TURN_KINDS:
            segments.append(_turn_scene(event, events[index - 1]["state"]))
    return "\n\n".join(segments) + "\n"


def _capability_note(reference: dict, before: dict) -> str:
    source = reference["source"]
    if source == "character.skills":
        value = before["character"]["skills"]
    elif source.startswith("world.records.") and source.endswith(".details"):
        record_id = source[len("world.records."):-len(".details")]
        value = before["world"]["records"][record_id]["details"]
    else:
        raise CampaignError(f"Unsupported capability source in accepted record: {source}")
    rating = value[reference["key"]]
    return f"{reference['key']} ({_value(rating)}; {reference['source']})"


def _adjudication_note(payload: dict, before: dict) -> str:
    adjudication = payload.get("adjudication")
    if adjudication is None:
        return ""
    lines = ["### Resolution record", f"Objective: {payload['objective']}", f"Outcome: {payload['outcome']}",
             f"Actor: {adjudication['actor']}. Task: {adjudication['task_band']}. Mode: {adjudication['mode']}."]
    primary = adjudication.get("capability")
    if primary is not None:
        lines.append("Primary capability: " + _capability_note(primary, before))
    for supporting in adjudication.get("supporting_capabilities", []):
        lines.append(f"Supporting capability: {_capability_note(supporting, before)}. Role: {supporting['role']}")
    for field in ("preparation", "opposition", "risk", "basis"):
        lines.append(f"{field.capitalize()}: {adjudication[field]}")
    return "\n\n".join(lines)


def _journey_notes(before: dict, after: dict) -> str:
    old_records = before.get("world", {}).get("records", {})
    records = after.get("world", {}).get("records", {})
    selected = [(record_id, record) for record_id, record in sorted(records.items())
                if record["kind"] == "journey" and
                (record["status"] in {"active", "blocked"} or old_records.get(record_id) != record)]
    if not selected:
        return "Journey distance for this interval: not recorded."
    lines = ["### Journey records", "Distances and progress below are recorded facts, not estimates from elapsed time."]
    for record_id, record in selected:
        lines.extend([f"#### {record['title']} ({record_id})", record["summary"],
                      f"Status: {record['status']}."])
        for key, value in sorted(record.get("details", {}).items()):
            lines.append(f"- {key.replace('_', ' ').capitalize()}: {value}")
        if record == old_records.get(record_id):
            lines.append("This journey record is unchanged in this turn; it establishes no additional distance travelled.")
    return "\n\n".join(lines)


def _review_note(review: dict) -> str:
    lines = [f"### Assessment: turns {review['from_turn']} to {review['to_turn']}"]
    for category in ("results", "decisions", "capabilities", "position", "gm_consistency", "next_constraint"):
        finding = review["findings"][category]
        references = ", ".join(str(turn) for turn in finding["evidence_turns"])
        lines.append(f"#### {category.replace('_', ' ').capitalize()}\n\n"
                     f"{finding['assessment']}\n\nEvidence turns: {references}.")
    return "\n\n".join(lines)


def _changes(events: list[dict]) -> str:
    if not events:
        return "Awaiting setup. No turn changes or assessments have been recorded.\n"
    opening = events[0]["state"]
    lines = ["[Read the latest scene](latest.md) · [Current character sheet](character-sheet.md) · "
             "[Threads](threads.md) · [World records](world.md)",
             "Elapsed totals count fictional time since the accepted opening. Unrecorded distance is unknown, "
             "not zero; journey details are preserved as supplied and overlapping routes are not summed.",
             "## Turn 0: starting position", f"Time: {_time(opening['time_seconds'])}. Location: {opening['location']}.",
             f"Elapsed since opening: {_duration(0)}."]
    for index, event in enumerate(events):
        if event["kind"] == "correction":
            lines.append(_correction_note(event, events[index - 1]["state"]))
        elif event["kind"] in TURN_KINDS:
            state, payload, before = event["state"], event["input"], events[index - 1]["state"]
            lines.extend([f"## Turn {state['turn']}",
                          f"{_time(before['time_seconds'])} to {_time(state['time_seconds'])}.",
                          f"Elapsed this turn: {_duration(payload['elapsed_seconds'])}.",
                          f"Elapsed since opening: {_duration(state['time_seconds'] - opening['time_seconds'])}.",
                          f"Location: {state['location']}.", f"Phase: {state['phase']}."])
            change_note = _turn_ledger(before, state, payload)
            if change_note:
                lines.append(change_note)
            lines.append(_journey_notes(before, state))
            adjudication_note = _adjudication_note(payload, before)
            if adjudication_note:
                lines.append(adjudication_note)
            authorization = payload.get("authorization")
            if authorization is not None:
                lines.append(f"Authorized scope: up to {_duration(authorization['max_elapsed_seconds'])}; "
                             f"stop condition: {authorization['stop_condition']}")
            checks = payload.get("checks", [])
            if checks:
                lines.append("### Checks")
                for check in checks:
                    lines.extend([f"Objective: {check['objective']}. Stakes: {check['stakes']}",
                                  f"Roll ({check['source']}): {check['roll']}; skill: {check['skill']}; "
                                  f"modifier: {check['modifier']:+d}; total: {check['total']}; "
                                  f"target: {check['target']}; margin: {check['margin']:+d}."])
            milestones = payload.get("milestones", [])
            if milestones:
                lines.append("### Milestones")
                for milestone in milestones:
                    references = ", ".join(str(turn) for turn in milestone["evidence_turns"])
                    lines.append(f"At {_duration(milestone['elapsed_seconds'])} into this turn: "
                                 f"{milestone['basis']} Evidence turns: {references}.")
            processed = payload.get("processed_tasks", {})
            if processed:
                lines.append("### Addressed deadlines\n\n" +
                             "\n".join(f"- {key}: {value}" for key, value in sorted(processed.items())))
            coverage = payload.get("coverage", {})
            if coverage:
                lines.append("### Record review\n\n| Record | Result | Basis |\n| --- | --- | --- |\n" +
                             "\n".join(f"| {_cell(key.capitalize())} | {item['status']} | {_cell(item['basis'])} |"
                                       for key, item in coverage.items()))
            if payload.get("review") is not None:
                lines.append(_review_note(payload["review"]))
            lines.append(f"Source event hash: `{event['hash']}`.")
    return "\n\n".join(lines) + "\n"


def _resume(events: list[dict]) -> str:
    if not events:
        return (
            "Awaiting setup. No initialized character state, resolved turn, or pending action is recorded in the ledger.\n\n"
            "Read AGENTS.md, rules/iron_engine.md, and docs/play_workflow.md. Validate the selected campaign store, "
            "then read any supplied starting character sheet in the selected story's root folder and establish only "
            "the missing setup details with the player. Examples and tests are not campaign facts.\n"
        )
    state = events[-1]["state"]
    character = state["character"]
    lines = [f"Current turn: {state['turn']}. Fictional time: {_time(state['time_seconds'])}.",
             f"Phase: {state['phase']}. Location: {state['location']}.",
             f"Character: {character['name']}. Aim: {character['aim']}",
             f"Age: {character['age']}. Condition: {condition_summary(character)}.",
             f"Spoiler cutoff: {state['campaign']['spoiler_cutoff']}. Resolution: {state['campaign']['resolution_mode']}.",
             "## Pending decision or fixed stakes", state["resume_note"] or "No pending resume note is recorded.",
             "## Interrupted plan"]
    if "condition" in character:
        condition = character["condition"]
        lines.insert(4, f"Condition tags: {'; '.join(condition['tags'])}. Basis: {condition['basis']}")
    plan = state["interrupted_plan"]
    if plan is None:
        lines.append("No interrupted plan is recorded.")
    else:
        lines.append(f"Objective: {plan['objective']}")
        if plan["endpoint_seconds"] is not None:
            lines.append(f"Planned endpoint: {_time(plan['endpoint_seconds'])}.")
        if plan["remaining_seconds"] is not None:
            lines.append(f"Recorded time remaining: {_duration(plan['remaining_seconds'])}.")
        lines.append("Stopping conditions:\n\n" + ("\n".join(f"- {item}" for item in plan["stopping_conditions"]) or "None recorded."))
    lines.extend(["## Obligations", "\n".join(f"- {item}" for item in state["obligations"]) or "None recorded.", "## Tasks"])
    if not state["tasks"]:
        lines.append("None recorded.")
    for task in state["tasks"]:
        due = "no deadline" if task["due_seconds"] is None else _time(task["due_seconds"])
        lines.append(f"- {task['id']} [{task['status']}]: {task['description']}. Due: {due}. Note: {task['note'] or 'None recorded.'}")
    lines.extend(["## Continuing world", "[All persistent records](world.md) and [active and closed threads](threads.md). "
                  "Use the focused context packet to inspect relevant records and every open deadline before advancing."])
    lines.append("## Continue")
    if not state["alive"]:
        lines.append(f"This character is dead: {state['death']['cause']} at {_time(state['death']['time_seconds'])}. "
                     "Do not advance this character or reverse the death. A successor requires an agreed separate setup.")
    lines.append(
        "Read AGENTS.md, rules/iron_engine.md, and docs/play_workflow.md. The context command validates the entire "
        "canonical event chain internally and returns current state, obligations, record references, and recent scenes. "
        "Retrieve relevant records and older turns on demand before resolving the next authorized action. "
        "Check the current head against this view, load the current sheet, "
        "and reconcile all pending obligations and decisions. Research notes do not grant character knowledge. "
        "Continue from recorded facts; do not invent a missing chat history or advance time merely by opening this file."
    )
    return "\n\n".join(lines) + "\n"


def _record_body(record_id: str, record: dict) -> str:
    lines = [f"### {record_id}: {record['title']}",
             f"Kind: {record['kind']}. Status: {record['status']}.", record["summary"]]
    for label in ("participants", "links", "known_by", "evidence_turns"):
        entries = record.get(label, [])
        lines.append(f"{label.replace('_', ' ').capitalize()}: " +
                     (", ".join(str(entry) for entry in entries) or "none recorded"))
    due = record.get("due_seconds")
    lines.append("Due: " + (_time(due) if due is not None else "not scheduled"))
    for key, value in sorted(record.get("details", {}).items()):
        lines.append(f"- {key}: {value}")
    return "\n\n".join(lines)


def _world(events: list[dict]) -> str:
    if not events:
        return "Awaiting setup. No world records are established.\n"
    state = events[-1]["state"]
    records = state.get("world", {}).get("records", {})
    lines = ["All persistent world records, including closed matters. Missing records remain unknown."]
    if not records:
        lines.append("No structured world records are established.")
    for record_id, record in sorted(records.items()):
        lines.append(_record_body(record_id, record))
    for field in ("relationships", "knowledge", "assumptions", "standing_orders"):
        lines.extend([f"## {field.replace('_', ' ').capitalize()}",
                      "\n".join(f"- {item}" for item in state[field]) or "None recorded."])
    lines.extend(["## Research", "Sources support these records; a source is not automatically character knowledge."])
    for source in state["research"]:
        lines.extend([f"### {source['id']}", source["claim"], f"Source: {source['source']}",
                      f"Scope: {source['scope']}", f"Confidence: {source['confidence']}",
                      f"Limits: {source['limitations']}"])
    if not state["research"]:
        lines.append("No research sources are recorded.")
    return "\n\n".join(lines) + "\n"


def _threads(events: list[dict]) -> str:
    if not events:
        return "Awaiting setup. No obligations, tasks, or continuing threads are established.\n"
    state = events[-1]["state"]
    lines = ["## Obligations", "\n".join(f"- {item}" for item in state["obligations"]) or "None recorded.",
             "## Standing orders", "\n".join(f"- {item}" for item in state["standing_orders"]) or "None recorded."]
    for label, active in (("Active and blocked", True), ("Closed", False)):
        lines.append(f"## {label}")
        entries = []
        for task in state["tasks"]:
            if (task["status"] in {"active", "blocked"}) == active:
                due = _time(task["due_seconds"]) if task["due_seconds"] is not None else "not scheduled"
                entries.append(f"- Task {task['id']} [{task['status']}]: {task['description']}. Due: {due}. "
                               f"{task['note']}")
        for record_id, record in sorted(state.get("world", {}).get("records", {}).items()):
            if record["kind"] not in {"thread", "project", "journey"}:
                continue
            if (record["status"] in {"active", "blocked"}) == active:
                due = _time(record["due_seconds"]) if record["due_seconds"] is not None else "not scheduled"
                entries.append(f"- {record_id} [{record['status']}]: {record['title']}. {record['summary']} "
                               f"Due: {due}. Full record: [world.md](world.md).")
        lines.append("\n".join(entries) or "None recorded.")
    plan = state["interrupted_plan"]
    if plan is not None:
        lines.extend(["## Interrupted plan", _value(plan)])
    return "\n\n".join(lines) + "\n"


def _decisions(events: list[dict]) -> str:
    if not events:
        return "Awaiting setup. No player decisions have been accepted.\n"
    lines = ["Derived from accepted turn events. This is an index, not a second source of truth."]
    resolved = [event for event in events if event["kind"] in TURN_KINDS]
    if not resolved:
        lines.append("No resolved player decisions yet. Turn 0 is setup, not a resolved action.")
    for event in resolved:
        payload, state = event["input"], event["state"]
        lines.extend([f"## Turn {state['turn']} | {_time(state['time_seconds'])}",
                      f"Objective: {payload['objective']}",
                      f"Outcome: {payload['outcome']}"])
        authorization = payload.get("authorization")
        if authorization is not None:
            lines.append(f"Authorized scope: up to {_duration(authorization['max_elapsed_seconds'])}; "
                         f"stop condition: {authorization['stop_condition']}")
        if payload.get("next_decision"):
            lines.append(f"Pending next decision: {payload['next_decision']}")
        lines.append(f"Source event hash: `{event['hash']}`.")
    return "\n\n".join(lines) + "\n"


def _latest(events: list[dict]) -> str:
    if not events:
        return "Awaiting setup. Read the supplied starting character sheet and establish missing setup details. " \
               "No opening scene or resolved turn has been invented.\n"
    indices = [index for index, event in enumerate(events) if event["kind"] in TURN_KINDS]
    if indices:
        index = indices[-1]
        return _turn_scene(events[index], events[index - 1]["state"]) + "\n"
    return _opening(events) + "\n"


def _landing(events: list[dict], seed_reference: str) -> str:
    lines = ["[Latest scene](latest.md) · [Character sheet](character-sheet.md) · [Resume](resume.md) · "
             "[Changes and assessments](changes.md) · [Decisions](decisions.md) · [Threads](threads.md) · "
             "[World](world.md) · [Complete reading history](story.md)"]
    if not events:
        lines.extend(["Awaiting setup. No campaign has been initialized and no opening narrative or turn is recorded.",
                      f"Read the supplied [starting character sheet]({seed_reference}), if provided. "
                      "It is preparation until an agreed setup is accepted."])
    else:
        state = events[-1]["state"]
        condition = state["character"].get("condition")
        health = condition["rating"] if condition is not None else "Not established"
        lines.extend([f"Campaign: {state['campaign']['title']}",
                      f"{state['character']['name']} | Age {state['character']['age']} | "
                      f"Condition: {health} | {state['location']}",
                      f"Turn {state['turn']} | {_time(state['time_seconds'])} | {state['phase']}"])
    lines.append("## Saved turns")
    entries = [f"- [Turn {event['state']['turn']}](turns/turn-{event['state']['turn']:06d}.md): "
               f"{_time(event['state']['time_seconds'])}; {event['state']['location']}"
               for event in events if event["kind"] in TURN_KINDS]
    if _opening_event(events) is not None:
        entries.insert(0, "- [Turn 0: opening](turns/turn-000000.md)")
    lines.append("\n".join(entries) or "No resolved turns.")
    return "\n\n".join(lines) + "\n"


def _safe_directory(path: str | os.PathLike, store: CampaignStore) -> Path:
    try:
        raw = os.fspath(path)
        if not isinstance(raw, str) or not raw.strip() or "\x00" in raw:
            raise CampaignError("Render output must be a nonempty valid directory path")
        raw.encode("utf-8")
        output = Path(raw).expanduser()
        if ".." in output.parts:
            raise CampaignError("Parent traversal is not allowed in render output paths")
        output = output.absolute()
        if output == store.path or store.path in output.parents or "events" in output.parts:
            raise CampaignError("Rendered views must be outside campaign stores and events directories")
        for part in reversed((output, *output.parents)):
            if part.is_symlink():
                raise CampaignError("Symbolic links are not allowed in render output paths")
        if output.exists() and not output.is_dir():
            raise CampaignError("Render output must be a directory")
        if (output / "events").exists() or (output / "events").is_symlink():
            raise CampaignError("Render output cannot be a directory containing an event store")
        return output
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        if isinstance(exc, CampaignError):
            raise
        raise CampaignError(f"Invalid render output path: {exc}") from exc


def _existing_generated(path: Path, filename: str) -> bytes | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise CampaignError(f"Render destination must be a regular unlinked file: {path}")
    data = path.read_bytes()
    if not data.startswith((_marker(filename) + "\n").encode("utf-8")):
        raise CampaignError(f"Refusing to overwrite a file not generated by Iron Engine: {path}")
    return data


def render_campaign(store: CampaignStore, output_dir: str | os.PathLike = "play") -> dict[str, Path]:
    """Write replaceable reading views, never changing canonical records or time.

    All destinations are checked before any file is published. Each replacement is
    atomic; the file set is not a transaction. Current views carry the latest hash.
    Historical turn pages carry only their accepted event hash and remain stable.
    """
    events = store.validate()
    output = _safe_directory(output_dir, store)
    head = events[-1]["hash"] if events else "awaiting-setup"
    records = Path(os.path.relpath(store.path / "events", output)).as_posix()
    sheet = render_character_sheet(events[-1]["state"]) if events else (
        "Awaiting setup. No initialized character state is stored in the ledger. Consult any supplied starting "
        "character sheet in the selected story's root folder; it remains preparation until setup is accepted.\n"
    )
    seed_reference = Path(os.path.relpath(store.path.parent / "character-sheet.md", output)).as_posix()
    bodies = {"story.md": ("Campaign story", _story(events)),
              "character-sheet.md": ("Character sheet", sheet),
              "resume.md": ("Resume campaign", _resume(events)),
              "README.md": ("Read this story", _landing(events, seed_reference)),
              "latest.md": ("Latest scene and current record", _latest(events)),
              "threads.md": ("Threads and commitments", _threads(events)),
              "world.md": ("Persistent world records", _world(events)),
              "decisions.md": ("Decision index", _decisions(events)),
              "changes.md": ("Changes and assessments", _changes(events))}
    contents = {name: ((_story_header(name, head) if name in {"story.md", "latest.md"}
                        else _story_header(name, head) + f"# {title}\n\n" if name in {"character-sheet.md", "README.md"}
                        else _header(name, title, head, records)) + body).encode("utf-8")
                for name, (title, body) in bodies.items()}
    opening_event = _opening_event(events)
    if opening_event is not None:
        name = "turns/turn-000000.md"
        contents[name] = (_story_header(name, opening_event["hash"]) + _opening(events) + "\n").encode("utf-8")
    for index, event in enumerate(events):
        if event["kind"] not in TURN_KINDS:
            continue
        turn = event["state"]["turn"]
        name = f"turns/turn-{turn:06d}.md"
        body = _turn_scene(event, events[index - 1]["state"]) + "\n"
        contents[name] = (_story_header(name, event["hash"]) + body).encode("utf-8")
    files = {name: output / name for name in contents}
    staging = []
    try:
        # Inspect every parent and destination before publishing any view.
        for parent in {path.parent for path in files.values()}:
            _safe_directory(parent, store)
        prior = {name: _existing_generated(path, name) for name, path in files.items()}
        output.mkdir(parents=True, exist_ok=True)
        for name, data in contents.items():
            if data == prior[name]:
                continue
            parent = _safe_directory(files[name].parent, store)
            parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(dir=parent, prefix=".iron-view-")
            temporary = Path(temporary)
            staging.append(temporary)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            _safe_directory(parent, store)
            current = _existing_generated(files[name], name)
            if current != prior[name]:
                raise CampaignError("A render destination changed during export; inspect and render again")
            if current is None:
                os.link(temporary, files[name])
            else:
                os.replace(temporary, files[name])
        return files
    except OSError as exc:
        raise CampaignError(f"Could not render campaign views: {exc}") from exc
    finally:
        for temporary in staging:
            temporary.unlink(missing_ok=True)
