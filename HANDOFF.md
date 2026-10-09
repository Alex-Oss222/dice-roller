# Project handoff

Use this file to continue development in a fresh chat without redesigning the project from scratch.

## What I want

I want a persistent ASOIAF / Game of Thrones alternate-history roleplaying experience where I make the important choices for my character and the AI acts as a realistic GM and narrative writer.

The experience should feel like a living historical world, not D&D and not an AI game report.

The basic loop is:

1. I say what my character chooses or attempts.
2. The AI loads that story's current character and world state.
3. The AI adjudicates what realistically follows from ability, knowledge, preparation, resources, relationships, opposition, politics, economics, geography, time, and prior consequences.
4. The AI writes the result as natural literary narrative.
5. Only lasting changes that may matter later are saved.
6. The scene stops when I have another meaningful choice.

I do not want numerical RPG clutter, giant skill trees, constant dice, relationship meters, automatic growth scores, or bookkeeping for facts that do not matter.

## End goal

The finished project should support long-running, independent ASOIAF campaigns that can diverge dramatically from canon while remaining internally consistent.

A character should be able to fight, negotiate, marry, inherit, travel, command armies, govern, build roads, ports, mines or settlements, change laws or taxes, develop or ruin lands, create alliances, suffer wounds, die, and alter the political or economic world. Those consequences should persist realistically.

The AI should know how to write the resulting scenes without exposing mechanics or producing formulaic AI prose.

Later, Railway should provide a thin persistent execution/hosting layer around the same simple story model. Railway should not become a second game system.

## Current repository model

Each campaign is isolated:

```text
stories/
  story-001/
    CHARACTER.md
    STORY.md
    WORLD.md

  story-002/
    CHARACTER.md
    STORY.md
    WORLD.md
```

Shared material:

```text
AGENTS.md
rules/
  NARRATIVE.md
  TURN_OUTPUT.md
  COMBAT.md
references/
  ECONOMY.md
  Westeros_283_AC_Economic_Model.xlsx
  NARRATIVE_RESEARCH.md
```

## What has been done

- The old complicated engine/research/report structure was removed from `main`.
- Story 1 is Eddard Stark beginning in 283 AC.
- Story 2 is Jon Snow beginning in 298 AC.
- Each story has its own character, story, and world files.
- The stories are explicitly isolated from each other.
- A shared Westeros economic model is in the repo.
- Story 1 begins with its own qualitative 283 AC economic snapshot.
- Story 2 begins with its own qualitative 298 AC economic snapshot. Neither snapshot claims to be a fully counted treasury, price list, or supply ledger.
- Each story's economy can change persistently because of war, development, trade, taxation, population, infrastructure, harvests, debt, destruction, administration, and player decisions.
- Economic development is causal rather than a generic percentage-growth mechanic.
- A long narrative research document was preserved as source material.
- Compact mandatory narrative rules now control normal scene writing.
- Combat and battle writing have a separate small add-on loaded only when needed.
- `AGENTS.md` tells the GM exactly which files to load for a turn.
- A compact turn-output contract is established: Name, Age, ending Location, turn/date/time, elapsed time, narrative, an optional `Changed this turn` section only for persistent changes, and `Next` only for a real player decision.

## Agenda and current status

Work through the remaining agenda in order. Do not add complexity preemptively.

1. **Complete: clean the character sheets.** Removed Blood & Gold labels, numerical capability and condition scales, domain tables, rating-based adjudication, and progression rules. Retained biography, training, specific strengths, limitations, equipment, relationships, and knowledge. Jon's additional languages remain explicit campaign premises; obsolete links to deleted setup notes were removed.
2. **Complete: establish each opening world state.** Each `WORLD.md` now records the relevant authority, alliances or household relationships, local ground, immediate unresolved situation, and qualitative economic baseline. Unknown troop counts, accounts, prices, routes, and hidden events have not been invented as established facts.
3. **Complete: write each opening scene.** Each `STORY.md` now contains a Turn 0 opening in `rules/TURN_OUTPUT.md` format, with a real pending decision. These are initial situations, not completed player turns. No player decision, execution, battle outcome, or later canon event has been resolved.
4. **Conditional: clarify canon and character knowledge if play exposes ambiguity.** Canon establishes the starting world except for recorded campaign premises; later story facts can permanently diverge. Existing rules already separate GM knowledge from character knowledge. No additional policy file is needed before an actual ambiguity appears.
5. **Next: play-test before building more systems.** Run roughly 5 to 10 meaningful player decisions in at least one story. **Progress: 0 decisions played.** Add a new record or rule only when actual play demonstrates that the existing three story files cannot reliably preserve something important. Confirm that later turns use saved consequences and that the unselected campaign remains unchanged.
6. **Deferred: after the narrative loop is proven, add Railway.** Keep it thin: load story state, serve readable pages/API, support safe persistence, and later add protected writes if needed. The current persistence is the repository's three files per story; no hosted service has been built.
7. **Optional only after play-testing:** add a small narrative validator/editor pass if mechanical language, exposition-heavy dialogue, or repeated AI-style prose continues to leak into saved scenes.

## Next session

Ask the player to choose one campaign and give that character's first response. Load only that campaign for play.

- **Story 1:** Ned is in his command tent beside the Trident at 18:00, before the expected battle. A captain needs orders about two overdue scouts. Two other riders await instructions; one needs a replacement mount. No search has been authorized.
- **Story 2:** Jon is at the holdfast at about 08:00, before the deserter's execution. Bran has asked whether leaving was the man's only offense. Jon has not answered or intervened, and the prisoner is still alive.

Do not simulate the player's choices to mark the play-test complete. Preserve the opening time until the player's response authorizes the scene to proceed.

## Development guardrail

Do not solve hypothetical future problems by rebuilding a large engine.

The project should remain understandable from the repository root. New machinery must earn its existence by solving a problem that appeared during actual play.
