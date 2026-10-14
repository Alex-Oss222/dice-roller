# Iron Engine

Narrative guidance and persistent memory for an ASOIAF role-playing chat.

The role-play happens in chat. This repository stores what happened and what remains true so the next turn or a fresh conversation can use the saved facts.

You choose what your character attempts. The GM resolves what follows from the people, their capabilities and knowledge, the circumstances, and prior consequences. It writes the result as fiction and saves lasting changes.

Book continuity supplies the foundation and scale. Campaign events can diverge. Troop strengths, losses, money, supplies, and time remain meaningful without RPG scores or constant dice.

Each campaign uses three live files:

- `CHARACTER.md` holds the character's established identity, experience, limits, and current record.
- `WORLD.md` holds current army strengths and losses, money available, spending and commitments, holdings, development projects and their costs, relationships, and lasting consequences. Keep each fact's location, date, and scope clear where they matter.
- `STORY.md` holds accepted scenes or indexes their numbered files, preserving the events behind the current state.

A campaign may also link a conditional future-event calendar. It tracks pending historical baselines and countdowns; accomplished outcomes still belong in the live character, world and story records.

The work ahead is to keep these records accurate during play and verify that later chats use them.

## Stories

### Story 1 · Eddard Stark · 283 AC

- [Character](stories/story-001/CHARACTER.md)
- [Story](stories/story-001/STORY.md)
- [World](stories/story-001/WORLD.md)

Begins beside the Trident during Robert's Rebellion.

### Story 2 · Jon Snow · 298 AC

- [Character](stories/story-002/CHARACTER.md)
- [Story](stories/story-002/STORY.md)
- [World](stories/story-002/WORLD.md)

Begins at the holdfast north of Winterfell on the morning of the Night's Watch deserter's execution.

### Story 3 · Jon Stark in Cregan Stark's body · 126 AC restart

- [Character sheet](stories/story-003/Jon_Stark_487_AC_.md)
- [Current character state](stories/story-003/CHARACTER.md)
- [Story](stories/story-003/STORY.md)
- [World](stories/story-003/WORLD.md)
- [Saved Turn 0 opening](stories/story-003/turns/TURN_000.md)
- [Conditional future events and countdowns](stories/story-003/FUTURE_EVENTS.md)
- [Opening fiscal model for 126 AC](stories/story-003/references/FISCAL_126_AC.md)
- [North price book, retained revised monetary scale](stories/story-003/references/North_126AC_Price_Book.xlsx)

Restarted by the player's explicit request on 2026-10-13. Resume at **Turn 0, 126/01/03, morning, Winterfell's lord's solar**. The next player action is **Turn 1**. The accepted 124–126 backstory is retained. The steward and clerk await Jon with routine returns and an unopened White Harbor letter. No setup step advances time or resolves his first action.

The previous run's Turns 1–21 remain in Git history at `5bb34223974fa3b3b3527a30cd8add53e52a92c8` but no longer govern this campaign. The unimported Turn 22 continuation package is retired, not awaiting import. The source profile and writing rules remain; later played campaigns, construction, grants, injuries and magical obligations do not. The development program is an unapproved proposal again. The [old 129 fiscal path](stories/story-003/references/FISCAL_129_AC.md) identifies retired material rather than supplying a current account.

See [HANDOFF.md](HANDOFF.md) for the current position, accepted premise, retained monetary convention and startup instructions.

## Play

Use a plain chat with repository access, without a preconfigured RPG chatbot's additional instructions.

1. Select one campaign and load one consistent repository snapshot.
2. Say what the character chooses or attempts.
3. The GM adjudicates before writing.
4. The GM writes and self-edits the complete scene under the narrative rules and research.
5. Derive lasting changes from the accepted scene.
6. Save the complete turn and all affected live files in one coherent Git commit.
7. Verify the repository write before reporting the turn as saved.
8. Stop at the next meaningful choice.

The detailed turn and save procedure is in [rules/TURN_PROCESS.md](rules/TURN_PROCESS.md).

Each campaign develops independently. Its own recorded facts govern subsequent turns. Save during play and review continuity and prose after completed Turns 20, 40, 60, and so on. These checkpoints use the existing files and take no fictional time; the procedure is in `AGENTS.md`.

For a new chat:

> Use Alex-Oss222/dice-roller on main. Read HANDOFF.md and AGENTS.md, then one consistent current snapshot of stories/story-003: CHARACTER.md, WORLD.md, the STORY.md index and its latest active linked turn, the linked character sheet, FUTURE_EVENTS.md, references/FISCAL_126_AC.md, and the required writing rules. Resume the restarted run at Turn 0 on 126/01/03, morning, in Winterfell's lord's solar; my first action will be Turn 1. If a later turn has been saved after the explicit reset, use that new-run position, not a higher-numbered turn from the retired history. Preserve the accepted pre-opening backstory, full memories, completed physical adaptation, and Arra's prior knowledge of Jon's identity. Keep recorded cash separate from estimated annual income and GDP, and follow WORLD's retained monetary-scale instructions. Do not import the retired Turns 1–22 or the old Turn 22 ZIP. I control Jon's meaningful choices. Keep the mandatory turn output and do not advance time before my action.

If the chat cannot write, retain both player actions and GM responses from the current run for later reconciliation. Confirm the import before resuming elsewhere. An explicit later reset supersedes older awaiting-import packages.

## Rules and references

- [GM rules](AGENTS.md)
- [Full turn and save process](rules/TURN_PROCESS.md)
- [Narrative rules](rules/NARRATIVE.md)
- [Turn format](rules/TURN_OUTPUT.md)
- [Combat and battle](rules/COMBAT.md)
- [Economic reference](references/ECONOMY.md)

`rules/NARRATIVE.md` is mandatory every turn. At the first resolved turn in a new chat, and whenever a scene's dialogue, combat, historical institutions, or prose quality requires it, the GM must consult the relevant sections of [the longer narrative research](references/NARRATIVE_RESEARCH.md). The research supports drafting and revision; it is not merely archive material.

Each economy begins at its campaign's date and changes through events. The shared workbook informs relationships and scale; its 283 AC figures are not automatically another period's prices or reserves. The GM may establish needed campaign quantities consistently and preserve them.
