# Playing from the repository

The player selects a story, reads its output, and gives the next decision. The GM handles research, adjudication, prose, commands, and publication. The repository holds the durable records; the engine applies accepted changes and builds the reading pages. Chat memory is never the source of truth. No server, hosting service, API key, or background process is required.

## Start and continue

The player can say: “Start Story 1 from its character sheet and opening. Save the output in the repository and send me the reading link.” The GM reads that story's `character-sheet.md`, local instructions, staged `setup.json`, and `opening.md`. Do not ask again for supplied facts or turn examples into a character.

Before start, validate that `opening.md` exactly mirrors `setup.json.opening_narrative` and that the prepared opening follows the shared opening guidance in `rules/narrative.md`. Then run the actual repository command `python -m iron_engine --story story-001 start`; do not reproduce its event/hash/render logic outside the engine. Setup is Turn 0. An opening presents the situation for the player's action; it does not authorize invented PC speech, decisions, or a resolved Turn 1. If accepted records already exist, continue from them instead of resetting. The first authorized action produces Turn 1.

For a genuinely new story, `create-story NEW-ID --character-sheet FILE` creates a preparation folder from that character's document. It does not borrow another story's assets, knowledge, history, or choices. Fill only missing essentials before initialization: era, region, permitted books/spoiler scope, character facts, system, starting time/place, and established assets. Unknown quantities remain unknown.

For subsequent turns the player can say “Continue Story 1. My next action is …”. The GM completes this sequence:

1. Validate the selected story and read its focused context packet. Retrieve the people, storylines, capability evidence, or earlier turns the decision needs.
2. Establish the objective, maximum authorized elapsed time, and stopping condition. Research consequential uncertainty and adjudicate from the relevant capability, knowledge, preparation, opposition, and circumstances.
3. Write the narrative once under `rules/narrative.md`, identify the actual pending player decision if one stops further authorized activity, and prepare compact changes with evidence. Account for affected records, due consequences, and any required review or long-interval milestones.
4. Submit one `advance` input with `next_decision` set to that pending decision or `null`. The engine validates it, applies changes once, saves the event and full resulting state, copies the pending decision into the resume state, and regenerates the reading views using `templates/turn-output.md`.
5. Inspect and publish the accepted event and refreshed views together. Verify the remote commit, then reply briefly: “Turn N is saved. Read it here.”

The player does not maintain JSON, copy summaries between chats, or update the sheet by hand. A new chat with repository tools resumes from the saved records. Actual reading and writing must succeed before it reports completion.

## Focused context

The engine validates the complete history internally. The GM does not need every past scene and full sheet in model context on every turn.

```bash
python -m iron_engine --story story-001 context --recent 2 --max-chars 12000
python -m iron_engine --story story-001 context --focus RECORD-ID --recent 1
python -m iron_engine --story story-001 records --status inactive --offset 10 --limit 25
python -m iron_engine --story story-001 record RECORD-ID
python -m iron_engine --story story-001 history --turn 12
```

The packet keeps current identity, physical state, capability ratings, obligations, deadlines, unfinished plans, and all open record indexes available. It includes the first ten compact closed-record entries and tells the GM how to retrieve the rest. `records` can search by text or filter by kind/status and page through the full index. Focused records supply details and links. Recent prose is bounded, with explicit references for omitted text. `--max-chars` limits only those narrative excerpts, not the whole packet or its token count; mandatory state and selected records remain complete.

Use the index to retrieve what matters. Before changing a capability, read its actual evidence/training; before resolving a storyline, read its record and causal history. Retrieve the full ten-turn evidence window when a review is due. Summaries never license invented missing facts. Reuse checked research and browse again for unresolved material questions.

The model writes one narrative and only the changes. Code carries forward unchanged state, renders complete reading views, and writes generated files only when their bytes change. This reduces duplicated input/output without deleting history.

## Turn input and enforcement

Prepared workflow stories select `campaign.workflow_version: "1"` with adjudicated resolution. Complete [advance.json](../templates/advance.json) from current state and submit it with `advance`. Its blank fields are deliberate placeholders, not a runnable example. See [record_contract.md](record_contract.md) for exact fields.

```bash
python -m iron_engine --story story-001 advance stories/story-001/.work/advance.json
```

Each input has the current `expected_hash`/`expected_turn`, a stable unique `request_id`, actual result/prose, and positive elapsed seconds. Operations name expected old values and causal evidence. The engine owns counters and resource arithmetic. It rejects stale drafts, unsupported paths, inconsistent coverage, lost task/record IDs, unsettled deadlines, missing reviews, and time beyond authorization. A research or correction event also makes an earlier hash stale; reconcile the action against current facts instead of merely changing its hash.

Open world records include both active and blocked matters. If their deadline passes, settle them explicitly or record a future deadline with a reason; marking them blocked does not make the obligation disappear. A newly discovered resource amount can be recorded with `resource_establish`, including an established zero. Use `resource_adjust` thereafter. Unknown balances stay unknown until evidence establishes them.

Every turn checks nine categories: character, resources, relationships, obligations, tasks, knowledge, assumptions, plans, and world. Each says `changed` or `unchanged` and why. This does not demand changes everywhere. An unaffected peasant requires no invented noble relationships or kingdom accounts. Code compares coverage to actual changes; the GM remains responsible for the explanation's truth.

Consequential uncertainty identifies the actor and an existing relevant capability, task band, preparation, opposition, risk, and basis. Strong combat skill cannot substitute for weak intrigue. Player foreknowledge is not automatically character knowledge. Preparation can change feasibility without granting universal competence. Routine supported actions need a routine explanation, not invented dice. No success quota, failure quota, or plot armor applies. Code validates the evidence structure, not prose quality or fair judgment.

The full-replacement `turn` input remains for legacy campaigns. Workflow-enabled stories reject it, so it cannot bypass the stricter process.

## Time and assessments

A turn resolves an authorized action or meaningful partial result over seconds, hours, days, weeks, or a longer authorized interval. Narrative length and reply count do not determine time. Discussing a five-year plan at a council authorizes that council, not a five-year skip. Stop at a material new decision and retain unfinished work.

Use the slowest applicable travel profile for the actual party. Routine sleep and food stops are part of the adopted daily-rate convention; add genuine extra delays once. A procession can be slower than a lone traveler. Shared distance data stays unchanged; local roadblocks and detours belong to the story. See [travel.md](travel.md).

Turns 10, 20, and so on require the six-part evidence-based review in that same event: results, decisions, capabilities, position, GM consistency, and next constraint. Support favorable and adverse findings alike. The boundary grants no automatic skill rise, healing, income, or punishment.

An interval of at least 30 days also requires ordered milestones through its endpoint. Account for intermediate progress/failure, expenses/receipts, physical change, training evidence, and news when relevant. Milestones do not replace state operations, due-task settlement, or the tenth-turn review. Use enough milestones for the actual consequences, not two decorative timestamps.

Condition changes when wounds, illness, exhaustion, hunger, treatment, or recovery justify it. Preserve rating, tags, basis, and detailed effects. Training credit requires actual elapsed periods and relevant evidence. An assessment can correctly find no capability improvement.

## Reading pages and continuing records

The story's `play/README.md` is the entry point. Generated views include:

| Page | Purpose |
| --- | --- |
| `latest.md` | Current opening or latest accepted turn |
| `turns/turn-000001.md`, etc. | Individual accepted-turn reading pages |
| `story.md` | Accepted prose in chronological order |
| `character-sheet.md` | Current character and recorded possessions/obligations |
| `resume.md` | Continuation point and pending work |
| `decisions.md` | Derived index of accepted player objectives, outcomes and pending decisions |
| `threads.md` | Active and settled storylines |
| `world.md` | Relevant people, facts, divergences, journeys, projects, and account notes |

Each view identifies its source. The original sheet remains starting input after setup; generated files are never separately editable truth. Correct genuine errors with an evidenced correction event, preserving the original scene. If rendering fails after acceptance, run `render` again without replaying the action.

Stable record IDs and links preserve causes and dependencies. A divergence records what changed, why, and which later assumptions it affects. A project records its stage, commitments, dependencies, and next date when established. Record account/asset ownership and separate personal from household or territorial resources. Numerical balances belong in resources with explicit units; account notes are not a second balance ledger. A later economy sheet can add supported detail without invented prices or wealth now.

Keep closed threads and completed projects in history. Book events require surviving prerequisites; do not restore a defeated threat to match the published timetable. An uploaded old chat, including a 37-turn reference, is not imported campaign state.

## Isolation, publication, and recovery

Shared engine, rules, books, distances, and templates serve every story. Ordinary play changes only `stories/SELECTED-ID/`. A story pins its shared baseline. Drift stops normal mutations for reviewed maintenance; it never authorizes silently changing pins or shared sources. Another story's outcomes do not enter this one.

Exact request-ID retries return the accepted result without another turn, interval, payment, or roll. If publication fails, retain that event and retry publishing it. Never reinitialize, reroll, force-push, or overwrite concurrent work to repair an upload. Publish events and views as one coherent Git change and verify the remote commit before claiming success.

Research, correction, and checkpoint events consume no fictional time. Research grants no character knowledge. A checkpoint preserves pending player-safe stakes/resume details in `resume_note`; a resolved turn clears it. Records are player-readable, with no durable hidden GM store.

Git preserves the event chain. The GM can also export a complete story save every tenth turn, at session end, on request, and after death. Exports belong in the story's ignored `saves/` folder. They need the matching shared baseline for a complete handoff. Restore only into an empty matching destination. Compare the latest confirmed Git commit before treating an older valid prefix as current.

A dead character's record remains final. A successor starts with its own supplied character sheet and explicit continuity from that world's saved state. Private knowledge, possessions, and authority do not transfer automatically. An unrelated Story 2 starts independently.
