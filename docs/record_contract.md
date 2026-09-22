# Record contract, version 1

This project is a local, Python-standard-library campaign ledger. The GM researches and resolves fictional actions; the code validates and saves the result. It does not autonomously simulate Westeros or prove narrative fairness.

## Storage

The store directory (default `campaign`) contains only `events/000000.json`, `000001.json`, etc. Each immutable event contains the full resulting state and a SHA-256 link to the previous event. Event sequence and fictional turn are separate: setup, research, and correction events consume no turns or fictional time. No mutable HEAD or second canonical character sheet. Latest validated event owns current state. `status` renders it. Turn-ten reviews are inside the same event as their result and sheet.

Publish one complete UTF-8 JSON event using a flushed temporary file and an exclusive same-filesystem link, never an overwrite. Concurrent writes to the same next sequence fail cleanly. Repeating an identical `request_id` and input returns its existing event with no additional cost/time/roll; changed input with the same ID fails. Validate the entire chain on every operation. Malformed or missing events fail closed. Reject unknown input fields rather than silently ignore misspellings. All input must be JSON objects; reject nonfinite numbers and booleans where numbers are expected.

Event envelope: `schema_version: 1`, `sequence`, `kind`, `request_id`, `input` (normalized submitted command), `previous_hash` (null for setup), `state`, `hash` (canonical JSON SHA-256 of envelope excluding hash). Canonical JSON uses sorted keys, compact separators, UTF-8, and allow_nan=False. Local hashes detect inconsistency, not malicious rewriting of every file; Git history supplies external version history.

## State

Top-level fields: `campaign`, `turn`, `time_seconds`, `phase`, `location`, `character`, `resources`, `relationships`, `obligations`, `tasks`, `knowledge`, `assumptions`, `research`, `standing_orders`, `interrupted_plan`, `resume_note`, `alive`, `death`.

`campaign`: required nonempty strings `id`, `title`, `era`, `region`, `spoiler_cutoff`, `day_zero_anchor`, `rules_version`; `resolution_mode` is `adjudicated` or `real_dice`. No default era, protagonist, spoiler cutoff, or invented starting assets.

`character`: required `name`, `age` (nonnegative integer), `status`, `background`, `aim`; `skills` is a string-to-integer map bounded 0..5; `conditions` and `equipment` are lists of strings. `resources` is a string-to-nonnegative-integer map, with each key its own unit. No currency conversion or float accounting.

`turn` and `time_seconds` are nonnegative integers. Time is seconds since campaign Day 0 midnight, not a real-world timestamp. `phase` and `location` are nonempty strings. `relationships`, `obligations`, `knowledge`, `assumptions`, `standing_orders` are lists of strings. `alive` is boolean. `death` is null while alive; when dead it is `{cause: nonempty string, time_seconds: current campaign time}`. No new turns or reversal of death are allowed after death.

`tasks`: list of objects with unique string `id`, string `description`, `status` in active/completed/blocked/failed/expired/abandoned, `due_seconds` nonnegative integer or null, string `note`. `interrupted_plan` is null or `{objective: string, endpoint_seconds: integer or null, remaining_seconds: integer or null, stopping_conditions: list of strings}`; at least one endpoint/remaining value is required. `research`: list of unique-ID source records described below.

## Commands and API

Implement `iron_engine/engine.py` with `CampaignError`, `CampaignStore(path)`, `.initialize(payload)`, `.commit_turn(payload)`, `.add_research(payload)`, `.correct(payload)`, `.checkpoint(payload)`, `.validate()` returning the list of validated events, `.current()` returning current state, `.export_save(path)`, and `.restore_save(input_path)` into an empty store. Methods returning a created/reused event return its full envelope. `iron_engine/__main__.py` exposes `python -m iron_engine --store DIR init|turn|research|correct|checkpoint INPUT.json`, `validate`, `status`, `head`, `save OUTPUT.json`, `restore INPUT.json`, and `roll --sides 20 --count 1`. `roll` is an explicitly public random-number helper, does not save or advance state, uses `secrets`, and makes no claim of secret precommitment or resistance to rerolling. Rule instructions require fixed stakes before rolling.

Initialize input: `{request_id, state}`. Turn must be 0, alive true, death null, resume_note null. All state fields are explicit. Setup is excluded from ordinary turn numbering. Committed state must have no overdue active tasks.

Turn input: `{request_id, expected_hash, expected_turn, elapsed_seconds, objective, outcome, narrative, resources_delta, changes, evidence, processed_tasks, checks, review}`. Required nonempty objective/outcome/narrative; positive integer elapsed_seconds; expected_turn must match current turn. resources_delta is integer adjustments per named unit; keys must already exist in resources, or be explicitly introduced with a zero balance in setup/correction. `changes` replaces complete allowed state fields: phase/location/character/relationships/obligations/tasks/knowledge/assumptions/standing_orders/interrupted_plan/alive/death. Other fields cannot be replaced. `evidence` maps each changed field or resource unit (use `resources.UNIT`) to a nonempty causal explanation. All deltas must reconcile without negative resources. Time and turn are set by the code exactly once.

`processed_tasks` is a map of task ID to nonempty outcome explanation. Every previously active task whose deadline is at or before the ending time requires an entry and must be retained in the resulting task list with a settled status (including blocked) or a future deadline with an explanatory note. New active tasks cannot be overdue. Do not silently delete existing task IDs; settle them instead. These are direct deadline checks, not a simulation of dependent events.

`checks`: list of `{source, roll, skill, modifier, target, total, margin, objective, stakes}`. source is `player` or `tool`; roll is integer 1..20, skill 0..5, modifier -4..4, target integer; total and margin must match arithmetic; objective/stakes nonempty. Require an empty list in adjudicated mode. In real_dice mode allow an empty list for routine/certain actions. Code checks arithmetic, not the honesty of submitted dice or whether a check was necessary. Every consequential result must still be justified by the GM.

`review` is null unless the resulting turn is divisible by 10; then it is required with exact `from_turn`, `to_turn`, and `findings`. `findings` has exactly results/decisions/capabilities/position/gm_consistency/next_constraint. Each is `{assessment: nonempty string, evidence_turns: nonempty list of integers in this ten-turn window}`. Reviews must distinguish facts, inference, and uncertainty and explain both favorable and adverse findings. The engine enforces coverage and references, not the truth of the prose.

Research input: `{request_id, expected_hash, sources}`. Source records have exactly `id`, `claim`, `source`, `type`, `scope`, `confidence`, `limitations`; all nonempty strings. type is canon/secondary/author/historical_analogy/campaign_assumption. URLs or genuinely checked book locators go in source; inventions use `campaign convention` and must identify their assumption. Research IDs cannot be overwritten. Research records do not grant PC knowledge, change time, or advance turns. Use turn knowledge changes for information acquired in-world. Only player-safe research belongs in this store.

Correction input: `{request_id, expected_hash, reason, changes, resources_delta, evidence}`. Reason and evidence are required. Same change rules and resource arithmetic as turns, but no time/turn change and no alive/death change. May introduce a resource unit with a nonnegative delta, including zero, with evidence. This repairs recorded facts without rewriting earlier events. It is not a way to undo a valid loss or death. Corrected state must have no overdue active tasks. Setup campaign metadata cannot be silently changed.

Save export: `{schema_version: 1, events: [...]}` containing the validated complete chain. Restore validates every hash and replays every input to confirm the stored state, including review/deadline checks, before publishing into an empty target; reject nonempty targets and unsafe links/paths. Save includes only what the player-safe store actually knows. It is not a hidden GM export.

Checkpoint input: `{request_id, expected_hash, resume_note}`. `resume_note` is a nonempty string or null to clear. This event changes only the state's resume_note, without time or turn advancement. Use it to record the authorized action, a pending check's fixed target/modifiers/stakes, and other player-safe resume instructions before a session save. It cannot grant information to the PC or change a capability. The next committed turn clears resume_note automatically; ordinary changes cannot set it. Export/restore and status include the note.

## Draft version checks

Every post-setup mutation requires `expected_hash`, the hash of the latest validated event when the input was prepared. For a new request it must match the current event hash. Check exact request-ID retries first so a successful request remains safely repeatable after later events. Replay also checks expected_hash against the immediately preceding event. `head` prints the current event hash and fails when awaiting setup. A research, correction, or checkpoint event changes this hash even when the turn stays the same. A stale draft must be reconciled against current state, not merely stamped with the new hash.

## User workflow

The user can speak naturally: Start campaign, Status, Save, Review, Continue the journey, Advance one week. AGENTS.md directs the GM to handle JSON, commands, checks, and coherent Git commits. Do not ask the user to maintain the ledger manually. An unconfigured repository is explicitly awaiting setup, not Turn 1. Templates and examples are never live campaign facts.
