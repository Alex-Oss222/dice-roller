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
- Story 1 begins with its own 283 AC economic snapshot.
- Story 2 begins with its own 298 AC economic snapshot.
- Each story's economy can change persistently because of war, development, trade, taxation, population, infrastructure, harvests, debt, destruction, administration, and player decisions.
- Economic development is causal rather than a generic percentage-growth mechanic.
- A long narrative research document was preserved as source material.
- Compact mandatory narrative rules now control normal scene writing.
- Combat and battle writing have a separate small add-on loaded only when needed.
- `AGENTS.md` tells the GM exactly which files to load for a turn.
- A compact turn-output contract is established: Name, Age, ending Location, turn/date/time, elapsed time, narrative, an optional `Changed this turn` section only for persistent changes, and `Next` only for a real player decision.

## What still needs to be done

Do these in this order. Do not add complexity preemptively.

1. **Clean the character sheets.** Preserve their useful biography and established capabilities, but remove old Blood & Gold / numerical capability / progression-system remnants that encourage mechanical play.
2. **Establish each opening world state.** Put only the political, military, geographic, social, and economic facts that actually matter at the start of that campaign into its `WORLD.md`.
3. **Write or confirm the opening scene for each story using `rules/TURN_OUTPUT.md`.** Each `STORY.md` should begin with a proper narrative opening and stop at the player's first real decision.
4. **Clarify canon and character-knowledge policy if play exposes ambiguity.** Canon establishes the starting world; later story facts can permanently diverge. GM knowledge must remain separate from character knowledge.
5. **Play-test before building more systems.** Run roughly 5 to 10 meaningful decisions in at least one story. Add a new record or rule only when actual play demonstrates that the existing three story files cannot reliably preserve something important.
6. **After the narrative loop is proven, add Railway.** Keep it thin: load story state, serve readable pages/API, support safe persistence, and later add protected writes if needed.
7. **Optional only after play-testing:** add a small narrative validator/editor pass if mechanical language, exposition-heavy dialogue, or repeated AI-style prose continues to leak into saved scenes.

## Development guardrail

Do not solve hypothetical future problems by rebuilding a large engine.

The project should remain understandable from the repository root. New machinery must earn its existence by solving a problem that appeared during actual play.
