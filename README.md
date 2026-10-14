# Iron Engine

Narrative guidance and persistent memory for an ASOIAF role-playing chat.

Use the [new-chat prompt](#start-a-new-chat-choose-a-story) to choose Story 1, 2, or 3. No story is selected by default.

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

For Story 3, see [HANDOFF.md](HANDOFF.md) for its current position, accepted premise and retained monetary convention. A handoff for one story does not select that story or override your choice of another campaign.

## Play

Use a plain chat with repository access, without a preconfigured RPG chatbot's additional instructions.

1. Choose Story 1, 2, or 3 before loading campaign state, then use one consistent repository snapshot.
2. Say what the character chooses or attempts.
3. The GM adjudicates before writing.
4. The GM writes and self-edits the complete scene under the narrative rules and research.
5. Derive lasting changes from the accepted scene.
6. Save the complete turn and all affected live files in one coherent Git commit.
7. Verify the repository write before reporting the turn as saved.
8. Stop at the next meaningful choice.

The detailed turn and save procedure is in [rules/TURN_PROCESS.md](rules/TURN_PROCESS.md).

Each campaign develops independently. Its own recorded facts govern subsequent turns. Save during play and review continuity and prose after completed Turns 20, 40, 60, and so on. These checkpoints use the existing files and take no fictional time; the procedure is in `AGENTS.md`.

### Start a new chat: choose a story

Copy the whole prompt below into a new chat. It will ask you to choose a story. You can also include "Story 1", "Story 2", or "Story 3" with the prompt to select it immediately.

> Use Alex-Oss222/dice-roller on main. Read README.md and AGENTS.md. Before loading any campaign state, ask me which story I want to play and show these choices:
>
> 1. Story 1: Eddard Stark, opening in 283 AC (`stories/story-001`).
> 2. Story 2: Jon Snow, opening in 298 AC (`stories/story-002`).
> 3. Story 3: Jon Stark in Cregan Stark's body, opening in 126 AC (`stories/story-003`).
>
> If I have already explicitly selected a story in my message, use that selection without asking again. Otherwise, wait for my choice. Do not choose a default or infer my selection from HANDOFF.md, a previous chat, or the highest turn number.
>
> After I choose, record the current main commit and read one consistent snapshot of only the selected story: CHARACTER.md, WORLD.md, STORY.md and its latest active linked turn if it is an index, any linked full character sheet or source profile, any linked future-event calendar, and the applicable fiscal references. Consult HANDOFF.md only for information that applies to the selected story; a handoff about another campaign must not redirect you or supply its state.
>
> Follow the shared AGENTS.md, rules/TURN_PROCESS.md, rules/NARRATIVE.md and mandatory rules/TURN_OUTPUT.md. Consult the relevant narrative research and combat or economic references when required. Resume the selected campaign's latest active saved position, respecting explicit resets and excluding retired runs and superseded import packages. If no player turn has been resolved in the active run, present its saved opening rather than inventing or replaying an action.
>
> I control my character's meaningful choices. Keep each campaign's people, knowledge, resources and events separate. Use its recorded monetary units and distinguish counted cash from annual income estimates and GDP. Do not advance fictional time, resolve my first action, reset a campaign or edit repository files during selection and setup. Once play begins, save accepted turns and affected state together and verify the write before claiming success.

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
