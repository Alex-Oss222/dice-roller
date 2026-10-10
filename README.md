# Iron Engine

Narrative guidance and persistent memory for an ASOIAF role-playing chat.

The role-play happens in chat. This repository stores what happened and what remains true so the next turn or a fresh conversation can use the saved facts.

You choose what your character attempts. The GM resolves what follows from the people, their capabilities and knowledge, the circumstances, and prior consequences. It writes the result as fiction and saves lasting changes.

Book continuity supplies the foundation and scale. Campaign events can diverge. Troop strengths, losses, money, supplies, and time remain meaningful without RPG scores or constant dice.

Each campaign uses three live files:

- `CHARACTER.md` holds the character's established identity, experience, limits, and current condition.
- `WORLD.md` holds current army strengths and losses, money available, spending and commitments, holdings, development projects and their costs, relationships, and lasting consequences. Keep each fact's location, date, and scope clear where they matter.
- `STORY.md` holds accepted scenes, preserving the events behind the current state.

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

### Story 3 · Jon Stark in Cregan Stark's body · 126 AC

- [Character sheet](stories/story-003/Jon_Stark_487_AC_.md)
- [Current character state](stories/story-003/CHARACTER.md)
- [Story](stories/story-003/STORY.md)
- [World](stories/story-003/WORLD.md)
- [Fiscal reference for 126 AC](stories/story-003/references/FISCAL_126_AC.md)

A fresh run from the original opening. The first player action will be Turn 1. `Jon_Stark_487_AC_.md` is the full character sheet; `CHARACTER.md` records his current situation in Cregan's body. The sheet's legacy scores are inactive. Supporting fiscal material and its graphs live in Story 3's `references/` folder.

See [HANDOFF.md](HANDOFF.md) for the current position, unresolved premise, and development agenda.

## Play

Use a plain chat with repository access, without a preconfigured RPG chatbot's additional instructions.

1. Select one campaign and load its current files and relevant rules.
2. Say what the character chooses or attempts.
3. The GM resolves the interaction and writes the events as fiction.
4. Save the accepted scene and material changes.
5. Stop at the next meaningful choice.

Each campaign develops independently. Its own recorded facts govern subsequent turns. Save during play and review continuity and prose after completed Turns 20, 40, 60, and so on. These checkpoints use the existing files and take no fictional time; the procedure is in `AGENTS.md`.

For a new chat:

> Use Alex-Oss222/dice-roller on main. Read HANDOFF.md, then AGENTS.md. Open the current run of stories/story-003 from its latest saved position. Read its CHARACTER.md, STORY.md, WORLD.md, linked character sheet, and required writing rules. Use the live files without importing the retired play-test. If no player turn has been resolved in this run, present the saved opening for my first action; otherwise resume the latest saved situation. Resolve any flagged premise when it affects the scene, and wait for my action. I control Jon's meaningful choices. Do not advance time before my response.

If the chat cannot write, retain both player actions and GM responses from the current run for later reconciliation. Confirm the import before resuming elsewhere.

## Rules and references

- [GM rules](AGENTS.md)
- [Narrative rules](rules/NARRATIVE.md)
- [Turn format](rules/TURN_OUTPUT.md)
- [Combat and battle](rules/COMBAT.md)
- [Economic reference](references/ECONOMY.md)

Each economy begins at its campaign's date and changes through events. The shared workbook informs relationships and scale; its 283 AC figures are not automatically another period's prices or reserves. The GM may establish needed campaign quantities consistently and preserve them.

[Longer narrative research](references/NARRATIVE_RESEARCH.md) is source material, not required reading for every turn.
