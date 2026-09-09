from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
_LOAD_BLOCK = re.compile(r"for \(const file of \[(?P<body>.*?)\]\) load\(file\);", re.S)
_QUOTED_FILE = re.compile(r'"([^"]+\.js)"')
_DEPENDENCIES = {
    "browser-attack.js": [
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-attack-helpers.js",
    ],
    "browser-saves.js": [
        "browser-resources.js",
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-save-helpers.js",
    ],
}


def _sync_files(files: list[str]) -> list[str]:
    result = list(files)
    for consumer, dependencies in _DEPENDENCIES.items():
        if consumer not in result:
            continue
        for dependency in dependencies:
            result = [item for item in result if item != dependency]
        consumer_index = result.index(consumer)
        result[consumer_index:consumer_index] = dependencies
    return result


def _render(files: list[str]) -> str:
    lines = []
    for index in range(0, len(files), 4):
        chunk = ", ".join(f'"{name}"' for name in files[index:index + 4])
        lines.append(f"  {chunk},")
    return "for (const file of [\n" + "\n".join(lines) + "\n]) load(file);"


def _sync_text(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        files = _QUOTED_FILE.findall(match.group("body"))
        return _render(_sync_files(files))

    return _LOAD_BLOCK.sub(replace, text)


def main() -> int:
    changed = []
    for path in sorted(FRONTEND.glob("*.test.cjs")):
        original = path.read_text(encoding="utf-8")
        updated = _sync_text(original)
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))
    print(f"BROWSER_HARNESS_SYNC changed={len(changed)}")
    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
