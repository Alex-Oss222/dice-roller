"""Compact player sheet derived from accepted state; detailed evidence stays in records.

The page reads as a description of the person first: background, experience,
disposition, identity, ties and knowledge. The rating tables follow as an
appendix, with provisional estimates kept apart from established abilities.
"""

from .capabilities import TRAINABLE, development_required
from .condition import rating_label


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _table(values, left, right):
    return (f"| {left} | {right} |\n| --- | --- |\n" +
            "\n".join(f"| {_cell(key.replace('_', ' ').capitalize())} | {_cell(value)} |" for key, value in values.items()))


def _capabilities(character, usage):
    ratings, records = character["skills"], character.get("capabilities", {})
    lines = ["## Capabilities"]
    if not records:
        if ratings:
            lines.append("\n".join(f"- {key}: {value}" for key, value in ratings.items()))
        return lines
    lines.append("0 untrained · 1 novice · 2 familiar · 3 trained · 4 skilled · 5 veteran · 6 highly skilled · 7 expert · 8 exceptional · 9 extraordinary. "
                 "Development is progress toward the next rating. Used lists the turns in which the ability "
                 "governed or supported an accepted action.")
    domains = [key for key, record in records.items() if record["kind"] == "domain"]
    lines.append("| Domain | Rating |\n| --- | ---: |\n" +
                 "\n".join(f"| {_cell(key)} | {ratings[key]} |" for key in domains))
    grouped = {key: [] for key in domains}
    provisional = []
    for key, record in records.items():
        if record["kind"] == "domain":
            continue
        if record["kind"] == "derived":
            provisional.append(key)
            continue
        domain = records[record["parent"]]["domain"] if record["kind"] == "specialty" else record["domain"]
        grouped.setdefault(domain, []).append(key)

    def used(key):
        turns = usage.get(key)
        return ", ".join(str(turn) for turn in turns) if turns else "—"

    for domain, keys in grouped.items():
        if not keys:
            continue
        rows = [f"### {domain}", "| Ability | Rating | Development | Used |", "| --- | ---: | --- | --- |"]
        for key in keys:
            record = records[key]
            progress = "—"
            if record["kind"] in TRAINABLE:
                needed = development_required(ratings[key], record["aptitude"])
                progress = "Maximum" if needed is None else f"{record['development']} / {needed}"
            rows.append(f"| {_cell(key)} | {ratings[key]} | {progress} | {used(key)} |")
        lines.append("\n".join(rows[:1]) + "\n\n" + "\n".join(rows[1:]))
    if provisional:
        rows = ["### Provisional estimates", "Inferred from related abilities; they become established only through evidenced play.",
                "| Ability | Domain | Rating | Used |", "| --- | --- | ---: | --- |"]
        for key in provisional:
            rows.append(f"| {_cell(key)} | {_cell(records[key]['domain'])} | {ratings[key]} | {used(key)} |")
        lines.append("\n".join(rows[:2]) + "\n\n" + "\n".join(rows[2:]))
    return lines


def render_character_sheet(state, usage=None):
    character = state["character"]
    profile = character.get("profile", {})
    usage = usage or {}
    day, rest = divmod(state["time_seconds"], 86400)
    hour, rest = divmod(rest, 3600)
    minute = rest // 60
    condition = character.get("condition")
    health = (f"{condition['rating']} — {rating_label(condition['rating'])}"
              if condition is not None else "Not established")
    lines = [f"## {character['name']}", state["campaign"]["title"],
             "| Current record | Details |\n| --- | --- |\n"
             f"| Turn | {state['turn']} |\n"
             f"| Time | Day {day}, {hour:02}:{minute:02} |\n"
             f"| Age | {character['age']} |\n"
             f"| Standing | {_cell(character['status'])} |\n"
             f"| Location | {_cell(state['location'])} |\n"
             f"| Condition | {_cell(health)} |",
             "## Background", character["background"]]
    for section, heading in (("background_details", "Experience"), ("disposition", "Disposition")):
        values = profile.get(section, {})
        if values:
            lines.append(f"## {heading}")
            lines.extend(f"**{key.replace('_', ' ').capitalize()}:** {value}" for key, value in values.items())
    for section, heading in (("identity", "Identity"), ("appearance", "Appearance")):
        values = profile.get(section, {})
        if values:
            lines.append(f"## {heading}")
            lines.extend(f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in values.items())
    if profile.get("natural_attributes"):
        lines.extend(["## Natural attributes", _table(profile["natural_attributes"], "Attribute", "Detail")])
    if profile.get("kinship"):
        lines.extend(["## Family", _table(profile["kinship"], "Family", "Detail")])
    languages = profile.get("languages", [])
    if languages:
        lines.extend(["## Languages", "| Language | Speaking | Reading | Writing |\n| --- | --- | --- | --- |\n" +
                      "\n".join(f"| {_cell(item['language'])} | {_cell(item['spoken'])} | {_cell(item['read'])} | {_cell(item['written'])} |"
                                for item in languages)])
    if profile.get("literacy"):
        lines.extend(f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in profile["literacy"].items())
    lines.extend(["## Physical condition", health])
    if condition:
        lines.append(condition["basis"])
    lines.extend(character["conditions"])
    if not state["alive"]:
        lines.append(f"Died: {state['death']['cause']}.")
    if character["equipment"]:
        lines.extend(["## Equipment", "\n".join(f"- {item}" for item in character["equipment"])])
    for section, heading in (("property", "Property and supplies"), ("social_position", "Standing and ties")):
        if profile.get(section):
            lines.append(f"## {heading}")
            lines.extend(f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in profile[section].items())
    if state["resources"]:
        lines.extend(["## Counted resources", "\n".join(f"- {key}: {value}" for key, value in sorted(state["resources"].items()))])
    for key, heading in (("relationships", "Relationships"), ("knowledge", "Knowledge"),
                         ("obligations", "Duties and commitments"), ("standing_orders", "Standing orders")):
        if state[key]:
            lines.extend([f"## {heading}", "\n".join(f"- {item}" for item in state[key])])
    lines.extend(["## Present aim", character["aim"]])
    lines.extend(_capabilities(character, usage))
    return "\n\n".join(lines) + "\n"
