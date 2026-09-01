from __future__ import annotations

from app.content.audited_fighter import build_karnok_stoneward
from app.content.canonical_progression import advance_template_data
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


def _progression_features(level: int) -> dict[str, object]:
    features: dict[str, object] = {}
    if level >= 3:
        features.update(
            critical_hit_minimum=19,
            initiative_advantage=True,
            athletics_advantage=True,
            critical_move_fraction=0.5,
        )
    if level >= 5:
        features["tactical_shift_fraction"] = 0.5
    return features


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


def _apply_level_five_scaling(data: dict[str, object]) -> None:
    weapon_attack = data["weapon_attack"]
    alternate_attacks = data["alternate_weapon_attacks"]
    saving_throws = data["saving_throw_bonuses"]
    skills = data["skill_bonuses"]
    if not isinstance(weapon_attack, dict) or not isinstance(alternate_attacks, list) or not isinstance(saving_throws, dict) or not isinstance(skills, dict):
        raise ValueError("Karnok Fighter 5 base snapshot has an unexpected schema.")
    weapon_attack["attack_bonus"] = 7
    shortbow = next((item for item in alternate_attacks if isinstance(item, dict) and item.get("id") == "karnok-shortbow"), None)
    if shortbow is None:
        raise ValueError("Karnok Fighter 5 requires the audited Shortbow attack.")
    shortbow["attack_bonus"] = 4
    saving_throws["strength"] = 7
    saving_throws["constitution"] = 6
    skills["athletics"] = 7
    attack_ids = ["karnok-greatsword", "karnok-shortbow"]
    data["attack_action"] = {
        "id": "extra-attack",
        "name": "Extra Attack",
        "slots": [{"attack_ids": attack_ids}, {"attack_ids": attack_ids}],
    }


def build_karnok_stoneward_level(level: int) -> CombatantTemplate:
    """Level the same canonical Fighter one step at a time; unsupported levels fail closed."""
    if level == 1:
        return build_karnok_stoneward()
    if level not in (2, 3, 4, 5):
        raise ValueError(f"Karnok Fighter level {level} is not certified yet.")

    previous = build_karnok_stoneward_level(level - 1)
    data = advance_template_data(previous, "fighter", level)
    constitution_modifier = 3 if level >= 4 else 2
    source_by_level = {
        2: "D&D Beyond Basic Rules 2024: Fighter 2, Orc, Soldier, Savage Attacker, Equipment",
        3: "D&D Beyond Basic Rules 2024: Fighter 3 Champion, Orc, Soldier, Savage Attacker, Equipment",
        4: "D&D Beyond Basic Rules 2024: Fighter 4 Ability Score Improvement, Second Wind, Weapon Mastery, Champion, Orc, Soldier, Savage Attacker, Equipment",
        5: "D&D Beyond Basic Rules 2024: Fighter 5 Extra Attack and Tactical Shift, Champion, Orc, Soldier, Savage Attacker, Equipment",
    }
    data.update(
        max_hp=fixed_class_hit_points(level, 10, constitution_modifier),
        resources=[item.model_dump() for item in _resources(level)],
        source=source_by_level[level],
        progression_features=_progression_features(level),
    )
    if level == 4:
        _apply_level_four_advancement(data)
    if level == 5:
        _apply_level_five_scaling(data)
    return CombatantTemplate.model_validate(data)
