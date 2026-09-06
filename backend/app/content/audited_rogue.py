from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.class_subclass_composer import base_class_combat_features, compose_class_subclass_features
from app.content.hero_combat_feature_registry import compile_progression_feature_fields, unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.rogue_attacks import build_mara_shortbow_attack, build_mara_shortsword_attack
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.content.rogue_equipment import build_rogue_visual_loadout
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition
from app.domain.traits import CombatTrait


def mara_rogue_features(level: int) -> tuple[str, ...]:
    if level < 3:
        return base_class_combat_features("rogue", level, ROGUE_COMBAT_LEVELS)
    return compose_class_subclass_features("rogue", "thief", level, ROGUE_COMBAT_LEVELS)


def unsupported_mara_rogue_features(level: int) -> tuple[str, ...]:
    return unsupported_hero_engine_features(mara_rogue_features(level))


def _scores(level: int) -> AbilityScores:
    return AbilityScores(
        strength=13,
        dexterity=18 if level >= 4 else 17,
        constitution=16 if level >= 4 else 15,
        intelligence=10,
        wisdom=10,
        charisma=10,
    )


def _max_hp(level: int) -> int:
    hp = 10 + 7 * (level - 1)
    return hp + level if level >= 4 else hp


def build_mara_quickstep_level(level: int) -> CombatantTemplate:
    """Compile Mara from the canonical Rogue/Thief combat spine; unsupported levels fail closed."""
    if level not in ROGUE_COMBAT_LEVELS:
        raise ValueError(f"Mara Rogue level {level} must be between 1 and 20.")
    unsupported = unsupported_mara_rogue_features(level)
    if unsupported:
        raise ValueError(f"Mara Rogue level {level} awaits combat support for: {', '.join(unsupported)}")
    if level > 4:
        raise ValueError("Mara Rogue levels above 4 await Cunning Strike and reaction support.")

    row = ROGUE_COMBAT_LEVELS[level]
    scores = _scores(level)
    dexterity_mod = scores.modifier("dexterity")
    constitution_mod = scores.modifier("constitution")
    shortsword = build_mara_shortsword_attack().model_copy(update={
        "attack_bonus": row.proficiency_bonus + dexterity_mod,
        "damage_bonus": dexterity_mod,
    })
    shortbow = build_mara_shortbow_attack().model_copy(update={
        "attack_bonus": row.proficiency_bonus + dexterity_mod,
        "damage_bonus": dexterity_mod,
    })
    hero = HERO_BY_CLASS["rogue"]
    return CombatantTemplate(
        id=canonical_template_id("rogue", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        ability_scores=scores,
        armor_class=11 + dexterity_mod,
        max_hp=_max_hp(level),
        speed_ft=30,
        initiative_bonus=dexterity_mod,
        weapon_attack=shortsword,
        alternate_weapon_attacks=[shortbow],
        saving_throw_bonuses={
            "strength": scores.modifier("strength"),
            "dexterity": dexterity_mod + row.proficiency_bonus,
            "constitution": constitution_mod,
            "intelligence": scores.modifier("intelligence") + row.proficiency_bonus,
            "wisdom": scores.modifier("wisdom"),
            "charisma": scores.modifier("charisma"),
        },
        skill_bonuses={
            "athletics": scores.modifier("strength") + row.proficiency_bonus,
            "acrobatics": dexterity_mod + row.proficiency_bonus,
        },
        combat_traits=[CombatTrait.SAVAGE_ATTACKER, CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
        weapon_masteries=["shortsword", "shortbow"],
        progression_features=compile_progression_feature_fields(mara_rogue_features(level), level),
        visual=build_rogue_visual_loadout(),
        resources=[
            ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ],
        source=f"D&D Beyond Basic Rules 2024: Rogue {level}, Thief, Orc, Soldier, Savage Attacker, Leather Armor, Shortsword, Shortbow, Vex",
    )
