from __future__ import annotations

from app.content.audited_fighter import build_karnok_stoneward
from app.content.canonical_progression import advance_template_data
from app.content.fighter_level9 import apply_fighter_level9
from app.content.fighter_progression_deltas import (
    apply_level_eight, apply_level_five, apply_level_four, apply_level_seven, apply_level_six,
)
from app.content.level_resources import (
    fighter_action_surge_uses, fighter_indomitable_uses, fighter_second_wind_uses,
    fixed_class_hit_points, orc_adrenaline_rush_uses,
)
from app.domain.models import CombatantTemplate, ResourceDefinition

_SOURCES = {
    2: "D&D Beyond Basic Rules 2024: Fighter 2, Orc, Soldier, Savage Attacker, Equipment",
    3: "D&D Beyond Basic Rules 2024: Fighter 3 Champion, Orc, Soldier, Savage Attacker, Equipment",
    4: "D&D Beyond Basic Rules 2024: Fighter 4 Ability Score Improvement, Second Wind, Weapon Mastery, Champion, Orc, Soldier, Savage Attacker, Equipment",
    5: "D&D Beyond Basic Rules 2024: Fighter 5 Extra Attack and Tactical Shift, Champion, Orc, Soldier, Savage Attacker, Equipment",
    6: "D&D Beyond Basic Rules 2024: Fighter 6 Ability Score Improvement, Champion, Orc, Soldier, Savage Attacker, Equipment",
    7: "D&D Beyond Basic Rules 2024: Fighter 7 Champion Additional Fighting Style, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment",
    8: "D&D Beyond Basic Rules 2024: Fighter 8 Ability Score Improvement, Champion, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment",
    9: "D&D Beyond Basic Rules 2024: Fighter 9 Indomitable and Tactical Master, Champion, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment",
}
_DELTAS = {4: apply_level_four, 5: apply_level_five, 6: apply_level_six, 7: apply_level_seven,
           8: apply_level_eight, 9: apply_fighter_level9}


def _resources(level: int) -> list[ResourceDefinition]:
    rows = [
        ("second-wind", "Second Wind", fighter_second_wind_uses(level)),
        ("action-surge", "Action Surge", fighter_action_surge_uses(level)),
        ("indomitable", "Indomitable", fighter_indomitable_uses(level)),
        ("adrenaline-rush", "Adrenaline Rush", orc_adrenaline_rush_uses(level)),
        ("relentless-endurance", "Relentless Endurance", 1),
    ]
    return [ResourceDefinition(id=resource_id, name=name, max_uses=uses) for resource_id, name, uses in rows if uses > 0]


def _progression_features(level: int) -> dict[str, object]:
    features: dict[str, object] = {}
    if level >= 3:
        features.update(critical_hit_minimum=19, initiative_advantage=True, athletics_advantage=True,
                        critical_move_fraction=0.5)
    if level >= 5:
        features["tactical_shift_fraction"] = 0.5
    if level >= 7:
        features["great_weapon_fighting"] = True
    if level >= 9:
        features.update(indomitable_bonus=level, tactical_master_sap=True)
    return features


def build_karnok_stoneward_level(level: int) -> CombatantTemplate:
    """Level the same canonical Fighter one step at a time; unsupported levels fail closed."""
    if level == 1:
        return build_karnok_stoneward()
    if level not in range(2, 10):
        raise ValueError(f"Karnok Fighter level {level} is not certified yet.")
    previous = build_karnok_stoneward_level(level - 1)
    data = advance_template_data(previous, "fighter", level)
    constitution_modifier = 4 if level >= 8 else 3 if level >= 4 else 2
    data.update(
        max_hp=fixed_class_hit_points(level, 10, constitution_modifier),
        resources=[item.model_dump() for item in _resources(level)],
        source=_SOURCES[level],
        progression_features=_progression_features(level),
    )
    delta = _DELTAS.get(level)
    if delta is not None:
        delta(data)
    return CombatantTemplate.model_validate(data)
