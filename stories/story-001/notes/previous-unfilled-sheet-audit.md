> Historical audit of the superseded unfilled input. Read character-sheet-audit.md for the current Eddard seed.

# Character sheet organization and rules audit

The supplied `A_Song_of_Blood_and_Gold_Cleaned_Character_Sheet(2).md` combines a capability rulebook, extensive reference lists, and a mostly blank character sheet. It establishes adjudicated resolution with a 0 to 9 capability scale, but it does not establish an actual character, starting era, region, resources, or first turn.

This audit applies only to Story 1's supplied starting sheet. Other stories select their own character and settings. The separation is now:

- [Capability rules](../../../rules/capabilities.md): scale, domains, reference lists, anchors, derivation, aptitude, and advancement.
- [This story's starting character sheet](../character-sheet.md): current facts, evidence, resources, work, relationships, knowledge, and resume information.
- [Story journal](../play/story.md): the rendered narrative from accepted turns.
- [Live character sheet](../play/character-sheet.md) and [resume view](../play/resume.md): rendered current state and continuation details.

The story is played in chat. Accepted outcomes and resulting state belong together in immutable campaign events; journal and sheet are views of those records. A displayed chat turn is not a confirmed repository save until the actual write and GitHub publication succeed. No new service, private background simulation, or manual player bookkeeping is required.

## Concrete corrections

| Original issue | Correction | Why it matters |
| --- | --- | --- |
| Sheet mixed current facts with long rule/reference sections | Moved detailed mechanics and optional skill lists to `rules/capabilities.md` | The live sheet can stay focused on what is established and currently relevant. |
| New sheet used 0 to 9 while earlier engine rules used 0 to 5 | Preserved the chosen 0 to 9 adjudicated system explicitly | Clipping or silently converting ratings changes the user's rules and loses meaning. Dice requires an explicitly compatible rule. |
| Blank fields sometimes said None, Normal, or implied no wounds | Replaced unverified absence/health/assets with TBD or Not established | Missing information does not establish a healthy, equipped, unencumbered character. |
| Current turn 0 could be mistaken for initialized play | Marked current turn/event/time as not started pending setup | A template does not authorize creating a protagonist or opening outcome. |
| Equipment, mounts, money, wounds, oaths, and debts appeared repeatedly | One equipment/asset catalogue, one condition record, one balance table, and one obligation record; summaries use IDs | A purchase, wound, horse, or payment must not have competing current versions. |
| Copper pennies and stars shared one amount | Separate currency units with no assumed conversion | Balances must not combine different denominations or imply an unverified exchange rate. |
| Domain rounding was ambiguous | Explicit half-up rounding once after weighting | A result such as 4.5 cannot vary by programming-language rounding behavior. |
| Anchor count and weight language allowed broad competence to be inferred from too little evidence | Require 3 to 5 established anchors, weights totaling 100%, maximum 40% each; insufficient anchors leave a domain unset | Known narrow skills remain usable without inventing other competence. |
| Derived skills could strengthen the domain that produced them | Derived abilities cannot be anchors or inputs to another derivation | Prevents circular numerical growth without new experience. |
| Cavalry example promoted an infantry commander to 7D from a weighted formula | Preserve the candidate arithmetic but leave actual Cavalry Command unestablished absent mounted-command exposure | Correct arithmetic is not evidence of missing technical experience. |
| Promotion from a provisional ability lacked a clear cost | Establish with the same or lower supported rating and zero Development ordinarily; different historical findings require an evidenced correction | A derived estimate cannot become free advancement or retroactive training. |
| “Age 7” and “minimum” experience years could impose rigid age exclusions | Label age, years, and aptitude percentages as contextual house pacing guidance with evidenced exceptions | The sheet should not prohibit supported young ability or grant a veteran rating from age alone. These figures were not supplied with research. |
| Development awards lacked uniquely identified elapsed periods | Record capability, period ID, start/end, duration, basis, award, evidence, and last credited period; prohibit overlapping credit | Repeating a save, reviewing a turn, or renaming the same practice cannot award progress twice. |
| Threshold consumption, excess progress, and top-rank behavior were unspecified | Consume each threshold once, carry legitimate excess, require advancement evidence, cap rating at 9 with Development 0 | Stops accidental free levels and undefined progress above the scale. |
| Aptitude rounding and double application could vary | Apply to Development or experience, never both; round adjusted Development thresholds upward | A 7% reduction of 12 still requires 12 whole points, not 11. |
| Relationships and reports lacked durable identity and full provenance | Add relationship/knowledge IDs, whose assessment, source, event time, and information arrival | NPC attitudes and rumors are attributed evidence, not universal scores or omniscient truth. |
| Claims and duties did not clearly expose practical prerequisites | Add authority, recognition/dispute, legal basis, needs, blocking resources, and deadlines | A claimed right or issued order does not guarantee possession, obedience, or completion. |
| Long-term continuity fields were incomplete | Add event/hash, phase/time, latest review, confirmed save version, interrupted plan, and checkpoint/resume details | The next session can locate the actual saved result and unfinished authorized work. |

## What remains unset

The source provides no completed answers for campaign title, starting era/event, region, permitted books, spoiler cutoff, Day 0 anchor, current location, name, age, status, background, or immediate aim. It does not establish starting skill ratings, health, possessions, money, relationships, claims, or obligations. Those cannot be filled by copying illustrative examples.

Use the player's supplied setup facts, ask together only for the missing essentials, and propose starting capabilities/assets from the chosen history before they affect stakes. Descriptive details that do not affect the opening can remain unset. Appearance, family, ambitions, and private motives are not permission to invent the player's choices or interiority.

The selected adjudicated mode and 0 to 9 capability model can be retained without another confirmation. No actual world research dossier can be completed responsibly before the era/region and spoiler boundary are known. Research should then constrain relevant institutions, travel, equipment, and access, with sources and assumptions separated from information the PC learned in-world.

The template introduces no scene, protagonist, relationship, resource grant, training credit, or Turn 1. All example numbers in the capability reference remain rules examples.
