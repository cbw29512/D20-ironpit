from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_RUNTIME = ROOT / "backend" / "app" / "combat"
BROWSER = ROOT / "frontend"

IDENTITY_COMPARISON = re.compile(
    r"""(?:class_id|archetype).*?(?:===|!==|==|!=).*?["'][A-Za-z][^"']*["']"""
)


def _runtime_files() -> list[Path]:
    files = sorted(PY_RUNTIME.glob("*.py"))
    files.extend(sorted(
        path for path in BROWSER.glob("browser-*.js")
        if not path.name.endswith(".test.js")
    ))
    return files


def main() -> None:
    violations: list[str] = []
    for path in _runtime_files():
        relative = path.relative_to(ROOT)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if IDENTITY_COMPARISON.search(line):
                violations.append(f"{relative}:{number}: {line.strip()}")
    if violations:
        detail = "\n".join(violations)
        raise SystemExit(
            "Combat runtime must dispatch from semantic capability data, not class/archetype identity:\n"
            + detail
        )
    print("Semantic runtime identity guard: clean")


if __name__ == "__main__":
    main()
