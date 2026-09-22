# The Iron Engine: shared rules, separate stories

A solo ASOIAF RPG with researched rulings, flexible turns, current character records, and evidence-based reviews every ten turns. Reusable engine, rules, and references form the shared base. Each character's story lives in its own folder, with its own history and saves.

Read [Start and continue](START_HERE.md) and [the story layout](stories/README.md). The prepared `story-001` folder contains the supplied Eddard Stark character seed for later play. No setup event or Turn 1 has been created.

The GM researches and resolves the fiction. Standard-library Python validates, records, and renders the results. No hosted runtime, database service, subscription, or background simulation is required. The existing [Star Wars browser dice roller](index.html) remains a separate tool with its original rules and no campaign-ledger integration.

## Shared base

- [Common play rules](rules/iron_engine.md), [Condition](rules/condition.md), [narrative guidance](rules/narrative.md), and the optional [Blood & Gold 0 to 9 capability module](rules/capabilities.md).
- [Book reference catalog and policy](references/books.md), [research guidance](docs/research.md), and [travel guidance](docs/travel.md).
- The [distance catalog](data/travel_distances.json) and other source data.
- [Engine](iron_engine/engine.py), [record contract](docs/record_contract.md), [tests](tests/test_engine.py), and blank [templates](templates/README.md).

The book catalog records references and source policy. It does not contain ebook texts or establish that the GM has read inaccessible sources. Each story independently selects permitted books, spoiler cutoff, resolution, and compatible capability rules.

## Separate stories

Every story has a root `character-sheet.md`, read first. Before initialization it can be completed with the player's agreed facts. After initialization it preserves starting input; current state comes from that story's accepted events and generated sheet.

Each story keeps its own NPCs, claims, outcomes, knowledge, assumptions, special agreements, notes, journal, and saves. A new story never inherits them from Story 1. A blocked road, detour, local price, invention, or source interpretation belongs in the selected story's notes and canonical assumptions/research, not in the common distance or book files. The [supplied-sheet audit](stories/story-001/notes/character-sheet-audit.md) concerns Story 1's input only.

A story's `story.json` pins shared file hashes. Shared drift blocks ordinary story mutations. Reading, rendering, and saving existing history remain available with a warning. There is no automatic re-pin or migration command. Common maintenance requires a separate review of effects on all affected stories; do not change the baseline merely to accommodate one character.

## Play in chat

Identify the story: “Continue story-001. Read its character sheet and latest saved records first.” For a new character, supply that character's own sheet and ask the GM to create a separate story folder.

The GM handles records and asks together only for missing essentials: era/region, books/spoiler cutoff, identity/background/aim, starting abilities/assets, time/location, and system choices. The Blood & Gold module is available when selected; its adjudicated 0 to 9 ratings are never silently converted to the legacy dice scale.

During play, say “Inspect the delivery,” “Spend a week training and performing household duties,” “Continue the journey,” “Status,” “Save,” or “Review.” A turn can cover seconds, hours, days, or weeks. A meaningful interruption preserves remaining work and costs already paid. Elapsed time and causes govern learning, recovery, income, and world activity. Ten-turn reviews examine player decisions and GM consistency without automatic advancement or punishment.

## Commands for maintainers

The GM performs these steps. From the repository root, a new story requires its own character document:

```sh
python -m iron_engine create-story story-001 --character-sheet /path/to/this-story-character.md
```

This illustrates creation; do not recreate the already prepared `story-001` folder. Use a fresh ID for a genuinely new story. Creation copies its starting document and pins shared files. It does not initialize a character or resolve an action.

Select the story explicitly for campaign commands:

```sh
python -m iron_engine --story story-001 validate
python -m iron_engine --story story-001 status
python -m iron_engine --story story-001 head
python -m iron_engine --story story-001 init stories/story-001/.work/setup.json
python -m iron_engine --story story-001 turn stories/story-001/.work/turn.json
python -m iron_engine --story story-001 render
python -m iron_engine --story story-001 save turn-010.json
```

The GM prepares inputs from agreed facts and resolved actions. `head` requires initialization. Events go to `stories/story-001/campaign/`, rendered views to `stories/story-001/play/`, and that save to `stories/story-001/saves/turn-010.json`. There is no implicit default store. Explicit `--store PATH` remains available for legacy stores and isolated tests, never as a bypass for story baseline protection. See [the full workflow](docs/play_workflow.md).

A story-mode save includes story identity, baseline hashes, and the complete event chain. It does not bundle engine files, reference content, datasets, or unaccepted local notes. Use the matching project package or Git baseline for a complete handoff. Restore checks identity and baseline; bare legacy engine exports are not story-mode saves.

## Consistent records

Temporary Condition uses a separate 0–9 physical-function scale with descriptive tags and an evidence basis. Ordinary health is 8; 9 requires exceptional readiness; 0 means dead. Multiple tags do not each deduct a point, and time or reviews never heal automatically. Older records without this optional field retain their hashes.

Each accepted event contains its input, full resulting state, and previous hash. Generated journals and sheets reference that chain. Every tenth turn includes its review in the same event. Exact request retries return the existing result; changed content under the same ID and stale inputs are rejected. A failed write never authorizes another roll or deduction.

Hashes detect inconsistency, not a deliberate rewrite of all history. A missing final suffix can leave a valid older prefix; compare the last confirmed Git version or save. Validation cannot prove lore accuracy, good prose, or impartial adjudication. All records are player-readable, with no hidden GM store.

Tests and shared lookup tools run independently of live story mutations:

```sh
python -m unittest discover -s tests -v
python -m iron_engine distance --mode road --from "Castle Black" --to Winterfell
python -m iron_engine travel-profiles
python -m iron_engine travel --mode road --from "Castle Black" --to Winterfell --profile small_party_riding --pace average
python -m iron_engine roll --sides 20 --count 1
```

The travel catalog contains 577 source-linked entries and seven road pace profiles. These are estimates; party, route access, supplies, rest, and interruptions govern actual travel. Record local deviations in the selected story. Sea/raven estimates need an explicit rate assumption. Dice are public draws made only after stakes are fixed in a compatible dice story; the helper saves nothing and proves no secret precommitment.

## Publication status

This build is prepared for [Alex-Oss222/dice-roller](https://github.com/Alex-Oss222/dice-roller). The last upload attempt failed with HTTP 403, `Resource not accessible by integration`; it did not publish the build. See [build status](BUILD_STATUS.md). Python does not upload automatically.

With working write access, publish a story's accepted event and refreshed views together, verify the remote commit, and report that version. Common maintenance is a separate reviewed change. If upload fails, retain the local result and retry publication of the same bytes without replaying the action.

The distance catalog is a snapshot of [ASOIAF Timeline - Vandal Proof](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit#gid=1), read on 22 September 2026. It imports distance matrices and road rates, not the plot timeline. Fan estimates and sea/raven unit assumptions are identified in the travel documentation; no automatic spreadsheet connection is needed.
