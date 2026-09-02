from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.class_subclass_composer import base_class_combat_features, compose_class_subclass_features
from app.content.hero_combat_feature_registry import compile_progression_feature_fields, unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.rogue_attacks import build_mara_shortbow_attack, build_mara_shortsword_attack
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.content.rogue_equipment import build_rogue_visual_loadout
from app.domain.models import CombatantTemplate, ResourceDefinition
from app.domain.traits import CombatTrait


def mara_rogue_features(level: int) -> tuple[str, ...]:
    if level < 3:
        return base_class_combat_features("rogue", level, ROGUE_COMBAT_LEVELS)
    return compose_class_subclass_features("rogue", "thief", level, ROGUE_COMBAT_LEVELS)


def unsupported_mara_rogue_features(level: int) -> tuple[str, ...]:
    return unsupported_hero_engine_features(mara_rogue_features(level))


def build_mara_quickstep_level(level: int) -> CombatantTemplate:
    """Compile Mara from Rogue base + Thief overlay + canonical Orc/Soldier combat build."""
    if level not in ROGUE_COMBAT_LEVELS:
        raise ValueError(f"Mara Rogue level {level} must be between 1 and 20.")
    unsupported = unsupported_mara_rogue_features(level)
    if unsupported:
        raise ValueError(f"Mara Rogue level {level} awaits combat support for: {', '.join(unsupported)}")
    if level != 1:
        raise ValueError("Mara Rogue build progression beyond level 1 is not yet compiled from the build overlay.")

    row = ROGUE_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["rogue"]
    return CombatantTemplate(
        id=canonical_template_id("rogue", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        armor_class=14,
        max_hp=10,
        speed_ft=30,
        initiative_bonus=3,
        weapon_attack=build_mara_shortsword_attack(),
        alternate_weapon_attacks=[build_mara_shortbow_attack()],
        saving_throw_bonuses={
            "strength": 1,
            "dexterity": 5,
            "constitution": 2,
            "intelligence": 2,
            "wisdom": 0,
            "charisma": 0,
        },
        skill_bonuses={"acrobatics": 5},
        combat_traits=[
            CombatTrait.SAVAGE_ATTACKER,
            CombatTrait.ADRENALINE_RUSH,
            CombatTrait.RELENTLESS_ENDURANCE,
        ],
        weapon_masteries=["shortsword", "shortbow"],
        progression_features=compile_progression_feature_fields(mara_rogue_features(level), level),
        visual=build_rogue_visual_loadout(),
        resources=[
            ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ],
        source="D&D Beyond Basic Rules 2024: Rogue 1, Orc, Soldier, Savage Attacker, Leather Armor, Shortsword, Shortbow, Vex",
    )
