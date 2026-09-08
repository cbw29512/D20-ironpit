from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

DEPENDENCIES = {
    "browser-attack.js": (
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-attack-helpers.js",
    ),
    "browser-saves.js": (
        "browser-forced-movement.js",
        "browser-control.js",
        "browser-save-helpers.js",
    ),
}


def _ordered_before(text: str, dependency: str, consumer: str) -> bool:
    dep_index = text.find(f'"{dependency}"')
    consumer_index = text.find(f'"{consumer}"')
    return dep_index >= 0 and consumer_index >= 0 and dep_index < consumer_index


def main() -> int:
    failures: list[str] = []
    for path in sorted(FRONTEND.glob("*.test.cjs")):
        text = path.read_text(encoding="utf-8")
        for consumer, dependencies in DEPENDENCIES.items():
            if f'"{consumer}"' not in text:
                continue
            missing = [dep for dep in dependencies if not _ordered_before(text, dep, consumer)]
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
