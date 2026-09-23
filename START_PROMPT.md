# Starting prompt

Copy this into a chat with repository read/write access and the ability to run the included Python engine, replacing `<id>` with the story (`story-001` Eddard Stark, started; `story-002` Jon Snow, prepared):

> Use https://github.com/Alex-Oss222/dice-roller on current main. Follow AGENTS.md and `<id>`'s scoped instructions. Read its character sheet and validate the shared baseline and saved records. If the story has not started, validate its setup and opening, then use the actual repository start command to accept Turn 0. Otherwise resume from the latest accepted state without resetting or replaying anything. Give me the current reading link and pending decision, then wait for my action. Do not choose the character's actions or skip ahead. Publish any accepted updates and generated views together, and verify and show publication (remote head equals local commit) before saying they are saved.

After reading the opening or the latest turn:

> Continue `<id>`. My decision is: [describe what I attempt and the intended duration, if relevant]. Resolve only the authorized activity, following AGENTS.md: action first, then the specific capabilities that causally apply, shown through the scene without naming ratings; the exact turn-output template; changes on the separate changes page; every affected record updated; the actual pending decision preserved; the engine advance workflow; publication verified and shown; then the reading link.

The opening is Turn 0. The first resolved player action is Turn 1.
