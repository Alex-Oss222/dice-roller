# Project handoff

Read this first, then `AGENTS.md`. Continue the existing project.

## Purpose

Build a persistent, literary ASOIAF alternate-history roleplaying experience. The player makes the character's meaningful choices. The GM resolves attempts through established competence, knowledge, intentions, resources, opposition, circumstances, and prior consequences, then writes the resulting events as fiction.

Book continuity supplies the foundation and scale; future events can diverge. Useful quantities belong in the world. Avoid RPG scores, constant rolls, menus, and unnecessary bookkeeping.

## Working model

Each campaign has three live files:

- `CHARACTER.md`: the character's established identity, experience, limits, and current condition.
- `WORLD.md`: lasting facts, relationships, obligations, resources, and unresolved business.
- `STORY.md`: accepted scenes.

`AGENTS.md` owns the general adjudication and saving instructions. `rules/NARRATIVE.md` and `rules/TURN_OUTPUT.md` govern scene writing. Load combat and economic references when relevant. Source profiles and archives provide evidence, not competing game instructions.

Use a plain repository-enabled chat for this project. Save accepted scenes and material changes during play when writes are available. Otherwise preserve the conversation and reconcile the player's chosen batch before changing chats. Five turns is a review interval, not a memory limit.

## Current status

- Story 1: Eddard Stark, 283 AC, at its Turn 0 opening.
- Story 2: Jon Snow, 298 AC, at its Turn 0 opening.
- Story 3: Jon Stark from 487 AC in Cregan Stark's body in 126 AC. Turns 1 through 5 are imported; no sixth turn has occurred. The full profile is inside Story 3 and its legacy scores are inactive.
- The original [Story 3 transcript](stories/story-003/ChatGPT-Play%20Story%20003-20261009-0251.md), source profile, economic workbook, and narrative research are preserved.
- Railway is a documented proposal in [RAILWAY.md](RAILWAY.md). No application or deployment configuration has been built for it.

## What the first batch established

The reviewed chat carried deadlines, delegation costs, travel, NPC doubts, bodily adaptation, negotiation, and player-directed consequences through five turns. Its presentation repeatedly used action menus, citations inside scenes, and administrative narration; it also paraphrased the saved opening. The transcript came from a custom RPG chatbot, but its unavailable configuration has not been proven to cause every issue.

The import retained the opening and played events, removing citation wrappers, two setup notes, and ending menus from the reading copy. The archive remains intact.

The shared guidance now expresses one general adjudication principle. Domain references supply circumstances, quantities, and consequences. These instruction changes still need ordinary play to demonstrate their effect. Fresh-chat continuation, consequential spending, and battle-loss accounting have not yet been tested in this campaign.

## Next play session

Continue Story 3 from its live files and linked source profile. Do not replay Turn 0 or use the full transcript unless a discrepancy needs reconciliation.

Current scene: the evening of the 26th day of the fourth moon, 126 AC, in Winterfell's working chamber. Arra has delivered her inquiry and warned that staff fear punishment through the audit. Jon has not replied. Read `WORLD.md` for the settlement, deaths, absent people, completed appointments, and outstanding work.

One premise remains unresolved: the opening placed Arra before marriage to Cregan, while the player called her his wife. The GM explicitly retained the unmarried interpretation without confirming the player's intent. Ask whether they were already married at the opening before relying on marital status. Preserve played events; do not invent an intervening wedding.

Then resume and wait for the player's action. Let resource commitments, the Moat survey, and wider consequences arise from play. Missing useful quantities may be established consistently under the existing rules; do not prolong audits merely to avoid giving amounts.

Deliberate false-memory and campaign-isolation probes are optional and outside canon. The player reports a longer previous campaign that retained numbers; its log has not been reviewed here. No fixed turn count guarantees or disproves continuity.

## Development agenda

1. Apply the general adjudication and writing guidance in ordinary continuation. Fix observed problems at the appropriate shared rule, without accumulating action-specific exceptions.
2. Verify that a fresh chat uses the current saved situation and that material changes persist. Keep all campaigns independent.
3. Review the Railway proposal before implementation: choose the playing interface, establish a usable read/write connection, and agree on the initial scope and running cost.
4. Build the smallest authorized service only if it removes demonstrated loading, saving, or access friction. Retain one authoritative campaign store.
5. Consider further validation or infrastructure only when an observed problem warrants it.

Do not simulate player decisions, advance time during maintenance, or turn hosting into a second game system.
