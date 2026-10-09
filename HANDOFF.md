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

  story-003/
    CHARACTER.md
    STORY.md
    WORLD.md
```

Shared material:

```text
AGENTS.md
Jon_Stark_487_AC_.md  # preserved source profile for Story 3
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
- Story 3 is Jon Stark's consciousness from 487 AC inhabiting Cregan Stark in 126 AC. It is the selected pilot campaign. The user's complete prior-life profile remains at `Jon_Stark_487_AC_.md`.
- Each story has its own character, story, and world files.
- The stories are explicitly isolated from each other.
- A shared Westeros economic model is in the repo.
- Story 1 begins with its own qualitative 283 AC economic snapshot.
- Story 2 begins with its own qualitative 298 AC economic snapshot.
- Story 3 begins with its own qualitative 126 AC economic snapshot. These snapshots do not claim to be fully counted treasuries, price lists, or supply ledgers.
- Each story's economy can change persistently because of war, development, trade, taxation, population, infrastructure, harvests, debt, destruction, administration, and player decisions.
- Economic development is causal rather than a generic percentage-growth mechanic.
- A long narrative research document was preserved as source material.
- Compact mandatory narrative rules now control normal scene writing.
- Combat and battle writing have a separate small add-on loaded only when needed.
- `AGENTS.md` tells the GM exactly which files to load for a turn.
- A compact turn-output contract is established: Name, Age, ending Location, turn/date/time, elapsed time, narrative, an optional `Changed this turn` section only for persistent changes, and `Next` only for a real player decision.

## Agenda and current status

Work through the remaining agenda in order. Do not add complexity preemptively.

1. **Complete: prepare non-mechanical active character records.** Stories 1 and 2 have cleaned sheets that retain biography, strengths, limits, equipment, relationships, and knowledge. Story 3 has a compact current record linked to the user's complete 487 AC profile. That uploaded source remains intact; its legacy scores and progression instructions are explicitly inactive.
2. **Complete: establish each opening world state.** Each `WORLD.md` now records the relevant authority, alliances or household relationships, local ground, immediate unresolved situation, and qualitative economic baseline. Unknown troop counts, accounts, prices, routes, and hidden events have not been invented as established facts.
3. **Complete: write each opening scene.** Each `STORY.md` now contains a Turn 0 opening in `rules/TURN_OUTPUT.md` format, with a real pending decision. These are initial situations, not completed player turns. No player decision, execution, battle outcome, or later canon event has been resolved.
4. **Addressed for Story 3; refine only when needed.** Its character and world records distinguish Jon's prior-life knowledge from Cregan's current body, authority, resources, and personal memories. Book continuity is the foundation, with no predetermined future. The precise transfer assumptions are explicit in `stories/story-003/CHARACTER.md`; unanswered magical or bodily effects remain unestablished until relevant clarification. No separate policy system was added.
5. **Next: play-test Story 3 before building more systems.** The player plans a first batch of five meaningful decisions, then will supply the complete chat log. **Progress: 0 of 5 decisions played.** Five is an initial review point within the original roughly 5 to 10 decision test, not proof by turn count alone. Confirm believable consequences, player agency, remembered state, and campaign isolation. Add a record or rule only for a concrete problem observed in play.
6. **Deferred: after the narrative loop is proven, add Railway.** Keep it thin: load story state, serve readable pages/API, support safe persistence, and later add protected writes if needed. The current persistence is the repository's three files per story; no hosted service has been built.
7. **Optional only after play-testing:** add a small narrative validator/editor pass if mechanical language, exposition-heavy dialogue, or repeated AI-style prose continues to leak into saved scenes.

## Next session

Continue **Story 3**, unless the player explicitly chooses another campaign. Read its three files and the linked `Jon_Stark_487_AC_.md` source profile. The setup references that profile rather than reproducing it.

Turn 0 is ready: Jon has arrived in Cregan's body in Winterfell, shortly after Bennard's imprisonment and before Cregan's marriage to Arra. A steward is awaiting an answer about Bennard's request for a private audience without a clerk. Jon has issued no order.

The player can start in the current chat or open a repository-enabled chat using the prompt in [README.md](README.md). Present the saved opening, then let the player give the first action. That begins Turn 1.

For the planned five-decision batch:

- Keep play in one chat. A meaningful decision is an attempted action or choice whose outcome changes what follows, not merely a message, correction, or explanation.
- Save accepted turns and lasting changes when writing directly to the repository. If playing without writes or using the player's batch-import option, clearly identify the turns as awaiting import and preserve the complete conversation until reconciliation.
- After five decisions, review the supplied transcript, including user actions, GM responses, and corrections. The player can attach it or upload `stories/story-003/PLAYTEST_CHAT.md`; do not create a placeholder log.
- Reconcile accepted events into the three story files before resuming in a different chat. If the log and saved state conflict and the accepted version is unclear, ask about that specific conflict rather than silently overwriting either.
- Report what worked, what failed, what was actually persisted, and the smallest justified next change. After importing the batch, use the next turn in a fresh chat to check that the saved files carry the situation forward without the original conversation. Extend toward ten decisions only if the first batch leaves a concrete issue untested.

Stories 1 and 2 remain at their own Turn 0 openings. Story 3's former-life profile is not a continuation of Story 2 and must not change it.

Do not simulate the player's choices to complete the test or advance fictional time while awaiting a response.

## Development guardrail

Do not solve hypothetical future problems by rebuilding a large engine.

The project should remain understandable from the repository root. New machinery must earn its existence by solving a problem that appeared during actual play.
