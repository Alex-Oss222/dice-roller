# Research that changes play

The user-supplied [distance workbook](https://docs.google.com/spreadsheets/d/1ZsY3lcDDtTdBWp1Gx6mfkdtZT6-Gk0kdTGeSC_Dj7WM/edit#gid=1) has been imported as [a source-linked travel catalog](../data/travel_distances.json). Read [travel.md](travel.md) for its scope, unit assumptions, and calculation limits. This is a fan-estimate baseline, not a canonical plot schedule. In-world travel and news still depend on means, access, and elapsed time.

The GM uses available web and reading tools. The Python ledger has no web client or autonomous research process. Save the evidence actually checked and the limitation that matters to the ruling. Research before the first scene, after the era, region, and spoiler cutoff are settled, then investigate new material uncertainties as they arise.

Begin with the selected area's authority, institutions, immediate circumstances, routes, equipment, and obligations. Build only the local world needed for the character's present choices. Do not prefill a campaign dossier with later plot events or invent a region-specific law from a generic medieval example.

## Evidence order and limits

- **Canon:** permitted published text or companion material genuinely consulted. Record the checked work and locator. A character's claim inside a book can remain unreliable within that fiction.
- **Secondary:** an accessible reference that identifies its book support. Describe it as a secondary summary; a linked book citation does not mean the GM read the chapter. Use it to locate primary evidence when a consequential conflict needs resolving.
- **Author:** an author statement, with its date/context and whether accessed directly or through an archive. Supplement the selected books rather than silently changing their continuity.
- **Historical analogy:** relevant scholarship, museum material, or primary historical evidence. Record period, place, and limits. It can inform a physical procedure without establishing Westerosi prices, succession rules, distances, or universal combat results.
- **Campaign assumption:** an openly established convention where the setting leaves a gap. Use `campaign convention` as the source and explain the estimate or invention. Consistency after it governs a choice matters; later research does not erase a committed outcome.

Check what the source actually supports. Do not invent quotations, page numbers, exact dates, source access, travel speeds, or casualty rates. Prefer a bounded estimate over false precision. If sources conflict, identify the conflict and its effect on the pending decision. If no reliable evidence is available, label the assumption and proceed unless the missing fact prevents a usable choice.

## Starter sources, checked 22 September 2026

These support research practice and physical plausibility. They do not constitute an era-specific campaign dossier. Linked pages may contain material outside the player's selected cutoff; check relevant passages without publishing unrelated excerpts or spoiler-bearing link text.

| Source | Supported claim | Campaign use and limit |
| --- | --- | --- |
| George R. R. Martin, [The Show, the Books](https://georgerrmartin.com/notablog/2015/05/18/the-show-the-books/), 18 May 2015 | Martin describes the books and television adaptation as different tellings that have diverged. | Keep book and television details separate. This statement does not resolve a particular disputed book fact. |
| [Size of Westeros](https://www.westeros.org/citadel/ssm/entry/size_of_westeros/), archived author statement, 17 April 2008 | Martin says he deliberately kept geographic scale imprecise and warns indirectly against forcing travel chronology from map measurements. | Label extrapolated road distances and arrival estimates as assumptions. This is a fan-hosted archive of an author statement, not a complete canonical distance table. |
| Dirk H. Breiding, The Metropolitan Museum of Art, [Arms and Armor: Common Misconceptions and Frequently Asked Questions](https://www.metmuseum.org/essays/arms-and-armor-common-misconceptions-and-frequently-asked-questions), section 4, 1 October 2004 | Properly fitted historical field armor allowed substantial movement; blanket claims that the wearer could not rise or run are unsupported. | Consider fit, coverage, training, terrain, and fatigue. A historical analogy does not guarantee a particular injured or exhausted character's mobility and is not a universal combat modifier. |
| George R. R. Martin, [FAQ](https://georgerrmartin.com/for-fans/faq/), “How do you research your novels?” | Martin describes broad historical and specialized reading and cautions against putting every researched detail into the story. | Let research constrain actions and costs; keep irrelevant exposition and citations outside the scene. The dated recommendations are background, not current price or availability information. |

The narrow summaries above were checked against accessible page content. They do not claim access to all books mentioned on those pages. Starter sources are not automatically appended to a live campaign; add only sources actually used, with scope suitable for that campaign.

## Source record

Each `research` command takes a stable `request_id`, the latest event's `expected_hash`, and a `sources` list. Read `head` for that hash and reconcile any intervening changes before submitting. Every source record has exactly:

- `id`: unique within the campaign, never reused for a changed claim.
- `claim`: the specific proposition supported, including the intended ruling where useful.
- `source`: checked URL or genuinely checked work/locator; `campaign convention` for an invention.
- `type`: `canon`, `secondary`, `author`, `historical_analogy`, or `campaign_assumption`.
- `scope`: applicable era/region, relevant source section or date, and safe spoiler scope.
- `confidence`: plain-language strength of support; avoid invented probabilities.
- `limitations`: uncertainty, dispute, source-access limits, and what cannot be inferred.

Research adds an immutable event without consuming a turn or fictional time. It cannot alter a balance, grant a skill, or give the PC information. The CLI validates fields, not source truth, citation accuracy, or spoiler safety. The GM remains responsible for those checks.

## Source notes and character knowledge

Keep the research note OOC. A turn may add a separate player-known report such as “The carrier reports that loading finished yesterday; heard Day 2 morning; not independently confirmed.” That knowledge describes who learned what and when. It does not claim the carrier is correct merely because the GM has a source.

The entire repository is player-readable. Do not store unrevealed plot information and hope a field label keeps it secret. When a source includes later revelations, publish only the permitted claim and a safe locator/label. If a useful source cannot be described safely, defer the note or find a safe source. Hidden lore is not required for a credible local scene.

Research can inform an unresolved ruling. After a result is committed, correct a genuine factual/accounting error openly with evidence; do not use a new source as permission to retry an unwanted result. Respect campaign divergences before consulting later published history.
