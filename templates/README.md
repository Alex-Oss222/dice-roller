# Input templates

Copy the relevant template into `.work/`, then fill it from the player's agreed setup or the GM's resolved result. Codex owns this preparation. Empty required values are intentional: no template should start a fictional campaign or fabricate evidence by accident.

- [setup.json](setup.json): explicit starting facts and resources. Campaign time is seconds from Day 0 midnight; use 28800 for Day 0 at 08:00 if that is the agreed start.
- [turn.json](turn.json): one resolved reply. Complete ordinary substeps within the same turn. Set elapsed time, resource changes, changed state fields, and their causal evidence.
- [review.json](review.json): copy the completed object into the turn's `review` field at turns 10, 20, 30, etc. Supply all six findings and real turn references.
- [research.json](research.json): player-safe source records. Research alone grants the PC no knowledge and advances no fictional time.
- [correction.json](correction.json): an explicit correction of a recorded error. Retrying a failed save should reuse the original turn input and ID instead.
- [checkpoint.json](checkpoint.json): pending check stakes or other player-safe resume instructions, saved without advancing time or granting new knowledge.

Every request ID must be unique within a campaign. An exact repeated request is safe to retry; a changed request using the same ID is rejected. `expected_turn` names the current turn before the new result. Every post-setup input also carries `expected_hash`, captured with the `head` command before drafting. Research, correction, and checkpoint events change this version even when the turn number stays unchanged. Reconcile stale drafts with current state before preparing a new request. Do not reuse IDs across distinct actions.

Resource amounts are integer units keyed by their own names. Establish denominations and rates as sourced facts or explicit assumptions; the engine does not invent conversions. Only a turn or correction changes resource balances. Explain every adjustment under `evidence` using `resources.UNIT` as the key.

`changes` contains complete replacements for changed state fields. Omit unchanged fields. Never place turn, time, campaign metadata, resources, or research directly in `changes`. The code owns counters, resource arithmetic, and research append operations.

When a deadline falls inside a turn, retain the task record, record its disposition in `processed_tasks`, and update its status or explain a new future deadline. For a meaningful interruption, commit the actual elapsed interval and retain the original endpoint or remaining work in `interrupted_plan`.

Examples of checks and tasks are specified in the [record contract](../docs/record_contract.md). Test fixtures are demonstration data and are never live campaign history.
