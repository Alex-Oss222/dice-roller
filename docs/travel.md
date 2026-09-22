# Travel distance reference

The bundled `data/travel_distances.json` preserves 577 numeric routes from the user's [ASOIAF workbook](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit): 276 road, 91 sea, and 210 raven routes, plus seven labeled road speed profiles. It is a fan-made estimate, not a canonical survey. The snapshot was read on 2026-09-22. Every route retains its sheet, gid, and cell; every lookup returns a direct source link.

The import includes distance matrices and labeled road rates only. It does not import plot timelines, future events, or character movements. The sheet's title is provenance, not permission to introduce chronology into play.

## What the numbers mean

Road distances use miles. The workbook's road speed sheet explicitly labels miles and reproduces the Castle Black to Winterfell distance of 680. The sea and raven matrix titles omit units. Treating their values as miles is an explicit campaign convention consistent with the workbook's miles-per-day rates, rather than a verified unit label in those headers. The helper reports this assumption and performs no unit conversion.

Distance cells are used as written, including inconsistencies. Castle Black to Winterfell is 680 by road and 640 by raven. Reversing a route returns the same matrix cell; it does not establish equally easy travel in both directions. A missing route produces an error. The helper never fills gaps, combines routes, or substitutes a computed shortest path.

Locations match exact names after ignoring capitalization and redundant whitespace. The only additional aliases are `Kneeling Man` for `Inn of Kneeling Man`, and `Harroway's Twn` for `Lord Harroway's Town`. Misspellings are rejected rather than silently choosing another place.

## Slowest applicable travel

Campaign travel always uses the slowest supported pace for the actual means and party. A road estimate requires an explicit applicable profile. If several profiles apply, supply all of them: the slowest daily rate governs the party. A lone rider is not assigned a royal procession's rate, and a royal procession cannot use a lone rider's rate to erase its baggage and wheelhouse. The GM must identify the actual party; the helper cannot infer who is present or which transport is available.

These slow rates are copied from the workbook, not a universal rate invented for every journey. Their applicability requires suitable people, animals, support, and roads. The unlabeled source row remains excluded.

| Profile | Slow miles per day | Source row | Applicability |
| --- | ---: | --- | --- |
| `large_group_walking` | 10 | A8:E8 | Large party traveling on foot |
| `small_party_riding` | 18 | A9:E9 | Single rider or small mounted party |
| `large_group_riding` | 16 | A10:E10 | Large mounted group |
| `horse_relays` | 30 | A11:E11 | Supported changes of horses every 10 to 12 miles |
| `army_with_supply_train` | 6 | A12:E12 | Army bringing its supply train |
| `army_without_supply_train` | 12 | A13:E13 | Army without a supply train |
| `royal_wheelhouse` | 5 | A14:E14 | Royal party with a wheelhouse |

All source rows above belong to the `Road travel speed rates` sheet. A mounted royal party with its wheelhouse uses 5 miles per day, while a lone rider uses the small-party slow rate of 18. A large mounted group uses 16. These are different source profiles, not a claim that adding one person produces a mechanically exact penalty. Travel duration is calculated from the requested route, with no hardcoded journey duration.

Road estimates reject explicit rate overrides, average or fast paces, and speed multipliers above one. `multiplier` changes speed: `0.5` halves the slow daily rate. It must be positive, finite, and at most one. Supply `condition_basis` to record the established reason for a reduction. The calculation introduces no bad weather, hostile roadblock, encounter, breakdown, fatigue damage, or recovery schedule of its own.

Sea and raven travel require a positive finite `rate_mpd` plus `rate_basis`, documenting a sourced conservative rate or an explicit conservative GM assumption for the available means and conditions. The imported data does not establish their slowest rate, so the helper does not invent one or claim it verified a supplied minimum. The workbook describes its ship model as rough and its old travel calculator as unreliable. Those formulas are not imported. A sea distance cannot supply a ship, favorable sailing conditions, embarkation time, or port access. A raven distance cannot supply an available trained bird, a destination it knows, successful delivery, or a recipient's knowledge.

## Daily routine and additional delays

The daily rate represents overall progress across an ordinary travel day. By the user's campaign convention, it already allows eight hours of human sleep, meals, and normal stops. Do not add another eight hours per travel day or append meal breaks as extra delays. The workbook provides daily rates but does not specify an eight-hour sleep budget; that exact budget is a campaign rule, not an attributed historical fact. It is also not a claim about a raven's physiology or whether a ship can keep moving while some crew sleep.

`travel_days` equals distance divided by the effective slow rate. The older output field `moving_days` has the same value and does not mean continuous movement for 24 hours. `rest_days` adds only explicit extra stationary time, such as an established two-day repair delay. Record its reason with `delay_basis`; do not count the same interruption again through another delay entry. Normal sleep and meals add zero extra seconds.

Elapsed days equal travel days plus additional rest/delay days. `elapsed_seconds` rounds the exact calculation upward to whole seconds. Extra rest days must be finite and nonnegative; fractional days are supported. The helper returns its assumptions, the selected profile and all declared applicable profiles, and a daily-baseline explanation. It changes no campaign records.

## Command line

Run these commands from the repository root. They print JSON and leave campaign records untouched.

```sh
python -m iron_engine distance --mode road --from "Castle Black" --to "Winterfell"
python -m iron_engine travel-profiles
python -m iron_engine travel --mode road --from "Castle Black" --to "Winterfell" --profile small_party_riding
python -m iron_engine travel --mode road --from "Castle Black" --to "Winterfell" --profile large_group_riding --profile royal_wheelhouse --rest-days 2 --delay-basis "Established extra repair delay"
python -m iron_engine travel --mode sea --from "White Harbor" --to "Eastwatch-by-the-Sea" --rate-mpd 100 --rate-basis "Explicit conservative GM assumption for this example vessel and route"
```

The sea rate `100` is an example assumption, not an asserted normal or sourced minimum sailing speed. `--speed-multiplier 0.5` halves effective speed; pair it with `--condition-basis` to explain an established constraint. `--rest-days` accepts fractional days. Distance lookup does not require a speed. Both ordinary `travel` and story-scoped `travel` enforce the slowest applicable policy. Faster paces and rate overrides cannot bypass it.

## Python API

```python
from iron_engine.travel import load_catalog

catalog = load_catalog()  # Optional path to a compatible local JSON catalog.
distance = catalog.lookup("road", "Castle Black", "Winterfell")
plan = catalog.estimate_slow(
    "road", "Castle Black", "Winterfell",
    profile=["large_group_riding", "royal_wheelhouse"],
    rest_days=2, delay_basis="Established extra repair delay",
)
message = catalog.estimate_slow(
    "raven", "Castle Black", "Winterfell",
    rate_mpd=100,  # Example assumption, not a claimed default raven speed.
    rate_basis="Explicit conservative GM assumption for the available bird and route.",
)
```

`lookup` returns canonical origin and destination, distance, classification, units, source cell and URL, and assumptions. `estimate_slow` adds the base and effective rates, rate provenance, travel days, extra rest days, elapsed days and seconds, the enforced policy, warnings, and limitations. Results are JSON-safe independent copies. Module-level `lookup` and `estimate_slow` support the same calls with an optional `catalog=` argument. `catalog.profiles` lists road rates and `catalog.summary` lists source metadata, route counts, units, and aliases. Invalid input raises `TravelError`.

The older `estimate` Python API remains available only for compatibility with general arithmetic and prior callers. It retains its average profile default and explicit fast-pace endurance warnings. It does not enforce this campaign policy and must not be used to approve story travel. Public travel commands use `estimate_slow`.

## Using an estimate in a turn

For play, select the story explicitly, for example `python -m iron_engine --story story-001 travel --mode road --from "Castle Black" --to Winterfell --profile small_party_riding`. This checks that story's shared baseline before using the catalog. Bare travel commands are shared reference lookups and establish no story facts.

Every story reads the same source catalog. A route blocked by war, a damaged bridge, a deliberate detour, an unusual local pace, or a disputed distance is recorded in that story's notes and accepted assumptions/evidence. Preserve the original source value and explain the local adjustment separately. Do not edit `data/travel_distances.json` to make that journey work. Local notes are not automatically loaded overrides; a lookup still returns the shared source value. A verified dataset correction is separate shared maintenance with explicit baseline handling for existing stories.

Travel lookups never open or write the campaign store. They do not change time, location, money, supplies, injuries, deadlines, or NPC knowledge. Use a result as a proposed schedule. Establish availability, access, intended pace, supplies, and known constraints before departure. If an encounter or player decision interrupts the journey, commit only the time actually elapsed and record the remaining task in the normal turn ledger. A fractional duration can span multiple turns, and a weekly turn can contain several legs. Arrival, resource spending, fatigue, and delivery need explicit resolved events.

Record the route's source link and rate assumption alongside the turn evidence when they matter. Keep research provenance outside the narrative; the character learns only what the fiction establishes. A map lookup supplies neither hidden events nor automatic knowledge.
