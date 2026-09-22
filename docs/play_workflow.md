# Playing and saving a campaign

Tell the GM what the character tries to do. The GM handles research, narrative resolution, JSON, validation, and recording. “Advance one week,” “Continue the journey,” “Status,” “Review,” and “Save” are sufficient player instructions. This page also documents the commands for anyone maintaining the repository.

The engine uses standard-library Python from the repository root. It records outcomes; it neither generates a story nor browses the internet. No service runs between messages.

## First session

Read [the rules](../rules/iron_engine.md). Supply the missing era/start point and region, permitted books/spoiler cutoff, character name/age/status/background/aim, and resolution mode. The GM establishes starting resources and abilities from those details, researches the permitted setting, and prepares a complete setup input. No live campaign exists merely because templates are present.

```bash
python -m iron_engine --store campaign init setup.json
python -m iron_engine --store campaign validate
python -m iron_engine --store campaign status
```

`setup.json` is a prepared input file, not a required filename supplied automatically. Initialization creates event `000000.json` at Turn 0 with the complete agreed state. The first playable situation is presented without resolving an action the player has not chosen. Do not initialize over an existing campaign.

## Ordinary turn

The GM reads validated current state, identifies the authorized objective, checks relevant uncertainty, and resolves it. A routine week can be one turn. A two-hour interruption can also be one turn. The event records actual elapsed seconds; an interrupted plan preserves its remaining work or original endpoint.

The input includes a unique `request_id`, the current `expected_turn`, the latest event's `expected_hash`, elapsed time, objective, outcome, narrative, resource deltas, changed complete state fields, causal evidence, due task results, any actual dice checks, and review or `null`. Read the latest hash before preparing the input:

```bash
python -m iron_engine --store campaign head
```

The exact structure is in [record_contract.md](record_contract.md). The engine increments time and turn once. Do not manually advance them inside a replacement state.

```bash
python -m iron_engine --store campaign turn turn-input.json
python -m iron_engine --store campaign validate
python -m iron_engine --store campaign status
```

An accepted turn writes one immutable event containing its input and full resulting state. No separate sheet update is needed; the latest validated state is the sheet. Replacing a field such as `character` or `tasks` means supplying its complete new value, including unchanged details. Every changed field and resource delta needs evidence. Retain settled task IDs so deadlines and outcomes remain inspectable.

If another event changed the store, `expected_hash` catches a stale draft even when research, correction, or a checkpoint left the turn unchanged. `expected_turn` separately checks the intended turn. Reload and reconcile the authorized attempt before proceeding; do not blindly change the expected hash or number. State the conflict if it affects a result already given to the player.

## Retry, correct, or research

Retry a failed or uncertain write using exactly the same input and `request_id`. An already accepted identical request returns the existing event without another turn, charge, or elapsed interval. The same ID with different content is rejected. Publication problems never justify rerolling a result.

Use a new correction input for a genuine recorded error, with reason, changes/deltas, and evidence. Use a research input to append verified player-safe sources. Each post-setup mutation requires the current `expected_hash`; a just-added research event invalidates an older turn draft. Both create events but consume no turns or fictional time.

```bash
python -m iron_engine --store campaign correct correction-input.json
python -m iron_engine --store campaign research research-input.json
```

A correction preserves the earlier record and explains the repair. It cannot reverse death or undo a valid defeat. Research does not grant character knowledge. Information actually acquired by the character belongs in the corresponding turn's knowledge change. Do not edit an old event to make the chain fit a preferred story.

## Dice

In real-dice mode, the GM fixes objective, target, skill, modifier, time, and outcome stakes before the roll. Then use a player-supplied roll or a public tool result:

```bash
python -m iron_engine roll --sides 20 --count 1
```

Record source and arithmetic with the resolved turn. The helper saves nothing and does not prevent rerolling or prove secret precommitment. The ledger checks arithmetic; the GM checks whether the stakes and resolution were justified. Adjudicated mode uses no check records. Routine actions need no dice even in real-dice mode.

## Every tenth turn

The GM reads the preceding nine turns and the current result, then includes a review for the complete ten-turn window in that same turn input. All six findings need supporting turn references: results, decisions, capabilities, position, GM consistency, next constraint. Favorable evidence counts. Skill change needs demonstrated practice or capability, not a round number.

The engine rejects a tenth turn without its review. Complete that pending input rather than skipping the assessment or creating a second fictional result. The GM then shows the full current sheet, the review, and a save. A separate “Review” request reads evidence without consuming time or resetting the ten-turn schedule.

## Save and resume

Before ending a session with an unresolved check or other pending decision, the GM records its fixed numbers, stakes, and authorized action in a checkpoint input with `request_id` and the current `expected_hash`. This changes only `resume_note`, adds no fictional time or character knowledge, and is included in the next export. A resolved turn clears it. A checkpoint with `resume_note: null` can clear a note explicitly.

```bash
python -m iron_engine --store campaign checkpoint checkpoint-input.json
mkdir -p .work/exports
python -m iron_engine --store campaign save .work/exports/campaign-save.json
```

The checkpoint command is needed only when resume details need recording. The export contains every validated event and resulting state. Export after turns 10, 20, and so on, on request/session end, and after death. This automatic schedule is performed by the GM workflow, not a background process in the CLI. The exported file is a portable copy, not a second canonical ledger. `.work/exports/` is ignored: do not commit a growing full-chain copy at every checkpoint when events already preserve that history. Do not claim the save includes a conversation detail unless it was recorded.

In a later session with the same repository, validate and show status, then continue from the last result without advancing time. To restore a supplied save into a new empty store:

```bash
python -m iron_engine --store restored-campaign restore .work/exports/campaign-save.json
python -m iron_engine --store restored-campaign status
```

Restore validates hashes and replays input to check the stored states before accepting the chain. It refuses a nonempty destination. Keep the existing campaign if present; do not restore over it. Missing, malformed, or conflicting history must be reconciled openly, never filled with invented events. After death, the character cannot take another turn. A successor uses a new agreed setup and separate store.

## GitHub persistence

The canonical store contains only immutable events. Each event carries its full state, result, and due review, so publishing a turn does not depend on updating a mutable sheet afterward. Publish one complete Git commit per coherent change through the authorized repository workflow. Publication requires an actual Git or connector operation: the Python engine does not browse, authenticate, or upload. Do not describe independent file-update requests as an atomic transaction.

Verify the accepted event and latest remote history, reconcile any conflicting new events, and confirm the resulting GitHub commit before reporting upload success. Unique event filenames prevent a writer from silently replacing another accepted next event. State the actual destination/version. If local recording succeeded but publication failed, retain the accepted event and retry publication of the same bytes. Explain which version is local and which remote checkpoint is confirmed. Do not resolve another copy of the action to compensate.

SHA-256 links detect accidental alteration and broken continuity. They do not stop someone from rewriting every file and recomputing every hash; Git history gives an external history to compare. Removing complete final events also leaves a valid older prefix, so compare the last confirmed Git version or save before treating it as the latest campaign. All stored material is player-readable, and there is no private world state or hidden simulation. Keep unrevealed secrets out of commits and exports.

Examples and test stores are disposable demonstrations. Never run them against the live `campaign` directory or treat their character, skills, dates, or money as the player's established facts.
