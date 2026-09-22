from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.class_subclass_composer import base_class_combat_features, compose_class_subclass_features
from app.content.hero_combat_feature_registry import compile_progression_feature_fields, unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.character_math import fixed_hit_points
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


_MARA_LOADOUT_INERT_FEATURES = frozenset({"thief-fast-hands"})


def unsupported_mara_rogue_features(level: int) -> tuple[str, ...]:
    """Fail closed on real engine gaps, excluding features inert for Mara's certified loadout."""
    active = tuple(
        feature
        for feature in mara_rogue_features(level)
        if feature not in _MARA_LOADOUT_INERT_FEATURES
    )
    return unsupported_hero_engine_features(active)


def _ability_scores(level: int) -> AbilityScores:
    if level >= 4:
        return AbilityScores(
            strength=13, dexterity=18, constitution=16,
            intelligence=10, wisdom=10, charisma=10,
        )
    return AbilityScores(
        strength=13, dexterity=17, constitution=15,
        intelligence=10, wisdom=10, charisma=10,
    )


def build_mara_quickstep_level(level: int) -> CombatantTemplate:
    """Compile Mara from Rogue base + Thief overlay + canonical Orc/Soldier combat build."""
    if level not in ROGUE_COMBAT_LEVELS:
        raise ValueError(f"Mara Rogue level {level} must be between 1 and 20.")
    unsupported = unsupported_mara_rogue_features(level)
    if unsupported:
        raise ValueError(f"Mara Rogue level {level} awaits combat support for: {', '.join(unsupported)}")
    row = ROGUE_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["rogue"]
    scores = _ability_scores(level)
    dexterity_mod = scores.modifier("dexterity")
    constitution_mod = scores.modifier("constitution")
    strength_mod = scores.modifier("strength")
    intelligence_mod = scores.modifier("intelligence")
    attack_bonus = row.proficiency_bonus + dexterity_mod
    return CombatantTemplate(
        id=canonical_template_id("rogue", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        ability_scores=scores,
        armor_class=11 + dexterity_mod,
        max_hp=fixed_hit_points(level, 8, constitution_mod),
        speed_ft=30,
        initiative_bonus=dexterity_mod,
        weapon_attack=build_mara_shortsword_attack(
            attack_bonus=attack_bonus, damage_bonus=dexterity_mod,
        ),
        alternate_weapon_attacks=[build_mara_shortbow_attack(
            attack_bonus=attack_bonus, damage_bonus=dexterity_mod,
        )],
        saving_throw_bonuses={
            "strength": strength_mod,
            "dexterity": row.proficiency_bonus + dexterity_mod,
            "constitution": constitution_mod,
            "intelligence": row.proficiency_bonus + intelligence_mod,
            "wisdom": scores.modifier("wisdom"),
            "charisma": scores.modifier("charisma"),
        },
        skill_bonuses={
            "athletics": row.proficiency_bonus + strength_mod,
            "acrobatics": row.proficiency_bonus + dexterity_mod,
        },
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
        source=f"D&D Beyond Basic Rules 2024: Rogue {level}, Orc, Soldier, Savage Attacker, Leather Armor, Shortsword, Shortbow, Vex",
    )
