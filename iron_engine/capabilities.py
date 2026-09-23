"""Opt-in Blood & Gold capability records and arithmetic checks.

The GM establishes experience and applicability. Arithmetic is a consistency
check, never evidence that a human learned a craft in a particular number of days.
Ratings live only in character.skills; these records describe their basis.
"""

from .engine import _fail, _integer, _list, _object, _string


SYSTEM = "blood_and_gold_0_9"
THRESHOLDS = (6, 8, 10, 12, 14, 16, 18, 20, 30)
APTITUDE_PERCENT = {"poor": 125, "ordinary": 100, "strong": 93, "exceptional": 90}
EXPOSURE = {"specialist": 1, "expected": 0, "plausible": -1, "little": -2}
TRAINABLE = {"subskill", "specialty"}
COMMON = {"kind", "basis", "evidence_turns"}
TRAINING_FIELDS = {"development", "aptitude", "experience", "training"}
RECORD_FIELDS = {
    "domain": COMMON | {"anchors"},
    "subskill": COMMON | TRAINING_FIELDS | {"domain"},
    "specialty": COMMON | TRAINING_FIELDS | {"parent"},
    "derived": COMMON | {"domain", "derivation"},
}
PROFILE_SECTIONS = {
    "identity", "background_details", "appearance", "natural_attributes",
    "literacy", "property", "social_position", "kinship", "adjudication", "languages",
}


def _evidence_turns(value, turn, label):
    references = _list(value, label)
    if not references:
        _fail(f"{label} needs at least one reference; use turn 0 for established setup history")
    for reference in references:
        _integer(reference, label, 0, turn)


def _weights(value, label, total, *, minimum_count=1, maximum_count=None, maximum_weight=100):
    _object(value, label)
    if len(value) < minimum_count or (maximum_count is not None and len(value) > maximum_count):
        _fail(f"{label} has an invalid number of contributing capabilities")
    for key, weight in value.items():
        _string(key, f"{label} capability ID")
        _integer(weight, f"{label}.{key}", 1, maximum_weight)
    if sum(value.values()) != total:
        _fail(f"{label} weights must total {total}%")


def development_required(rating, aptitude):
    """Return the next threshold, rounded upward after one aptitude adjustment."""
    _integer(rating, "rating", 0, 9)
    if rating == 9:
        return None
    percent = APTITUDE_PERCENT[aptitude["level"]] if aptitude["applied_to"] == "development" else 100
    return (THRESHOLDS[rating] * percent + 99) // 100


def _half_up_hundredths(value):
    # Values below zero ultimately clamp to zero; integer arithmetic stays exact.
    return (value + 50) // 100


def derived_ceiling(ratings, record):
    """Candidate ceiling only; technical prerequisites still need GM evidence."""
    derivation = record["derivation"]
    hundredths = 40 * ratings[record["domain"]]
    hundredths += sum(ratings[key] * weight for key, weight in derivation["related"].items())
    hundredths += 100 * EXPOSURE[derivation["exposure"]]
    ceiling = max(0, min(9, _half_up_hundredths(hundredths)))
    if derivation["exposure"] != "specialist":
        ceiling = min(ceiling, ratings[record["domain"]])
    return ceiling


def validate_profile(profile, ratings):
    _object(profile, "character.profile")
    if not set(profile) <= PROFILE_SECTIONS:
        _fail(f"Unknown profile sections: {sorted(set(profile) - PROFILE_SECTIONS)}")
    for section, fields in profile.items():
        if section == "languages":
            names = set()
            for language in _list(fields, "profile.languages"):
                _object(language, "language", {"language", "spoken", "read", "written", "capability", "basis"})
                for key in ("language", "spoken", "read", "written", "basis"):
                    _string(language[key], f"language.{key}")
                if language["language"] in names:
                    _fail("Duplicate language record")
                names.add(language["language"])
                if language["capability"] is not None:
                    _string(language["capability"], "language.capability")
                    if language["capability"] not in ratings:
                        _fail("A language capability reference must name an existing skill")
            continue
        _object(fields, f"profile.{section}")
        if section == "natural_attributes" and not set(fields) <= {
            "strength", "agility", "endurance", "intelligence", "perception", "appearance", "willpower"
        }:
            _fail("Unknown natural attribute; use the seven descriptive attribute names")
        for key, description in fields.items():
            _string(key, f"profile.{section} field")
            if key.casefold() in {"skills", "capabilities", "conditions", "equipment", "resources",
                                  "name", "age", "status", "aim"}:
                _fail(f"profile.{section}.{key} duplicates a canonical character/state field")
            _string(description, f"profile.{section}.{key}")


def validate_capabilities(state):
    character = state["character"]
    ratings = character["skills"]
    records = _object(character.get("capabilities"), "character.capabilities")
    if set(records) != set(ratings):
        _fail("capabilities metadata must have exactly the same keys as the skills rating map")
    # Validate shapes before following references, so malformed data fails cleanly.
    for key, record in records.items():
        _object(record, f"capabilities.{key}")
        kind = _string(record.get("kind"), f"capabilities.{key}.kind")
        if kind not in RECORD_FIELDS:
            _fail(f"Unknown capability kind: {kind}")
        _object(record, f"capabilities.{key}", RECORD_FIELDS[kind])
        _string(record["basis"], f"capabilities.{key}.basis")
        _evidence_turns(record["evidence_turns"], state["turn"], f"capabilities.{key}.evidence_turns")
        if kind in {"subskill", "derived"}:
            _string(record["domain"], f"capabilities.{key}.domain")
        if kind == "specialty":
            _string(record["parent"], f"capabilities.{key}.parent")
        if kind == "domain":
            _weights(record["anchors"], f"capabilities.{key}.anchors", 100,
                     minimum_count=3, maximum_count=5, maximum_weight=40)
        elif kind == "derived":
            derivation = _object(record["derivation"], "derivation", {"related", "exposure", "basis"})
            _string(derivation["basis"], "derivation.basis")
            _string(derivation["exposure"], "derivation.exposure")
            if derivation["exposure"] not in EXPOSURE:
                _fail("Derived exposure must be specialist, expected, plausible, or little")
            _weights(derivation["related"], "derivation.related", 60, maximum_weight=60)
        if kind in TRAINABLE:
            _integer(record["development"], f"capabilities.{key}.development", 0)
            if ratings[key] == 9 and record["development"] != 0:
                _fail("Rating 9 has no further Development track; development must be zero")
            aptitude = _object(record["aptitude"], "aptitude", {"level", "applied_to"})
            _string(aptitude["level"], "aptitude.level")
            _string(aptitude["applied_to"], "aptitude.applied_to")
            if aptitude["level"] not in APTITUDE_PERCENT:
                _fail("Aptitude level must be poor, ordinary, strong, or exceptional")
            if aptitude["applied_to"] not in {"development", "experience"}:
                _fail("Apply aptitude to development or experience, never both")
            _string(record["experience"], f"capabilities.{key}.experience")
            credited = _list(record["training"], f"capabilities.{key}.training")
            seen = set()
            for period in credited:
                _object(period, "training period", {"id", "start_seconds", "end_seconds", "development",
                                                   "activity", "basis", "evidence_turns"})
                for name in ("id", "activity", "basis"):
                    _string(period[name], f"training.{name}")
                if period["id"] in seen:
                    _fail(f"Duplicate credited training ID for {key}: {period['id']}")
                seen.add(period["id"])
                _integer(period["start_seconds"], "training.start_seconds", 0)
                _integer(period["end_seconds"], "training.end_seconds", 0, state["time_seconds"])
                if period["end_seconds"] <= period["start_seconds"]:
                    _fail("Credited training must cover a positive elapsed period")
                _integer(period["development"], "training.development", 1)
                _evidence_turns(period["evidence_turns"], state["turn"], "training.evidence_turns")
            end = -1
            for period in sorted(credited, key=lambda item: item["start_seconds"]):
                if period["start_seconds"] < end:
                    _fail(f"Overlapping credited training periods for {key}; group distinct causes in one entry")
                end = period["end_seconds"]
    for key, record in records.items():
        kind = record["kind"]
        if kind == "domain":
            for anchor in record["anchors"]:
                source = records.get(anchor)
                if source is None or source["kind"] != "subskill" or source["domain"] != key:
                    _fail(f"Domain {key} anchors must be established subskills belonging to that domain")
            calculated = _half_up_hundredths(sum(ratings[anchor] * weight for anchor, weight in record["anchors"].items()))
            if ratings[key] != calculated:
                _fail(f"Domain {key} rating must equal its half-up weighted anchor result: {calculated}")
        elif kind == "specialty":
            parent = records.get(record["parent"])
            if parent is None or parent["kind"] != "subskill":
                _fail("A specialty must name an established subskill as its parent")
        elif kind == "derived":
            parent = records.get(record["domain"])
            if parent is None or parent["kind"] != "domain":
                _fail("A derived capability needs an established parent domain")
            for related in record["derivation"]["related"]:
                source = records.get(related)
                if source is None or source["kind"] != "subskill":
                    _fail("Derived inference can use only established subskills, never other derived records")
            ceiling = derived_ceiling(ratings, record)
            if ratings[key] > ceiling:
                _fail(f"Derived {key} exceeds its evidence-based arithmetic ceiling {ceiling}")
        elif record["domain"] in records and records[record["domain"]]["kind"] != "domain":
            _fail("A subskill's domain name cannot refer to a non-domain capability")


def validate_setup(state):
    if state["campaign"].get("capability_system") != SYSTEM:
        return
    for key, record in state["character"]["capabilities"].items():
        if record["kind"] in TRAINABLE and record["training"]:
            _fail(f"Setup training for {key} must be empty; record pre-campaign experience descriptively")


def validate_transition(before, after):
    """Normal-turn advancement; corrections retain their explicit repair role."""
    if before["campaign"].get("capability_system") != SYSTEM:
        return
    old = before["character"]["capabilities"]
    new = after["character"]["capabilities"]
    old_ratings, new_ratings = before["character"]["skills"], after["character"]["skills"]
    for key, previous in old.items():
        if previous["kind"] in TRAINABLE and key not in new:
            _fail(f"Established capability {key} cannot be deleted on a normal turn")
    for key, current in new.items():
        previous = old.get(key)
        if current["kind"] not in TRAINABLE:
            if previous is not None and previous["kind"] in TRAINABLE:
                _fail("An established trainable capability cannot become provisional or a domain on a normal turn")
            continue
        if previous is None:
            if new_ratings[key] != 0:
                _fail("A newly recorded trainable capability starts at rating 0; repair established background with a correction")
            if current["development"] != sum(period["development"] for period in current["training"]):
                _fail("New capability Development must equal its credited training awards")
            continue
        if previous["kind"] not in TRAINABLE:
            if previous["kind"] != "derived":
                _fail("A domain cannot be relabeled as an established skill on a normal turn")
            if new_ratings[key] > old_ratings[key] or current["development"] != 0 or current["training"]:
                _fail("Derived reclassification allows the same or lower rating, zero Development, and no credited training")
            continue
        old_periods = {period["id"]: period for period in previous["training"]}
        new_periods = {period["id"]: period for period in current["training"]}
        for period_id, period in old_periods.items():
            if new_periods.get(period_id) != period:
                _fail(f"Credited training {key}/{period_id} cannot be changed or deleted on a normal turn")
        awarded = sum(period["development"] for period_id, period in new_periods.items() if period_id not in old_periods)
        reclassified = (previous["kind"] != current["kind"] or previous.get("domain") != current.get("domain")
                        or previous.get("parent") != current.get("parent"))
        if reclassified and new_ratings[key] > old_ratings[key]:
            _fail("Reclassification cannot grant a higher rating on the same turn")
        if new_ratings[key] > old_ratings[key] + 1:
            _fail(f"{key} can rise by at most one rating in a single event; surplus Development carries forward")
        consumed = sum(development_required(rating, current["aptitude"])
                       for rating in range(old_ratings[key], new_ratings[key]))
        expected = previous["development"] + awarded - consumed
        # Mastery has no next rank. Keep actual earned awards in training history,
        # but do not force a GM to understate an award to hit the last threshold.
        if expected >= 0 and new_ratings[key] == 9:
            expected = 0
        if expected < 0 or current["development"] != expected:
            _fail(f"Development for {key} must reconcile old points + credited awards - advancement thresholds ({expected})")


def render_details(state):
    """All optional player-safe records are visible, including advancement basis."""
    character = state["character"]
    lines = []
    if "profile" in character:
        lines.extend(["", "## Character profile", ""])
        if not character["profile"]:
            lines.append("Details not established.")
        for section, fields in character["profile"].items():
            lines.extend(["", f"### {section.replace('_', ' ').capitalize()}", ""])
            if not fields:
                lines.append("Details not established.")
            if section == "languages":
                for language in fields:
                    lines.append("; ".join(f"{key.capitalize()}: {value if value is not None else 'not recorded'}"
                                           for key, value in language.items()))
            else:
                for key, description in fields.items():
                    lines.append(f"{key.replace('_', ' ').capitalize()}: {description}")
    if "capabilities" not in character:
        return lines
    lines.extend(["", "## Capabilities", "", "0..9; descriptive evidence, never dice bonuses."])
    if not character["capabilities"]:
        lines.append("Capabilities not established.")
    for key, record in character["capabilities"].items():
        rating = character["skills"][key]
        lines.extend(["", f"### {key}: {rating}{'D' if record['kind'] == 'derived' else ''} [{record['kind']}]", ""])
        lines.append(f"Basis: {record['basis']}; evidence turns: {record['evidence_turns']}")
        if record["kind"] in TRAINABLE:
            target = development_required(rating, record["aptitude"])
            lines.append(f"Development: {record['development']}/{target if target is not None else 'maximum rating'}")
            if rating == 9:
                lines.append("Rating cap reached; surplus Development is not banked for a further rank.")
            lines.append(f"{('Domain: ' + record['domain']) if record['kind'] == 'subskill' else ('Parent: ' + record['parent'])}")
            lines.append(f"Aptitude: {record['aptitude']['level']}; applied to: {record['aptitude']['applied_to']}")
            lines.append(f"Relevant experience: {record['experience']}")
            for period in record["training"]:
                lines.append(f"Training {period['id']}: seconds {period['start_seconds']} to {period['end_seconds']}, "
                             f"+{period['development']} Development; {period['activity']}; {period['basis']}; "
                             f"evidence turns: {period['evidence_turns']}")
        elif record["kind"] == "domain":
            lines.append("Anchors: " + ", ".join(f"{anchor} {weight}%" for anchor, weight in record["anchors"].items()))
        else:
            derivation = record["derivation"]
            lines.append(f"Domain: {record['domain']} 40%; exposure: {derivation['exposure']}")
            lines.append("Related: " + ", ".join(f"{related} {weight}%" for related, weight in derivation["related"].items()))
            lines.append(f"Inference: {derivation['basis']}; arithmetic ceiling: {derived_ceiling(character['skills'], record)}")
    return lines
