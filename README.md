# Dice Roller and the Iron Engine

A book-based, solo ASOIAF campaign with researched rulings, flexible turn durations, a current character sheet, and an evidence-based review every ten turns.

The repository's existing [Star Wars browser dice roller](index.html) is preserved as a separate tool. Its traits, advantage options, clamped totals, and outcome tiers belong to its original rules. Use the Python dice helper and [campaign formula](rules/iron_engine.md) below for Iron Engine checks. The browser page does not save campaign turns or update the ledger.

The GM researches and resolves the fictional world. A small Python ledger checks and preserves the results. It runs locally with Python 3.10 or newer and the standard library. There is no hosted runtime, database service, subscription, or background simulation to configure.

## Play through Codex

Open this repository in Codex and say **Start a campaign**. Codex follows [AGENTS.md](AGENTS.md), handles records and commands, and asks together for the missing setup details: era and region, permitted books/spoiler cutoff, character and immediate aim, and adjudicated or real-dice resolution.

No campaign has been started in this repository. There is no default protagonist, house, era, or spoiler cutoff. [Templates](templates/README.md) are deliberately incomplete and are not campaign facts.

During play, speak naturally:

- **Inspect the delivery before accepting it.** Resolve the authorized attempt and update the sheet.
- **Spend a week training and doing my household duties.** Cover the interval, stopping for a meaningful decision if necessary.
- **Continue the journey.** Resume the recorded plan and retain work already completed.
- **Status.** Show the current character and world record without advancing time.
- **Save.** Export the full player-safe record for resuming elsewhere.
- **Review.** Explain the evidence behind results and rulings; the scheduled full review still falls on turns 10, 20, 30, and so on.

A turn may last seconds, hours, days, or longer. Turn count never awards skill growth, healing, income, or political progress. Costs, injuries, obligations, and knowledge update after each resolved turn. The ten-turn review evaluates both the character's decisions and the GM's consistency.

## What is included

- [Integrated campaign rules](rules/iron_engine.md): agency, time, research, dice, prose, consequences, and permanent death.
- [Play and save workflow](docs/play_workflow.md): setup, turns, reviews, corrections, saves, and Git publication.
- [Research guide and checked starting references](docs/research.md): canon, historical analogy, inventions, and PC knowledge boundaries.
- [Travel guide](docs/travel.md) and [distance catalog](data/travel_distances.json): 577 source-linked distance entries from the supplied spreadsheet, with seven road pace profiles and explicit assumptions.
- [Record contract](docs/record_contract.md): precise input and persistence rules for maintainers.
- [Input templates](templates/README.md): setup, turn, review, research, and correction.
- [Ledger implementation](iron_engine/engine.py) and [tests](tests/test_engine.py).

## How records stay consistent

Each saved event contains its input, the entire resulting character/world state, and a hash link to the previous event. Its file is published as one complete record. The current sheet is rendered from the latest validated record, so there is no separately edited sheet that can silently fall behind the turn history.

Every tenth turn requires its evidence-based review in the same event. Retrying the identical request returns the existing result. Reusing its ID with different contents fails. A stale input is rejected even if an intervening correction or research event left the turn number unchanged. A failed write does not authorize a reroll or a second deduction. Missing intermediate records, changed records, or invalid records stop loading with an explicit error.

Hash checks detect inconsistency, not deliberate rewriting of all history. Git supplies version history. Removing complete final events can leave a valid older prefix; compare the last confirmed Git version or save to detect that rollback. The ledger checks arithmetic, chronology, references, and record shape; it cannot verify lore, determine whether prose is good, or prove a GM is unbiased.

## Local commands for maintainers

The player does not need to maintain JSON or run these commands; Codex does that as part of play. From the repository root:

```sh
python -m unittest discover -s tests -v
python -m iron_engine --store campaign validate
python -m iron_engine --store campaign status
python -m iron_engine --store campaign head
```

`status` and `validate` report whether setup is still needed. `head` needs an initialized campaign and supplies the version hash for preparing a new input. After the GM fills a template with the agreed setup or resolved action:

```sh
python -m iron_engine --store campaign init .work/setup.json
python -m iron_engine --store campaign turn .work/turn.json
python -m iron_engine --store campaign research .work/research.json
python -m iron_engine --store campaign correct .work/correction.json
python -m iron_engine --store campaign checkpoint .work/checkpoint.json
python -m iron_engine --store campaign save campaign-save.json
python -m iron_engine --store restored-campaign restore campaign-save.json
```

Restore uses a new empty destination. Keep exports out of unrelated repositories and public locations if they contain personal notes. All campaign records here are player-readable; this is not storage for unrevealed GM secrets.

For actual random dice, after fixing the check and its stakes:

```sh
python -m iron_engine roll --sides 20 --count 1
```

The helper makes a public random draw. It does not prevent someone from requesting another draw or prove hidden precommitment. The rules forbid rerolling merely to change an unwelcome result. In real-dice mode, submitted checks retain their source and arithmetic.

## Travel lookup

Codex can look up a route or estimate an authorized journey using the imported source:

```sh
python -m iron_engine distance --mode road --from "Castle Black" --to Winterfell
python -m iron_engine travel-profiles
python -m iron_engine travel --mode road --from "Castle Black" --to Winterfell --profile small_party_riding --pace average
```

The source gives 680 miles for that road route and 24 miles per day for the average small riding party, about 28.3 days before additional rest or delay. These are planning estimates. Route access, party condition, supplies, and interruptions still govern the actual turn. Sea and raven estimates require an explicit rate assumption. No lookup changes the campaign ledger.

## GitHub use

This build is prepared for [Alex-Oss222/dice-roller](https://github.com/Alex-Oss222/dice-roller). See [build status](BUILD_STATUS.md) for publication and verification details. The distance catalog is a bundled snapshot of [ASOIAF Timeline - Vandal Proof](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit#gid=1), read on 22 September 2026. It imports distance matrices and labeled road rates, not the plot timeline. Values are fan estimates, and sea/raven matrix units are documented assumptions. No Google credentials or automatic spreadsheet connection is needed during play.

Commit a turn's complete event together with any related rules or research changes through the agreed repository workflow. Check the remote version before reporting a successful upload. A local event is not proof of GitHub persistence. Follow any existing repository branch and review requirements; never overwrite an unrelated campaign or rewrite settled outcomes to pass a check.
