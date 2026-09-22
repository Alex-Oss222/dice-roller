"""Compact player sheet derived from accepted state; detailed evidence stays in records."""

from .capabilities import TRAINABLE, development_required
from .condition import RATING_LABELS


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_character_sheet(state):
    character = state["character"]
    profile = character.get("profile", {})
    day, rest = divmod(state["time_seconds"], 86400)
    hour, rest = divmod(rest, 3600)
    minute = rest // 60
    condition = character.get("condition")
    health = (f"{condition['rating']} — {RATING_LABELS[condition['rating']]}"
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
    for section, heading in (("background_details", "Experience"), ("identity", "Identity"),
                             ("appearance", "Appearance"), ("natural_attributes", "Natural attributes"),
                             ("kinship", "Family")):
        values = profile.get(section, {})
        if values:
            lines.append(f"## {heading}")
            lines.extend(f"**{key.replace('_', ' ').capitalize()}:** {value}" for key, value in values.items())
    languages = profile.get("languages", [])
    if languages:
        lines.extend(["## Languages", "| Language | Speaking | Reading | Writing |\n| --- | --- | --- | --- |\n" +
                      "\n".join(f"| {_cell(item['language'])} | {_cell(item['spoken'])} | {_cell(item['read'])} | {_cell(item['written'])} |"
                                for item in languages)])
    ratings, records = character["skills"], character.get("capabilities", {})
    lines.append("## Capabilities")
    if records:
        domains = [key for key, record in records.items() if record["kind"] == "domain"]
        lines.append("5 veteran · 6 highly skilled · 7 expert · 8 exceptional · 9 extraordinary. "
                     "Development records progress toward the next rating; a dash means no separate training track.")
        lines.append("| Domain | Rating |\n| --- | ---: |\n" +
                     "\n".join(f"| {_cell(key)} | {ratings[key]} |" for key in domains))
        grouped = {key: [] for key in domains}
        for key, record in records.items():
            if record["kind"] == "domain":
                continue
            domain = (records[record["parent"]]["domain"] if record["kind"] == "specialty" else record["domain"])
            grouped.setdefault(domain, []).append(key)
        for domain, keys in grouped.items():
            if not keys:
                continue
            lines.append(f"### {domain}")
            rows = ["| Ability | Rating | Development |", "| --- | ---: | --- |"]
            for key in keys:
                record = records[key]
                progress = "—"
                if record["kind"] in TRAINABLE:
                    needed = development_required(ratings[key], record["aptitude"])
                    progress = "Maximum" if needed is None else f"{record['development']} / {needed}"
                rows.append(f"| {_cell(key)} | {ratings[key]} | {progress} |")
            lines.append("\n".join(rows))
    else:
        lines.append("\n".join(f"- {key}: {value}" for key, value in ratings.items()) or "Not established.")
    lines.extend(["## Physical condition", health])
    if condition:
        lines.append(condition["basis"])
    lines.extend(character["conditions"])
    if not state["alive"]:
        lines.append(f"Died: {state['death']['cause']}.")
    lines.extend(["## Equipment", "\n".join(f"- {item}" for item in character["equipment"]) or "Not established."])
    for section, heading in (("property", "Property and supplies"), ("social_position", "Standing and ties")):
        if profile.get(section):
            lines.append(f"## {heading}")
            lines.extend(f"**{key.replace('_', ' ').capitalize()}:** {value}" for key, value in profile[section].items())
    lines.extend(["## Counted resources", "\n".join(f"- {key}: {value}" for key, value in sorted(state["resources"].items()))
                  or "Personal balances and counted reserves are not established."])
    for key, heading in (("relationships", "Relationships"), ("knowledge", "Knowledge"),
                         ("obligations", "Duties and commitments"), ("standing_orders", "Standing orders")):
        if state[key]:
            lines.extend([f"## {heading}", "\n".join(f"- {item}" for item in state[key])])
    lines.extend(["## Present aim", character["aim"]])
    return "\n\n".join(lines) + "\n"
