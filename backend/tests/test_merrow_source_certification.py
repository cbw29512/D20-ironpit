from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _attack_shape(template) -> list[tuple[str, str, str | None, int | None, str | None]]:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return [
        (
            attack.id,
            attack.weapon.attack_kind.value,
            attack.control_effect.forced_movement.direction if attack.control_effect and attack.control_effect.forced_movement else None,
            attack.control_effect.forced_movement.max_distance_ft if attack.control_effect and attack.control_effect.forced_movement else None,
            attack.control_effect.forced_movement.distance_mode if attack.control_effect and attack.control_effect.forced_movement else None,
        )
        for attack in attacks
    ]


def test_merrow_compiled_runtime_matches_canonical_source() -> None:
    row = next(item for item in load_monster_rows() if item["name"] == "Merrow")
    template = next(item for item in build_arena_roster().monsters if item.name == "Merrow")
    issues = audit_monster_source(template, row)
    assert issues == [], f"Merrow issues={issues}; runtime_attacks={_attack_shape(template)}"
