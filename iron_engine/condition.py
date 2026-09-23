"""Temporary whole-person Condition, separate from learned capability ratings.

Tags record relevant causes, not fixed deductions. The GM judges their combined
effect; these helpers add no penalties, automatic recovery, or advancement.
"""

from .engine import _fail, _integer, _list, _object, _string


RATING_LABELS = (
    "Dead", "Dying", "Critical", "Severe", "Poor", "Impaired",
    "Worn", "Sound", "Hale", "Exceptional",
)
RATING_BANDS = (
    "Dead", "Dying", "Critical", "Critical", "Impaired", "Impaired",
    "Strained", "Strained", "Healthy", "Healthy",
)


def rating_label(rating):
    _integer(rating, "condition.rating", 0, 9)
    return RATING_LABELS[rating]


def condition_band(rating):
    _integer(rating, "condition.rating", 0, 9)
    return RATING_BANDS[rating]


def validate_condition(value, alive):
    _object(value, "character.condition", {"rating", "tags", "basis"})
    _integer(value["rating"], "condition.rating", 0, 9)
    tags = _list(value["tags"], "condition.tags")
    if not tags:
        _fail("condition.tags must name at least one established factor")
    for tag in tags:
        _string(tag, "condition tag")
    _string(value["basis"], "condition.basis")
    if type(alive) is not bool:
        _fail("alive must be a boolean")
    if (value["rating"] == 0) != (not alive):
        _fail("Condition 0 means dead; a living character requires Condition 1..9")


def condition_summary(character):
    """A concise reading header; absence remains unknown rather than baseline 8."""
    if "condition" not in character:
        return "Not established"
    condition = character["condition"]
    return f"{condition['rating']}/9 {rating_label(condition['rating'])} ({condition_band(condition['rating'])})"


def render_condition(character):
    lines = ["", "## Condition", ""]
    if "condition" not in character:
        lines.append("Condition: Not established. No rating is assumed.")
        return lines
    condition = character["condition"]
    lines.extend([f"Condition: {condition_summary(character)}",
                  "Tags: " + "; ".join(condition["tags"]),
                  f"Basis: {condition['basis']}",
                  "Temporary combined assessment, separate from learned capabilities."])
    return lines
