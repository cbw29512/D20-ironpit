from __future__ import annotations

import ast
from pathlib import Path

from app.content.capability_registry import build_monster_templates_from_capabilities

_COMBAT_DIR = Path(__file__).resolve().parents[1] / "app" / "combat"


def _monster_identity_literals() -> set[str]:
    identities: set[str] = set()
    for monster in build_monster_templates_from_capabilities():
        identities.update({monster.id, monster.name})
        identities.update(
            attack.id for attack in [monster.weapon_attack, *monster.alternate_weapon_attacks]
        )
        identities.update(action.id for action in monster.saving_throw_actions)
        identities.update(action.id for action in monster.forced_movement_actions)
        identities.update(action.id for action in monster.swallow_actions)
    return identities


def _string_literals(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def test_combat_engine_contains_no_compiled_monster_identity_literals() -> None:
    identities = _monster_identity_literals()
    violations: list[str] = []
    for path in sorted(_COMBAT_DIR.glob("*.py")):
        overlap = sorted(_string_literals(path) & identities)
        if overlap:
            violations.append(f"{path.name}: {', '.join(overlap)}")

    assert violations == [], (
        "Monster-specific identities are forbidden in the universal combat engine. "
        "Move behavior into declarative capability data:\n" + "\n".join(violations)
    )
