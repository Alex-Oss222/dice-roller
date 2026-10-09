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

### Story 3 · Jon Stark in Cregan Stark's body · 126 AC

- [Current character](stories/story-003/CHARACTER.md)
- [Story and opening decision](stories/story-003/STORY.md)
- [World](stories/story-003/WORLD.md)
- [Complete prior-life profile: Jon Stark, 487 AC](Jon_Stark_487_AC_.md)

Jon retains his own consciousness, memories, personality, knowledge, and experience while occupying Cregan Stark's body and public position. This is the selected five-decision pilot. Book continuity supplies the opening world; subsequent events can diverge.

The opening is placed just after Cregan's removal of Bennard's regency, before his marriage to Arra Norrey. The character file identifies the transfer assumptions. The uploaded profile is preserved as a reference; its legacy capability scores are not active mechanics.

## Shared rules

- [GM rules](AGENTS.md)
- [Narrative rules](rules/NARRATIVE.md)
- [Turn output](rules/TURN_OUTPUT.md)
- [Combat and battle rules](rules/COMBAT.md)
- [Economic model rules](references/ECONOMY.md)
- [Project handoff / remaining work](HANDOFF.md)

The full narrative research is preserved in [references/NARRATIVE_RESEARCH.md](references/NARRATIVE_RESEARCH.md). It is source material, not something the GM must load every turn.

## Economy

The economic model is instantiated at each campaign's opening date:

- Story 1 begins with a 283 AC economic snapshot.
- Story 2 begins with a 298 AC economic snapshot.
- Story 3 begins with a qualitative 126 AC economic snapshot. The workbook supplies modeling relationships, not period-specific figures ready to copy backward.

Each story then develops forward from its own opening economy. Player choices can permanently change holdings, production, trade, infrastructure, debt, taxation, population, supply, and other material conditions when the causes support those changes.

## Play

1. Choose one story.
2. Tell the GM what that character attempts.
3. The GM loads that story's character, story, world, and the small rules relevant to the turn.
4. The GM adjudicates first, then writes the result as fiction.
5. The player-facing turn shows Name, Age, ending Location, time, the scene, only lasting changes when there are any, and the next real decision.
6. Only lasting facts that may matter later are updated in the story files.
7. Stop for the next meaningful player choice.

Each story is isolated. One story never changes another.

## Starting the five-decision pilot

You can play in the current chat or open a new chat with access to this repository. For a fresh chat, use:

> Use Alex-Oss222/dice-roller on main. Read HANDOFF.md, then AGENTS.md. Play stories/story-003, Jon Stark in Cregan Stark's body in 126 AC. Load its three story files, the linked Jon_Stark_487_AC_.md profile, and the required narrative and turn-output rules. Present the saved opening and wait for my first action. I control Jon's meaningful choices. Keep the book-based world persistent and let events diverge through consequences. We will play five meaningful decisions, then review the full transcript.

The opening is Turn 0. Your first consequential response begins Turn 1. Say what Jon attempts, says, asks, or orders in ordinary language. No command syntax is needed.

Keep the five decisions in one chat. Clarifications, corrections, and requests to explain a rule do not count as played decisions. Do not compress several important choices into one GM response just to reach five turns.

With write access, the GM saves accepted scenes and lasting changes as play proceeds. If you prefer a batch import after five decisions, or the play chat cannot write, keep the complete transcript and treat those turns as awaiting import. Do not start a new chat from the older repository state in the middle of that batch.

After the fifth decision, attach the full chat here or upload it to the repository as `stories/story-003/PLAYTEST_CHAT.md`. Include both your actions and the GM's responses, plus corrections that establish which version was accepted. The transcript is review evidence, not a fourth live state file. Review it, reconcile `STORY.md`, `CHARACTER.md`, and `WORLD.md`, and identify concrete problems before building anything else. The next turn can then begin in a fresh chat from those saved files, which checks whether the campaign resumes correctly without relying on the old conversation.

Railway will be added later as a thin hosting/persistence layer after the core play loop is proven.
