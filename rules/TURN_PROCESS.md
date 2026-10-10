# Turn process

Use this process for every accepted player turn. The purpose is to keep the prose, character state, world state, and Git history consistent.

## 1. Open one consistent repository snapshot

1. Select one campaign only.
2. Record the current `main` commit before reading campaign state.
3. Read that story's `CHARACTER.md`, `STORY.md`, and `WORLD.md` from that same commit.
4. If `CHARACTER.md` links a source sheet, read it for established background and limits. The live story files govern the current date, body, location, authority, possessions, knowledge, and consequences.
5. Read `rules/NARRATIVE.md` and `rules/TURN_OUTPUT.md`.
6. Read `rules/COMBAT.md` and economic references only when relevant.
7. If the selected story links a future-event calendar, read it from the same commit. Its baselines describe possible future history; the live story and world records determine what has actually happened.

Do not combine state from different commits or campaigns.

## 2. Establish the authorized action

Identify what the player is attempting, how they are attempting it, and how much action or elapsed time the instruction authorizes.

A stated desired result is not proof that it happens. A long-term plan does not authorize skipping every later decision required to carry it out.

## 3. Adjudicate before writing

Determine what follows from the character's established ability, knowledge, preparation, authority, relationships, resources, opposition, timing, geography, material limits, and prior consequences.

NPCs act from their own knowledge, interests, obligations, judgment, and means. Do not manufacture resistance or cooperation merely to prolong the plot.

### Conditional events during elapsed time

When the selected campaign has a future-event calendar, use it before resolving any passage of time:

1. Identify the authorized start and end, due dates or windows, ongoing threats and reports in transit. Do not advance time merely to reach an event.
2. Process events in causal and chronological order. If a baseline remains viable, let it proceed even outside the player's view. If its prerequisites changed, determine what now happens and reassess affected descendants. Date order overrides an outline's topic order.
3. Preserve uncertainty. For year-only or seasonal events, use the calendar's scheduling guidance to record a plausible working date or narrower window as play approaches it. Label this as a campaign assumption; do not silently invent canon precision or postpone viable events forever.
4. Adjudicate actual attempts, defenses, resources, losses and outcomes. Historical deaths and victories are not automatic. A general period summary and its component events must not apply the same consequence twice.
5. Keep an event's occurrence separate from when news reaches the character. Stop if the next consequential action is the player's to choose; a historical counterpart's choice is not authorization.

Changes can accelerate events as well as delay or prevent them. Plans alone do not establish successful intervention. Use existing preparation and accomplished work from the live state when assessing effects.

Do not show scored comparisons or mechanics to the player.

## 4. Write the complete narrative scene

Write the scene under `rules/NARRATIVE.md` and format it under `rules/TURN_OUTPUT.md`.

The narrative is mandatory for a resolved turn. Do not replace it with a summary, state update, ledger, explanation of adjudication, or `Changed this turn` list.

Stop at the next consequential choice that belongs to the player.

## 5. Run the narrative gate

Before saving, review the draft against `rules/NARRATIVE.md` and the relevant parts of `references/NARRATIVE_RESEARCH.md`.

Confirm that:

- the scene is fiction rather than a report about the fiction;
- mechanics and adjudication language are absent;
- viewpoint knowledge is respected;
- dialogue follows the speakers' relationship, knowledge, work, and immediate concerns rather than explaining the plot;
- competence and limitation appear through action and consequence;
- practical procedure and material constraints are present where the situation requires them;
- no meaningful player choice was invented or resolved without authorization;
- the ending stops at the real next decision without a forced moral, resonant image, or menu of options.

If the draft fails this gate, revise it before saving. This is a mandatory self-edit, not an optional separate checker.

## 6. Derive persistent changes from the accepted scene

Prepare complete replacement contents for every changed live file before writing anything.

### `STORY.md`

Append the accepted turn exactly once. Do not silently rewrite earlier accepted turns during ordinary play.

### `CHARACTER.md`

After every accepted turn, update the current turn, date, time, and location so they match the end of the scene. Update age when the passage of time requires it.

Update deeper character state only when it changed, such as injury, health limitation, title, office, possession, holding, relationship, knowledge, obligation, authority, reputation, or demonstrated experience.

### `WORLD.md`

Update only lasting external facts likely to matter later, including important NPC changes, political events, army strengths and losses, money, stores, payments, commitments, holdings, development projects, travel, deaths, obligations, economic changes, and canon divergences.

Preserve units, date, location, scope, and whether a quantity is counted, estimated, reported, or an authored assumption.

### Linked future-event calendar, when present

Synchronize its saved turn, date and remaining-time summary with the accepted scene. Update statuses and dated notes for changed prerequisites, working dates, actual outcomes and affected later events. Preserve original baseline dates for comparison. Do not leave resolved events counting down as pending or show an invented exact date for an uncertain event. Where a row groups several events, record partial resolution explicitly.

Save lasting consequences to `WORLD.md` and new character knowledge to `CHARACTER.md`; the future calendar is not a substitute for either. An offscreen event may belong in the world and calendar without entering the viewpoint scene. Save the calendar with the rest of the same coherent turn commit. A same-date turn still requires reassessing any prerequisites changed by the action.

### `HANDOFF.md`

Do not update it for every ordinary turn. Update it at a reset, major development boundary, continuity checkpoint, or when another chat needs a changed premise or current development status.

## 7. Cross-check the save set

Before committing, verify:

- the new turn number follows the previous accepted turn;
- `STORY.md` contains the complete accepted scene once;
- the ending date, time, and location agree across the scene and `CHARACTER.md`;
- elapsed time is plausible and authorized;
- lasting injuries, knowledge, possessions, payments, losses, commitments, projects, and world events are reflected in the correct live file;
- private GM facts have not been added to character knowledge;
- any linked future calendar agrees with the ending date, uses valid countdown arithmetic and reflects due or changed events without forcing player choices or duplicating consequences;
- `Changed this turn` lists only changes actually represented in `CHARACTER.md` or `WORLD.md`;
- `Next` matches the point where the narrative stopped.

## 8. Save one turn as one coherent Git commit

When repository tools allow it:

1. Build one Git tree containing every changed live file.
2. Create one commit with the previously recorded head as its parent.
3. Update `main` only if its head still equals the recorded head.

Do not save `STORY.md`, `CHARACTER.md`, and `WORLD.md` as unrelated sequential commits for one turn. A turn should not exist in a partially saved state.

If `main` moved, inspect the newer commit and reconcile it. Do not force-push, discard unrelated work, reroll the outcome, replay costs, or advance time again.

## 9. Verify before reporting success

Read back the new branch head and the affected files. Confirm that the commit is live and that the accepted turn appears once.

Only then say that the turn was saved.

If the write failed or tools are unavailable, keep the accepted player action and GM result together and label the turn `awaiting import`. Do not claim it is in the repository.

On retry, first check whether the accepted turn already exists. Never duplicate a turn, payment, loss, project advance, or elapsed interval because acknowledgement failed.

## 10. Show the turn and stop

Present the accepted turn using `rules/TURN_OUTPUT.md`, briefly confirm the saved commit outside the fiction, and stop for the player's next meaningful choice.
