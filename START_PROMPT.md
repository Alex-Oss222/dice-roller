# Starting prompt

Copy this into a chat with repository read/write access and the ability to run the included Python engine:

> Use https://github.com/Alex-Oss222/dice-roller on current main. I am starting story-001 from zero. First follow AGENTS.md and the story's scoped instructions, then validate the shared baseline, current character sheet, setup.json, opening.md, setup decisions, and generated awaiting-setup views. Confirm that story-001 has no accepted campaign events. If any accepted event exists, stop and tell me instead of resuming it. If the story is clean, run the actual repository start command so the prepared opening is accepted as Turn 0 and the engine regenerates the reading pages. Publish the Turn 0 event and generated views together, verify the remote commit/checks, give me the reading link, and wait. Do not choose Eddard's actions, do not resolve Turn 1, do not skip ahead, and do not hand-build event hashes or reading pages outside the engine.

After reading the opening:

> Continue story-001. My decision is: [describe what I attempt and the intended duration, if relevant]. Resolve only the authorized activity. Follow the shared narrative and turn-output contracts, update every affected record, preserve the actual pending next decision, run the engine advance workflow, publish the accepted turn and regenerated views together, verify them, and give me the reading link.

The opening is Turn 0. The first resolved player action is Turn 1.
