"""Deterministic, disposable reading views of the validated campaign event chain."""

import json
import os
from pathlib import Path
import stat
import tempfile

from .engine import CampaignError, CampaignStore, character_sheet
from .condition import condition_summary


FILENAMES = ("story.md", "character-sheet.md", "resume.md")


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


def _header(filename: str, title: str, head: str, records: str) -> str:
    return (
        f"{_marker(filename)}\n"
        f"<!-- source-event-hash:{head} -->\n\n"
        f"# {title}\n\n"
        "Generated reading view. The immutable event chain is authoritative; regenerate this file instead of editing it.\n\n"
        f"Source event hash: `{head}`. Compare with the ledger's current `head` to detect a stale view.\n\n"
        f"Canonical records, relative to this directory: `{records}`.\n\n"
    )


def _turn_ledger(before: dict, after: dict, payload: dict) -> str:
    """A changed-only reading view, derived from the accepted event and evidence."""
    lines = []
    for unit, delta in sorted(payload["resources_delta"].items()):
        opening, closing = before["resources"][unit], after["resources"][unit]
        if delta and opening != closing:
            lines.append(f"- {unit}: {opening} → {closing} ({delta:+d}). "
                         f"Evidence: {payload['evidence']['resources.' + unit]}")
    for field in sorted(payload["changes"]):
        if before[field] == after[field]:
            continue
        evidence = payload["evidence"][field]
        if field == "character":
            old_character, character = before[field], after[field]
            if old_character.get("condition") != character.get("condition"):
                condition = character["condition"]
                lines.append(f"- Condition: {condition_summary(old_character)} → {condition_summary(character)}. "
                             f"Tags: {'; '.join(condition['tags'])}. Basis: {condition['basis']} "
                             f"Evidence: {evidence}")
            changed_keys = sorted(key for key in set(old_character) | set(character)
                                  if key != "condition" and old_character.get(key) != character.get(key))
            if changed_keys:
                labels = ", ".join(key.replace("_", " ") for key in changed_keys)
                lines.append(f"- Character ({labels}): updated. Evidence: {evidence}")
            continue
        label = field.replace("_", " ").capitalize()
        if field in {"location", "phase"}:
            change = f"{before[field]} → {after[field]}"
        elif field == "alive":
            label, change = "Life status", "living" if after[field] else "dead"
        elif field == "death":
            change = f"{after[field]['cause']} at {_time(after[field]['time_seconds'])}"
        else:
            change = "updated"
        lines.append(f"- {label}: {change}. Evidence: {evidence}")
    return "### Ledger\n\n" + "\n".join(lines) if lines else ""


def _story(events: list[dict]) -> str:
    if not events:
        return ("Awaiting setup. No character state has been initialized and no turns have been saved in the ledger. "
                "A supplied starting character sheet may exist in the selected story's root folder.\n")
    segments = [f"Campaign: {events[-1]['state']['campaign']['title']}"]
    if not any(event["kind"] == "turn" for event in events):
        segments.append("No turns have been resolved. Setup is recorded at Turn 0.")
    for index, event in enumerate(events):
        state, payload = event["state"], event["input"]
        if event["kind"] == "turn":
            before = events[index - 1]["state"]
            phase = state["phase"] if before["phase"] == state["phase"] else f"{before['phase']} → {state['phase']}"
            place = state["location"] if before["location"] == state["location"] else f"{before['location']} → {state['location']}"
            condition = state["character"].get("condition")
            condition_note = (f"Condition tags: {'; '.join(condition['tags'])}. Basis: {condition['basis']}\n\n"
                              if condition is not None and condition == before["character"].get("condition") else "")
            segments.append(
                f"## Turn {state['turn']}\n\n"
                f"Name: {state['character']['name']} | Age: {state['character']['age']} | "
                f"Condition: {condition_summary(state['character'])} | Location: {state['location']}\n\n"
                f"{_time(before['time_seconds'])} to {_time(state['time_seconds'])}. "
                f"Elapsed: {_duration(payload['elapsed_seconds'])}.\n\n"
                f"Phase: {phase}. Location: {place}.\n\n"
                + condition_note + payload["narrative"]
            )
            ledger = _turn_ledger(before, state, payload)
            if ledger:
                segments.append(ledger)
            if payload["review"] is not None:
                review = payload["review"]
                lines = [f"### OOC assessment: turns {review['from_turn']} to {review['to_turn']}",
                         "This assessment is recorded with the turn; it is separate from the accepted scene prose."]
                for category in ("results", "decisions", "capabilities", "position", "gm_consistency", "next_constraint"):
                    finding = review["findings"][category]
                    references = ", ".join(str(turn) for turn in finding["evidence_turns"])
                    lines.append(f"#### {category.replace('_', ' ').capitalize()}\n\n"
                                 f"{finding['assessment']}\n\nEvidence turns: {references}.")
                segments.append("\n\n".join(lines))
        elif event["kind"] == "correction":
            lines = [f"### OOC record note: correction at Turn {state['turn']}",
                     f"Event {event['sequence']}; {_time(state['time_seconds'])}. No fictional time elapsed.",
                     f"Reason: {payload['reason']}",
                     "This corrects the recorded state. Earlier accepted story text is preserved."]
            for field, value in sorted(payload["changes"].items()):
                lines.append(f"- Recorded {field}: {_value(value)}. Evidence: {payload['evidence'][field]}")
            for unit, delta in sorted(payload["resources_delta"].items()):
                lines.append(f"- Resource adjustment, {unit}: {delta:+d}; resulting balance: {state['resources'][unit]}. "
                             f"Evidence: {payload['evidence']['resources.' + unit]}")
            segments.append("\n\n".join(lines))
    return "\n\n".join(segments) + "\n"


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
    lines.append("## Continue")
    if not state["alive"]:
        lines.append(f"This character is dead: {state['death']['cause']} at {_time(state['death']['time_seconds'])}. "
                     "Do not advance this character or reverse the death. A successor requires an agreed separate setup.")
    lines.append(
        "Read AGENTS.md, rules/iron_engine.md, docs/play_workflow.md, and the entire validated canonical event chain "
        "before resolving the next authorized action. Check the current head against this view, load the current sheet, "
        "and reconcile all pending obligations and decisions. Research notes do not grant character knowledge. "
        "Continue from recorded facts; do not invent a missing chat history or advance time merely by opening this file."
    )
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
    """Write three replaceable views, never changing canonical records or time.

    All destinations are checked before any file is published. Each replacement is
    atomic; the three-file set is not a transaction. Every file carries its source
    hash, so interrupted renders remain recognizable and safe to repeat.
    """
    events = store.validate()
    output = _safe_directory(output_dir, store)
    head = events[-1]["hash"] if events else "awaiting-setup"
    records = Path(os.path.relpath(store.path / "events", output)).as_posix()
    sheet = (character_sheet(events[-1]["state"]).replace("\n", "  \n") + "\n") if events else (
        "Awaiting setup. No initialized character state is stored in the ledger. Consult any supplied starting "
        "character sheet in the selected story's root folder; it remains preparation until setup is accepted.\n"
    )
    bodies = {"story.md": ("Campaign story", _story(events)),
              "character-sheet.md": ("Character sheet", sheet),
              "resume.md": ("Resume campaign", _resume(events))}
    contents = {name: (_header(name, title, head, records) + body).encode("utf-8")
                for name, (title, body) in bodies.items()}
    files = {name: output / name for name in FILENAMES}
    staging = []
    try:
        prior = {name: _existing_generated(path, name) for name, path in files.items()}
        output.mkdir(parents=True, exist_ok=True)
        for name, data in contents.items():
            if data == prior[name]:
                continue
            fd, temporary = tempfile.mkstemp(dir=output, prefix=".iron-view-")
            temporary = Path(temporary)
            staging.append(temporary)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            _safe_directory(output, store)
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
