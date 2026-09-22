# Blood & Gold capabilities

This is the capability reference extracted from the supplied cleaned character sheet. It governs the `blood_and_gold_0_9` capability system in adjudicated play. The [main rules](iron_engine.md) continue to govern agency, outcomes, time, research, injuries, and saves. The [blank sheet](../templates/character-sheet.md) records only the character's established facts.

## Scale and authority

Learned capabilities use ratings **0 to 9**. These are evidence about competence, not dice modifiers. There is no hidden conversion to the earlier 0 to 5 dice scale. Changing to dice requires an explicit compatible rule before using these ratings numerically; do not squeeze 7 into 5 or use 9 as a bonus to the old check.

| Rating | Meaning |
| ---: | --- |
| 0 | Untrained; no dependable practical competence |
| 1 | Novice; rudimentary exposure |
| 2 | Familiar; basic practical competence |
| 3 | Trained; dependable in ordinary professional conditions |
| 4 | Skilled; solid professional ability |
| 5 | Veteran; broad and tested professional experience |
| 6 | Highly skilled; uncommon proficiency |
| 7 | Expert; elite competence within the field |
| 8 | Exceptional; rare or career-defining mastery |
| 9 | Extraordinary; exceptional mastery supported by an exceptional history |

An unknown ability is **not established**, not Rating 0. A rating describes the relevant activity, not social rank, reputation, adulthood, or a moral judgment. A young person is not excluded from a demonstrated ability by the label “veteran”; an old person does not gain it for years lived. Renown is evidence about reputation and need not accurately reflect skill.

Use the most relevant established sub-skill or specialty, the broad domain only for genuinely broad work, and a derived estimate only where actual exposure supports transfer. Consider equipment, physical attributes, wounds, fatigue, numbers, information, preparation, position, opposition, and resources separately. Do not add a domain and its contributing sub-skill as two advantages. Routine feasible work succeeds directly; impossibility needs no check. Briefly identify the decisive cause for consequential outcomes.

The one authoritative numeric value for an individual capability lives in the character's skills map; matching metadata describes its type, basis, development, and prerequisites. Views and summaries reference it. See [the record contract](../docs/record_contract.md) for storage details.

## Layers and natural attributes

- **Domains** summarize a field using established anchor skills. They have no Development track.
- **Sub-skills** are specific established learned abilities. They have a rating and Development toward the next rating.
- **Specialties** distinguish a narrower activity when it changes play. They can develop independently, but cannot earn duplicate credit for the same work already credited to their parent.
- **Derived sub-skills**, marked `D`, are provisional estimates. They have no Development and cannot anchor a domain or serve as an input for another derived estimate.

Record only distinctions relevant to the background or play. Avoid an exhaustive catalogue of every possible action.

Strength, agility, endurance, intelligence, perception, appearance, and willpower remain descriptive natural attributes. Record established relevant distinctions without inventing an attribute score. Attributes can affect feasibility and circumstances but cannot replace training. The player owns the PC's intentions and feelings; an attribute entry does not authorize the GM to choose them.

## Domains and anchors

| Domain | Scope |
| --- | --- |
| Diplomacy | Open influence, negotiation, conduct, mediation, and persuasion |
| Martial | Personal combat, warfare, military command, tactics, and strategy |
| Stewardship | Administration, finance, trade, property, resources, and organization |
| Intrigue | Deception, espionage, secrecy, counterintelligence, and covert activity |
| Learning | Scholarship, literacy, medicine, law, religion, languages, and formal knowledge |
| Fieldcraft | Hunting, tracking, travel, survival, riding, navigation, and scouting |
| Craft | Trades, manufacture, construction, repair, and skilled productive work |

An additional domain needs a major established field that cannot sensibly fit these seven. No domain grants every skill in its reference list.

A numeric domain requires **3 to 5 distinct established anchor sub-skills**, positive integer percentage weights totaling **100%**, and **no weight above 40%**. Anchors must represent the actual career. Do not manufacture extra skills, use derived estimates, or count both a skill and its overlapping specialty to reach three anchors. If fewer than three suitable anchors are established, leave the domain **not established / insufficient anchors** and use the known sub-skills directly. This does not invalidate those skills or prevent play.

Multiply each anchor rating by its percentage weight, sum, and divide by 100. Round once at the end using **half-up rounding**: 4.49 becomes 4; 4.50 becomes 5. All ratings are nonnegative, so the integer formula is `floor((sum(rating * integer_weight) + 50) / 100)`. Do not use round-to-even or round each contribution first.

Example only, not a character assignment:

| Established anchor | Rating | Weight | Contribution |
| --- | ---: | ---: | ---: |
| Two-Handed Sword | 8 | 35% | 2.80 |
| Frontline Leadership | 8 | 25% | 2.00 |
| Tactics | 8 | 20% | 1.60 |
| Strategy | 7 | 10% | 0.70 |
| Mounted Warfare | 6 | 10% | 0.60 |
| Total | | 100% | 7.70 |

This supports Martial 8 while Strategy remains 7 and Mounted Warfare 6. Non-anchor skills retain their own ratings. Recalculate when an anchor improves or a justified career change alters the anchor structure. Explain such changes; do not switch weights to manufacture a higher domain.

## Derived estimates and prerequisite gaps

An omitted skill may already be partly supported by related abilities and actual background. First check whether the character had reasonable exposure and meets essential prerequisites. A high domain cannot create literacy, a language, specialized technique, mounted command, surgery, ship command, or another technical competence merely because it sounds adjacent.

When evidence permits a provisional estimate, calculate an **upper candidate**, not an entitlement:

`40% established parent domain + 60% relevant established skills + exposure adjustment`

Divide the 60% among named relevant established skills; weights total 100%. State the supporting background, missing prerequisites, and limits. A derived skill may not be an anchor, an input skill, or a parent in this calculation.

| Exposure supported by the record | Candidate adjustment |
| --- | ---: |
| Explicit specialist experience | +1 |
| Clearly expected from established background | 0 |
| Plausible but not established | -1 |
| Little relevant experience | -2 |
| No reasonable exposure or an unmet essential prerequisite | Do not derive a numeric rating |

Apply adjustment, half-up round once, and bound the candidate to 0 through 9. The actual provisional rating must be at or below that candidate and no higher than the parent domain without specific evidence of exceptional specialization. Record a lower ceiling when the demonstrated exposure supports less. A formula cannot overrule a prerequisite gap. When only plausibility exists and competence cannot be bounded responsibly, leave it not established and adjudicate the limited attempt from known abilities.

### Correcting the cavalry example

Martial 8, Tactics 8, Frontline Leadership 8, and Riding 6 at weights 40/20/20/20 produce 7.6. Applying -1 produces 6.6 and a rounded **candidate** of 7. That arithmetic does not establish Cavalry Command 7D. Riding and infantry leadership do not demonstrate mounted formation control, cavalry training, or experience issuing workable mounted orders.

With only the original infantry-command background and speculative cavalry exposure, record **Cavalry Command: not established; specific mounted-command experience unproven**. Related skills may help with ordinary communication or terrain assessment, but cannot grant expert mounted command. A numeric provisional estimate requires evidence of actual exposure and an explained conservative limit. Do not substitute an arbitrary 5D merely to make the number smaller.

Derived entries earn no Development. When new evidence establishes an ability, ordinarily adopt the same provisional rating or a lower supported rating with zero Development, then track future growth normally. An unusually different historical rating or preexisting progress needs an explicit correction with evidence, not a free promotion from the formula. Removing or lowering a provisional estimate does not retroactively rerun settled outcomes.

## Development periods

Development records lasting improvement, not action count or success count. An ordinary successful task, casual practice, or repetition of easy familiar work earns no automatic points. Improvement needs meaningful learning through practice, instruction, professional use, difficulty, refinement, or experimentation over actual fictional time.

| Activity basis for a meaningful period | Typical award |
| --- | ---: |
| Occasional use or casual practice | 0 |
| Sustained deliberate practice | +1 |
| Regular professional use with meaningful development | +1 |
| Formal instruction from a superior practitioner | +1 |
| Meaningful difficult experience | +1 |
| Exceptional period, with a stated additional basis | +2 |

These award sizes are **house pacing conventions**, not researched rates of human learning. Establish the intended period's duration and activity before evaluating its result. Appropriate periods vary with the skill, training schedule, demands, and circumstances. A turn can contain only part of a period or several completed periods. Ten turns never creates a development award by itself.

For every credited period retain: unique period ID; capability ID; start and end in campaign seconds; actual duration; training/use undertaken; instruction, challenge, or practice basis; award; evidence turns/source facts; and the capability's last credited period. The ledger's credited-period list contains positive awards only. Explain evaluated intervals earning zero in the turn's outcome/evidence or task notes. Distinguish scheduled duration from time actually completed after an interruption.

End must be after start. Credited periods for one capability cannot overlap or reuse the same work. Combine several causes within one period into one justified award: a lesson is not three awards because it was practice, instruction, and difficult. An exceptional +2 replaces that period's ordinary award; it does not stack on top. Splitting one period into several records must not increase its credit. Distinct skills or a parent/specialty need distinct learning evidence and a plausible allocation of the actual time; they cannot each claim the full same work automatically.

Experience before Day 0 is described in the agreed background. Do not create invented negative-time periods or a fictional lifetime ledger. Establish initial ratings and any existing progress from the agreed history. An empty template does not imply either zero progress or a completed training period.

## Thresholds and experience guidance

Both meaningful Development and relevant experience must support an advance. Years measure **total relevant exposure**, not extra years added at each step and not simple age. The supplied table is preserved as **contextual house guidance**, not a universal minimum or a sourced claim about realistic ages:

| Advancement | Base Development required | Typical total relevant experience |
| --- | ---: | --- |
| 0 to 1 | 6 | 1 to 2 years |
| 1 to 2 | 8 | 2 to 4 years |
| 2 to 3 | 10 | 4 to 7 years |
| 3 to 4 | 12 | 7 to 12 years |
| 4 to 5 | 14 | 12 to 18 years |
| 5 to 6 | 16 | 18 to 25 years |
| 6 to 7 | 18 | 25 to 35 years |
| 7 to 8 | 20 | 35+ years of exceptional practice and experience |
| 8 to 9 | 30 | An exceptional career and extraordinary opportunity |

The former reference to structured training around age 7 is also a contextual house convention, **not a minimum age for recording skills**. Younger children may possess evidenced age-appropriate learned abilities. A skill's demands, intensity of exposure, quality of teaching, opportunities, and an established exceptional history can justify a different trajectory. Explain exceptions from the background or recorded experience; neither age nor a formula grants a rating. Do not infer that all veteran soldiers must be at least 19, or that a renowned young practitioner is impossible, from adding seven to the table.

At ratings 0 to 3, ordinary instruction and deliberate practice may suffice. At 4 to 5, increasingly difficult work, wider experience, and refinement matter. At 6 to 7, unusual problems, capable teachers/rivals, demanding responsibility, and experimentation become important. Ratings 8 and 9 require extraordinary demonstrated mastery and opportunity, not accumulating easy work. A court position, long career, war, famous teacher, or exceptional aptitude is evidence to assess, never automatic rank. Do not use the top rating to claim universal competence or invulnerability.

When a threshold is met and prerequisites support advancement, consume that threshold from accumulated Development and add one rating. Carry legitimate excess forward toward the next threshold. If prerequisites remain unmet, retain recorded progress without granting the rating. Do not consume the same progress twice. Further advancement needs its own evidence and threshold; no bulk leap from a balance alone. At Rating 9, there is no next threshold: Development is 0, and no further progress balance accumulates. Preserve historical awards and consumed totals in the event record.

### Capability-specific aptitude

| Established aptitude | House pacing adjustment |
| --- | --- |
| Poor | 25% more Development or relevant-experience guideline |
| Ordinary | No adjustment |
| Strong | 7% less Development or relevant-experience guideline |
| Exceptional | 10% less Development or relevant-experience guideline |

The percentages are explicit house conventions, not measured learning advantages or canonical facts. Apply the adjustment to **one** of Development or experience guidance for a given advancement, never both. Record which basis is used. For Development, multiply the base threshold by 1.25, 1, 0.93, or 0.90 and round **up** to a whole point. For example, a base threshold of 12 with Strong aptitude becomes `ceil(12 * 0.93) = 12`, not 11. Threshold ceiling differs deliberately from domain half-up rounding.

If aptitude is not established, use no adjustment without asserting an Ordinary trait as fact. In the record, `level: ordinary` can represent that neutral accounting convention; say in the capability's basis that no distinct aptitude has been established. Aptitude does not improve today's roll or outcome, eliminate prerequisites, create a high starting rating, or justify retroactive advancement.

## Reference lists

These lists are possibilities, not prefilled abilities. Use one authoritative record when labels overlap. In particular, conversational fluency, reading, writing, translation, and scholarly language knowledge can differ; do not duplicate the same fluency under both Diplomacy and Learning.

### Diplomacy

Persuasion; Negotiation; Court Etiquette; Oratory; Mediation; Hospitality; Protocol; Public Leadership; Noble Customs; Small Council Politics; Bargaining; Conversational Languages.

Open influence can derive from different careers. A household officer, traveling knight, and court negotiator need not share court protocol, local relationships, or languages.

### Martial

- **Weapons:** Longsword; Two-Handed Sword; Sword and Shield; Spear; Polearm; Axe; Mace; Dagger; Bow; Crossbow; Lance.
- **Combat:** Armored Fighting; Shield Use; Wrestling; Mounted Combat; Duelling; Formation Fighting; Defensive Fighting; Protector; Battlefield Awareness.
- **Command:** Frontline Leadership; Infantry Command; Cavalry Command; Archer Command; Formation Command; Discipline; Morale; Logistics of War.
- **Warfare:** Tactics; Strategy; Siege Warfare; Raiding; Ambush; Defensive Warfare; Naval Warfare; Scouting Operations.

Personal weapons, group command, naval operations, and siege work are distinct. A high military domain does not fill every gap.

### Stewardship

Estate Management; Household Management; Accounting; Taxation; Trade; Appraisal; Logistics; Supply; Agriculture; Livestock Management; Warehousing; Labor Management; Construction Management; Guild Administration; Merchant Networks; Budgeting; Provisioning; Record Keeping.

Managing labor, a commercial network, a household, and an estate can share some methods while requiring different knowledge and relationships.

### Intrigue

Deception; Detecting Lies; Espionage; Counterintelligence; Disguise; Concealment; Eavesdropping; Information Networks; Rumor; Blackmail; Manipulation; Criminal Contacts; Smuggling; Surveillance; Codes and Ciphers; Secret Correspondence; Court Intrigue; Street Intrigue.

Detecting Lies is fallible inference from information and conduct, never access to private thoughts. A recorded network or contact needs actual people, access, resources, and obligations; a capability name does not create them.

### Learning

Reading; Writing; History; Law; Theology; Medicine; Surgery; Herbalism; Anatomy; Heraldry; Genealogy; Languages; Mathematics; Astronomy; Geography; Philosophy; Natural Philosophy; Architecture; Engineering; Ravenry; Administration Theory.

Literacy and technical knowledge depend on education and exposure. A general Learning rating does not establish each language or authorize successful surgery without training and suitable means.

### Fieldcraft

Survival; Hunting; Tracking; Foraging; Navigation; Scouting; Riding; Horse Handling; Animal Handling; Camping; Fishing; Trapping; Trailcraft; Mountain Travel; Forest Travel; Desert Travel; Winter Travel; Concealment in Wilderness; Reading Terrain.

Record relevant terrain and animal familiarity. Riding does not itself establish military command, horse ownership, or veterinary medicine.

### Craft

Blacksmithing; Weaponsmithing; Armorsmithing; Carpentry; Joinery; Masonry; Stonecutting; Leatherworking; Tanning; Tailoring; Weaving; Shoemaking; Pottery; Brewing; Cooking; Baking; Shipbuilding; Wheelwrighting; Fletching; Bowmaking; Jewelry; Mining; Metalworking; Construction. Add relevant narrower specialties such as toolmaking, horseshoes, or engraving when the background supports them.

Identify the profession and actual techniques, tools, materials, and experience. A capable village smith and an exceptional armorer may have different domain anchors and large gaps outside their own work.

## Overlapping work

Cavalry operations may draw on Martial command and Fieldcraft riding. Castle administration may draw on Stewardship, Diplomacy, and relevant law. A maester's duties may involve Learning, mediation, and accounts. An information network may need Intrigue, recruitment, and resource management. Choose the ability responsible for the actual task and use other relevant facts as context. Overlap does not justify double advantages, duplicate Development, or an unsupported new skill.
