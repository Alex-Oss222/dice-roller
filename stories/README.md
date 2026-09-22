# Story boundaries

Shared engine, rules, book reference policy, distance data and templates live at the repository root. Each story owns its character, history, local rules and world changes. Ordinary turns only change that story's folder.

| Story file | Role |
| --- | --- |
| character-sheet.md | Supplied starting character, read first |
| setup.json and opening.md | Prepared setup and opening, accepted only when play starts |
| story.json | Story identity, imported-sheet provenance and shared baseline hashes |
| campaign/events/ | Authoritative immutable events and resulting state |
| play/README.md | Generated reading index |
| play/latest.md and play/turns/ | Latest output and individual accepted turns |
| play/character-sheet.md | Current generated character |
| play/threads.md and play/world.md | Storylines and persistent world records |
| play/resume.md | Continuation point |
| notes/ | Player-safe supporting material, not competing state |
| .work/ | Ignored local drafts |
| saves/ | Ignored portable history exports |

An independent story starts with its own supplied character. It does not inherit another story's events, money, inventions, relationships or private knowledge. Use `create-story story-002 --character-sheet /path/to/its-sheet.md`, then prepare its setup. Creation alone initializes nothing. Story1 is already prepared; start only when requested.

A road closure or local price stays in its story. It does not change shared distances or book sources. The GM records each local assumption and its actual effects. Story selectors and output paths are explicit; there is no global active-character pointer.

After a PC dies, an explicitly requested `create-successor new-id --from-story old-id --character-sheet /path/to/new-sheet.md` prepares a linked continuation. It preserves the predecessor's ending state and hash in notes/predecessor-world.json, without changing the old story or initializing the new one. New setup must map surviving world consequences, clock and deadlines, with explicit inheritance and knowledge attribution. Old death remains final. Independent creation never invokes this transfer.

Shared-file changes are detected before further play. Existing history can still be read, rendered and exported. Retain the matching Git version or perform reviewed shared maintenance; never silently re-pin a story just to bypass drift. Hashes identify the baseline but do not archive its files, so retain repository history.

See [Start here](../START_HERE.md), [play workflow](../docs/play_workflow.md), and [record contract](../docs/record_contract.md).
