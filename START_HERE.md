# Start and continue

Use a chat that can read and write this repository and run the included Python engine. Give it the [starting prompt](START_PROMPT.md). The chat handles records and commits. You read the story and give your next decision.

## The stories

Story 1, Eddard Stark on the evening before the expected Battle of the Trident, 283 AC, is started: its opening is accepted as Turn 0 and its first resolved decision produces Turn 1. Read its [reading page](stories/story-001/play/README.md) and [current sheet](stories/story-001/play/character-sheet.md); its chosen chronology and starting choices are in [setup decisions](stories/story-001/notes/setup-decisions.md).

Story 2, Jon Snow on the morning of a deserter's execution near Winterfell, 298 AC, is prepared and not started. Read its [character sheet](stories/story-002/character-sheet.md) and [setup decisions](stories/story-002/notes/setup-decisions.md), then say "Start story-002" to accept its opening as Turn 0.

The GM reads the latest accepted state and continues from it; it never initializes an opening twice. The same starting prompt works in a fresh chat after later turns because it checks the repository's current position first.

## Your normal loop

1. Open the story's reading page, then its latest output.
2. Say in chat: "Continue story-00N. My decision is: [what I attempt]." Include the intended duration when it matters.
3. The GM loads current records, starts with your action, applies the specific relevant capabilities, writes the scene once, and submits changes to the engine.
4. The engine updates the relevant pages. The GM publishes the complete result, shows the push proof, and sends the reading link.

The GM stops for a real decision. A five-year plan does not authorize skipping the meeting where you propose it. No time passes while you are away. A turn is a saved action interval, not a fixed week.

The turn output follows [the template](templates/turn-output.md): the four-row summary, turn, ending time and location, elapsed duration, the scene, and a real pending decision when needed. Competence appears through what the character notices and does. Stat changes, lasting consequences, travel progress and assessments update the separate records. Turns 10, 20, 30 and so on receive an evidence-based assessment in `play/changes.md`; improvement is earned and recorded, and an ability rises at most one rating between assessments.

## Finding things

Every story has the same pages under `stories/<id>/play/`, listed in [the record contract](docs/record_contract.md#generated-reading-views): `README.md` is the reading index, `latest.md` the latest scene, `turns/turn-000000.md` the opening and `turn-NNNNNN.md` each accepted turn, `story.md` the whole story in order, `changes.md` time elapsed and material updates grouped by turn, `character-sheet.md` the current character, `decisions.md`, `threads.md`, `world.md` and `resume.md` the current records. `campaign/events/` is the authoritative history.

The starting sheet and setup.json are preparation inputs; accepted events determine current state after setup. The turn header tells you how much time passed in that turn and where the character ended; `changes.md` keeps the running total since the opening. A captured prince or an unexpected death remains part of that story's world; a one-off speech needs no follow-up unless it creates a lasting effect.

## A fresh chat

Say: "Use Alex-Oss222/dice-roller. Continue story-00N from its saved state. My next decision is: [action]. Follow AGENTS.md and publish the updated turn."

The model gets a focused packet of current facts and relevant records; Python validates the full history without putting it all into the chat. To pause, say "Save story-00N and stop." A failed upload is retried with the accepted result; your action is not played again.

## Other stories and later expansion

An independent story begins with its own supplied sheet and `create-story NEW-ID --character-sheet FILE`; see [story boundaries](stories/README.md). A successor after a character's death uses `create-successor`, described in [the record contract](docs/record_contract.md). Neither inherits another story's events, money, relationships or knowledge.
