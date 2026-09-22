# Travel distance reference

The bundled `data/travel_distances.json` preserves 577 numeric routes from the user's [ASOIAF workbook](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit): 276 road, 91 sea, and 210 raven routes, plus seven labeled road speed profiles. It is a fan-made estimate, not a canonical survey. The snapshot was read on 2026-09-22. Every route retains its sheet, gid, and cell; every lookup returns a direct source link.

The import includes distance matrices and labeled road rates only. It does not import plot timelines, future events, or character movements. The sheet's title is provenance, not permission to introduce chronology into play.

## What the numbers mean

Road distances use miles. The workbook's road speed sheet explicitly labels miles and reproduces the Castle Black to Winterfell distance of 680. The sea and raven matrix titles omit units. Treating their values as miles is an explicit campaign convention consistent with the workbook's miles-per-day rates, rather than a verified unit label in those headers. The helper reports this assumption and performs no unit conversion.

Distance cells are used as written, including inconsistencies. Castle Black to Winterfell is 680 by road and 640 by raven. Reversing a route returns the same matrix cell; it does not establish equally easy travel in both directions. A missing route produces an error. The helper never fills gaps, combines routes, or substitutes a computed shortest path.

Locations match exact names after ignoring capitalization and redundant whitespace. The only additional aliases are `Kneeling Man` for `Inn of Kneeling Man`, and `Harroway's Twn` for `Lord Harroway's Town`. Misspellings are rejected rather than silently choosing another place.

## Rate and time assumptions

An estimate requires either an explicit rate in miles per day or an explicit road profile. A selected road profile defaults to its `average` pace. Other pace names are `slow`, `fast_unconditioned`, and `fast_conditioned`. Using both a profile and an explicit rate is an error.

The seven profiles are `large_group_walking`, `small_party_riding`, `large_group_riding`, `horse_relays`, `army_with_supply_train`, `army_without_supply_train`, and `royal_wheelhouse`. Their values are copied from the named source rows; they are estimates requiring suitable people, animals, support, and roads. An unlabeled row is deliberately not assigned an invented mode.

Sea and raven travel always require a GM-supplied rate. The workbook describes its ship model as rough and its old travel calculator as unreliable. Those formulas and their supposed precision are not imported. A sea distance cannot supply a ship, favorable sailing conditions, embarkation time, or access to a port. A raven distance cannot supply an available trained bird, a destination it knows, successful delivery, or a recipient's knowledge.

`multiplier` changes speed: `0.5` halves the rate and doubles moving time. `rest_days` adds explicit nonmoving days after that calculation. Moving days equal distance divided by effective rate. Elapsed days equal moving days plus rest days. `elapsed_seconds` rounds that exact calculation upward to whole seconds. Rates and multipliers must be positive and finite; rest days must be nonnegative and finite. Fractional days are supported. The per-day rate already represents a day's overall progress, not an hourly speed maintained for 24 hours.

A fast road profile requiring more than three moving days returns a prominent `ENDURANCE` warning and `requires_endurance_assumption: true`. This is arithmetic to inspect, not an endorsement that a fast pace is sustainable. Record a concrete GM endurance, relay, or staged-travel assumption with `endurance_assumption` before using it as the journey plan. The warning remains visible even when that assumption is supplied. Rest days alone do not establish how a journey is staged. The helper does not invent fatigue damage or a safe recovery schedule.

## Command line

Run these commands from the repository root. They print JSON and leave campaign records untouched.

```sh
python -m iron_engine distance --mode road --from "Castle Black" --to "Winterfell"
python -m iron_engine travel-profiles
python -m iron_engine travel --mode road --from "Castle Black" --to "Winterfell" --profile small_party_riding --pace average --rest-days 2
python -m iron_engine travel --mode sea --from "White Harbor" --to "Eastwatch-by-the-Sea" --rate-mpd 100
```

The sea rate `100` is an example input, not an asserted normal sailing speed. `--speed-multiplier 0.5` halves effective speed. `--endurance-assumption "Replacement mounts and riders are available at established relay points"` records an explicit GM assumption; its factual basis still needs to exist in the campaign. `--rest-days` accepts fractional days. Distance lookup does not require a speed. The `travel` command requires `--rate-mpd` or a road `--profile`, and rejects missing, zero, negative, and nonfinite rates.

## Python API

```python
from iron_engine.travel import load_catalog

catalog = load_catalog()  # Optional path to a compatible local JSON catalog.
distance = catalog.lookup("road", "Castle Black", "Winterfell")
plan = catalog.estimate(
    "road", "Castle Black", "Winterfell",
    profile="small_party_riding", pace="average", rest_days=2,
)
message = catalog.estimate(
    "raven", "Castle Black", "Winterfell",
    rate_mpd=100,  # Example GM assumption, not a claimed default raven speed.
)
```

`lookup` returns canonical origin and destination, distance, classification, units, source cell and URL, and assumptions. `estimate` adds the base and effective rates, rate provenance when using a profile, moving days, rest days, elapsed days and seconds, warnings, and limitations. Results are JSON-safe independent copies. Module-level `lookup` and `estimate` support the same calls with an optional `catalog=` argument. `catalog.profiles` lists road rates and `catalog.summary` lists source metadata, route counts, units, and aliases. Invalid input raises `TravelError`.

## Using an estimate in a turn

For play, select the story explicitly, for example `python -m iron_engine --story story-001 travel --mode road --from "Castle Black" --to Winterfell --profile small_party_riding`. This checks that story's shared baseline before using the catalog. Bare travel commands are shared reference lookups and establish no story facts.

Every story reads the same source catalog. A route blocked by war, a damaged bridge, a deliberate detour, an unusual local pace, or a disputed distance is recorded in that story's notes and accepted assumptions/evidence. Preserve the original source value and explain the local adjustment separately. Do not edit `data/travel_distances.json` to make that journey work. Local notes are not automatically loaded overrides; a lookup still returns the shared source value. A verified dataset correction is separate shared maintenance with explicit baseline handling for existing stories.

Travel lookups never open or write the campaign store. They do not change time, location, money, supplies, injuries, deadlines, or NPC knowledge. Use a result as a proposed schedule. Establish availability, access, intended pace, supplies, and known constraints before departure. If an encounter or player decision interrupts the journey, commit only the time actually elapsed and record the remaining task in the normal turn ledger. A fractional duration can span multiple turns, and a weekly turn can contain several legs. Arrival, resource spending, fatigue, and delivery need explicit resolved events.

Record the route's source link and rate assumption alongside the turn evidence when they matter. Keep research provenance outside the narrative; the character learns only what the fiction establishes. A map lookup supplies neither hidden events nor automatic knowledge.
