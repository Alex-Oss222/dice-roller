# Independent stories

The shared engine, rules, book reference index, and distance catalog live at the repository root. Each story owns everything specific to its character and course of events.

Start with `stories/<id>/character-sheet.md`. This is the story's starting character input, prepared before setup. Create a story folder from its own supplied sheet; never choose a protagonist by copying example data or another story's current state. Once setup is accepted, immutable events own the current character, and `play/character-sheet.md` displays it. The starting sheet remains historical input.

Inside each story:

- `character-sheet.md`: starting character and setup preparation.
- `story.json`: story identity, imported-sheet provenance, and exact shared baseline hashes.
- `AGENTS.md`: instructions scoped to this story.
- `campaign/events/`: authoritative turns, character/world state, reviews, research, and corrections.
- `play/character-sheet.md`: current generated sheet; awaiting setup until initialized.
- `play/story.md`: accepted scene prose in order.
- `play/resume.md`: pending choices and continuation details.
- `notes/`: local planning, source notes, and documented assumptions. Accepted consequences still require an event.
- `.work/`: local drafts, never another canonical ledger.
- `saves/`: portable full saves created on request or at a checkpoint; ignored by Git because events already preserve history.

Story 1 may record a destroyed bridge, different travel route, altered ruler, or special ruling. That belongs only to Story 1. Story 2 still consults the same shared reference baseline and its own circumstances. A local note is not an automatic executable override or a change to the common map. The GM must identify the local assumption when using it and record its actual effects in that story's turn.

The supplied Eddard Stark sheet is staged as `story-001` preparation. His identity and starting premise are supplied, but no setup event, resolved action, or Turn 1 has been created. Additional stories are created only when requested with their own starting sheets. Story IDs are explicit on every operation; no shared active-story pointer is maintained.

Examples from the repository root, using an actual supplied sheet:

```sh
python -m iron_engine create-story story-002 --character-sheet /path/to/its-own-sheet.md
python -m iron_engine --story story-001 status
python -m iron_engine --story story-001 render
python -m iron_engine --story story-001 save turn-010.json
```

Creation prepares files only. It does not parse a sheet into an initialized character. The GM first reads and completes the selected story's actual setup with the player, then commits Turn 0. Save requires an initialized story and a new simple filename. Story-mode output paths are fixed within that story; a caller cannot redirect its sheet or save into another story.

Shared-file changes are detected against a story's recorded baseline before further play. Existing history can still be read, rendered, and exported, with drift reported. Continue on the retained matching baseline or carry out explicit shared maintenance and a reviewed migration. Do not silently rewrite manifest hashes. Hashes identify a baseline but do not archive it; retain the corresponding repository commit or complete project package. There is no automatic baseline upgrade tool.

General shared maintenance is distinct from a story turn. Ordinary story commits contain only paths under their selected story folder. See [the play workflow](../docs/play_workflow.md) and [Start here](../START_HERE.md).
