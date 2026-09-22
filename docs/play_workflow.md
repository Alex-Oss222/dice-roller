# Playing and saving isolated stories

The player identifies the story and speaks naturally. The GM handles research, judgment, prose, JSON, commands, and recording. The engine validates and renders outcomes; it does not browse, generate a story, or advance time between messages. See [Start and continue](../START_HERE.md) and [the story layout](../stories/README.md).

## Character first, then setup

Every new story requires its own supplied character document:

```bash
python -m iron_engine create-story story-001 --character-sheet /path/to/this-story-character.md
```

This illustrates creation; do not recreate the prepared `story-001` folder. Use a fresh ID for a genuinely new story. Creation copies the starting document and pins shared files in `story.json`; it does not initialize live state. No additional story exists merely because documentation describes this process.

Read `stories/story-001/character-sheet.md` first. Complete missing agreed facts there before initialization. Its import hash records provenance, not a ban on filling a blank input. After initialization the root sheet preserves starting input; current changes belong in accepted events. Never populate a new story from another story's NPCs, claims, outcomes, knowledge, assumptions, or exceptions.

Select resolution and capability system from this story's document. The optional [Blood & Gold module](../rules/capabilities.md) supports adjudicated 0 to 9 play; its availability does not select it for all characters. Do not convert those ratings to the legacy dice scale.

Ask together only for missing era/region, permitted books/spoiler cutoff, name/age/status/background/aim, system choices, abilities/assets, time, and location. Research the selected setting. The prepared Story 1 sheet supplies Eddard Stark and a starting premise; it remains preparation until the player starts. Do not ask again for supplied facts. The GM prepares setup from the agreed facts:

```bash
python -m iron_engine --story story-001 init stories/story-001/.work/setup.json
python -m iron_engine --story story-001 validate
python -m iron_engine --story story-001 status
python -m iron_engine --story story-001 render
```

All input filenames represent drafts prepared by the GM. Initialization creates that story's event `000000.json` at Turn 0. Present an opening situation, then wait for the player's action. Never initialize over accepted history.

## Routing and shared baseline

Campaign commands require explicit `--story ID` or legacy `--store PATH`; there is no implicit default store. Story selection routes records to `stories/ID/campaign`, views to `stories/ID/play`, and save filenames to `stories/ID/saves`. Legacy stores support explicit maintenance/tests, not a way to bypass story isolation or baseline checks.

Shared engine, rules, [book catalog](../references/books.md), and source data serve separate stories. The catalog contains reference information and source policy, not ebook texts or a claim of access. Each story observes its own permitted books and spoiler cutoff.

The manifest pins shared-file hashes. Drift blocks initialization, turns, research, corrections, and checkpoints. Existing records can still be read, rendered, and saved with a warning. There is no automatic re-pin or implemented baseline migrator. Necessary common maintenance requires separate review of its effects on all affected stories. Do not update pins simply to make an action pass.

Story-specific roadblocks, detours, prices, local inventions, interpretations, and special agreements belong in that story's notes and canonical assumptions/research. Notes can support preparation, but accepted facts affecting play must also enter event state. Do not edit common distance data, book references, or rules to accommodate Story 1.

## Resolve and record a turn

Read this story's validated state, deadlines, interrupted plan, and resume note. Identify the authorized objective, investigate material uncertainties, and resolve under its selected system. A turn can cover a quiet week or two hours before a meaningful interruption. Preserve paid costs and remaining work.

Read the latest hash before drafting:

```bash
python -m iron_engine --story story-001 head
```

A complete input includes stable `request_id`, current `expected_turn`/`expected_hash`, objective, outcome, narrative, elapsed seconds, resource deltas, changed complete fields, evidence, due-task dispositions, checks if applicable, and review or `null`. See [record_contract.md](record_contract.md). The engine increments time and turn once.

```bash
python -m iron_engine --story story-001 turn stories/story-001/.work/turn.json
python -m iron_engine --story story-001 validate
python -m iron_engine --story story-001 render
```

Each accepted event contains its full resulting state. Keep unchanged detail within replaced fields and retain settled task IDs. Prose must agree with the ledger. Track temporary physical function in `character.condition`, separately from learned skills; preserve its rating, tags, and basis within complete character replacements. See [Condition](../rules/condition.md). Use the [turn presentation](../templates/turn-output.md) with Name, Age, Condition, and Location; keep a visible Ledger only for meaningful changes and offer no action menu unless requested. An intervening event makes a draft stale even if the turn number is unchanged; reload/reconcile instead of merely changing the expected values.

## Story and records

Put the resolved scene into the turn's `narrative`, then present the same prose in chat. Rendering produces:

- `stories/story-001/play/story.md`: accepted scenes in turn order and actual time intervals.
- `stories/story-001/play/character-sheet.md`: current state from events.
- `stories/story-001/play/resume.md`: recorded continuation point.

Before setup the views report that no initialized character state or saved turn exists. A supplied character seed remains in the story root. After every accepted mutation, including research/checkpoints, regenerate views and check their source hash. Rendering never changes outcomes or time. Views can be replaced from history; do not edit them to create state. Corrections appear as OOC notes beside retained prose. If rendering fails, keep the accepted event and render again without resolving twice.

## Retry, correct, research, checkpoint

An identical input/request ID returns its existing accepted result without another charge, roll, interval, or turn. Different contents under that ID fail. Publication failure never justifies replaying an action.

Use a correction for genuine recorded errors, research for checked player-safe sources, and checkpoints for pending fixed stakes or resume instructions:

```bash
python -m iron_engine --story story-001 correct stories/story-001/.work/correction.json
python -m iron_engine --story story-001 research stories/story-001/.work/research.json
python -m iron_engine --story story-001 checkpoint stories/story-001/.work/checkpoint.json
```

These are independent examples. Each draft needs the current `expected_hash` after preceding accepted events. Corrections require evidence and cannot erase valid defeat/death. Research grants no PC knowledge. Checkpoints change only `resume_note`; a resolved turn clears it, and a checkpoint with `null` can clear it explicitly. None consumes fictional time. Refresh views afterward.

## Dice and reviews

For a compatible real-dice story, fix objective, target, skill, modifiers, duration, and outcome stakes before a player roll or public draw:

```bash
python -m iron_engine roll --sides 20 --count 1
```

The helper saves nothing, prevents no reroll, and proves no secret precommitment. Record source/arithmetic in the resolved turn. Adjudicated stories use no check records. Routine acts need no dice, and Blood & Gold ratings never become legacy die bonuses.

Every tenth resulting turn includes its review in the same event. Read the prior nine turns and current draft; supply findings for results, decisions, capabilities, position, GM consistency, and next constraint, each citing that story's evidence. Recognize favorable results and distinguish luck from choice quality. Missing review blocks that draft until completed. Do not resolve a second action or skip to Turn 11. Show full sheet/review and export a save; the boundary creates no time or advancement.

## Save and resume

Checkpoint any pending details before ending a session. Export with a plain filename:

```bash
python -m iron_engine --story story-001 save turn-010.json
```

This writes `stories/story-001/saves/turn-010.json`. Save after turns 10, 20, and so on, on request/session end, and after death. The GM performs this schedule; it is not a background process. Avoid redundant complete-history exports in every Git commit when canonical events already preserve history.

Story saves wrap story ID, shared-baseline hashes, and the full canonical event chain. They do not contain actual engine/reference/data files or unaccepted local notes. A complete handoff needs the matching project package or Git baseline. A current sheet alone cannot reconstruct earlier scenes and review evidence.

For ordinary resume, identify the same story, read its starting sheet, validate baseline/history, show current status/resume, and wait for action. Restore is only for an empty campaign destination:

```bash
python -m iron_engine --story story-001 restore /path/to/matching-story-save.json
python -m iron_engine --story story-001 render
```

That example must not be used over existing events. Story-mode restore verifies matching story identity and shared baseline and rejects another story's save or bare legacy engine JSON. Legacy exports remain supported with explicit `--store`. Restore validates hashes and replays inputs to check states. Reconcile missing/conflicting history openly. A dead PC cannot take another turn; a successor needs a separate story and its own character document.

## Publication and limits

Publish an accepted story event and refreshed views together in one coherent commit, keeping common maintenance separate. GitHub needs actual authenticated write access; Python does not upload. The last attempt failed with HTTP 403, `Resource not accessible by integration`. See [build status](../BUILD_STATUS.md).

Verify remote history and the resulting commit before reporting upload success. If publication fails, retain the exact local result and retry publication without replaying events. Never force-push or overwrite another story. A local record is not confirmed GitHub persistence.

Hashes detect inconsistency, not a complete malicious rewrite or removal of every final event. Compare the latest confirmed commit/save before accepting an older valid prefix as current. Records are player-readable, with no hidden GM store. Run tests/examples in isolated temporary stores, never a live story.
