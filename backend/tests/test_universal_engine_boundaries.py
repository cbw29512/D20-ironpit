from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMBAT_ROOT = ROOT / "backend" / "app" / "combat"
MONSTER_ID = re.compile(r"['\"]srd-[a-z0-9-]+['\"]")
MONSTER_NAME_BRANCH = re.compile(r"template\.name\s*(?:==|!=|in\s*\{)")


def test_combat_engine_does_not_branch_on_monster_identity() -> None:
    violations: list[str] = []
    for path in sorted(COMBAT_ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if MONSTER_ID.search(text):
            violations.append(f"{path.relative_to(ROOT)} contains an SRD monster id")
        if MONSTER_NAME_BRANCH.search(text):
            violations.append(f"{path.relative_to(ROOT)} branches on template.name")
    assert not violations, "Monster behavior must be data-driven:\n" + "\n".join(violations)
