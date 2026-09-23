# Resolved turn output template

Shared presentation contract for accepted resolved turns. The generated turn page must follow this structure. Apply [narrative guidance](../rules/narrative.md) and the selected story's accepted facts. Replace placeholders; do not show instructional text or empty sections in play. Do not use this template for setup, Turn 0, research, audits, or other OOC-only operations.

| Field | Current |
| --- | --- |
| Name | [Established name and any explicitly established titles used by the story] |
| Age | [Recorded age] |
| Condition | [Recorded 0 to 9 number only, or Not established] |
| Location | [Actual ending location] |

## Turn [N] | Day [D], [ending time] | [ending location] | Elapsed: [duration]

### [Scene/event title, only if useful]

[The resolved scene. Write what happened and what the viewpoint could perceive, including supported procedure, dialogue, reactions, and consequences. Capabilities and circumstances shape the result without numerical Capability ratings, calculations, modifiers, or mechanical outcome labels in the prose. Preserve the PC's decisions, dialogue, intentions, loyalties, and interiority for the player.]

[Add another scene section only for a genuinely distinct scene, event, location, or meaningful passage of time.]

### Next

[Only the accepted `next_decision` that actually requires player input. Omit when null. Do not offer possible actions, plans, objectives, or menus unless requested.]

## Example page

An invented character in an invented situation, shown only so the shape of a complete page is unambiguous. Nothing here is a story fact.

| Field | Current |
| --- | --- |
| Name | Alys Coldwater |
| Age | 31 |
| Condition | 7 |
| Location | The mill road, two miles short of Harrow Ford |

## Turn 4 | Day 2, 15:30 | The mill road, two miles short of Harrow Ford | Elapsed: 5 hours

### The carter's cart

The cart had lost its off-side wheel where the road dipped to the stream. Alys walked the length of it before she said anything. The axle was sound; the linchpin was gone, and the wheel lay in the reeds with two spokes cracked.

"You want it lifted," the carter said. He was already looking for a pole.

She did not want it lifted. She had him unload the four hindmost sacks first, then set the pole under the axle box with a flat stone beneath it. The wheel went back on with the cracked spokes to the top. She cut a linchpin from a green ash stick, thicker than the old one, and drove it in with the back of her hatchet. It would hold to the ford and probably to the mill. It would not hold a full load at a trot.

They reloaded three of the four sacks. The fourth she left on the bank with the carter's mark on it. He argued for the length of the reloading and stopped when she gave him her hand to climb up.

The ford was down to knee height. They crossed at a walk.

### Next

The miller offers to buy the whole load at the price he paid last autumn, tonight, cash, or to hold it until the road is repaired and pay the market rate then.

## Contract notes

- The four-row summary is part of the generated turn format. The renderer and tests must agree with this file.
- Condition is a separate physical summary, never a Capability bonus or substitute for wound effects. Use [the shared Condition scale](../rules/condition.md). Do not append tags, bands or a mechanical explanation to its number here.
- This is the complete reading-page format. Do not append a Ledger, assessment, capability list, source/hash stamp, validation message or save report. The scene must show competence and limitations through action, perception and consequence.
- Material changes, precise stat updates, time accounting and scheduled reviews are saved and rendered separately in `play/changes.md`; current character/world/thread pages update from the same accepted state. Keeping them out of this output does not make them optional.
- The player-facing pending decision is stored in the accepted advance as `next_decision`, copied into current `resume_note`, and rendered here. It is not inferred later from prose.
- Keep any required public dice stakes/arithmetic, requested audits, source notes, and persistence confirmation outside this narrative page. Adjudicated stories do not invent dice.
- Save one accepted narrative and its state changes together. A publication retry preserves the same result, costs, time, turn number, and pending decision.
- All examples are placeholders. This file establishes no character, age, Condition, location, or first turn.
