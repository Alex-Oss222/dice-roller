"""Explicit story directories with a pinned, shared rules/reference baseline."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile

from .engine import (CampaignError, CampaignStore, _canonical, _integer, _object, _publish, _safe_path,
                     _string, _sync_directory, _validate_events, read_json)
from .journal import render_campaign


PROJECT_ROOT = Path(__file__).parent.parent
FIXED_SHARED = {
    "AGENTS.md", "data/travel_distances.json", "references/books.md", "docs/research.md",
    "docs/play_workflow.md", "docs/record_contract.md", "docs/travel.md",
    "templates/advance.json", "templates/turn-output.md",
}
STORY_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}\Z", re.ASCII)
SHARED_MODULE = re.compile(r"(?:iron_engine/[A-Za-z0-9_-]+\.py|rules/[A-Za-z0-9_-]+\.md)\Z", re.ASCII)
DIGEST = re.compile(r"[a-f0-9]{64}\Z", re.ASCII)


def project_root(root=None):
    return _safe_path(PROJECT_ROOT if root is None else root)


def _identifier(value):
    if not isinstance(value, str) or STORY_ID.fullmatch(value) is None:
        raise CampaignError("Story ID must contain 1..64 lowercase ASCII letters, digits, or hyphens, starting with a letter or digit")
    return value


def _bytes(path):
    path = _safe_path(path)
    descriptor = None
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise CampaignError(f"Expected a regular file: {path}")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            return stream.read()
    except OSError as exc:
        raise CampaignError(f"Could not read story/reference file {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _shared_paths(root):
    paths = set(FIXED_SHARED)
    try:
        for directory, extension in (("iron_engine", "*.py"), ("rules", "*.md")):
            parent = _safe_path(root / directory)
            if parent.exists():
                for path in parent.glob(extension):
                    relative = path.relative_to(root).as_posix()
                    if SHARED_MODULE.fullmatch(relative) is None:
                        raise CampaignError(f"Unsupported shared source filename: {relative}")
                    paths.add(relative)
    except OSError as exc:
        raise CampaignError(f"Could not inspect shared source paths: {exc}") from exc
    return paths


def _snapshot(root):
    paths = _shared_paths(root)
    if not any(name.startswith("iron_engine/") for name in paths) or not any(name.startswith("rules/") for name in paths):
        raise CampaignError("Story creation requires the shared engine modules and rules Markdown files")
    return {name: hashlib.sha256(_bytes(root / name)).hexdigest() for name in sorted(paths)}


def _digest(value, label):
    _string(value, label)
    if DIGEST.fullmatch(value) is None:
        raise CampaignError(f"{label} must be a lowercase SHA-256 digest")


class Story:
    """An existing story's paths, identity, and original shared-source baseline."""

    def __init__(self, story_id, *, root=None):
        self.id = _identifier(story_id)
        self.root = project_root(root)
        self.path = _safe_path(self.root / "stories" / self.id)
        self.play_path = _safe_path(self.path / "play")
        self.character_sheet_path = _safe_path(self.path / "character-sheet.md")
        self.store = CampaignStore(self.path / "campaign")
        self.manifest = read_json(self.path / "story.json")
        _object(self.manifest, "story manifest", {"schema_version", "story_id", "character_sheet_sha256", "shared_files"})
        _integer(self.manifest["schema_version"], "story schema_version", 1, 1)
        if self.manifest["story_id"] != self.id:
            raise CampaignError("Story manifest identity does not match its selected directory")
        _digest(self.manifest["character_sheet_sha256"], "Imported character sheet digest")
        shared = _object(self.manifest["shared_files"], "shared_files")
        if not FIXED_SHARED <= set(shared):
            raise CampaignError("Story manifest omits a required shared reference")
        if not any(name.startswith("iron_engine/") for name in shared) or not any(name.startswith("rules/") for name in shared):
            raise CampaignError("Story manifest must pin engine modules and rule files")
        for name, digest in shared.items():
            if name not in FIXED_SHARED and SHARED_MODULE.fullmatch(name) is None:
                raise CampaignError(f"Unsafe or unsupported shared manifest path: {name}")
            _digest(digest, f"shared_files.{name}")

    def baseline_mismatches(self):
        mismatches = []
        try:
            current = _shared_paths(self.root)
        except CampaignError as exc:
            current = set()
            mismatches.append(str(exc))
        pinned = self.manifest["shared_files"]
        for name in sorted(current - set(pinned)):
            mismatches.append(f"added shared file: {name}")
        for name, digest in pinned.items():
            try:
                actual = hashlib.sha256(_bytes(self.root / name)).hexdigest()
            except CampaignError:
                mismatches.append(f"missing or unsafe shared file: {name}")
                continue
            if actual != digest:
                mismatches.append(f"changed shared file: {name}")
        return mismatches

    def require_current_baseline(self):
        mismatches = self.baseline_mismatches()
        if mismatches:
            raise CampaignError("Story shared baseline differs; mutation/estimation is blocked until an explicitly reviewed baseline upgrade: "
                                + "; ".join(mismatches))

    def _identity(self, state):
        state = _object(state, "story campaign state")
        campaign = _object(state.get("campaign"), "story campaign metadata")
        if campaign.get("id") != self.id:
            raise CampaignError(f"Campaign id must equal the selected story id '{self.id}'")

    def validate(self):
        events = self.store.validate()
        for event in events:
            self._identity(event["state"])
        return events

    def check_setup(self, payload):
        self.require_current_baseline()
        self.validate()
        # The imported digest is provenance, not an edit lock. Preparation can be
        # filled before setup; only the accepted event establishes campaign truth.
        _bytes(self.character_sheet_path)
        payload = _object(payload, "setup input")
        self._identity(payload.get("state"))
        if "opening_narrative" in payload:
            opening_path = _safe_path(self.path / "opening.md")
            if not opening_path.exists():
                raise CampaignError("Prepared setup with opening_narrative requires story opening.md")
            try:
                opening = _bytes(opening_path).decode("utf-8").rstrip("\n")
            except UnicodeError as exc:
                raise CampaignError("Story opening.md must be UTF-8 text") from exc
            if opening != payload["opening_narrative"].rstrip("\n"):
                raise CampaignError("story opening.md must exactly mirror setup.json opening_narrative")

    def start(self):
        """Accept the staged opening once, or resume without resetting the story."""
        self.require_current_baseline()
        events = self.validate()
        if events:
            event = events[-1]
        else:
            payload = read_json(self.path / "setup.json")
            self.check_setup(payload)
            event = self.store.initialize(payload)
        try:
            render_campaign(self.store, self.play_path)
        except CampaignError as exc:
            raise CampaignError(f"Setup/state is saved at {event['hash']}; repair reading output and run render. {exc}") from exc
        return event

    def check_restore(self, path):
        self.require_current_baseline()
        self.validate()
        wrapper = read_json(path)
        _object(wrapper, "story save")
        if "story_save_version" not in wrapper:
            raise CampaignError("Story restore requires a versioned story save including its shared baseline; "
                                "use an explicit --store outside stories/ for a legacy engine-only save")
        _object(wrapper, "story save", {"story_save_version", "story_id", "shared_files", "campaign_save"})
        _integer(wrapper["story_save_version"], "story_save_version", 1, 1)
        if wrapper["story_id"] != self.id:
            raise CampaignError("Story save identity does not match the selected story")
        shared = _object(wrapper["shared_files"], "story save shared_files")
        if shared != self.manifest["shared_files"]:
            raise CampaignError("Story save shared baseline differs from the destination story; "
                                "retain the matching project/Git version rather than silently adopting new sources")
        bundle = wrapper["campaign_save"]
        _object(bundle, "save", {"schema_version", "events"})
        _integer(bundle["schema_version"], "save.schema_version", 1, 1)
        events = _validate_events(bundle["events"])
        if not events:
            raise CampaignError("Save has no setup event")
        for event in events:
            self._identity(event["state"])
        return bundle

    def export_save(self, filename):
        events = self.validate()
        if not events:
            raise CampaignError("Cannot export a story awaiting setup")
        output = self.save_path(filename)
        wrapper = {"story_save_version": 1, "story_id": self.id,
                   "shared_files": self.manifest["shared_files"],
                   "campaign_save": {"schema_version": 1, "events": events}}
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _publish(output, _canonical(wrapper) + b"\n", output.parent)
            return output
        except FileExistsError as exc:
            raise CampaignError("Story save destination already exists; choose a new filename") from exc
        except OSError as exc:
            raise CampaignError(f"Could not export story save: {exc}") from exc

    def restore_save(self, path):
        bundle = self.check_restore(path)
        temporary = None
        try:
            # Feed the exact checked bytes to restore even if the input is edited
            # between validation and publication; never import another identity.
            with tempfile.NamedTemporaryFile(dir=self.path, prefix=".checked-restore-", suffix=".json", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(json.dumps(bundle, ensure_ascii=False, allow_nan=False).encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            return self.store.restore_save(temporary)
        except OSError as exc:
            raise CampaignError(f"Could not stage checked story restore: {exc}") from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def save_path(self, filename):
        _string(filename, "save filename")
        if filename in {".", ".."} or "/" in filename or "\\" in filename or Path(filename).name != filename:
            raise CampaignError("Story saves take a filename only and stay inside the selected story's saves directory")
        return _safe_path(self.path / "saves" / filename)


def create_story(story_id, character_sheet, *, root=None, _continuity=None):
    """Create a new isolated preparation folder without initializing a PC or turn."""
    story_id, root = _identifier(story_id), project_root(root)
    imported = _bytes(character_sheet)
    try:
        imported.decode("utf-8")
    except UnicodeError as exc:
        raise CampaignError("Starting character sheet must be UTF-8 text") from exc
    manifest = {"schema_version": 1, "story_id": story_id,
                "character_sheet_sha256": hashlib.sha256(imported).hexdigest(), "shared_files": _snapshot(root)}
    stories = _safe_path(root / "stories")
    target = _safe_path(stories / story_id)
    lock, staging = stories / f".create-{story_id}.lock", None
    locked = False
    try:
        stories.mkdir(parents=True, exist_ok=True)
        _safe_path(lock).mkdir()
        locked = True
        if target.exists():
            raise CampaignError("Story directory already exists; creation never replaces it")
        staging = Path(tempfile.mkdtemp(dir=stories, prefix=f".prepare-{story_id}-"))
        for directory in ("campaign", "play", "saves", "notes"):
            (staging / directory).mkdir()
        scope = (f"# Scope: {story_id}\n\n"
                 "Read character-sheet.md first, then ../../AGENTS.md and the selected shared rules. "
                 "This folder is one independent story.\n\n"
                 f"Use `python -m iron_engine --story {story_id} ...` from the repository root. "
                 "Never write another story, the shared engine, rules, references, or travel data as a side effect of play.\n\n"
                 "Start with character-sheet.md. It is editable preparation until setup, not an initialized character. "
                 "Obtain only missing player details; never convert blanks into invented possessions or abilities. "
                 f"The accepted setup must use campaign.id `{story_id}`.\n\n"
                 "The campaign/events chain becomes authoritative after setup. play/ is generated reading material; "
                 "saves/ holds portable exports; notes/ is player-safe supporting material, never competing state. "
                 "Do not auto-apply later edits to the preparation sheet.\n\n"
                 "story.json pins the shared baseline. Drift blocks new results until a separately reviewed upgrade. "
                 "Do not silently edit baseline hashes. Its character-sheet hash records import provenance only.\n")
        files = {"character-sheet.md": imported,
                 "story.json": (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
                 "AGENTS.md": scope.encode("utf-8"),
                 "notes/README.md": ("# Story notes\n\nPlayer-safe preparation and supporting notes only. "
                                      "Accepted facts belong in campaign/events. These notes do not initialize or advance play.\n").encode("utf-8")}
        if _continuity is not None:
            files["notes/predecessor-world.json"] = (_canonical(_continuity) + b"\n")
            files["notes/succession.md"] = (
                "# Continuing an existing world\n\n"
                f"Predecessor: `{_continuity['predecessor_story_id']}` at `{_continuity['predecessor_hash']}`.\n\n"
                "predecessor-world.json preserves the validated ending state and its source coordinates. "
                "The predecessor remains dead. This preparation has no initialized character or turns.\n\n"
                "Use the supplied new character sheet. Keep the same world clock and surviving world consequences "
                "when preparing setup. Record campaign.world_id, predecessor_story_id and predecessor_hash. "
                "Carry each relevant world record explicitly with its original source and turn references in details; "
                "use evidence_turns [0] for the accepted inherited setup. Replace predecessor 'pc' references with "
                "an explicit person ID. Review known_by for the new viewpoint. A new PC receives only justified "
                "knowledge, property, authority, relationships and personal obligations; none transfer automatically. "
                "World deadlines continue at the same time_seconds. Pending institutions and projects survive even "
                "when outside the new character's control. Do not import previous PC tasks as personal duties without basis.\n\n"
                "Accept setup only after this mapping is checked. Normal create-story remains independent.\n"
            ).encode("utf-8")
        for relative, contents in files.items():
            with (staging / relative).open("xb") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
        render_campaign(CampaignStore(staging / "campaign"), staging / "play")
        _sync_directory(staging)
        _safe_path(target)
        if target.exists():
            raise CampaignError("Story directory appeared during creation; nothing was replaced")
        os.rename(staging, target)
        staging = None
        _sync_directory(stories)
        return target
    except OSError as exc:
        raise CampaignError(f"Could not create a new story: {exc}") from exc
    finally:
        if staging is not None:
            shutil.rmtree(staging)
        if locked:
            lock.rmdir()


def create_successor(story_id, character_sheet, predecessor_id, *, root=None):
    """Preserve a dead predecessor's world for an explicit new-character setup."""
    predecessor = Story(predecessor_id, root=root)
    predecessor.require_current_baseline()
    events = predecessor.validate()
    if not events or events[-1]["state"]["alive"]:
        raise CampaignError("A successor requires an initialized, deceased predecessor; use create-story for an independent character")
    final = events[-1]
    continuity = {"predecessor_story_id": predecessor.id, "predecessor_hash": final["hash"],
                  "world_id": final["state"]["campaign"].get("world_id", predecessor.id),
                  "state": final["state"]}
    return create_story(story_id, character_sheet, root=predecessor.root, _continuity=continuity)
