# Integration and verification

Repository: [Alex-Oss222/dice-roller](https://github.com/Alex-Oss222/dice-roller). Reviewed 23 September 2026.

## Implemented

The shared base separates engine and state, narrative rules, resolved-turn presentation, travel, and story-owned records. Workflow 1 accepts compact evidenced advances with explicit authorization, adjudication (a primary ability and supporting abilities with roles), coverage, deadlines, reviews, long-interval milestones and a player-facing `next_decision`. The engine refuses mechanics inside the narrative, refuses routine mode with no ability when an advance records a death, a lowered Condition or a divergence, caps a trainable rating at one step per event, and validates journey progress keys. The context packet carries each rating with its basis and the turns it has governed, plus the character's disposition; `history --turn N --no-prose` serves a records-only reviewer.

Generated reading views are the ten pages listed in [the record contract](docs/record_contract.md#generated-reading-views). Turn pages follow the template exactly; the changes page groups material updates per turn with plain time and duration; the sheet reads person first with the rating tables as an appendix and a use column.

Shared baseline drift covers the engine modules, rules, `AGENTS.md`, the workflow and record contracts, research and travel policy, distance data, the advance template and the turn-output template (`FIXED_SHARED` in `iron_engine/stories.py`). Ordinary story play cannot silently adopt a changed shared contract; a reviewed re-pin is recorded in each story's `notes/baseline-adoption.md`.

Repository hooks (`.claude/settings.json`, `scripts/hooks/`) block direct edits under any story's `play/` and `campaign/events/`, refuse to end a turn while story validation or the test suite fails, and print the baseline check at session start.

Conservative travel uses the slowest applicable party profile. There is no economy simulator; unknown balances remain unknown.

## Stories

Story 1 (Eddard Stark, Trident eve, 283 AC) is started: Turn 0 setup plus two Turn 0 corrections (the 22 September sheet reconciliation and the 23 September wording rewrite), no resolved turn. Its person records predate the opposition rule and carry no ratings; they are filled at first contested contact.

Story 2 (Jon Snow, the deserter's execution near Winterfell, 298 AC) is started at Turn 0, with opposition and household person records in its accepted setup.

## Verification

The GitHub workflow and the Stop hook run the complete test suite and `scripts/check_stories.py`, which checks every story's baseline, validates staged setups in a disposable store, and renders staged views without touching a live campaign.

Tests cover immutable replay, stale-input rejection, exact retries, deadline settlement, authorization, reviews, capability development and the one-step cap, Condition, compact operations, resource establishment, typed world records and person ratings, story isolation, focused context including the capability index and records-only history, start and resume behaviour, opening and setup synchronization, turn presentation, the narrative lint, the named-ability guard, pending-decision persistence and generated decision indexing.

## Limits

The GM remains responsible for lore, fair causal adjudication, truthful authorization and coherent prose. Schema checks cannot prove literary quality or factual judgment. Records are player-readable; no hidden GM store exists. Publication occurs through the available GitHub connection and must be verified and shown before completion is claimed. The world never advances unattended.
