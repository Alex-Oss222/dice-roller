# Integration and verification

Repository: [Alex-Oss222/dice-roller](https://github.com/Alex-Oss222/dice-roller). Reviewed 22 September 2026.

## Implemented

The shared base separates engine/state, narrative rules, resolved-turn presentation, travel, and story-owned records. Workflow 1 accepts compact evidenced advances with explicit authorization, adjudication, coverage, deadlines, reviews, long-interval milestones and a player-facing `next_decision`. The accepted pending decision is preserved in resume state and rendered under `Next`.

Generated reading views include the current story, character, resume point, storylines/world records and a derived decision index. The decision index is not a second truth store; it is built from accepted turn events.

Shared baseline drift now covers the active workflow/record contract, travel policy, advance template and turn-output template in addition to the engine, rules, book policy, research policy and distance data. Ordinary story play cannot silently adopt a changed shared contract.

Conservative travel uses the slowest applicable party profile. Daily rest and meals are included by the stated house convention; actual extra delays are added once. The source distance snapshot remains shared and story-local obstacles remain local.

There is still no economy simulator. Numerical resources are established only from actual evidence, and account notes are descriptive. Unknown balances remain unknown until a future shared economy module or in-story evidence establishes them.

## Story 1

Story 1 is prepared but uninitialized. There are no accepted campaign events. Its human starting sheet, machine setup and prepared opening are aligned on the authorized steel field harness and other starting equipment. The prepared opening is a substantial Turn 0 scene, but it makes no Eddard decision and resolves no Turn 1 action.

Repository preparation, validation and tests do not start play. The start command requires the prepared opening file to mirror the setup opening exactly and accepts it only when the player explicitly starts the story.

## Verification

The GitHub workflow runs the complete Python test suite and story validation. Story validation checks the selected baseline, validates staged setup in a disposable store, and renders the staged reading views without touching the live campaign.

Tests cover immutable replay, stale-input rejection, exact retries, deadline settlement, authorization, reviews, capability development, Condition, compact operations, resource establishment, typed world records, story isolation, focused context, start/resume behavior, opening/setup synchronization, turn presentation, pending-decision persistence and generated decision indexing.

## Limits

The GM remains responsible for lore, fair causal adjudication, truthful authorization and coherent prose. Schema checks cannot prove literary quality or factual judgment. Records are player-readable; no hidden GM store exists.

The engine saves events and renders views. Publication still occurs through the available GitHub connection and must be verified before completion is claimed. The world never advances unattended.
