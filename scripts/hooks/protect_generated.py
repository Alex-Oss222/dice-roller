"""PreToolUse hook: refuse direct edits to generated pages and accepted events.

Reads the tool call from stdin as JSON. Exit code 2 blocks the call and returns
the message on stderr to the model. Everything else passes through.
"""

import json
import re
import sys

PROTECTED = re.compile(r"(^|/)stories/[^/]+/(play/|campaign/events/)")


def main() -> int:
    try:
        call = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    tool_input = call.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if PROTECTED.search(path.replace("\\", "/")):
        print("Blocked: this path is generated from accepted events. Use a correction or advance event and "
              "`python -m iron_engine --story <id> render`; never hand-edit play/ pages or campaign/events/.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
