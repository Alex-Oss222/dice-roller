# Shared input templates

Templates are reusable blank structures, not live characters or campaign facts. Each new story begins with its own supplied character document, read first. The GM prepares that story's input files, for example under `stories/story-001/.work/`. Do not copy another story's populated state. See [the story layout](../stories/README.md).

- [character-sheet.md](character-sheet.md): starting checklist with optional Blood & Gold capability tables. Fill it for the particular character when no more specific supplied document governs. The story-root copy is starting input; the generated `play/character-sheet.md` inside that story becomes the current view after initialization.
- [setup.json](setup.json): explicit starting facts/resources. Select resolution and capability system from that story's own document; any example selection in this JSON is not a global default. The optional [0 to 9 module](../rules/capabilities.md) requires adjudicated resolution. Keep books and spoiler cutoff separate. Empty abilities do not establish incompetence. Time is seconds since Day 0 midnight; 28800 represents 08:00 only if agreed.
- [turn-output.md](turn-output.md): compact player-facing reply with Name/Age/Condition/Location, turn/time, scene prose, a changed-only Ledger omitted when empty, and an actual pending decision. No unsolicited options menus. See [narrative guidance](../rules/narrative.md).
- [turn.json](turn.json): one resolved reply with authorized substeps, elapsed time, resource/field changes, and evidence.
- [review.json](review.json): six findings placed in that story's turn input at turns 10, 20, 30, and so on, citing its real evidence.
- [research.json](research.json): local, player-safe checked sources. Research grants no PC knowledge or fictional time and does not rewrite common references.
- [correction.json](correction.json): evidenced repair of a recorded error. Retry a failed save using its original input/ID instead.
- [checkpoint.json](checkpoint.json): pending fixed stakes or resume instructions, without time or new knowledge.

The setup JSON includes `condition: {rating: 8, tags: ["Hale"], basis: ""}` only as an example of an established normal healthy adult. The empty basis deliberately requires completion. Before use, establish the story's actual physical state and replace rating/tags as needed; do not grant health to a blank character. If overall condition remains unknown, omit the optional summary rather than fabricate a score. Once accepted, it cannot be removed. [Condition rules](../rules/condition.md) define all ratings/tags and retain detailed wound notes separately.

Create a story using its own character file, then select it with `--story ID`. There is no implicit default store. Its `story.json` pins shared-file hashes; do not edit common templates/rules/data or re-pin during play to accommodate one character. Local interpretations and special agreements stay in that story's notes and accepted state.

Request IDs are unique within the selected story. Exact repeats are safe; changed content under the same ID is rejected. `expected_turn` is the current turn before the new result. Post-setup inputs also require the latest `expected_hash` from that story's `head`. Research, corrections, and checkpoints change the hash without advancing the turn. Reconcile stale drafts, rather than replacing expected values blindly.

Resources are integer amounts in distinct named units. Establish rates/conversions as supported facts or explicit local assumptions. Explain each adjustment in `evidence` under `resources.UNIT`. Only accepted turns or corrections change balances.

`changes` supplies complete replacements for changed fields, preserving unchanged details within them. Do not place counters, campaign metadata, resources, or research directly there. The engine owns counters, arithmetic, and source appends.

Retain due task IDs, record their disposition in `processed_tasks`, and settle their status or explain a future deadline. For interruptions, commit actual elapsed time and preserve the endpoint or remaining work in `interrupted_plan`.

See [the record contract](../docs/record_contract.md) for exact schemas. Rule examples and test fixtures are never live story history.
