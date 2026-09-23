# Shared input templates

Templates are reusable blank structures, not live characters or campaign facts. Each new story begins with its own supplied character document, read first. The GM prepares that story's input files, for example under `stories/<id>/.work/`. Do not copy another story's populated state. See [the story layout](../stories/README.md) and [the record contract](../docs/record_contract.md) for exact schemas; this page only says what each file is for.

- [character-sheet.md](character-sheet.md): the shape of a starting sheet, written as description, with the Blood & Gold rating tables as an appendix. The story-root copy is starting input; the generated `play/character-sheet.md` becomes the current view after initialization.
- [person-record.json](person-record.json): a `person` world record for a figure who may contest the character, with goals, what the character knows, and rated abilities each paired with a `<ability> basis` detail. Delete the `_template` key before use; the engine rejects unknown fields. Required before Turn 1 for every principal opposing figure.
- [setup.json](setup.json): explicit starting facts. `age`, `phase`, `condition.basis` and, for Blood & Gold, `permitted_books` are placeholders that must be filled or validation fails; the empty `condition.basis` deliberately refuses to grant health to a blank character. The `profile` may include `background_details` (Experience prose) and `disposition`. Time is seconds since Day 0 midnight.
- [turn-output.md](turn-output.md): the complete reading-page format with one worked example.
- [advance.json](advance.json): the workflow input. `adjudication.capability` is `{source, key}` and each supporting capability `{source, key, role}`; `authorization.objective` must equal `objective`; empty strings and zero time are placeholders that must be completed.
- [turn.json](turn.json): legacy full-replacement input; workflow-enabled stories reject it.
- [review.json](review.json): the six findings for turns 10, 20, 30 and so on.
- [research.json](research.json): player-safe checked sources; research grants no character knowledge or fictional time.
- [correction.json](correction.json): evidenced repair of a recorded error; at Turn 0 it may also carry `opening_narrative` to revise the opening. Retry a failed save with its original input and ID instead of a correction.
- [checkpoint.json](checkpoint.json): pending fixed stakes or resume instructions, without time or new knowledge; it replaces the whole `resume_note`.

Create a story with `create-story ID --character-sheet FILE`, then select it with `--story ID`; there is no implicit default store. Only `advance.json` and `turn-output.md` among these templates are pinned in a story's baseline. Rule examples and test fixtures are never live story history.
