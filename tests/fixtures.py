"""Fully explicit test inputs. These are deliberately not campaign facts."""

from copy import deepcopy


def bind_head(store, payload):
    """Bind a new draft to its actual read state, without submitting or retrying it."""
    draft = deepcopy(payload)
    draft["expected_hash"] = store.validate()[-1]["hash"]
    return draft


def starting_state(mode="adjudicated"):
    return {
        "campaign": {
            "id": "test-only-campaign",
            "title": "Invented test fixture",
            "era": "Unspecified test era",
            "region": "Invented test region",
            "spoiler_cutoff": "No published plot events in this fixture",
            "day_zero_anchor": "Invented test day, midnight",
            "rules_version": "1",
            "resolution_mode": mode,
        },
        "turn": 0,
        "time_seconds": 0,
        "phase": "Test household service",
        "location": "Invented test store yard",
        "character": {
            "name": "Test Adult",
            "age": 24,
            "status": "Test retainer",
            "background": "Invented for automated tests only",
            "aim": "Check the test account",
            "skills": {"accounts": 2, "sword": 0},
            "conditions": [],
            "equipment": ["Test ledger"],
        },
        "resources": {"silver_stags": 8, "ration_days": 7},
        "relationships": [],
        "obligations": [],
        "tasks": [],
        "knowledge": [],
        "assumptions": ["Every named fact in this state is an invented test fixture."],
        "research": [],
        "standing_orders": [],
        "interrupted_plan": None,
        "resume_note": None,
        "alive": True,
        "death": None,
    }


def setup_payload(state=None, request_id="setup-test"):
    return {"request_id": request_id, "state": deepcopy(state or starting_state())}


def review_for(turn):
    return {
        "from_turn": turn - 9,
        "to_turn": turn,
        "findings": {
            category: {
                "assessment": "Test finding: routine work is recorded; ability remains uncertain.",
                "evidence_turns": [turn - 9, turn],
            }
            for category in (
                "results", "decisions", "capabilities", "position", "gm_consistency", "next_constraint"
            )
        },
    }


def turn_payload(turn=0, seconds=3600, **overrides):
    payload = {
        "request_id": f"test-turn-{turn + 1}",
        "expected_turn": turn,
        "elapsed_seconds": seconds,
        "objective": "Complete a routine test inspection",
        "outcome": "The routine inspection is complete",
        "narrative": "The test clerk records the count and closes the test account.",
        "resources_delta": {},
        "changes": {},
        "evidence": {},
        "processed_tasks": {},
        "checks": [],
        "review": review_for(turn + 1) if (turn + 1) % 10 == 0 else None,
    }
    payload.update(deepcopy(overrides))
    return payload


def task(due=7200, status="active", note="", task_id="test-delivery"):
    return {
        "id": task_id,
        "description": "Resolve the invented test delivery",
        "status": status,
        "due_seconds": due,
        "note": note,
    }


def source(source_id="test-source"):
    return {
        "id": source_id,
        "claim": "The invented test yard has a loading record",
        "source": "campaign convention",
        "type": "campaign_assumption",
        "scope": "This test fixture only",
        "confidence": "Explicit assumption",
        "limitations": "Not a canon fact or character knowledge",
    }


def correction(**overrides):
    payload = {
        "request_id": "test-correction",
        "reason": "Repair a duplicate recorded charge in the invented test account",
        "changes": {},
        "resources_delta": {"silver_stags": 1},
        "evidence": {"resources.silver_stags": "One stag was charged twice in the test entry"},
    }
    payload.update(deepcopy(overrides))
    return payload
