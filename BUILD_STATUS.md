# Integration and verification

Repository: [Alex-Oss222/dice-roller](https://github.com/Alex-Oss222/dice-roller). Reviewed 22 September 2026.

## Implemented

The shared base separates engine/state, narrative rules, resolved-turn presentation, travel, and story-owned records. Workflow 1 accepts compact evidenced advances with explicit authorization, adjudication, coverage, deadlines, reviews, long-interval milestones and a player-facing `next_decision`. The accepted pending decision is preserved in resume state and rendered under `Next`.

Generated reading views include the current story, character, resume point, storylines/world records and a derived decision index. The decision index is not a second truth store; it is built from accepted turn events.

Shared baseline drift now covers the active workflow/record contract, travel policy, advance template and turn-output template in addition to the engine, rules, book policy, research policy and distance data. Ordinary story play cannot silently adopt a changed shared contract.

Conservative travel uses the slowest applicable party profile. Daily rest and meals are included by the stated house convention; actual extra delays are added once. The source distance snapshot remains shared and story-local obstacles remain local.

There is still no economy simulator. Numerical resources are established only from actual evidence, and account notes are descriptive. Unknown balances remain unknown until a future shared economy module or in-story evidence establishes them.

## Story 1

Story 1 has its accepted Turn 0 setup and a transparent Turn 0 correction incorporating the player's latest uploaded character sheet. No resolved Turn 1 exists. The correction preserves the original setup event, applies the changed abilities and leather/mail inventory, and accepts an opening stripped of mechanical commentary. The campaign clock remains at Day 0, 18:00, mapped to the chosen first day of the first moon, 283 AC.

The uploaded sheet is preserved as source input. Learning and Craft totals and Development denominators are recalculated; Diplomacy anchors reflect the uploaded mediation strength. The current sheet is generated from the corrected state. Shared presentation changes do not alter another story's character, distances or history.

Narrative pages contain only the agreed presentation. Detailed changes, time accounting and assessments have their own page. Focused context follows related persistent divergences even after their immediate follow-up has closed. Journey distances require explicit accepted records; the renderer does not infer mileage from location names.

## Verification

The GitHub workflow runs the complete Python test suite and story validation. Story validation checks the selected baseline, validates staged setup in a disposable store, and renders the staged reading views without touching the live campaign.

Tests cover immutable replay, stale-input rejection, exact retries, deadline settlement, authorization, reviews, capability development, Condition, compact operations, resource establishment, typed world records, story isolation, focused context, start/resume behavior, opening/setup synchronization, turn presentation, pending-decision persistence and generated decision indexing.

## Limits

The GM remains responsible for lore, fair causal adjudication, truthful authorization and coherent prose. Schema checks cannot prove literary quality or factual judgment. Records are player-readable; no hidden GM store exists.

The engine saves events and renders views. Publication still occurs through the available GitHub connection and must be verified before completion is claimed. The world never advances unattended.
