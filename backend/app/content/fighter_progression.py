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


def _champion_features() -> dict[str, object]:
    return {
        "critical_hit_minimum": 19,
        "initiative_advantage": True,
        "athletics_advantage": True,
        "critical_move_fraction": 0.5,
    }


def _apply_level_four_advancement(data: dict[str, object]) -> None:
    weapon_attack = data["weapon_attack"]
    saving_throws = data["saving_throw_bonuses"]
    skills = data["skill_bonuses"]
    masteries = data["weapon_masteries"]
    if not isinstance(weapon_attack, dict) or not isinstance(saving_throws, dict) or not isinstance(skills, dict) or not isinstance(masteries, list):
        raise ValueError("Karnok Fighter 4 base snapshot has an unexpected schema.")

    weapon_attack["attack_bonus"] = 6
    weapon_attack["damage_bonus"] = 4
    saving_throws["strength"] = 6
    saving_throws["constitution"] = 5
    skills["athletics"] = 6
    masteries.append("longsword")


def build_karnok_stoneward_level(level: int) -> CombatantTemplate:
    """Return currently certified Karnok progression snapshots; unsupported levels fail closed."""
    if level == 1:
        return build_karnok_stoneward()
    if level not in (2, 3, 4):
        raise ValueError(f"Karnok Fighter level {level} is not certified yet.")

    data = build_karnok_stoneward().model_dump()
    constitution_modifier = 3 if level == 4 else 2
    source_by_level = {
        2: "D&D Beyond Basic Rules 2024: Fighter 2, Orc, Soldier, Savage Attacker, Equipment",
        3: "D&D Beyond Basic Rules 2024: Fighter 3 Champion, Orc, Soldier, Savage Attacker, Equipment",
        4: "D&D Beyond Basic Rules 2024: Fighter 4 Ability Score Improvement, Second Wind, Weapon Mastery, Champion, Orc, Soldier, Savage Attacker, Equipment",
    }
    data.update(
        id=f"karnok-stoneward-l{level}",
        level=level,
        max_hp=fixed_class_hit_points(level, 10, constitution_modifier),
        resources=[item.model_dump() for item in _resources(level)],
        source=source_by_level[level],
    )
    if level >= 3:
        data["progression_features"] = _champion_features()
    if level == 4:
        _apply_level_four_advancement(data)
    return CombatantTemplate.model_validate(data)
