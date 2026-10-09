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

The section is a concise reading summary of persistent changes. It does not replace the actual state files.

### Movement

The header already shows the ending location.

Do not add a location change merely because the character walked across a castle, moved between rooms, or made other incidental movement.

Include movement under `Changed this turn` only when the movement itself matters later, such as:

- beginning or completing a journey;
- relocating to another settlement, castle, region, army, or court;
- arriving after consequential travel;
- changing an important route, escort, party, or logistical situation.

## Narrative

The scene itself follows `NARRATIVE.md`.

Do not put mechanics, adjudication explanations, state ledgers, or repository language into the prose.

Keep web and repository citations out of the scene and its Name/Age/Location table. Any essential factual or source note belongs separately and briefly outside the fiction. Play-test counters, import status, and transcript reviews also belong outside the scene.

## Next

Show `Next` only when the scene has reached a real decision the player should make.

Do not provide menus of suggested actions unless the player asks for options. A paragraph listing four possible actions is still a menu. A brief question about the actual pending choice is sufficient.

Do not resolve the pending decision on the player's behalf.
