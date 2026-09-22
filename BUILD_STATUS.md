# Integration and verification

Prepared for https://github.com/Alex-Oss222/dice-roller on 22 September 2026.

Publication is blocked. GitHub rejected the create-tree write with HTTP 403, `Resource not accessible by integration`. No commit or branch update was performed. The repository's main branch was confirmed unchanged at `f1801a597b375f4178de552a3a89b59850684da7`. Repository metadata reported user write access, but that did not establish the connection's effective write permission. This package contains the finished local build; it is not evidence of a successful GitHub upload.

## Repository integration

The repository originally contained README.md and index.html. The existing Star Wars browser dice page is retained without changes. The Iron Engine is a separate Python and Codex campaign workflow; the browser page does not save campaign records or supply Iron Engine outcome rules.

The build includes integrated campaign rules, research guidance, variable-length turns, per-turn character state, ten-turn evidence reviews, checkpoints, corrections, portable saves, a source-backed travel helper, and a read-only GitHub checks workflow. It requires Python 3.10 or newer with no third-party packages or hosted service.

The originally supplied Blood & Gold framework is organized into a generic setup template and a separate capability reference. Its adjudicated 0 to 9 system has explicit backward-compatible storage, descriptive profiles/languages, domain and provisional-skill safeguards, credited training periods, and Development accounting. Earlier 0 to 5 event hashes remain unchanged. Each story's generated `stories/<id>/play/` folder contains its readable narrative, current sheet, and resume view; before setup these explicitly contain no live character or story. `START_HERE.md` explains chat play and repository persistence.

The base is now shared across independent stories. The engine, reusable rules, book reference index, and unmodified distance catalog remain common. Every story starts with its own character sheet and owns its events, views, local rulings, notes, and saves. CLI state operations require an explicit story ID or legacy store. Output routing and campaign identity checks prevent accidental cross-story writes. Story manifests pin shared reference hashes; portable story saves retain those pins and identity. Reference changes cannot silently affect ongoing play. No automatic baseline upgrader is included; retain the matching project package or Git history for earlier baselines.

`stories/story-001/` now contains the supplied Eddard Stark character seed for the evening before the expected Battle of the Trident. It remains preparation only. Its adjudicated mode, ratings, background, appearance, and opening premise are local to that story. The original attachment and superseded unfilled sheet are archived locally with the story; source checks and the preparation audit distinguish evidence, assumptions, and remaining setup work. No second story was invented. The former root `play/` contained only awaiting-setup placeholders and has been removed. The sheet-specific audit lives with Story 1's notes rather than in the common rules.

No campaign or character state has been initialized. No first scene or Turn 1 was generated. Story 1 has proposed Condition 8, Hale, labeled as a campaign assumption from its healthy starting premise. Explicit permitted-book titles, a relative evening clock anchor, and detailed derived-capability metadata remain setup work for when the player starts.

The shared Condition module implements the supplied temporary physical scale, all tags and functional bands, and an explicit causal basis, separately from skills. Rating 0 must agree with death; a recorded Condition cannot disappear during character replacement. Legacy events retain their original hashes without injected defaults. Ratings do not cause automatic damage, healing, or capability advancement.

The three supplied writing documents are preserved as reference inputs and consolidated into shared narrative and turn-presentation guidance. Name/Age/Condition/Location headers, concrete procedure, player agency, a changed-only Ledger, and no unsolicited action menu are documented. Style targets cannot manufacture failed assumptions, costs, deception, or plot consequences. Story 1's preparation baseline is adopted through the documented shared-maintenance review in its notes; no initialized history was migrated.

## Distance source

The user-supplied ASOIAF Timeline - Vandal Proof spreadsheet was read through Google Sheets on 22 September 2026. The imported snapshot contains 276 road, 91 sea, and 210 raven distances, plus seven labeled road pace profiles. Each distance retains its exact source cell and tab ID. The source workbook was not edited.

Only distance matrices and labeled road rates are imported. Plot timelines, story-specific movement notes, unlabeled rate rows, and the old ship calculator are excluded. Values remain fan-made estimates. Sea and raven matrix units are a documented miles convention, since those matrix headers do not state units. Rate, rest, speed adjustment, and endurance assumptions remain explicit. A lookup never advances campaign time.

## Verification

All 109 tests passed under Python 3.12.14: 32 ledger, 20 travel, 19 capability, 15 journal, 13 story-isolation, and 10 Condition tests. The Condition tests cover validation, custom tags, no automatic recovery, explicit change evidence, death consistency, retained records, capability independence, unchanged legacy hashes, save restoration, and readable views. The additional journal tests check actual changed-only Ledger entries, omission of unchanged data, and preservation of earlier turn prose and changes after corrections. Coverage includes charge-once retries, concurrent writers, stale drafts, deadlines, reviews, death finality, exact legacy hashes, replay/save integrity, source-linked travel, capability and Development accounting, verbatim story rendering, correction/review visibility, and safe output handling. The isolation tests verify that advancing, correcting, rendering, and saving one story leaves another story and shared files byte-for-byte unchanged; they also cover explicit selection, character preparation, identity binding, baseline drift, and version-preserving save restoration.

The earlier complete CLI campaign walkthrough also passed setup, research, checkpoint, variable time, a retried charged turn, ten-turn review, pending-check preservation, save, and restore with identical sheets and hashes. Active documentation links and JSON templates were checked. The reviewed Story 1 baseline matches all shared file hashes and live campaign validation reports awaiting setup. The original character/style attachments are preserved byte-for-byte in their designated source archives.

The included GitHub workflow is configured to run the test suite and campaign validation after publication. It has not run remotely because the upload failed. Other operating systems and Python versions were not exercised locally.

## Boundaries

The GM owns source quality, causal adjudication, narrative consistency, and player agency. The code checks records and calculations rather than proving canon accuracy or impartial judgment. All records are player-readable. Hash links detect inconsistency; Git history or a confirmed save is still needed to identify a valid older prefix as a rollback.

After publication, use the normal repository history to inspect the saved version. Do not edit old event records, invent missing campaign history, or retry a fictional action merely because its upload failed.
