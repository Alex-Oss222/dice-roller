# Record contract, version 1

This project is a local, Python-standard-library campaign ledger shared by independent stories. The GM researches and resolves fictional actions; the code validates and saves the result. It does not autonomously simulate Westeros or prove narrative fairness.

## Story selection and boundaries

The supported multi-story workflow uses an explicit `--story <id>` selector. Each story has `stories/<id>/character-sheet.md` as its own starting input, `story.json` as its identity and shared-reference manifest, `campaign/events/` as its canonical history, `play/` as its generated reading views, and `saves/` for portable exports. Story IDs use safe lowercase letters, digits, and hyphens. There is no global active-story pointer or implicit campaign destination.

`create-story <id> --character-sheet <path>` copies the supplied sheet into a new story folder and prepares awaiting-setup views. It creates no campaign events or character state. The GM reads this sheet first. It remains editable preparation until initialization; the manifest's imported-sheet hash is provenance, not a lock that prevents the player filling missing facts. After setup, the starting document is historical input and immutable event state owns the current character.

Shared engine files, rules, the distance dataset, reference policy, and book catalog are fingerprinted at story creation. New story mutations and story-scoped distance estimates require those shared bytes to match the selected story's baseline. A changed shared file is an explicit compatibility issue; never automatically update a manifest to make a turn work. Existing records can still be inspected, rendered, and exported with drift disclosed. Hashes identify the baseline; retain its actual files through the project package or repository history. No automatic baseline upgrade or per-story engine fork is implemented.

Initialization and restoration bind `campaign.id` to the selected story ID. Render destinations are fixed within that story, and story-mode saves accept a new simple filename under its `saves/` directory. Path traversal, symlink escape, accidental re-use of an existing story, and redirecting generated output into another story are rejected. `--story` and `--store` are mutually exclusive. Explicit `--store DIR` remains available for legacy records and maintenance; its render command requires an explicit output directory. The GM must never use this low-level route to evade a story boundary or a mismatched baseline.

Ordinary play changes only `stories/<id>/`. Story-specific road disruptions, altered history, source interpretations, local rates, and special rulings belong in its notes and canonical assumptions/research/events. Notes are not automatically executed overrides and do not change any state without an accepted event. They never modify shared book references or the source distance catalog, and are not inherited by another story.

## Storage

The explicitly selected store directory (normally `stories/<id>/campaign`) contains only `events/000000.json`, `000001.json`, etc. Each immutable event contains the full resulting state and a SHA-256 link to the previous event. Event sequence and fictional turn are separate: setup, research, and correction events consume no turns or fictional time. No mutable HEAD or second canonical character sheet. Latest validated event owns current state. `status` renders it. Turn-ten reviews are inside the same event as their result and sheet.

Publish one complete UTF-8 JSON event using a flushed temporary file and an exclusive same-filesystem link, never an overwrite. Concurrent writes to the same next sequence fail cleanly. Repeating an identical `request_id` and input returns its existing event with no additional cost/time/roll; changed input with the same ID fails. Validate the entire chain on every operation. Malformed or missing events fail closed. Reject unknown input fields rather than silently ignore misspellings. All input must be JSON objects; reject nonfinite numbers and booleans where numbers are expected.

Event envelope: `schema_version: 1`, `sequence`, `kind`, `request_id`, `input` (normalized submitted command), `previous_hash` (null for setup), `state`, `hash` (canonical JSON SHA-256 of envelope excluding hash). Canonical JSON uses sorted keys, compact separators, UTF-8, and allow_nan=False. Local hashes detect inconsistency, not malicious rewriting of every file; Git history supplies external version history.

## State

Required top-level fields: `campaign`, `turn`, `time_seconds`, `phase`, `location`, `character`, `resources`, `relationships`, `obligations`, `tasks`, `knowledge`, `assumptions`, `research`, `standing_orders`, `interrupted_plan`, `resume_note`, `alive`, `death`. Optional `world` contains structured story-local records described below. Optional extensions are never inserted into historical state during replay.

`campaign`: required nonempty strings `id`, `title`, `era`, `region`, `spoiler_cutoff`, `day_zero_anchor`, `rules_version`; `resolution_mode` is `adjudicated` or `real_dice`. Optional `permitted_books` is a list of nonempty strings. Optional `capability_system` can select `blood_and_gold_0_9`; this requires adjudicated resolution and nonempty permitted books. Omission preserves the original 0 to 5 record interpretation. No default era, protagonist, spoiler cutoff, or invented starting assets. Optional new fields are not injected into old records, so their original replay state and hashes remain valid.

`character`: required `name`, `age` (nonnegative integer), `status`, `background`, `aim`; `skills` is a string-to-integer map bounded 0..5 for legacy records, or 0..9 for the explicitly selected Blood & Gold system. In that system, required `capabilities` has metadata with exactly the same keys as `skills`; the numerical rating is stored only in `skills`. Optional `profile` holds descriptive character information as specified below. Optional `condition` is the overall physical summary defined below. Existing `conditions` and `equipment` remain lists of strings. `resources` is a string-to-nonnegative-integer map, with each key its own unit. Copper pennies and copper stars require different keys. No currency conversion or float accounting.

Optional `campaign.workflow_version` is the string `"1"`. It selects the compact, adjudicated workflow below. These stories reject legacy `turn` submissions so required time authorization, adjudication, and coverage cannot be bypassed. Omission preserves legacy input/replay behavior.

Optional nonempty strings `campaign.world_id`, `predecessor_story_id`, and `predecessor_hash` record an explicitly linked successor's provenance. `create-successor NEW-ID --from-story OLD-ID --character-sheet FILE` requires a validated dead predecessor and prepares a new folder containing its source hash and ending-state snapshot. It does not initialize the successor. The GM must map surviving world records, clock, obligations, and source references into the new setup while reviewing ownership and what the new viewpoint knows. Replace former `pc` references with an explicit person ID; preserve old evidence coordinates in details and use Turn 0 references for accepted inherited setup. The preparation snapshot is supporting evidence, not a second active state. The predecessor remains dead and independent stories remain isolated.

## Structured world records

Optional `world` has exactly `records`, an ID-to-record map. A record has exactly `kind`, `title`, `status`, `summary`, `participants`, `links`, `known_by`, `due_seconds`, `details`, and `evidence_turns`.

- `kind`: `person`, `thread`, `fact`, `divergence`, `project`, `journey`, or `account_note`.
- `status`: `active`, `blocked`, `completed`, `failed`, `expired`, `abandoned`, `closed`, or `dead`.
- `title` and `summary`: nonempty strings. `details`: string keys with nonempty string values.
- `participants`: list of existing person IDs or `pc`. `known_by`: existing person IDs, `pc`, or `public`. `links`: existing record IDs of any kind. These lists express references, not automatic knowledge transfers.
- `due_seconds`: nonnegative integer or null; an open record (`active` or `blocked`) cannot remain overdue after an accepted event.
- `evidence_turns`: nonempty list of established turn numbers from 0 through the resulting current turn.

Retain established IDs and close/settle records instead of deleting them. Descriptive details can record dependencies, ownership, reports, causes, or capability evidence when established. Numerical balances remain in `resources`; an account note is not a second balance. The record store does not infer economics, relationships, or entitlement from prose.

These records are player-readable, including `known_by`; that field tracks in-world access to already disclosed information and is not a private GM store. A research source or public reference does not automatically add PC knowledge.

## Compact advance input

`CampaignStore.advance(payload)` accepts `request_id`, `expected_hash`, `expected_turn`, `objective`, `outcome`, `narrative`, `elapsed_seconds`, `operations`, `authorization`, `adjudication`, `coverage`, `processed_tasks`, `review`, and `milestones`, plus the player-facing `next_decision` field. Older accepted workflow-1 events that predate `next_decision` replay as if it were null. `objective`, `outcome`, and `narrative` are nonempty strings; elapsed time is a positive integer. The story must select workflow version `"1"` and adjudicated resolution. There is no dice-check list in this input.

An accepted event has kind `advance` and retains the submitted compact input. The engine expands operations against prior state, applies ordinary state/capability/deadline/review checks, and saves the full resulting state. Replay repeats that deterministic expansion. It does not inject new defaults into older events or change their hashes.

`next_decision` is null when no new player choice stops the authorized activity, otherwise it is the exact nonempty player-facing decision that remains unresolved. The accepted value becomes current `resume_note`, appears under `### Next` in the turn reading page, and is indexed in `play/decisions.md`. It is never inferred later from prose. A death result requires it to be null.

`authorization` is exactly `{objective, max_elapsed_seconds, stop_condition}`. Its objective equals the input objective, the positive maximum bounds actual elapsed time, and the stopping condition is nonempty. The GM records the user's actual scope; an invented large maximum is not permission to skip an unresolved decision.

`adjudication` is exactly `{mode, actor, capability, preparation, opposition, risk, basis, task_band}`. Mode is `routine` or `uncertain`; actor is `pc` or an existing `person` record ID. Preparation, opposition, risk, and basis are nonempty explanations. Routine mode uses task band `routine`. Uncertain mode uses `ordinary`, `demanding`, `hard`, or `extreme` and requires an already established capability. A capability is `{source, key}`: PC source is `character.skills`; NPC source is `world.records.ID.details` for that same actor. The key must exist before resolution. Routine mode permits null capability. Code establishes that evidence exists, not that its relevance or explanation is honest.

Every operation has a nonempty `basis`. Other exact fields depend on `op`:

| Operation | Fields in addition to `op` and `basis` | Meaning |
| --- | --- | --- |
| `set` | `path`, `expected`, `value` | Replace an allowed leaf with its expected old value; null denotes a missing leaf |
| `list_add` / `list_remove` | `path`, `expected`, `value` | Add an absent item with expected false, or remove a present item with expected true |
| `resource_establish` | `unit`, `expected`, `value` | Establish a previously absent unit; expected must be null and value is an integer at least zero |
| `resource_adjust` | `unit`, `expected`, `delta` | Adjust an established integer-unit balance from the expected old amount |
| `task_upsert` | `id`, `expected`, `value` | Insert or replace one complete task; expected is its prior record or null |
| `world_upsert` | `id`, `expected`, `value` | Insert or replace one complete world record; expected is its prior record or null |
| `death` | `expected_alive`, `cause` | Record final death at the accepted ending time; expected_alive must be true |

`resource_establish` records an amount established during this action, such as counting a previously unrecorded purse. Its basis must explain that discovery or receipt. A known zero is different from an unknown balance, so establishing zero still changes resources. It cannot overwrite an existing unit; use `resource_adjust` for that. An established unit can be adjusted later in the same input. Genuine discoveries do not require pretending an earlier record was wrong and issuing a correction.

Paths are JSON lists of field names, never executable expressions. They cannot edit campaign metadata, counters, arbitrary state, or whole character/world replacements. Missing parent objects fail. `set` supports:

- `phase`, `location`, and `interrupted_plan` at top level.
- `character` fields `name`, `age`, `status`, `background`, `aim`, `condition`, and `profile`.
- `character.condition` fields `rating`, `tags`, and `basis`.
- Individual `character.skills.ID` and complete `character.capabilities.ID` records.
- Capability fields `development`, `basis`, `experience`, `aptitude`, `domain`, `parent`, `derivation`, `anchors`, and `kind`.
- A profile section or a field within a profile section.

List operations support top-level relationships, obligations, knowledge, assumptions, and standing_orders; character conditions/equipment; Condition tags; capability evidence_turns/training; and profile languages. Credited training is append-only on ordinary turns. Resource/task/world/liveness changes use their dedicated operations. Final state still must satisfy Condition/death consistency and capability-transition rules. A death operation never makes an unsupported lethal result justified.

`coverage` has exactly nine keys: `character`, `resources`, `relationships`, `obligations`, `tasks`, `knowledge`, `assumptions`, `plans`, and `world`. Each is `{status: "changed" | "unchanged", basis: nonempty string}` and must agree with actual before/after state. Character includes alive/death; plans includes phase, location, standing_orders, and interrupted_plan. No-op operations do not make an unchanged category changed.

`processed_tasks` retains its ordinary task-ID meanings below. It also uses `world.ID` for every previously open world record (`active` or `blocked`) whose deadline falls within the interval. Settle it as completed, failed, expired, abandoned, closed, or dead; or retain an open status with a future deadline and `details.deadline_reason`. Setting a world record to blocked does not settle its deadline or permit clearing the date. This differs from legacy tasks, whose blocked status retains its existing settled-deadline convention. Workflow task IDs cannot begin with the reserved `world.` prefix. Deadline handling is explicit; code does not simulate a dependency chain by itself.

`milestones` is a list of `{elapsed_seconds, basis, evidence_turns}`. Offsets are positive integers within the resolved interval, strictly increasing. A turn of at least 30 days requires at least two milestones and the final offset must equal its endpoint. Each entry cites the resulting turn in its evidence list. These summaries account for elapsed developments; actual consequences still need operations. They supplement, rather than replace, the review required at every tenth resulting turn.

The blank [advance template](../templates/advance.json) contains empty required strings and zero time deliberately. It must be completed from a real authorized action; it is not a live turn or a runnable claim that nothing changed.

## Overall Condition

Optional `character.condition` is exactly `{rating, tags, basis}`: `rating` is an integer from 0 through 9 (not boolean); `tags` is a nonempty list of nonempty strings; `basis` is a nonempty causal explanation. It is independent of the capability system and never enters `skills` or `capabilities`. The existing `character.conditions` list retains concrete wounds, effects, treatment, and recovery/deterioration notes. Neither a summary tag nor its removal changes an injury by itself.

Labels are 0 Dead, 1 Dying, 2 Critical, 3 Severe, 4 Poor, 5 Impaired, 6 Worn, 7 Sound, 8 Hale, 9 Exceptional. Functional bands are 8..9 Healthy, 6..7 Strained, 4..5 Impaired, 2..3 Critical, 1 Dying, 0 Dead. [Condition rules](../rules/condition.md) define the complete functional table, tags, and examples. Tags are extensible strings, not a fixed enum; precise tags such as `Arrow Wound`/`Blood Loss`, `Dying`, or `Dead` are permitted. Their semantic fit and severity require GM evidence, not a coded per-tag deduction.

The field is optional for legacy replay/hash compatibility and is not inserted into older states. Once present in an accepted state it must remain in later complete character replacements, including corrections. When present, `rating == 0` if and only if `alive == false`; existing death-cause/time requirements still apply. A lethal turn commits the resulting character summary and `alive`/`death` together. Initialization requires alive true, hence rating at least 1 if a summary is supplied. Corrections cannot reverse death or change alive/death through a Condition workaround.

The engine validates shape/range/persistence/death consistency, not medical plausibility, a tag's truth, or the appropriateness of a rating. There are no fixed roll modifiers, automatic healing/deterioration, Capability changes, or hit-point protection. Normal healthy adult 8/Hale is assigned only from established facts; 9 needs supported rest, nourishment, and preparedness. The setup template's 8/Hale and empty basis are an incomplete example, not an initialized health default.

## Blood & Gold capabilities

The event envelope remains schema version 1. The immutable setup's explicit `campaign.capability_system` identifies this optional extension; old events need no migration. The supplied setup template selects this system. It cannot be used as a 0 to 9 dice modifier: initialization with `real_dice` is rejected.

All capability metadata records have `kind`, nonempty `basis`, and `evidence_turns` referring to established turns, including setup Turn 0. Additional fields by kind:

- `domain`: `anchors`, a map of 3 to 5 established sub-skill IDs to integer percentage weights. Each weight is 1 to 40, their sum is 100, and each anchor names this domain. The domain rating must equal the weighted sum rounded half up. There is no domain Development.
- `subskill`: `domain`, `development`, `aptitude`, `experience`, `training`. The domain name need not already have a numerical domain record when too few anchors are established.
- `specialty`: `parent`, `development`, `aptitude`, `experience`, `training`. The parent is an established sub-skill.
- `derived`: `domain` and `derivation`. The domain must be an established domain. `derivation` contains `related` (established sub-skill IDs and integer weights summing to 60), `exposure` (`specialist`, `expected`, `plausible`, or `little`), and nonempty `basis`. Forty percent comes from the parent domain. The exposure adjustments are +1, 0, -1, and -2. The rounded, bounded calculation is a ceiling, not a guaranteed rating; a non-specialist estimate is also capped by the domain. Missing technical prerequisites can justify a lower estimate or no recorded capability. Derived records cannot anchor domains, act as related skills in another derivation, or earn Development.

`development` is a nonnegative integer. `aptitude` has `level` (`poor`, `ordinary`, `strong`, `exceptional`) and `applied_to` (`development` or `experience`). `experience` describes the actual relevant background and exposure; it is not a fabricated exact learning clock. [Capability rules](../rules/capabilities.md) explain the campaign's pacing conventions and limitations.

Each credited `training` entry has exactly `id`, `start_seconds`, `end_seconds`, `development`, `activity`, `basis`, `evidence_turns`. It covers a positive elapsed period no later than current campaign time, awards a positive integer amount, and has a unique ID within that capability. Periods for one capability cannot overlap. Group distinct causes in the same period into one explained award; routine use earning zero can be described in the turn or tasks without a credited entry. Duration and last credited endpoint are derived from these records.

At setup, training lists are empty; any agreed initial Development and pre-campaign exposure come from the established background. Normal turns preserve earlier credited entries. Final Development equals prior Development plus new awards minus the thresholds consumed by accepted rank increases. Thresholds for ranks 0 through 8 are 6, 8, 10, 12, 14, 16, 18, 20, 30. When aptitude applies to Development, multiply by 125%, 100%, 93%, or 90% and round upward once. Excess can carry forward, but rank 9 has no next-rank Development. The engine never awards advancement automatically or verifies that the narrative evidence warrants it.

A newly recorded trainable ability on an ordinary turn begins at rating 0 with only its credited Development. Discovering previously established expertise requires a documented correction. Converting a derived record to established competence allows the same or a lower rating, zero Development, and no inherited credited training; it is not a free advancement. Reclassification cannot increase rank in the same turn. A newly recorded domain can reflect its already established anchors. Genuine corrections retain their separate, explicit repair role.

Optional `character.profile` accepts descriptive section maps with string values: `identity`, `background_details`, `appearance`, `natural_attributes`, `literacy`, `property`, `social_position`, `kinship`, `adjudication`. Natural attributes use `strength`, `agility`, `endurance`, `intelligence`, `perception`, `appearance`, `willpower`. `languages` is instead a list of `{language, spoken, read, written, capability, basis}`; `capability` is an existing skill ID or null. Do not repeat canonical name, age, status, aim, numerical skills, balances, conditions, or equipment here. Store item condition/location in equipment entries, wounds and treatment in condition entries, and dated obligations in tasks. Human-readable IDs in those entries support cross-references without maintaining duplicate totals.

Missing capability records mean not established, not automatically rating 0. Unknown health, money, relatives, and assets also remain unknown until setup or subsequent evidence establishes them. Broad profile prose cannot grant an advantage outside its recorded causal basis.

## Remaining state fields

`turn` and `time_seconds` are nonnegative integers. Time is seconds since campaign Day 0 midnight, not a real-world timestamp. `phase` and `location` are nonempty strings. `relationships`, `obligations`, `knowledge`, `assumptions`, `standing_orders` are lists of strings. `alive` is boolean. `death` is null while alive; when dead it is `{cause: nonempty string, time_seconds: current campaign time}`. No new turns or reversal of death are allowed after death.

`tasks`: list of objects with unique string `id`, string `description`, `status` in active/completed/blocked/failed/expired/abandoned, `due_seconds` nonnegative integer or null, string `note`. `interrupted_plan` is null or `{objective: string, endpoint_seconds: integer or null, remaining_seconds: integer or null, stopping_conditions: list of strings}`; at least one endpoint/remaining value is required. `research`: list of unique-ID source records described below.

## Commands and API

`iron_engine/engine.py` exposes `CampaignError`, `CampaignStore(path)`, `.initialize(payload)`, `.advance(payload)`, legacy `.commit_turn(payload)`, `.add_research(payload)`, `.correct(payload)`, `.checkpoint(payload)`, `.validate()` returning validated events, `.current()` returning state, `.export_save(path)`, and `.restore_save(input_path)` into an empty store. Methods creating/reusing an event return its full envelope. The CLI exposes these commands with explicit `--story ID` or legacy `--store DIR` routing. Story mutations regenerate their reading views; direct Python store calls require an explicit `render_campaign` afterward.

`context`, `record ID`, `records`, and `history --turn N` provide focused reads. The context API is `context_packet(store, focus_ids=None, recent_turns=2, max_chars=12000, read_record_ids=None)`, with `record_packet(store, record_id)` and `history_packet(store, turn)` for detail. CLI `context --max-chars N` bounds recent narrative excerpts only; it is not a total packet-size or token limit. Mandatory state, all open record indexes, deadlines, and explicitly selected records stay complete. These reads validate history without advancing time.

Record selectors support a world ID, `world.ID`, `pc.character`, `capability.ID`, `task.ID`, and `research.ID`. The convenience alias `character` retrieves the PC only if no world record has that ID; `pc.character` is unambiguous. The packet identifies unloaded details and exact retrieval references. `history --turn 0` retrieves accepted setup and its opening; later history calls preserve exact accepted prose and separate subsequent same-turn correction notes.

The ordinary context packet includes at most ten compact closed-record entries and reports total, remaining count, and a retrieval command. `records --query TEXT --kind KIND --status STATUS --offset N --limit N` searches and pages through the full world index in stable ID order. Filters accept an exact kind/status; status aliases `open` and `inactive` select active/blocked or settled records respectively. Text search covers record fields, so details omitted from a context packet remain discoverable. API: `record_index_packet(store, query='', kind=None, status=None, offset=0, limit=25)`. Pagination changes only the read result; it never deletes or closes a record.

`roll --sides 20 --count 1` remains a public random-number helper for compatible legacy campaigns. It saves nothing, uses `secrets`, and makes no claim of secret precommitment or resistance to rerolling. Fix stakes before rolling. It does not convert adjudicated Blood & Gold ratings into dice bonuses.

Initialize input: `{request_id, state}` with optional nonempty `opening_narrative`. The opening is retained in the setup input, not inserted into historical state. Turn must be 0, alive true, death null, resume_note null. All required state fields are explicit. Setup is excluded from ordinary turn numbering. Committed state must have no overdue active tasks. Story `start` accepts its staged setup only when no accepted setup exists; it does not reset a campaign or invent Turn 1. When `opening_narrative` is present, story validation requires `opening.md` to contain the same text, apart from an optional final newline.

Legacy turn input: `{request_id, expected_hash, expected_turn, elapsed_seconds, objective, outcome, narrative, resources_delta, changes, evidence, processed_tasks, checks, review}`. Workflow version 1 rejects this route; its compact input is defined above. Required nonempty objective/outcome/narrative; positive integer elapsed_seconds; expected_turn must match current turn. resources_delta is integer adjustments per named unit; keys must already exist in resources, or be explicitly introduced with a zero balance in setup/correction. `changes` replaces complete allowed state fields: phase/location/character/relationships/obligations/tasks/knowledge/assumptions/standing_orders/interrupted_plan/alive/death and optional world. Other fields cannot be replaced. `evidence` maps each changed field or resource unit (use `resources.UNIT`) to a nonempty causal explanation. All deltas must reconcile without negative resources. Time and turn are set by the code exactly once.

`processed_tasks` is a map of task ID to nonempty outcome explanation. Every previously active task whose deadline is at or before the ending time requires an entry and must be retained in the resulting task list with a settled status (including blocked) or a future deadline with an explanatory note. New active tasks cannot be overdue. Do not silently delete existing task IDs; settle them instead. These are direct deadline checks, not a simulation of dependent events.

`checks`: list of `{source, roll, skill, modifier, target, total, margin, objective, stakes}`. source is `player` or `tool`; roll is integer 1..20, skill 0..5, modifier -4..4, target integer; total and margin must match arithmetic; objective/stakes nonempty. Require an empty list in adjudicated mode. In real_dice mode allow an empty list for routine/certain actions. Code checks arithmetic, not the honesty of submitted dice or whether a check was necessary. Every consequential result must still be justified by the GM.

`review` is null unless the resulting turn is divisible by 10; then it is required with exact `from_turn`, `to_turn`, and `findings`. `findings` has exactly results/decisions/capabilities/position/gm_consistency/next_constraint. Each is `{assessment: nonempty string, evidence_turns: nonempty list of integers in this ten-turn window}`. Reviews must distinguish facts, inference, and uncertainty and explain both favorable and adverse findings. The engine enforces coverage and references, not the truth of the prose.

Research input: `{request_id, expected_hash, sources}`. Source records have exactly `id`, `claim`, `source`, `type`, `scope`, `confidence`, `limitations`; all nonempty strings. type is canon/secondary/author/historical_analogy/campaign_assumption. URLs or genuinely checked book locators go in source; inventions use `campaign convention` and must identify their assumption. Research IDs cannot be overwritten. Research records do not grant PC knowledge, change time, or advance turns. Use turn knowledge changes for information acquired in-world. Only player-safe research belongs in this store.

Correction input: `{request_id, expected_hash, reason, changes, resources_delta, evidence}`. Reason and evidence are required. Same change rules and resource arithmetic as turns, but no time/turn change and no alive/death change. May introduce a resource unit with a nonnegative delta, including zero, with evidence. This repairs recorded facts without rewriting earlier events. It is not a way to undo a valid loss or death. Corrected state must have no overdue active tasks. Setup campaign metadata cannot be silently changed.

Save export: `{schema_version: 1, events: [...]}` containing the validated complete chain. Restore validates every hash and replays every input to confirm the stored state, including review/deadline checks, before publishing into an empty target; reject nonempty targets and unsafe links/paths. Save includes only what the player-safe store actually knows. It is not a hidden GM export.

That is the low-level/legacy event-save format. Story-mode saves wrap it as `{story_save_version: 1, story_id, shared_files, campaign_save: {schema_version: 1, events: [...]}}`. The wrapper preserves story identity and baseline hashes. Story-mode restore checks the wrapper, selected story ID, pinned references, and current baseline before handing the embedded event save to the unchanged ledger restore. It rejects unwrapped legacy saves rather than silently losing their reference provenance. The wrapper does not contain shared engine/source file bytes or unaccepted local notes; use the complete project package or retained matching repository version for a fully reproducible handoff.

Checkpoint input: `{request_id, expected_hash, resume_note}`. `resume_note` is a nonempty string or null to clear. This event changes only the state's resume_note, without time or turn advancement. Use it to record the authorized action, a pending check's fixed target/modifiers/stakes, and other player-safe resume instructions before a session save. It cannot grant information to the PC or change a capability. The next committed turn clears resume_note automatically; ordinary changes cannot set it. Export/restore and status include the note.

## Draft version checks

Every post-setup mutation requires `expected_hash`, the hash of the latest validated event when the input was prepared. For a new request it must match the current event hash. Check exact request-ID retries first so a successful request remains safely repeatable after later events. Replay also checks expected_hash against the immediately preceding event. `head` prints the current event hash and fails when awaiting setup. A research, correction, or checkpoint event changes this hash even when the turn stays the same. A stale draft must be reconciled against current state, not merely stamped with the new hash.

## User workflow

The user can speak naturally: Start campaign, Status, Save, Review, Continue the journey, Advance one week. AGENTS.md directs the GM to handle JSON, commands, checks, and coherent Git commits. Do not ask the user to maintain the ledger manually. An unconfigured repository is explicitly awaiting setup, not Turn 1. Templates and examples are never live campaign facts.

## Generated reading views

`python -m iron_engine --story <id> render` validates that story's chain and writes `README.md`, `latest.md`, numbered `turns/` pages, `story.md`, `character-sheet.md`, `resume.md`, `threads.md`, and `world.md` into its own `play/` directory. Files identify their source hash. Historical turn pages reference their accepted event instead of changing with each new global head. Only changed file bytes are written. No events or clocks change. The story preserves accepted narrative and places correction notes outside it; current views derive from latest state. Empty stores produce awaiting-setup views.

The turn reader uses accepted ending state for its compact Name/Age/Condition/Location header. It derives a changed-only Ledger from actual before/after differences and accepted evidence, including resource deltas and Condition changes, separately from the unchanged scene text. It omits that Ledger for elapsed time alone, zero deltas, and unchanged replacements. Condition can show rating, label/band, tags, and basis when present; absence remains not established. Scene prose contains no numerical Capability explanations or mechanical outcome labels. A player-facing Ledger shows only material persistent changes and is omitted when empty; no unsolicited options menu is added. The GM follows [the output template](../templates/turn-output.md) and [narrative guidance](../rules/narrative.md). Required public checks, reviews, source notes, and save reports stay outside scene prose.

Generated views are not canonical and must not be hand-edited to change state. The renderer refuses unsafe output targets and overwriting unrelated existing files. Regeneration may be retried after failure without resolving an action again. Publish accepted events and refreshed views together; verify remote publication separately. A view's presence is not proof of a successful GitHub commit.

The GM supplies accepted prose once. After verified publication, its chat response normally contains only the completed turn and reading link. A chat transcript, old example campaign, hand-edited reading page, or unaccepted working draft never supersedes the selected story's validated records.
