# Start and continue

Use a chat that can read and write this repository and run the included Python engine. Give it the [starting prompt](START_PROMPT.md). The chat handles records and commits. You read the story and give your next decision.

## Story 1 is ready for the first decision

Story 1's opening has been accepted as Turn 0. Its [current sheet](stories/story-001/play/character-sheet.md) and [reading page](stories/story-001/play/README.md) come from the saved records. The starting scene is at 18:00 on the first day of the first moon, 283 AC, using the story's chosen chronology. See [setup decisions](stories/story-001/notes/setup-decisions.md). Unknown money and unlisted possessions remain unknown.

Your first resolved decision produces Turn 1. The GM reads the latest accepted state and continues from it; it does not initialize the opening again. The same starting prompt works in a fresh chat after later turns because it checks the repository's current position first.

## Your normal loop

1. Open [Story 1's reading page](stories/story-001/play/README.md), then its latest output.
2. Say in chat: “Continue story-001. My decision is: [what I attempt].” Include the intended duration when it matters.
3. The GM loads current records, starts with your action, applies the specific relevant capabilities, writes the scene once, and submits changes to the engine.
4. The engine updates the relevant sheet, storylines, world records and resume point. The GM checks and publishes the complete result, then sends the reading link.

The GM stops for a real decision. A five-year plan does not authorize skipping the meeting where you propose it. No time passes while you are away. A turn is a saved action interval, not a fixed week.

The turn output contains the four-row character summary, turn/time/location and elapsed duration, the scene, and a real pending decision when needed. Competence appears through what the character notices and does. Stat changes, lasting consequences, travel progress and assessments update the separate records; they are not appended to the scene. Turns 10, 20, 30 and so on receive an evidence-based assessment in `play/changes.md`. Improvement is earned and recorded; reviews do not promise higher ratings.

## Finding things

| File within stories/story-001/ | Purpose |
| --- | --- |
| play/README.md | Reading index |
| play/latest.md | Latest scene |
| play/turns/turn-000001.md | An individual accepted turn |
| play/changes.md | Time elapsed, material updates and assessments, grouped by turn |
| play/character-sheet.md | Current character |
| play/decisions.md | Accepted objectives, outcomes and pending decisions |
| play/threads.md | Active and resolved storylines |
| play/world.md | People, divergences, projects and journeys |
| play/resume.md | Continuation point |
| campaign/events/ | Authoritative history and state |

The starting sheet and setup.json are preparation inputs. Accepted events determine current state after setup. The opening and numbered turns stay readable in sequence; you do not need to maintain the records yourself.

The turn header tells you how much time passed and where the character ended. Journey records keep established distances, progress and delays. A captured prince or an unexpected death remains part of this story's world; a one-off speech needs no follow-up unless it creates a lasting effect. Settled matters leave the active storyline list while their history remains available.

## A fresh chat

Say: “Use Alex-Oss222/dice-roller. Continue story-001 from its saved state. My next decision is: [action]. Follow AGENTS.md and publish the updated turn.”

The model gets a focused packet of current facts and relevant records. Python validates full history without putting it all into the chat. Older scenes and records are retrieved by turn number or stable ID as needed. This saves context without discarding history. There is no fixed token cost per turn.

To pause, say “Save story-001 and stop.” Pending instructions are checkpointed when necessary. A failed upload is retried with the accepted result; your action is not played again.

## Other stories and later expansion

An independent story begins with its own supplied sheet and create-story. Shared sources stay common; story-specific changes stay local. A peasant story does not automatically load kingdom accounts or relationships with major characters.

Projects, account notes, ownership facts and timed obligations can be recorded now. When you provide the North's economy workbook, its reusable calculation rules can be added to the shared base, with each story owning balances, institutions and projects. This build does not invent that missing economy model.

After a character dies, an explicitly requested successor can continue the saved world. create-successor preserves the predecessor's ending state for a new character's preparation. The GM maps surviving world consequences and justifies what the new character inherits and knows. It does not resurrect the predecessor or initialize the new character automatically.
