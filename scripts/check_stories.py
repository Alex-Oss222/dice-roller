"""Validate each selected story without creating or advancing any campaign."""

from pathlib import Path
import tempfile

from iron_engine.engine import CampaignError, CampaignStore, read_json
from iron_engine.journal import render_campaign
from iron_engine.stories import Story


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    stories = root / "stories"
    count = 0
    failures = []
    for path in sorted(stories.iterdir()) if stories.exists() else []:
        if not path.is_dir():
            continue
        try:
            story = Story(path.name, root=root)
            events = story.validate()
            story.require_current_baseline()
            if not events and (story.path / "setup.json").exists():
                payload = read_json(story.path / "setup.json")
                story.check_setup(payload)
                with tempfile.TemporaryDirectory() as temporary:
                    temporary = Path(temporary)
                    store = CampaignStore(temporary / "campaign")
                    store.initialize(payload)
                    render_campaign(store, temporary / "play")
            state = f"turn {events[-1]['state']['turn']}" if events else "awaiting character setup"
            print(f"{path.name}: valid, {state}")
            count += 1
        except (CampaignError, OSError, ValueError) as exc:
            failures.append(f"{path.name}: {exc}")
    legacy = root / "campaign"
    if legacy.exists():
        try:
            CampaignStore(legacy).validate()
            print("Legacy campaign: validated without migration")
        except (CampaignError, OSError, ValueError) as exc:
            failures.append(f"Legacy campaign: {exc}")
    for failure in failures:
        print(f"ERROR: {failure}")
    if not count and not failures:
        print("No story folders yet; no campaign created.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
