from __future__ import annotations

from app.content.audited_fighter import build_karnok_stoneward
from app.content.canonical_progression import advance_template_data
from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS, fighter_combat_features
from app.domain.models import CombatantTemplate, ResourceDefinition


_SUPPORTED_ENGINE_FEATURES = {
    "second-wind", "savage-attacker", "adrenaline-rush", "relentless-endurance",
    "action-surge", "tactical-mind", "improved-critical", "remarkable-athlete",
    "extra-attack", "tactical-shift", "great-weapon-fighting", "indomitable",
    "tactical-master-sap",
}


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _resources(level: int) -> list[ResourceDefinition]:
    row = FIGHTER_COMBAT_LEVELS[level]
    rows = [
        ("second-wind", "Second Wind", row.second_wind_uses),
        ("action-surge", "Action Surge", row.action_surge_uses),
        ("indomitable", "Indomitable", row.indomitable_uses),
        ("adrenaline-rush", "Adrenaline Rush", row.proficiency_bonus),
        ("relentless-endurance", "Relentless Endurance", 1),
    ]
    return [ResourceDefinition(id=resource_id, name=name, max_uses=uses)
            for resource_id, name, uses in rows if uses > 0]


def _progression_features(level: int, features: set[str]) -> dict[str, object]:
    critical_minimum = 18 if "superior-critical" in features else 19 if "improved-critical" in features else 20
    return {
        "critical_hit_minimum": critical_minimum,
        "initiative_advantage": "remarkable-athlete" in features,
        "athletics_advantage": "remarkable-athlete" in features,
        "critical_move_fraction": 0.5 if "remarkable-athlete" in features else 0.0,
        "tactical_shift_fraction": 0.5 if "tactical-shift" in features else 0.0,
        "great_weapon_fighting": "great-weapon-fighting" in features,
        "indomitable_bonus": level if "indomitable" in features else 0,
        "tactical_master_sap": "tactical-master-sap" in features,
    }


def _apply_row(data: dict[str, object], level: int) -> None:
    row = FIGHTER_COMBAT_LEVELS[level]
    features = set(fighter_combat_features(level))
    primary = data.get("weapon_attack")
    alternates = data.get("alternate_weapon_attacks")
    if not isinstance(primary, dict) or not isinstance(alternates, list):
        raise ValueError("Karnok Fighter attack snapshot has an unexpected schema.")
    shortbow = next((item for item in alternates if isinstance(item, dict) and item.get("id") == "karnok-shortbow"), None)
    if shortbow is None:
        raise ValueError("Karnok Fighter requires the audited Shortbow attack.")

    strength_mod = _modifier(row.strength)
    dexterity_mod = _modifier(row.dexterity)
    constitution_mod = _modifier(row.constitution)
    primary.update(attack_bonus=row.proficiency_bonus + strength_mod, damage_bonus=strength_mod,
                   damage_die_minimum=3 if "great-weapon-fighting" in features else None)
    shortbow.update(attack_bonus=row.proficiency_bonus + dexterity_mod, damage_bonus=dexterity_mod)
    ids = ["karnok-greatsword", "karnok-shortbow"]
    attack_action = None
    if row.attack_count > 1:
        attack_action = {"id": "extra-attack", "name": "Extra Attack",
                         "slots": [{"attack_ids": ids} for _ in range(row.attack_count)]}
    data.update(
        armor_class=row.armor_class,
        max_hp=row.max_hp,
        initiative_bonus=dexterity_mod,
        weapon_masteries=list(row.weapon_masteries),
        resources=[item.model_dump() for item in _resources(level)],
        attack_action=attack_action,
        saving_throw_bonuses={
            "strength": row.proficiency_bonus + strength_mod,
            "dexterity": dexterity_mod,
            "constitution": row.proficiency_bonus + constitution_mod,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
        skill_bonuses={"athletics": row.proficiency_bonus + strength_mod, "acrobatics": dexterity_mod},
        progression_features=_progression_features(level, features),
        source=row.source,
    )


def unsupported_fighter_engine_features(level: int) -> tuple[str, ...]:
    return tuple(feature for feature in fighter_combat_features(level) if feature not in _SUPPORTED_ENGINE_FEATURES)


def build_karnok_stoneward_level(level: int) -> CombatantTemplate:
    """Compile Karnok from the complete 1-20 Fighter combat table; unsupported mechanics fail closed."""
    if level not in FIGHTER_COMBAT_LEVELS:
        raise ValueError(f"Karnok Fighter level {level} must be between 1 and 20.")
    unsupported = unsupported_fighter_engine_features(level)
    if unsupported:
        raise ValueError(f"Karnok Fighter level {level} awaits engine support for: {', '.join(unsupported)}")
    if level == 1:
        return build_karnok_stoneward()
    previous = build_karnok_stoneward_level(level - 1)
    data = advance_template_data(previous, "fighter", level)
    _apply_row(data, level)
    return CombatantTemplate.model_validate(data)
