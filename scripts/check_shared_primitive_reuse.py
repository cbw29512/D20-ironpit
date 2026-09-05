from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PY_COMBAT = ROOT / "backend" / "app" / "combat"
FRONTEND = ROOT / "frontend"

_LEGACY_PATHS = (
    PY_COMBAT / "engine.py",
    PY_COMBAT / "movement.py",
    PY_COMBAT / "turns.py",
    PY_COMBAT / "encounter_turns.py",
)
_PY_DIRECT_D20_ALLOWED = {"rolls.py", "death_saves.py", "heroic_inspiration.py", "encounter_initiative.py"}
_BROWSER_DIRECT_D20_ALLOWED = {"browser-rolls.js"}


def _production_files(root: Path, suffix: str):
    return sorted(path for path in root.glob(f"*{suffix}") if not path.name.endswith((".test.py", ".test.js", ".test.cjs")))


def _add(violations: list[str], path: Path, reason: str) -> None:
    violations.append(f"{path.relative_to(ROOT)}: {reason}")


def main() -> None:
    violations: list[str] = []
    for path in _LEGACY_PATHS:
        if path.exists():
            _add(violations, path, "retired duplicate duel-engine path exists")

    for path in _production_files(PY_COMBAT, ".py"):
        text = path.read_text(encoding="utf-8")
        if path.name not in _PY_DIRECT_D20_ALLOWED and re.search(r"\b(?:dice|roller)\.roll\(20\)", text):
            _add(violations, path, "direct normal d20 roll bypasses shared roll/save primitives")
        if path.name != "rolls.py" and "advantage_sources > 0" in text and "disadvantage_sources > 0" in text:
            _add(violations, path, "duplicates Advantage/Disadvantage source collapse")
        if path.name != "rolls.py" and re.search(r"natural\s*!=\s*1\s+and\s*\(natural\s*==\s*20\s+or\s+total\s*>=", text):
            _add(violations, path, "duplicates universal attack-hit rule")
        if path.name != "bloodied.py" and re.search(r"current_hp\s*\*\s*2\s*<=|current_hp\s*<=\s*[^\n]{0,60}max_hp\s*/\s*2", text):
            _add(violations, path, "duplicates Bloodied threshold instead of shared helper")
        if path.name != "damage_defenses.py" and "damage_immunities" in text and "damage_resistances" in text and "damage_vulnerabilities" in text:
            _add(violations, path, "duplicates typed damage-defense collections")

    for path in _production_files(FRONTEND, ".js"):
        text = path.read_text(encoding="utf-8")
        if path.name not in _BROWSER_DIRECT_D20_ALLOWED and re.search(r"\.roll\(20\)", text):
            _add(violations, path, "direct browser d20 roll bypasses shared browser-rolls")
        if path.name != "browser-rolls.js" and re.search(r"advantage\s*>\s*0", text) and re.search(r"disadvantage\s*>\s*0", text):
            _add(violations, path, "duplicates browser Advantage/Disadvantage source collapse")
        if path.name != "browser-rolls.js" and re.search(r"natural\s*!==\s*1\s*&&\s*\(natural\s*===\s*20\s*\|\|\s*total\s*>=", text):
            _add(violations, path, "duplicates browser universal attack-hit rule")
        if path.name != "browser-state.js" and re.search(r"current_hp\s*\*\s*2\s*<=|current_hp\s*<=\s*[^\n]{0,60}max_hp\s*/\s*2", text):
            _add(violations, path, "duplicates browser Bloodied threshold")

    if violations:
        raise SystemExit("Shared primitive reuse violations:\n- " + "\n- ".join(violations))
    print("SHARED_PRIMITIVE_REUSE ok")


if __name__ == "__main__":
    main()
