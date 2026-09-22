# Condition

Condition is an overall **0 to 9 summary of present physical function**. It is separate from learned capabilities, natural attributes, skill ratings, and Development. Temporary injury, illness, fatigue, deprivation, exposure, or intoxication can change what the character can presently do without changing what they have learned.

The scale and examples below are house rules for fictional adjudication, not a detailed medical simulation. The GM assesses the combined established circumstances and records the cause. There are no fixed per-tag deductions, automatic recovery intervals, or numerical roll penalties.

## Rating and function

| Rating | Label | Functional meaning |
| ---: | --- | --- |
| 9 | Exceptional | Fully healthy, rested, nourished, and physically prepared. No meaningful impairment. |
| 8 | Hale | Healthy and fit for normal exertion, travel, labor, or combat. Minor discomforts have no meaningful effect. |
| 7 | Sound | Generally healthy but carrying minor wounds, fatigue, soreness, or mild illness. Fully functional with small limitations. |
| 6 | Worn | Noticeable physical strain. Minor wounds, persistent fatigue, hunger, sickness, or similar problems begin affecting demanding activity. |
| 5 | Impaired | Clearly below normal condition. Moderate wounds, illness, exhaustion, or deprivation interfere with difficult actions and prolonged effort. |
| 4 | Poor | Seriously compromised. Significant injury, disease, exhaustion, or deprivation limits normal activity. Fighting, riding, travel, and heavy labor become difficult. |
| 3 | Severe | Badly wounded or seriously ill. The character can still act, but only with substantial limitation and risk. Assistance may be required. |
| 2 | Critical | Barely functional. Movement and purposeful action are severely restricted. Without treatment, rest, or relief, deterioration is likely. |
| 1 | Dying | Life is immediately threatened. The character is usually incapable of meaningful sustained action and requires urgent aid. |
| 0 | Dead | The character has died. |

A normal healthy adult is **8**, when that health is actually established. **9** specifically requires supported rest, nourishment, and physical preparation; it is not the default for an unwounded character. A blank sheet or missing symptoms does not establish either rating. Record an explicit basis before assigning a value.

| Ratings | Functional band | Meaning |
| --- | --- | --- |
| 8 to 9 | Healthy | Normal or exceptional function |
| 6 to 7 | Strained | Functional but increasingly affected |
| 4 to 5 | Impaired | Significant penalties and limitations |
| 2 to 3 | Critical | Major loss of function and serious danger |
| 1 | Dying | Survival is the immediate concern |
| 0 | Dead | No further physical action |

“Penalties” here means the actual limitations of the recorded condition, not a fixed subtraction from dice or capabilities. At every rating, specific injuries and circumstances still matter. A rating is not a hit-point buffer: an established lethal event can kill immediately without passing through every lower score.

## Tags identify the cause

Tags describe what contributes to the rating; they do not each carry an automatic severity or deduction. The same tag can occur at different ratings. Use one or several as the facts require, with more precise tags where useful.

| Tag | Meaning |
| --- | --- |
| Hale | Healthy and unimpaired |
| Wounded | Physical injury |
| Bleeding | Active blood loss |
| Broken | Fracture or similar structural injury |
| Crippled | Major loss of mobility or function |
| Ill | General sickness |
| Fevered | Significant fever or systemic infection |
| Diseased | Serious or persistent disease |
| Poisoned | Toxic substance affecting the body |
| Exhausted | Severe fatigue or sleep deprivation |
| Starving | Prolonged lack of food |
| Dehydrated | Dangerous lack of water |
| Exposed | Harm from environmental exposure |
| Drunk | Significant intoxication |
| Drugged | Impaired by medicine, narcotics, or other substances |
| Recovering | Improving but not yet restored |
| Convalescent | Past immediate danger but requiring extended recovery |
| Maimed | Permanent serious injury |

The vocabulary is extensible, not a closed enum. `Arrow Wound` and `Blood Loss` can be more useful than generic `Wounded`; `Dying` or `Dead` can describe the corresponding state. A tag alone does not prove a diagnosis, impose its own rating, or clear an injury when removed from a summary. Detailed notes retain the actual injury, effects, treatment, and outstanding needs.

Examples of useful summaries are **Condition 7: Wounded**, **Condition 4: Wounded, Fevered, Exhausted**, and **Condition 5: Arrow Wound, Blood Loss**. These are illustrations, not facts about any character.

## Wound examples

These illustrate how the same cause can produce different function. Use the actual wound's location, effects, blood loss, treatment, and circumstances, rather than selecting a number from the tag alone.

| Condition | Tags | Illustrative wound state |
| ---: | --- | --- |
| 8 | Wounded | Small cut, bruising, or superficial injury without meaningful impairment |
| 7 | Wounded | Minor but meaningful wound |
| 6 | Wounded | Painful wound affecting demanding activity |
| 5 | Wounded | Moderate wound interfering with combat or movement |
| 4 | Wounded | Serious wound |
| 3 | Wounded | Severe wound with major loss of function |
| 2 | Wounded | Life-threatening wound |
| 1 | Wounded, Bleeding | Actively dying |

The earlier minor/serious/critical/fatal wound descriptions remain detailed classifications. They are not an automatic conversion table to Condition. A high aggregate score cannot cancel a specific restriction, such as inability to use an injured limb.

## Illness examples

| Condition | Tags | Illustrative illness state |
| ---: | --- | --- |
| 7 | Ill | Mild illness |
| 6 | Ill | Noticeable illness |
| 5 | Ill | Significant illness interfering with activity |
| 4 | Ill, Fevered | Serious illness |
| 3 | Diseased, Fevered | Severe illness |
| 2 | Diseased | Critical illness |
| 1 | Diseased, Dying | Death imminent without recovery or treatment |

These descriptions do not establish a fixed disease clock or guaranteed treatment result. Process supported deterioration, relief, and care over actual fictional time. A turn counter, save, or review never heals a character automatically.

## Combined conditions and recovery

Assess the whole situation instead of subtracting once per tag. A minor cut plus mild fatigue may still support Condition 7. A deep wound with blood loss, exhaustion, and infection may support Condition 3 or lower. Explain the functional basis rather than counting labels.

For example, a character at **6: Wounded** might become **4: Wounded, Fevered, Exhausted** after two days of marching with little food and an infected wound. That example does not mean two days always costs two points. The worsening wound, exertion, nutrition, care, and effects must actually be established. Neither infection nor deterioration is inserted to make a story harsh.

Recovery requires a supported cause and enough fictional time for that situation. Record treatment, rest, food, water, shelter, or other relevant relief and its limits. `Recovering` or `Convalescent` does not guarantee a particular next rating. Improvement in the overall summary does not erase permanent injury, return lost limbs, remove a restriction without cause, or grant capability Development. Condition 0 remains permanent death under the main rules.

## State and presentation

When used, store `character.condition` as an object with exactly:

- `rating`: integer 0 through 9.
- `tags`: a nonempty list of nonempty strings.
- `basis`: a nonempty causal explanation tied to established facts.

Keep `character.conditions`, the existing list of detailed wound/illness/treatment notes. The singular summary and plural detail list have different roles; neither creates duplicate injuries. Do not place Condition in capability metadata or alter skill ratings because the character is tired, hurt, or recovering.

The field is optional for legacy record/hash compatibility and is never injected during old-event replay. Once an accepted state contains it, later replacements cannot remove it. If present, rating 0 is valid **if and only if** the character is dead. Record death, its cause/time, and Condition 0 in the same accepted turn; there is no intermediate saved state declaring a living character dead in the header. Corrections cannot use the summary to reverse death or evade the death rules. Setup is alive and therefore cannot initialize at 0.

Use only the recorded number in the small turn header. Labels, tags, basis and material changes remain in the separate character and change records. Keep numeric Condition out of scene narration and never turn it into a Capability bonus. Narrate concrete effects instead. If a legacy state has no summary, show `Not established` rather than deriving a number without an accepted basis.

The setup template's 8/Hale values illustrate an established healthy adult. They are not an assignment to a blank PC: its deliberately empty basis must be completed from that story's actual facts, and rating/tags replaced when necessary. Unknown condition can remain absent until established in a compatible record.
