from __future__ import annotations

from app.content.audited_fighter import build_karnok_stoneward
from app.content.level_resources import (
    fighter_action_surge_uses,
    fighter_second_wind_uses,
    fixed_class_hit_points,
    orc_adrenaline_rush_uses,
)
from app.domain.models import CombatantTemplate, ResourceDefinition


def _resources(level: int) -> list[ResourceDefinition]:
    rows = [
        ("second-wind", "Second Wind", fighter_second_wind_uses(level)),
        ("action-surge", "Action Surge", fighter_action_surge_uses(level)),
        ("adrenaline-rush", "Adrenaline Rush", orc_adrenaline_rush_uses(level)),
        ("relentless-endurance", "Relentless Endurance", 1),
    ]
    return [ResourceDefinition(id=resource_id, name=name, max_uses=uses) for resource_id, name, uses in rows if uses > 0]


def build_karnok_stoneward_level(level: int) -> CombatantTemplate:
    """Return currently certified Karnok progression snapshots; unsupported levels fail closed."""
    if level == 1:
        return build_karnok_stoneward()
    if level != 2:
        raise ValueError(f"Karnok Fighter level {level} is not certified yet.")
    data = build_karnok_stoneward().model_dump()
    data.update(
        id="karnok-stoneward-l2",
        level=2,
        max_hp=fixed_class_hit_points(2, 10, 2),
        resources=[item.model_dump() for item in _resources(2)],
        source="D&D Beyond Basic Rules 2024: Fighter 2, Orc, Soldier, Savage Attacker, Equipment",
    )
    return CombatantTemplate.model_validate(data)
