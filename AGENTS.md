# Repository play contract

The repository holds the story. The player gives decisions in chat and reads saved output here. Use Python 3.10+ and the standard library. Read the selected story's scoped instructions. Do not initialize stories during maintenance or tests.

## Start and resume

1. Select the explicitly named story. First read its character-sheet.md. If unstarted, inspect setup.json, opening.md and setup decisions. Story 1 is prepared. Only when the player starts, run `python -m iron_engine --story story-001 start`. This accepts the opening as Turn 0; Turn 1 resolves the first player action. Repeating start resumes without resetting. Do not choose the PC's action.
2. For ongoing play, run `context`. Python validates full history internally. Load relevant `record ID` and `history --turn N` details when needed. Do not load all events, the full journal, all references or another story into context. Never omit active obligations, deadlines, Condition, pending decisions or applicable standing orders to meet a token target. Unknown information stays unknown.
3. At the beginning of a fresh chat, read rules/narrative.md and relevant rules/iron_engine.md sections; reuse them while that context remains available. Load Condition, capability, travel and research details when used. Archived inputs are provenance, not additional active instructions.

## Resolve and record

- Use `advance` for workflow version 1. See templates/advance.json and docs/record_contract.md. Write narrative once and justified operations. The engine derives the full state, verifies claimed changes and renders reading pages. Never hand-edit generated sheets or accepted events.
- Establish the player's objective, authorized duration and stopping point. A five-year proposal does not authorize skipping the meeting. Turns can cover minutes, days or weeks; stop for a consequential decision. Routine authorized activity needs no repeated permission.
- Match consequential uncertainty to the actor's relevant ability, knowledge, preparation, opposition, task difficulty and risk before writing the outcome. Martial standing cannot substitute for intrigue. Reader knowledge is not character knowledge. No plot protection, automatic success, artificial punishment, failure quotas or invented dice. Code checks required evidence, not its truth; the GM must judge causally and honestly.
- Review affected character, resources, relationships, obligations, tasks, knowledge, assumptions, plans and world records. Track material NPC, storyline, divergence, project and journey changes under stable world IDs. Retain closed records. Missing money is not zero money. Use optional modules only when relevant.
- Every tenth turn requires its evidence review in the same event. Retrieve the preceding nine turns. Intervals of 30 days or more also need ordered milestones covering the interval and endpoint; assess shorter intervals when consequences warrant it. No automatic skill gain, healing or economic growth.
- Travel uses the slowest applicable sourced party profile, with genuine extra delays/reductions recorded once. Normal sleep and meals are inside the daily rate by house convention. Sea/raven rates need an explicit conservative basis. Lookups consume no fictional time. Local obstacles never alter common distances.

## Save and publish

Submit the actual current hash, turn and a unique request ID. Exact retries return the accepted event. Never reroll, recharge or advance again after a save/upload failure. Reconcile stale drafts with the new state instead of merely replacing their hash. Research, corrections and checkpoints consume no fictional time. Corrections explain genuine record errors; they cannot reverse death or a valid defeat.

The player reads stories/<id>/play/README.md, latest.md, numbered turns/, character-sheet.md, threads.md, world.md and resume.md. These are generated from events. Validate the selected story and inspect affected views after mutations. Repair a failed render with `render` without replaying the action.

Publish an event and regenerated views together in one coherent Git commit. Ordinary play may change only paths under the selected story. Check current remote history, preserve unrelated work, never force-push, and verify publication. A local write alone is not an upload. Retry publication of the same result after transport failure. Normally reply only: **Turn N saved. Read it here: [link].** Add a real blocker or required question if necessary; do not duplicate the narrative, sheet or review in chat.

On pause, checkpoint unresolved instructions/fixed stakes if needed. Export a uniquely named save on request, every tenth-turn review, session end and death. Exports are portability copies, not another truth store; do not commit repeated full-history exports. Accepted events preserve history already.

## Boundaries

Shared engine, rules, book references, distances and templates serve every story. Characters, alternate history, local prices, routes, relationships and rebuilding projects belong to their story. Ordinary turns never re-pin shared hashes. Shared maintenance is separate, reviewed work; baseline drift blocks new results until addressed.

All repository records are player-readable. There is no hidden GM store. Research does not grant PC knowledge. Never guess lost facts or treat reference transcripts as imported history. Canon informs the starting character; it does not force later dialogue, values, loyalties or decisions. Record actual changes in conduct, relationships, reputation and learned ability with evidence, without snapping the character back to a book outcome. Player knowledge still is not PC knowledge. Death ends that PC's turns. `create-successor` prepares an explicitly requested continuation with a new supplied character and the predecessor's ending world; knowledge, assets and duties need justified setup. Independent stories use `create-story`.

For code changes, inspect relevant code and run focused checks plus the full suite. Use temporary stores, never live campaigns. Include a reviewed baseline decision for affected stories. Preserve user source inputs and accepted history during cleanup. Do not introduce hosted services, paid APIs, deployments, credentials, telemetry or background simulation.
