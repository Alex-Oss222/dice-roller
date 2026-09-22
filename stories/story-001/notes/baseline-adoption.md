# Reviewed preparation baseline adoption

Date: 22 September 2026.

The user explicitly requested shared Condition rules and engine integration, placement of supplied writing guidance, and replacement of Story 1's unfilled preparation with the Eddard seed. This is common maintenance and unstarted story preparation, not a ruling to accommodate a played outcome.

Before adoption, Story 1 had no campaign events. It still has none. No initialized history was migrated, reinterpreted, or replayed. No second story exists in this package. Existing shared-drift checks remain enforced; there is no automatic upgrader. Future initialized stories must undergo their own compatibility review before adopting shared changes.

The old manifest is preserved in [baseline-before-condition.json](baseline-before-condition.json). The preceding downloadable project version preserves the old implementation. The manifest's original character-sheet digest remains import provenance for the earlier unfilled document; the new seed does not turn that field into an edit lock. The earlier document remains in source-inputs, and the current root character sheet is the edited Eddard preparation.

New supplied Eddard attachment SHA-256: `be212adeb2c65d6e26ac5371131fbdc803b31d2094ea9c51c2fc45d8565bde80`.

Compatibility review found no legacy hash changes. Condition is optional in older records, requires an evidence basis when present, persists through replacements, and agrees with death status. New narrative rules contain no Story 1 identity or history. The added journal header and changed-only Ledger are derived views, preserving accepted scene text. The book reference file, distance data, and existing browser dice page remain byte-identical to the prior package.

## Shared files changed

| File | Previous SHA-256 | Adopted SHA-256 |
| --- | --- | --- |
| `AGENTS.md` | `aa4cd79aec5a5edb79d15bded000cc6d7aef60cdab544e2f776022e53b7699e2` | `06519bd2a477345f5433d21faefb9cf1c4b3c2174ec76e4219846c53058fe38e` |
| `iron_engine/__main__.py` | `e5f97351c54fbe343193b69f446a4b5d30c1367ab8c42741539592c4379d5128` | `5e1ae00908ba0c520c74a6ec0af8caf8b7fa61a4a490b2dd58177171f563b8c8` |
| `iron_engine/condition.py` | `new file` | `b78e940cfd1f2651f29622278d531d0d3de128d722cb62c7c225a759e72957ed` |
| `iron_engine/engine.py` | `78eb761e8ac92a63514e9abbef369abdc5404afd0150b6c98e7e4446212deef2` | `df969940cf9f3eff5bfaa1d608323f574c8868f3970f1a39d27177fa19e8d27a` |
| `iron_engine/journal.py` | `c28c8bbdf7b8f84d43bfe4729fa8a92ab436f8787f1166c2a3d5007c09e6ada8` | `3307176bb5fe7e6ed449d60bc44b3ebff3d0f9203c3c3463c0d6b8f8b2085d0a` |
| `rules/condition.md` | `new file` | `f04b048e3e32fd6d7991d71a417d8306d32e1bada10bf5a7f2b6e3969af6c65d` |
| `rules/iron_engine.md` | `b2574762bf40259dd2ec00bed22c746bf8b2e258c854146bd5dabe36924b9f5d` | `0d04dffcde3a897347e5cf4f559bc55ece1c892a38b005c6bd5878bcfea8cf5c` |
| `rules/narrative.md` | `new file` | `d8111ad8675c5dc6fa1470d43d06430303e972b5440de8d60706d189fa351f8f` |

These exact adopted hashes are now in `../story.json`. The old and new records make this preparation upgrade explicit; they do not authorize a later pin edit merely to bypass a blocked turn.
