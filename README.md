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

### Story 3 · Jon Stark in Cregan Stark's body · 129 AC

- [Character sheet](stories/story-003/Jon_Stark_487_AC_.md)
- [Current character state](stories/story-003/CHARACTER.md)
- [Story](stories/story-003/STORY.md)
- [World](stories/story-003/WORLD.md)
- [Conditional future events and countdowns](stories/story-003/FUTURE_EVENTS.md)
- [Current fiscal account for 129 AC](stories/story-003/references/FISCAL_129_AC.md)
- [Historical fiscal reference for 126 AC](stories/story-003/references/FISCAL_126_AC.md)
- [North price book, revised for 129 AC](stories/story-003/references/North_126AC_Price_Book.xlsx)

Resume on **129/01/30, evening, after Turn 12**, in Winterfell's lord's solar. The next player action is Turn 13. The northern works account has closed; Jon has not answered Manderly’s succession letter or decided on a broader second roll. The Mormont and Reed gifts are authorized but unspent. The accepted 124–126 backstory remains in `STORY.md`; Turns 0–12 are preserved separately under `turns/`. The source profile records Jon's former life, and `CHARACTER.md` governs his present situation. No setup step advances time or restarts the 126 opening.

See [HANDOFF.md](HANDOFF.md) for the current position, accepted premise and startup instructions.

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

> Use Alex-Oss222/dice-roller on main. Read HANDOFF.md and AGENTS.md, then one consistent snapshot of stories/story-003: CHARACTER.md, WORLD.md, the STORY.md index and its latest linked turn, the linked character sheet, FUTURE_EVENTS.md, references/FISCAL_129_AC.md, and the required writing rules. Resume after Turn 12 on 129/01/30 in Winterfell's lord's solar; the next action is Turn 13. If a later turn has since been saved, resume that later position. Keep recorded cash separate from estimated annual income and GDP. Use the current monetary values in WORLD and the fiscal account. Keep routine calculations in those records; bring figures into a scene when they affect the action. The old works roll is closed. Mormont’s wharf and stone enclosure and Reed’s stores, landings, boats and food are authorized but unspent. Manderly’s letter and a broader second roll remain unanswered. I control Jon's meaningful choices. Do not replay the 126 opening or advance time before my action.

If the chat cannot write, retain both player actions and GM responses from the current run for later reconciliation. Confirm the import before resuming elsewhere.

## Rules and references

- [GM rules](AGENTS.md)
- [Full turn and save process](rules/TURN_PROCESS.md)
- [Narrative rules](rules/NARRATIVE.md)
- [Turn format](rules/TURN_OUTPUT.md)
- [Combat and battle](rules/COMBAT.md)
- [Economic reference](references/ECONOMY.md)

`rules/NARRATIVE.md` is mandatory every turn. At the first resolved turn in a new chat, and whenever a scene's dialogue, combat, historical institutions, or prose quality requires it, the GM must consult the relevant sections of [the longer narrative research](references/NARRATIVE_RESEARCH.md). The research supports drafting and revision; it is not merely archive material.

Each economy begins at its campaign's date and changes through events. The shared workbook informs relationships and scale; its 283 AC figures are not automatically another period's prices or reserves. The GM may establish needed campaign quantities consistently and preserve them.
