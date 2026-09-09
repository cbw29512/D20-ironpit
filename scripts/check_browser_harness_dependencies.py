from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
_LOAD_BLOCK = re.compile(r"for \(const file of \[(?P<body>.*?)\]\) load\(file\);", re.S)
_DIRECT_LOAD = re.compile(r'load\("([^"]+\.js)"\);')
_QUOTED_FILE = re.compile(r'"([^"]+\.js)"')

DEPENDENCIES = {
    "browser-attack.js": (
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-attack-helpers.js",
    ),
    "browser-saves.js": (
        "browser-resources.js",
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-save-helpers.js",
    ),
    "browser-spell-resolution.js": ("browser-resources.js",),
}


def _load_sequence(text: str) -> list[str]:
    events: list[tuple[int, list[str]]] = []
    for match in _LOAD_BLOCK.finditer(text):
        events.append((match.start(), _QUOTED_FILE.findall(match.group("body"))))
    for match in _DIRECT_LOAD.finditer(text):
        events.append((match.start(), [match.group(1)]))
    return [filename for _, files in sorted(events) for filename in files]


def _missing_dependencies(files: list[str], consumer: str) -> list[str]:
    if consumer not in files:
        return []
    consumer_index = files.index(consumer)
    return [dep for dep in DEPENDENCIES[consumer] if dep not in files[:consumer_index]]


def main() -> int:
    failures: list[str] = []
    for path in sorted(FRONTEND.glob("*.test.cjs")):
        files = _load_sequence(path.read_text(encoding="utf-8"))
        for consumer in DEPENDENCIES:
            missing = _missing_dependencies(files, consumer)
            if missing:
                failures.append(f"{path.relative_to(ROOT)}: {consumer} missing/late {', '.join(missing)}")
    if failures:
        print("BROWSER_HARNESS_DEPENDENCY_FAILURE")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Browser harness dependency order is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
