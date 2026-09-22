# Resolved turn output template

Shared presentation contract for accepted resolved turns. The generated turn page must follow this structure. Apply [narrative guidance](../rules/narrative.md) and the selected story's accepted facts. Replace placeholders; do not show instructional text or empty sections in play. Do not use this template for setup, Turn 0, research, audits, or other OOC-only operations.

| Field | Current |
| --- | --- |
| Name | [Established name and any explicitly established titles used by the story] |
| Age | [Recorded age] |
| Condition | [Recorded 0 to 9 value under the shared Condition scale, or Not established] |
| Location | [Actual ending location] |

## Turn [N] | Day [D], [ending time] | [ending location] | Elapsed: [duration]

[Optional phase line when it helps locate the action.]

### [Scene/event title, only if useful]

[The resolved scene. Write what happened and what the viewpoint could perceive, including supported procedure, dialogue, reactions, and consequences. Capabilities and circumstances shape the result without numerical Capability ratings, calculations, modifiers, or mechanical outcome labels in the prose. Preserve the PC's decisions, dialogue, intentions, loyalties, and interiority for the player.]

[Add another scene section only for a genuinely distinct scene, event, location, or meaningful passage of time.]

### Ledger

- [A material change to persistent state, with enough precision to identify the change.]

[Repeat only for additional actual changes. Record each in the accepted event/current state. Omit this entire section when no material character/world fact changed. Do not print unchanged status, “No changes,” or counters already conveyed by the header.]

### OOC assessment: turns [A] to [B]

[Only when the scheduled review is due. This is separate from the scene and Ledger.]

### Next

[Only the accepted `next_decision` that actually requires player input. Omit when null. Do not offer possible actions, plans, objectives, or menus unless requested.]

## Contract notes

- The four-row summary is part of the generated turn format. The renderer and tests must agree with this file.
- Condition is a separate physical summary, never a Capability bonus or substitute for wound effects. Use [the shared Condition scale](../rules/condition.md).
- The player-facing pending decision is stored in the accepted advance as `next_decision`, copied into current `resume_note`, and rendered here. It is not inferred later from prose.
- Keep dice stakes/arithmetic, requested audits, source notes, and persistence confirmation outside scene prose.
- Save one accepted narrative and its state changes together. A publication retry preserves the same result, costs, time, turn number, and pending decision.
- All examples are placeholders. This file establishes no character, age, Condition, location, or first turn.
