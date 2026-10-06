# The Iron Engine

A simple ASOIAF narrative RPG.

You make the character's choices in chat. The AI GM reads the current character and world state, adjudicates what reasonably happens, writes the narrative, and saves only the lasting changes that may matter later.

There is no D&D-style play loop to manage. You do not maintain stats, JSON, inventories, NPC databases, or turn records yourself.

## Play

### Story 2 · Jon Snow · 298 AC

[Read the current story](stories/story-002/play/README.md) · [Latest scene](stories/story-002/play/latest.md) · [Full character sheet](stories/story-002/play/character-sheet.md)

| Character | Current |
| --- | --- |
| Name | Jon Snow |
| Age | 14 |
| Standing | Acknowledged bastard son of Lord Eddard Stark, raised at Winterfell |
| Location | A holdfast in the hills north of Winterfell |
| Condition | Hale |
| Home | Winterfell |
| Holdings | Personal clothes and small possessions; housed, fed, and mounted through Winterfell |
| Relevant strengths | Observant, educated, good rider, trained young swordsman |
| Current situation | Riding with his father and household party for the execution of a Night's Watch deserter |

### Story 1 · Eddard Stark · 283 AC

[Read the current story](stories/story-001/play/README.md) · [Latest scene](stories/story-001/play/latest.md) · [Full character sheet](stories/story-001/play/character-sheet.md)

| Character | Current |
| --- | --- |
| Name | Eddard Stark |
| Age | About 20 |
| Standing | Lord of Winterfell, Warden of the North, rebel army commander |
| Location | Northern rebel encampment beside the Trident |
| Condition | Hale |
| Holdings | Winterfell and House Stark lands; campaign household and equipment |
| Relevant strengths | Experienced commander, strong fieldcraft, capable swordsman, educated noble |
| Current situation | The rebel coalition expects a major battle against Prince Rhaegar's army |

## How the game works

1. Read the latest scene for the story you want to continue.
2. Tell the GM what your character attempts.
3. The GM uses the character, current world state, established knowledge, relationships, circumstances, and prior consequences to adjudicate the result.
4. The GM writes the next scene.
5. Only meaningful lasting changes are saved, such as injuries, holdings, relationships, titles, knowledge, obligations, deaths, travel progress, or major world consequences.
6. Play stops when you have another meaningful choice.

Most actions do not need dice. Randomness is only useful when genuine uncertainty calls for it.

## Repository layout

- `stories/` — the campaigns and their saved state
- `iron_engine/` — validation and save logic
- `rules/` — GM and narrative rules
- `references/` — ASOIAF reference guidance
- `tests/` — checks that protect saved campaigns
- `START_HERE.md` — the short continuation instructions

Everything else is supporting infrastructure. The player should not need to manage it during normal play.

## Railway

Railway is not required to play. Later, it can host the Iron Engine and a clean campaign website/API, while GitHub remains the permanent story record. It should not become a second complicated game system.
