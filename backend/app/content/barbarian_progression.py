from __future__ import annotations

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_progression import advance_template_data
from app.content.hero_combat_feature_registry import (
    compile_progression_feature_fields,
    unsupported_hero_engine_features,
)
from app.domain.models import CombatantTemplate, ResourceDefinition


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _features(level: int) -> tuple[str, ...]:
    return canonical_combat_features("barbarian", level, "path-berserker")


def _resources(level: int) -> list[ResourceDefinition]:
    row = BARBARIAN_COMBAT_LEVELS[level]
    return [
        ResourceDefinition(id="rage", name="Rage", max_uses=row.rage_uses),
        ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]


def _apply_row(data: dict[str, object], level: int) -> None:
    row = BARBARIAN_COMBAT_LEVELS[level]
    features = _features(level)
    primary = data.get("weapon_attack")
    alternates = data.get("alternate_weapon_attacks")
    if not isinstance(primary, dict) or not isinstance(alternates, list):
        raise ValueError("Rokhan Barbarian attack snapshot has an unexpected schema.")
    handaxe = next((item for item in alternates if isinstance(item, dict) and item.get("id") == "rokhan-handaxe-thrown"), None)
    if handaxe is None:
        raise ValueError("Rokhan Barbarian requires the audited thrown Handaxe attack.")

    strength_mod = _modifier(row.strength)
    dexterity_mod = _modifier(row.dexterity)
    constitution_mod = _modifier(row.constitution)
    for attack in (primary, handaxe):
        attack.update(attack_bonus=row.proficiency_bonus + strength_mod, damage_bonus=strength_mod)
    attack_ids = ["rokhan-greataxe", "rokhan-handaxe-thrown"]
    attack_action = None
    if row.attack_count > 1:
        attack_action = {"id": "extra-attack", "name": "Extra Attack",
                         "slots": [{"attack_ids": attack_ids} for _ in range(row.attack_count)]}
    data.update(
        armor_class=row.armor_class,
        max_hp=row.max_hp,
        speed_ft=row.speed_ft,
        initiative_bonus=dexterity_mod,
        attack_action=attack_action,
        weapon_masteries=list(row.weapon_masteries),
        saving_throw_bonuses={
            "strength": row.proficiency_bonus + strength_mod,
            "dexterity": dexterity_mod,
            "constitution": row.proficiency_bonus + constitution_mod,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
        skill_bonuses={"athletics": row.proficiency_bonus + strength_mod, "acrobatics": dexterity_mod},
        progression_features=compile_progression_feature_fields(features, level),
        resources=[item.model_dump() for item in _resources(level)],
        rage_damage_bonus=row.rage_damage_bonus,
        source=row.source,
    )


def unsupported_barbarian_engine_features(level: int) -> tuple[str, ...]:
    return unsupported_hero_engine_features(_features(level))


def build_rokhan_stonefury_level(level: int) -> CombatantTemplate:
    """Compile Rokhan from Barbarian base + Berserker overlay; missing mechanics fail closed."""
    if level not in BARBARIAN_COMBAT_LEVELS:
        raise ValueError(f"Rokhan Barbarian level {level} must be between 1 and 20.")
    unsupported = unsupported_barbarian_engine_features(level)
    if unsupported:
        raise ValueError(f"Rokhan Barbarian level {level} awaits engine support for: {', '.join(unsupported)}")
    if level == 1:
        return build_rokhan_stonefury()
    previous = build_rokhan_stonefury_level(level - 1)
    data = advance_template_data(previous, "barbarian", level)
    _apply_row(data, level)
    return CombatantTemplate.model_validate(data)


def build_rokhan_stonefury_level7_candidate() -> CombatantTemplate:
    """Build L7 audit data without approving an automatic Instinctive Pounce combat policy."""
    previous = build_rokhan_stonefury_level(6)
    data = advance_template_data(previous, "barbarian", 7)
    _apply_row(data, 7)
    return CombatantTemplate.model_validate(data)
