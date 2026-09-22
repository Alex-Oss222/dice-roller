# The Iron Engine

A repository-based ASOIAF roleplaying campaign. You make decisions in chat. The GM reads the saved story, resolves the action, and commits the scene together with the records it changes. The next chat continues from those files.

**[Start playing](START_HERE.md)** · **[Story 1](stories/story-001/play/README.md)** · **[Starting prompt](START_PROMPT.md)** · **[Costs](docs/costs.md)**

Story 1 contains your Eddard Stark character at the supplied opening before the expected Battle of the Trident. The opening is accepted as Turn 0, and the latest supplied character changes have been reconciled into the saved state. Your first resolved action will be Turn 1. Read the scene, then give Ned’s intended action.

## What gets saved

| Shared by all stories | Owned by each story |
| --- | --- |
| Engine and resolution rules | Character, Condition, knowledge and possessions |
| Book reference policy | NPCs, relationships and storylines |
| Distance catalog and conservative travel helper | Actual journeys, delays and local obstacles |
| Reusable record templates | Divergences, projects, accounts and consequences |

Validated events are authoritative. Python generates the current sheet, numbered scenes, separate changes and time records, storyline records and resume packet. Closed threads remain retrievable. A story's changes never rewrite the common map or another story.

Turns can cover minutes, days or weeks. The engine checks authorized elapsed time, deadlines, affected records and every tenth-turn assessment. Long intervals require milestones. Abilities and Condition change only with recorded grounds. The GM must still judge evidence, uncertainty and prose honestly; software cannot certify realism.

## Running it

The GM needs repository read/write access and a Python execution tool. You do not need to maintain JSON or run commands yourself. No third-party Python packages, API calls, hosted services or background turns are required.

```sh
python -m iron_engine --story story-001 context
python -m unittest discover -s tests -v
python -m scripts.check_stories
```

See [the play workflow](docs/play_workflow.md), [record contract](docs/record_contract.md), [story boundaries](stories/README.md), [travel](docs/travel.md), and [verification](BUILD_STATUS.md). The original unrelated dice page is preserved in [archive](archive/README.md).

The shared catalog preserves 577 source-linked distances and seven road profiles from the supplied [distance workbook](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit#gid=1). It is a fan-made reference snapshot, not a canon guarantee or a live spreadsheet connection. The [book catalog](references/books.md) contains source guidance, not bundled book texts.
