from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
_LOAD_BLOCK = re.compile(r"for \(const file of \[(?P<body>.*?)\]\) load\(file\);", re.S)
_DIRECT_LOAD = re.compile(r'^(?P<indent>\s*)load\("(?P<name>[^"]+\.js)"\);\s*$')
_QUOTED_FILE = re.compile(r'"([^"]+\.js)"')
_SHARED = ["browser-forced-movement.js", "browser-control.js"]
_ATTACK_ONLY = ["browser-attack-helpers.js"]
_SAVE_ONLY = ["browser-resources.js", "browser-save-helpers.js"]


def _insert_before(result: list[str], consumer: str, dependencies: list[str]) -> list[str]:
    if consumer not in result:
        return result
    for dependency in dependencies:
        result = [item for item in result if item != dependency]
    consumer_index = result.index(consumer)
    result[consumer_index:consumer_index] = dependencies
    return result


def _sync_files(files: list[str]) -> list[str]:
    result = list(files)
    consumers = [name for name in ("browser-attack.js", "browser-saves.js") if name in result]
    if not consumers:
        return result
    for dependency in _SHARED:
        result = [item for item in result if item != dependency]
    earliest = min(result.index(consumer) for consumer in consumers)
    result[earliest:earliest] = _SHARED
    result = _insert_before(result, "browser-attack.js", _ATTACK_ONLY)
    result = _insert_before(result, "browser-saves.js", _SAVE_ONLY)
    return result


def _render_block(files: list[str]) -> str:
    lines = []
    for index in range(0, len(files), 4):
        chunk = ", ".join(f'"{name}"' for name in files[index:index + 4])
        lines.append(f"  {chunk},")
    return "for (const file of [\n" + "\n".join(lines) + "\n]) load(file);"


def _sync_direct_groups(text: str) -> str:
    lines = text.splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        match = _DIRECT_LOAD.match(lines[index])
        if match is None:
            result.append(lines[index])
            index += 1
            continue
        indent = match.group("indent")
        files: list[str] = []
        while index < len(lines):
            current = _DIRECT_LOAD.match(lines[index])
            if current is None or current.group("indent") != indent:
                break
            files.append(current.group("name"))
            index += 1
        result.extend(f'{indent}load("{name}");' for name in _sync_files(files))
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(result) + suffix


def _sync_text(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        files = _QUOTED_FILE.findall(match.group("body"))
        return _render_block(_sync_files(files))

    return _sync_direct_groups(_LOAD_BLOCK.sub(replace, text))


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
