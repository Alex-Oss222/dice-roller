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
- Story 3 is Jon Stark's consciousness from 487 AC inhabiting Cregan Stark in 126 AC. It is the selected pilot campaign. The user's complete prior-life profile is preserved inside Story 3 at `stories/story-003/Jon_Stark_487_AC_.md`; the root-level copy has been removed.
- Each story has its own character, story, and world files.
- The stories are explicitly isolated from each other.
- A shared Westeros economic model is in the repo.
- Story 1 begins with its own qualitative 283 AC economic snapshot.
- Story 2 begins with its own qualitative 298 AC economic snapshot.
- Story 3 began with a qualitative 126 AC economic snapshot. Its first household audit now supplies specific findings, but no quantified capital budget or complete northern balance sheet. The workbook has not been validated against the played economic findings.
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
3. **Complete: establish openings and preserve played scenes.** All campaigns retain their openings. Story 3 additionally contains imported Turns 1 through 5, ending on the evening of the 26th day of the fourth moon, 126 AC. Its original Turn 0 prose is unchanged. No sixth turn has occurred.
4. **One premise remains unresolved.** The opening assumed Arra was unmarried, but the first player action called her his wife. The GM explicitly retained the friend interpretation without establishing whether the player meant a premise change. Ask that one question before relying on marital status. Other transfer assumptions remain in the character record; Ghost's physical arrival is now an explicit player-authorized exception.
5. **First batch complete and imported; fresh continuation is next.** Five player-directed turns were played, several bundling multiple choices. The coherent-chat run exercised deadlines, delegation, testimony, negotiation, bodily adaptation, execution, and a qualitative audit. It did not test resumption in a fresh chat, quantified project spending, a completed survey, or distant political consequences. Use the next turn to test the imported state rather than repeating the opening or manufacturing more test decisions.
6. **Deferred: after the narrative loop is proven, add Railway.** Keep it thin: load story state, serve readable pages/API, support safe persistence, and later add protected writes if needed. The current persistence is the repository's three files per story; no hosted service has been built.
7. **Optional only after play-testing:** add a small narrative validator/editor pass if mechanical language, exposition-heavy dialogue, or repeated AI-style prose continues to leak into saved scenes.

## Review of the first batch

Reviewed on 2026-10-09 from the [complete uploaded transcript](stories/story-003/ChatGPT-Play%20Story%20003-20261009-0251.md). The archive and the relocated prior-life profile are unchanged. No new state tracker or game system was needed.

**What held up:** Bennard's due answer interrupted the wait for the maester; sending Donnel away narrowed Arra's inquiry; travel did not finish on demand. Arra's assistance did not erase her concern for Cregan. Sympathy for Bennard was distinguished from evidence of disobedience. Jon's experience survived the transfer while his body still required adjustment. His orders, not a forced canon plot, led to Bennard's death and Ghost's arrival.

**What did not meet the writing contract:** the saved opening was paraphrased; all six opening/turn outputs offered unsolicited action menus; citations appeared inside the prose and headers; repeated assurances about what had not been authorized or verified often read like an administrative explanation. No numerical RPG system appeared, but avoiding scores alone did not make every passage natural fiction.

The export identifies a custom RPG GPT and repeatedly shows preparation for four-option endings. Competing instructions are a possible cause of the menu pattern, not a verified diagnosis; its underlying instructions are not available. Prefer a plain repository-enabled chat for the next continuation test to reduce that uncertainty.

**What the import changed:** the original Turn 0 was retained. Turns 1 through 5 were appended with their events and dialogue intact; external citation wrappers, the two source/setup notes outside the scene, and unsolicited ending menus were removed from the reading copy. Brief open questions replace those menus. The original transcript preserves every response and the full review. This was not a prose rewrite or a new played turn.

`CHARACTER.md` and `WORLD.md` now distinguish direct actions and findings from Arra's reported evidence, uncounted amounts, and unanswered requests. The import leaves marital status explicitly unresolved rather than inventing a wedding. The small shared-rule edits reinforce the existing requirements for unchanged saved openings, fiction without citation clutter or administrative narration, and endings without unrequested menus. Their effect still needs testing in actual play.

**Remaining evidence gaps:** no cross-chat memory test or deliberate false-memory check has run. The financial work found useful discrepancies but supplied no spending amounts or priced project. The Moat party, Citadel response, wider returns, sons' later conduct, and broader reaction to the execution remain unresolved. These are future story consequences, not grounds for adding speculative machinery.

## Next session

Continue **Story 3 after Turn 5**, unless the player chooses another campaign. Read its three live files and the source profile linked from `CHARACTER.md`. For the fresh-chat continuation test, do not read the full transcript unless a specific discrepancy requires reconciliation.

First settle whether the player's earlier “my wife” was an intended change making Arra already married to Cregan at the opening. Preserve the played events while making any necessary targeted relationship corrections; do not invent an intervening wedding or force a new marriage choice.

Current scene: the evening of the twenty-sixth, in Winterfell's working chamber. Arra has delivered her local report and warned that household staff fear punishment through the audit. Jon has not replied.

The continuation must retain:

- Bennard is dead, executed on the twenty-second. His sons' witnessed protections, maintenance, and guarded lodging continue.
- Ghost is present. Only Arra has been told Jon's identity claim; her cooperation does not explain what happened to Cregan.
- The maester, Donnel, mason, and groom are still away. The seven-day inspection deadline was explicitly replaced by permission to take the time needed. The Citadel request is unanswered.
- Arra's personal answer and report have arrived; they are not still due. Edrik and Ronnel have not been convicted or dismissed.
- Local audit corrections exist, but no quantified project budget, new tax, major building approval, or comprehensive northern economic account has been established.

Use the [continuation prompt in README.md](README.md). Resume from this position, then wait for the player's next action. Check whether the resulting scene uses the saved facts and uncertainties without needing the old conversation.

Stories 1 and 2 remain at their original Turn 0 states. Their files were not changed by this import. Do not simulate the player's next choice or advance the clock during review.

## Development guardrail

Do not solve hypothetical future problems by rebuilding a large engine.

The project should remain understandable from the repository root. New machinery must earn its existence by solving a problem that appeared during actual play.
