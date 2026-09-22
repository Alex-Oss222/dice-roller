# Campaign architecture

This document maps the active contracts from a player prompt to a published reading page. It is explanatory; normative behavior lives in the pinned engine, rules, workflow contract, travel policy/data, and turn-output template.

## Shared base

Every story uses the shared Iron Engine for immutable events, replay, time, authorization, typed state changes, deadlines, reviews, rendering and retry safety. Shared narrative rules govern viewpoint, agency and prose. The shared turn-output template governs resolved-turn presentation. Shared travel code plus the distance catalog provide common sourced distances and conservative estimates. Capability and Condition rules are optional shared systems selected by a story.

There is no economy simulator yet. `resources` records only explicitly established integer balances, and `account_note` world records are descriptive. Unknown money remains unknown. A future economy module should add common calculation rules without moving story-owned balances, prices, institutions or projects into shared state.

## Story-owned state

Each story owns its character preparation, selected systems, setup/opening, accepted event chain, local assumptions, people, relationships, storylines, divergences, projects, journeys, resources and consequences. Ordinary play changes only that story. Shared baseline hashes prevent a rule or presentation change from silently altering an existing campaign.

`campaign/events/` is the sole authoritative live history after setup. Root preparation files and `notes/` remain provenance. `play/` is disposable generated reading material.

## Prompt to published output

1. Select the explicit story.
2. If unstarted, read its starting sheet, scoped instructions, setup, opening and setup decisions. Validate the pinned shared baseline and exact opening/setup mirror.
3. If started, validate the whole event chain and load focused context. Retrieve relevant people, storylines, capability evidence and older turns by stable ID only as needed.
4. Parse the player's authorization into objective, maximum elapsed time and stopping condition.
5. Apply only relevant shared systems, such as research, capabilities, Condition and travel. Do not invoke an absent economy model.
6. Adjudicate the actual result before prose, using character knowledge, capability, preparation, opposition, resources, physical constraints and established world state.
7. Write the scene once under the narrative rules. Identify the real unresolved `next_decision`, or null.
8. Submit one compact `advance` transaction with the current hash/turn, evidence-backed operations, coverage, deadlines, review/milestones when due, and `next_decision`.
9. The engine validates and accepts exactly one event, derives the full resulting state, stores the pending decision in `resume_note`, and renders all reading pages.
10. Publish the accepted event and all changed generated views together in one coherent Git commit. Verify the remote head and checks. A publication retry never re-adjudicates or advances again.
11. Return the reading link and wait for the player's next decision.

## Persistent records

World records use stable IDs. `thread` is the storyline record. `person`, `fact`, `divergence`, `project`, `journey` and `account_note` cover other durable world information. Records close in place instead of being deleted.

Player decisions remain authoritative in accepted turn events through `objective`, `authorization`, `outcome` and `next_decision`. `play/decisions.md` is only a generated index of those event fields. Durable consequences of a decision also appear in the appropriate task, standing order, obligation, relationship or world record.

## Presentation

Turn 0 is setup/opening and does not use the resolved-turn wrapper. Resolved turns use `templates/turn-output.md`: four-row Name/Age/Condition/Location summary, turn/time/location/elapsed header, scene prose, and `Next` only from accepted `next_decision`. Material changes, adjudication, per-turn and cumulative elapsed time, and scheduled reviews are rendered separately in `play/changes.md`.

Story-local instructions may add stricter style or presentation requirements. They cannot weaken player agency, state integrity, source boundaries, or persistence rules.
