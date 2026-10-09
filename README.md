# Iron Engine

A minimal ASOIAF narrative RPG.

You make the character's choices. The AI GM adjudicates what realistically happens, writes the narrative, and records only lasting changes that may matter later.

No D&D-style rules layer. No giant universal bookkeeping system. No constant dice.

## Stories

### Story 1 · Eddard Stark · 283 AC

- [Character](stories/story-001/CHARACTER.md)
- [Story](stories/story-001/STORY.md)
- [World](stories/story-001/WORLD.md)

Starts with Eddard Stark beside the Trident during Robert's Rebellion.

### Story 2 · Jon Snow · 298 AC

- [Character](stories/story-002/CHARACTER.md)
- [Story](stories/story-002/STORY.md)
- [World](stories/story-002/WORLD.md)

Starts with Jon Snow at the holdfast north of Winterfell on the morning of the Night's Watch deserter's execution.

## Shared rules

- [GM rules](AGENTS.md)
- [Narrative rules](rules/NARRATIVE.md)
- [Combat and battle rules](rules/COMBAT.md)
- [Economic model rules](references/ECONOMY.md)
- [Project handoff / remaining work](HANDOFF.md)

The full narrative research is preserved in [references/NARRATIVE_RESEARCH.md](references/NARRATIVE_RESEARCH.md). It is source material, not something the GM must load every turn.

## Economy

The economic model is instantiated at each campaign's opening date:

- Story 1 begins with a 283 AC economic snapshot.
- Story 2 begins with a 298 AC economic snapshot.

Each story then develops forward from its own opening economy. Player choices can permanently change holdings, production, trade, infrastructure, debt, taxation, population, supply, and other material conditions when the causes support those changes.

## Play

1. Choose one story.
2. Tell the GM what that character attempts.
3. The GM loads that story's character, story, world, and the small rules relevant to the turn.
4. The GM adjudicates first, then writes the result as fiction.
5. Only lasting facts that may matter later are updated.
6. Stop for the next meaningful player choice.

Each story is isolated. One story never changes the other.

Railway will be added later as a thin hosting/persistence layer after the core play loop is proven.
