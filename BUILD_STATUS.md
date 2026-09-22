# Integration and verification

Prepared for https://github.com/Alex-Oss222/dice-roller on 22 September 2026.

Publication is blocked. GitHub rejected the create-tree write with HTTP 403, `Resource not accessible by integration`. No commit or branch update was performed. The repository's main branch was confirmed unchanged at `f1801a597b375f4178de552a3a89b59850684da7`. Repository metadata reported user write access, but that did not establish the connection's effective write permission. This package contains the finished local build; it is not evidence of a successful GitHub upload.

## Repository integration

The repository originally contained README.md and index.html. The existing Star Wars browser dice page is retained without changes. The Iron Engine is a separate Python and Codex campaign workflow; the browser page does not save campaign records or supply Iron Engine outcome rules.

The build includes integrated campaign rules, research guidance, variable-length turns, per-turn character state, ten-turn evidence reviews, checkpoints, corrections, portable saves, a source-backed travel helper, and a read-only GitHub checks workflow. It requires Python 3.10 or newer with no third-party packages or hosted service.

No campaign or character has been initialized. Setup uses the player's actual era, region, spoiler cutoff, character, and resolution mode.

## Distance source

The user-supplied ASOIAF Timeline - Vandal Proof spreadsheet was read through Google Sheets on 22 September 2026. The imported snapshot contains 276 road, 91 sea, and 210 raven distances, plus seven labeled road pace profiles. Each distance retains its exact source cell and tab ID. The source workbook was not edited.

Only distance matrices and labeled road rates are imported. Plot timelines, story-specific movement notes, unlabeled rate rows, and the old ship calculator are excluded. Values remain fan-made estimates. Sea and raven matrix units are a documented miles convention, since those matrix headers do not state units. Rate, rest, speed adjustment, and endurance assumptions remain explicit. A lookup never advances campaign time.

## Verification

All 52 tests passed under Python 3.12.14: 32 ledger tests and 20 travel tests, including command-line checks. Coverage includes charge-once retries, concurrent writers, same-turn stale drafts, deadline handling, review requirements, death finality, replay integrity, save/restore, source-cell preservation, mode separation, invalid rates, explicit sea/raven rates, exact second rounding, and travel calculations that leave campaign state untouched.

The earlier complete CLI campaign walkthrough also passed setup, research, checkpoint, variable time, a retried charged turn, ten-turn review, pending-check preservation, save, and restore with identical sheets and hashes. Documentation links and JSON templates were checked. Live campaign validation reports awaiting setup.

The included GitHub workflow is configured to run the test suite and campaign validation after publication. It has not run remotely because the upload failed. Other operating systems and Python versions were not exercised locally.

## Boundaries

The GM owns source quality, causal adjudication, narrative consistency, and player agency. The code checks records and calculations rather than proving canon accuracy or impartial judgment. All records are player-readable. Hash links detect inconsistency; Git history or a confirmed save is still needed to identify a valid older prefix as a rollback.

After publication, use the normal repository history to inspect the saved version. Do not edit old event records, invent missing campaign history, or retry a fictional action merely because its upload failed.
