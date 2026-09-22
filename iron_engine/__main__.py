"""Command-line access to the local campaign ledger."""

import argparse
import json
import secrets
import sys

from .engine import CampaignError, CampaignStore, character_sheet, read_json
from .travel import TravelError, load_catalog


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Iron Engine player-safe campaign ledger")
    parser.add_argument("--store", default="campaign", help="Campaign event directory (default: campaign)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "turn", "research", "correct", "checkpoint", "restore"):
        child = subparsers.add_parser(command)
        child.add_argument("input", help="JSON input file")
    subparsers.add_parser("validate")
    subparsers.add_parser("status")
    subparsers.add_parser("head", help="Print the latest event hash for expected_hash")
    save = subparsers.add_parser("save")
    save.add_argument("output", help="New save filename, outside the event store")
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
            command.add_argument("--profile", help="Explicit road-party profile from travel-profiles")
            command.add_argument("--pace", choices=("slow", "average", "fast_unconditioned", "fast_conditioned"))
            command.add_argument("--rate-mpd", type=float, help="Explicit miles-per-day assumption, required for sea or raven")
            command.add_argument("--rest-days", type=float, default=0, help="Additional stationary days")
            command.add_argument("--speed-multiplier", dest="multiplier", type=float, default=1,
                                 help="Positive multiplier applied to movement speed")
            command.add_argument("--endurance-assumption", help="GM justification for a long fast-pace estimate")
    args = parser.parse_args(argv)
    try:
        if args.command in ("travel-profiles", "distance", "travel"):
            catalog = load_catalog()
            if args.command == "travel-profiles":
                result = {"profiles": catalog.profiles, "catalog": catalog.summary}
            elif args.command == "distance":
                result = catalog.lookup(args.mode, args.origin, args.destination)
            else:
                result = catalog.estimate(args.mode, args.origin, args.destination,
                    rate_mpd=args.rate_mpd, profile=args.profile, pace=args.pace,
                    rest_days=args.rest_days, multiplier=args.multiplier,
                    endurance_assumption=args.endurance_assumption)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "roll":
            if not 2 <= args.sides <= 1_000_000 or not 1 <= args.count <= 100:
                raise CampaignError("Roll requires 2..1000000 sides and 1..100 dice")
            print(json.dumps({"sides": args.sides, "rolls": [secrets.randbelow(args.sides) + 1 for _ in range(args.count)],
                              "note": "Public helper only. Fix stakes before rolling; rerolls are not prevented."}))
            return 0
        store = CampaignStore(args.store)
        if args.command == "validate":
            events = store.validate()
            if events:
                print(f"Valid: {len(events)} events; turn {events[-1]['state']['turn']}; latest hash {events[-1]['hash']}")
            else:
                print("Awaiting setup: no campaign events.")
        elif args.command == "status":
            events = store.validate()
            print(character_sheet(events[-1]["state"]) if events else "Awaiting setup: no character or Turn 1 exists yet.")
        elif args.command == "head":
            print(store.head())
        elif args.command == "save":
            print(f"Saved: {store.export_save(args.output)}")
        elif args.command == "restore":
            state = store.restore_save(args.input)
            print(f"Restored campaign at turn {state['turn']}.")
        else:
            method = {"init": store.initialize, "turn": store.commit_turn,
                      "research": store.add_research, "correct": store.correct,
                      "checkpoint": store.checkpoint}[args.command]
            event = method(read_json(args.input))
            print(json.dumps({"sequence": event["sequence"], "turn": event["state"]["turn"],
                              "kind": event["kind"], "request_id": event["request_id"], "hash": event["hash"]},
                             ensure_ascii=False, sort_keys=True))
        return 0
    except (CampaignError, TravelError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
