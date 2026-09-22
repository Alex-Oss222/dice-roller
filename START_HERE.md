# Start or continue a story

Play in chat. Name the story and describe what its character attempts. The GM reads that story's files, researches relevant uncertainties, resolves the action, writes the scene, and saves the result. You do not need to edit JSON or run Python.

## Two layers

**The shared base** contains the engine, common play rules, optional capability rules, [book reference catalog](references/books.md), and distance data. These serve separate stories. The book catalog contains reference information and source policy, not bundled ebook texts or a promise of source access.

**Each story folder** contains that story's own character, history, assumptions, journal, and saves. A new character starts from its own supplied sheet. It does not inherit another story's NPCs, claims, relationships, outcomes, knowledge, inventions, or special rules.

For the prepared `story-001`, read [its starting sheet](stories/story-001/character-sheet.md) first. It contains the supplied Eddard Stark seed for the evening before the expected Battle of the Trident. It is preparation only, with no setup event or Turn 1. Resolution and capability choices belong to that story's sheet/setup. Availability of the Blood & Gold module does not select it for every future story.

## Where the story goes

- `stories/story-001/character-sheet.md`: starting input, read first and completed before setup. After initialization, it preserves the starting document.
- `stories/story-001/story.json`: story identity and pinned shared-file hashes.
- `stories/story-001/campaign/events/`: authoritative outcomes and state, including research, corrections, and reviews.
- [stories/story-001/play/story.md](stories/story-001/play/story.md): the journal, preserving accepted turn prose.
- [stories/story-001/play/character-sheet.md](stories/story-001/play/character-sheet.md): the current sheet rendered from events.
- [stories/story-001/play/resume.md](stories/story-001/play/resume.md): the saved continuation point.
- `stories/story-001/saves/`: portable full-history saves.

The same layout applies independently to each story ID; see [the layout guide](stories/README.md). Current state follows validated events, not edits to the starting sheet. Story prose appears in chat and its journal. Rendered files identify their source version.

## First session

Say: “Start story-001. Read its character sheet first and ask together for only missing setup facts.” For another character, supply that character's sheet and ask the GM to create a new story folder before play.

Story 1 already supplies its protagonist, era, region, opening premise, aim, adjudicated mode, and spoiler policy. Its proposed Condition is 8, Hale, under the stated healthy starting assumption. No time, recovery, or scene has been resolved.

When you are ready to start, settle only the explicit permitted-book title list and a relative evening clock anchor. The GM prepares the detailed capability metadata from the supplied ratings and flags any unsupported derivation. Do not invent an exact calendar date, purse balance, carried equipment, or future knowledge. Other stories begin from their own sheets and only their own missing facts.

Once agreed, setup is saved as Turn 0 in that story only. The opening situation follows, then Turn 1 after the player's first resolved action. Creating a folder is not initializing its character.

## Turns and references

“Inspect the goods,” “Train and work for a week,” and “Continue the journey” are sufficient. A turn can cover minutes, hours, days, or weeks. The GM stops at meaningful choices and records remaining work. Costs and state changes are saved with the outcome, then readable views are refreshed. Every tenth turn reviews results, decisions, capability, position, and GM consistency.

A story's blocked road, detour, local price, invention, or interpretation stays in that story's notes and accepted assumptions/research. It does not rewrite shared distance or book files. Its manifest pins the common baseline. If shared files change, normal story writes stop; existing history can still be read, rendered, or saved with a warning. Common maintenance requires separate review across affected stories. There is no automatic re-pin, and the GM must not bypass the check merely to continue a turn.

## Pause and resume

Say: “Save story-001 and stop.” The GM checkpoints pending choices/fixed stakes, exports to that story's `saves/` folder, and refreshes its resume view. Saving consumes no fictional time.

Later, say: “Load story-001. Read its starting sheet, validate its records and shared baseline, show where we stopped, and wait for my next action.” The latest event is current state, not the original starting sheet or another story's history.

For a chat without repository access, attach the complete project package. A story JSON save includes its identity, baseline hashes, and events; it does not include actual engine/reference/data files or unaccepted local notes. It therefore needs the matching project or Git baseline elsewhere. A current sheet alone cannot recover earlier scenes or review evidence. Story restore checks identity and baseline and rejects another story's save or a bare legacy engine export.

Use one active copy of a particular story. Reconcile divergent copies before continuing. Separate stories can proceed independently.

## Confirmed saving

The engine writes local files. GitHub publishing requires repository write access, a coherent commit, and remote verification. No unattended upload service runs, and the world does not advance between messages.

The last upload attempt to `Alex-Oss222/dice-roller` failed with HTTP 403, `Resource not accessible by integration`. It did not publish the build. The downloadable package remains the handoff until write access works. A chat reply, local event, or rendered journal is not proof of upload.

After a local result, retry failed publication using that exact result. Do not replay the action, reroll, or charge again. If the current chat cannot write files, the GM provides a clear draft/handoff and states what remains unsaved.
