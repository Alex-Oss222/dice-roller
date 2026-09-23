"""Command-line access to the local campaign ledger."""

import argparse
import json
import secrets
import sys

from .engine import CampaignError, CampaignStore, _safe_path, character_sheet, read_json
from .journal import render_campaign
from .stories import Story, create_story, create_successor, project_root
from .travel import TravelError, load_catalog


def main(argv=None, *, root=None) -> int:
    parser = argparse.ArgumentParser(description="Iron Engine player-safe campaign ledger")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--story", help="Explicit isolated story ID under stories/")
    selection.add_argument("--store", help="Explicit legacy campaign directory, outside stories/")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create-story", help="Create a character-first preparation folder without initializing a campaign")
    create.add_argument("story_id")
    create.add_argument("--character-sheet", required=True, help="Starting UTF-8 character sheet to import")
    successor = subparsers.add_parser("create-successor", help="Prepare an explicit continuation after a predecessor's death, without starting play")
    successor.add_argument("story_id")
    successor.add_argument("--from-story", required=True)
    successor.add_argument("--character-sheet", required=True)
    subparsers.add_parser("start", help="Accept this story's prepared setup and opening once; otherwise resume its saved state")
    for command in ("init", "advance", "turn", "research", "correct", "checkpoint", "restore"):
        child = subparsers.add_parser(command)
        child.add_argument("input", help="JSON input file")
    context = subparsers.add_parser("context", help="Validate history and load a focused continuation packet")
    context.add_argument("--focus", action="append", default=[])
    context.add_argument("--recent", type=int, default=2)
    context.add_argument("--max-chars", type=int, default=12000)
    record = subparsers.add_parser("record", help="Retrieve one full world record by stable ID")
    record.add_argument("record_id")
    records = subparsers.add_parser("records", help="Search and page through world-record indexes")
    records.add_argument("--query", default="")
    records.add_argument("--kind")
    records.add_argument("--status")
    records.add_argument("--offset", type=int, default=0)
    records.add_argument("--limit", type=int, default=25)
    history = subparsers.add_parser("history", help="Retrieve one saved turn without loading the entire journal")
    history.add_argument("--turn", type=int, required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("status")
    subparsers.add_parser("head", help="Print the latest event hash for expected_hash")
    save = subparsers.add_parser("save")
    save.add_argument("output", help="With --story: a filename within its saves/. With --store: an explicit new save path")
    render = subparsers.add_parser("render", help="Generate story, character sheet, and resume views without advancing play")
    render.add_argument("--output", help="Required with --store; --story always uses its own play/ directory")
    roll = subparsers.add_parser("roll", help="Public random-number helper; does not save or advance state")
    roll.add_argument("--sides", type=int, default=20)
    roll.add_argument("--count", type=int, default=1)
    subparsers.add_parser("travel-profiles", help="List the source's labeled road-travel profiles")
    for name in ("distance", "travel"):
        command = subparsers.add_parser(name, help="Read sourced distance or estimate time without advancing play")
        command.add_argument("--mode", choices=("road", "sea", "raven"), required=True)
        command.add_argument("--from", dest="origin", required=True)
        command.add_argument("--to", dest="destination", required=True)
        if name == "travel":
            command.add_argument("--profile", action="append", help="Applicable road-party profile; repeat for a mixed party")
            command.add_argument("--pace", choices=("slow",), help="Slow is always used for story estimates")
            command.add_argument("--rate-mpd", type=float, help="Explicit miles-per-day assumption, required for sea or raven")
            command.add_argument("--rate-basis", help="Source or conservative assumption for a sea/raven rate")
            command.add_argument("--delay-basis", help="Reason for additional stationary days")
            command.add_argument("--condition-basis", help="Reason for any additional speed reduction")
            command.add_argument("--rest-days", type=float, default=0, help="Additional stationary days")
            command.add_argument("--speed-multiplier", dest="multiplier", type=float, default=1,
                                 help="Movement multiplier greater than zero and no greater than one")
    args = parser.parse_args(argv)
    try:
        selected_root = project_root(root)

        def legacy_path(path):
            result = _safe_path(path)
            stories_root = selected_root / "stories"
            if result == stories_root or stories_root in result.parents:
                raise CampaignError("Use --story for paths inside stories/; legacy routing cannot write another story")
            return result

        if args.command in {"create-story", "create-successor"}:
            if args.story is not None or args.store is not None:
                raise CampaignError("Story creation takes its own new ID; do not combine it with --story or --store")
            path = (create_story(args.story_id, args.character_sheet, root=selected_root)
                    if args.command == "create-story" else
                    create_successor(args.story_id, args.character_sheet, args.from_story, root=selected_root))
            print(f"Created preparation: {path}. Character first; no campaign or Turn 1 has been initialized.")
            return 0
        story = Story(args.story, root=selected_root) if args.story is not None else None
        if story is not None:
            story.validate()
            mutations = {"start", "init", "advance", "turn", "research", "correct", "checkpoint", "restore"}
            if args.command in mutations | {"travel", "distance", "travel-profiles"}:
                story.require_current_baseline()
            else:
                mismatches = story.baseline_mismatches()
                if mismatches:
                    print("Warning: story shared baseline differs. Reading/exporting existing records only: "
                          + "; ".join(mismatches), file=sys.stderr)
        if args.command in ("travel-profiles", "distance", "travel"):
            catalog = load_catalog(selected_root / "data" / "travel_distances.json")
            if args.command == "travel-profiles":
                result = {"profiles": catalog.profiles, "catalog": catalog.summary}
            elif args.command == "distance":
                result = catalog.lookup(args.mode, args.origin, args.destination)
            else:
                result = catalog.estimate_slow(args.mode, args.origin, args.destination,
                    rate_mpd=args.rate_mpd, profile=args.profile, pace=args.pace,
                    rest_days=args.rest_days, multiplier=args.multiplier,
                    rate_basis=args.rate_basis, delay_basis=args.delay_basis,
                    condition_basis=args.condition_basis)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "roll":
            if not 2 <= args.sides <= 1_000_000 or not 1 <= args.count <= 100:
                raise CampaignError("Roll requires 2..1000000 sides and 1..100 dice")
            print(json.dumps({"sides": args.sides, "rolls": [secrets.randbelow(args.sides) + 1 for _ in range(args.count)],
                              "note": "Public helper only. Fix stakes before rolling; rerolls are not prevented."}))
            return 0
        if story is None and args.store is None:
            raise CampaignError("Select a story with --story ID or an explicit legacy directory with --store DIR; there is no default campaign")
        store = story.store if story is not None else CampaignStore(legacy_path(args.store))
        if args.command in {"context", "record", "records", "history"}:
            from .context import context_packet, history_packet, record_packet, record_index_packet
            if args.command == "context":
                result = context_packet(store, focus_ids=args.focus, recent_turns=args.recent, max_chars=args.max_chars)
            elif args.command == "record":
                result = record_packet(store, args.record_id)
            elif args.command == "records":
                result = record_index_packet(store, query=args.query, kind=args.kind, status=args.status,
                                             offset=args.offset, limit=args.limit)
            else:
                result = history_packet(store, args.turn)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "start":
            if story is None:
                raise CampaignError("start requires --story; legacy stores use an explicit init input")
            event = story.start()
            print(json.dumps({"story_id": story.id, "turn": event["state"]["turn"],
                              "hash": event["hash"], "read": str(story.play_path / "latest.md")}, sort_keys=True))
        elif args.command == "validate":
            events = store.validate()
            if events:
                print(f"Valid: {len(events)} events; turn {events[-1]['state']['turn']}; latest hash {events[-1]['hash']}")
            else:
                print("Awaiting setup: no campaign events.")
        elif args.command == "status":
            events = store.validate()
            print(character_sheet(events[-1]["state"]) if events else "Awaiting setup: no initialized character state or saved turns. Read the selected story's starting sheet.")
        elif args.command == "head":
            print(store.head())
        elif args.command == "save":
            output = story.export_save(args.output) if story is not None else store.export_save(legacy_path(args.output))
            print(f"Saved: {output}")
        elif args.command == "render":
            if story is not None:
                if args.output is not None:
                    raise CampaignError("Story render uses its own play/ directory; --output is only for explicit legacy stores")
                output = story.play_path
            else:
                if args.output is None:
                    raise CampaignError("Legacy render requires an explicit --output directory")
                output = legacy_path(args.output)
            for path in render_campaign(store, output).values():
                print(f"Rendered: {path}")
        elif args.command == "restore":
            state = story.restore_save(args.input) if story is not None else store.restore_save(args.input)
            if story is not None:
                render_campaign(store, story.play_path)
            print(f"Restored campaign at turn {state['turn']}.")
        else:
            method = {"init": store.initialize, "advance": store.advance, "turn": store.commit_turn,
                      "research": store.add_research, "correct": store.correct,
                      "checkpoint": store.checkpoint}[args.command]
            payload = read_json(args.input)
            if story is not None and args.command == "init":
                story.check_setup(payload)
            event = method(payload)
            if story is not None:
                try:
                    render_campaign(store, story.play_path)
                except CampaignError as exc:
                    raise CampaignError(f"Event accepted at {event['hash']}, but reading views could not refresh. "
                                        f"Fix the output problem and run render; do not replay the action. {exc}") from exc
            if args.command in {"advance", "turn"}:
                words = len(payload["narrative"].split())
                note = (" Substantial scenes usually run 600 to 1,200 words; this is guidance, not a limit."
                        if words < 600 or words > 1200 else "")
                print(f"narrative: {words} words.{note}", file=sys.stderr)
            print(json.dumps({"sequence": event["sequence"], "turn": event["state"]["turn"],
                              "story_id": event["state"]["campaign"]["id"],
                              "kind": event["kind"], "request_id": event["request_id"], "hash": event["hash"]},
                             ensure_ascii=False, sort_keys=True))
        return 0
    except (CampaignError, TravelError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
