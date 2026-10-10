# Turn output

Use this format for every resolved player-facing turn.

The turn output is a reading format, not another source of truth. Persistent state lives in the selected story's `CHARACTER.md`, `WORLD.md`, and `STORY.md`.

## Format

```markdown
| Field | Current |
| --- | --- |
| Name | [current name] |
| Age | [current age] |
| Location | [actual ending location] |

## Turn [N] | [date] | [ending time]
Elapsed: [actual elapsed time]

### [Scene title, only if useful]

[Full narrative scene.]

### Changed this turn

[Only lasting changes created by this turn. Omit this entire section if there are none.]

### Next

[Only the real decision that now requires player input. Omit if there is no pending decision.]
```

## Narrative is required

Every resolved turn must contain the complete literary scene required by `rules/NARRATIVE.md`.

Do not substitute a synopsis, adjudication explanation, state ledger, repository update, `Changed this turn` section, or `Next` prompt for the scene. Out-of-character maintenance and research are not resolved turns and should not be presented as though they were.

The turn header's turn number, date, ending time, and location must agree with the scene and the selected story's updated `CHARACTER.md`.

## Physical profile

The top table stays deliberately small:

- Name
- Age
- Ending location

Do not show Condition, skill ratings, mechanics, holdings, money, relationships, projects, or other ledgers in the header.

The full current state belongs in the story files, not in every turn.

## Changed this turn

This section is conditional.

Show it only when the turn creates a lasting fact that is actually being saved to `CHARACTER.md` or `WORLD.md`.

Use only the categories that matter. Examples may include:

- Holdings
- Money or stores
- Project
- Relationship
- Political position
- Title or office
- Obligation
- Knowledge
- Injury
- Military
- Travel
- Economic
- World event

Do not print a fixed checklist. Do not add "no change" entries.

The section is a concise reading summary of persistent changes. It does not replace the actual state files. Every listed change must match a change actually written to `CHARACTER.md` or `WORLD.md` in the same turn commit.

### Movement

The header already shows the ending location.

Do not add a location change merely because the character walked across a castle, moved between rooms, or made other incidental movement.

Include movement under `Changed this turn` only when the movement itself matters later, such as:

- beginning or completing a journey;
- relocating to another settlement, castle, region, army, or court;
- arriving after consequential travel;
- changing an important route, escort, party, or logistical situation.

## Narrative

The scene itself follows `rules/NARRATIVE.md` and must pass its mandatory narrative gate before saving.

Do not put mechanics, adjudication explanations, state ledgers, or repository language into the prose. Event codes, calendar status labels and countdown notices must not appear in the scene, header, `Changed this turn` or `Next`. Refer to actual developments by their ordinary names. Keep countdown tracking in the calendar; show a separate out-of-character countdown only when the player asks for it.

Keep web and repository citations out of the scene and its Name/Age/Location table. Any essential factual or source note belongs separately and briefly outside the fiction. Play-test counters, import status, and transcript reviews also belong outside the scene.

## Next

Show `Next` only when the scene has reached a real decision the player should make.

Do not provide menus of suggested actions unless the player asks for options. A paragraph listing four possible actions is still a menu. A brief question about the actual pending choice is sufficient.

Do not resolve the pending decision on the player's behalf.
