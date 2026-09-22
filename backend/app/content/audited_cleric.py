from __future__ import annotations

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_hero_policy import canonical_template_id
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.cleric_divine_intervention import build_divine_intervention_damage
from app.content.cleric_life_domain import AID, DISPEL_MAGIC, LESSER_RESTORATION
from app.content.cleric_runtime_loadout import (
    build_seraphine_healing,
    build_seraphine_resources,
    build_seraphine_save_spells,
    seraphine_source,
)
from app.content.cleric_runtime_progression import build_seraphine_progression_features
from app.content.cleric_runtime_stats import (
    build_seraphine_mace_attack,
    seraphine_saving_throw_bonuses,
    seraphine_skill_bonuses,
)
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.offensive_spell_effects import build_guiding_bolt
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.traits import CombatTrait

def _modifier(score: int) -> int:
    return (score - 10) // 2


def _features(level: int) -> tuple[str, ...]:
    return canonical_combat_features("cleric", level, "life-domain")


def _build_seraphine(level: int) -> CombatantTemplate:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Seraphine Cleric level {level} must be between 1 and 20.")
    features = _features(level)
    unsupported = unsupported_hero_engine_features(features)
    if unsupported:
        raise ValueError(
            f"Seraphine Cleric level {level} awaits combat support for: {', '.join(unsupported)}"
        )

    row = CLERIC_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["cleric"]
    wisdom_modifier = _modifier(row.wisdom)
    charisma_modifier = _modifier(row.charisma)
    save_dc = 8 + row.proficiency_bonus + wisdom_modifier
    spell_attack_bonus = row.proficiency_bonus + wisdom_modifier

    defenses = [BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)]
    if level >= 3:
        defenses.insert(0, AID.model_copy(deep=True))

    traits = [CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE]
    if "disciple-of-life" in features:
        traits.append(CombatTrait.LIFE_DOMAIN)

    return CombatantTemplate(
        id=canonical_template_id("cleric", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        ability_scores=AbilityScores(
            strength=10, dexterity=10, constitution=10, intelligence=14,
            wisdom=row.wisdom, charisma=row.charisma,
        ),
        armor_class=row.armor_class,
        max_hp=row.max_hp,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=build_seraphine_mace_attack(row.proficiency_bonus),
        saving_throw_actions=[build_divine_intervention_damage(save_dc)] if level >= 10 else [],
        spell_save_actions=build_seraphine_save_spells(level, save_dc, wisdom_modifier, features),
        spell_attack_actions=[build_guiding_bolt(spell_attack_bonus)],
        defensive_spell_actions=defenses,
        healing_actions=build_seraphine_healing(level, wisdom_modifier, features),
        condition_removal_actions=[LESSER_RESTORATION.model_copy(deep=True)] if level >= 3 else [],
        effect_removal_actions=[DISPEL_MAGIC.model_copy(deep=True)] if level >= 5 else [],
        progression_features=build_seraphine_progression_features(level),
        saving_throw_bonuses=seraphine_saving_throw_bonuses(
            row.proficiency_bonus, wisdom_modifier, charisma_modifier,
        ),
        skill_bonuses=seraphine_skill_bonuses(
            row.proficiency_bonus, wisdom_modifier, charisma_modifier,
        ),
        combat_traits=traits,
        visual=VisualLoadout(
            armor="chain-shirt", main_hand="mace",
            off_hand="shield", body_style="humanoid",
        ),
        resources=build_seraphine_resources(level),
        source=seraphine_source(level),
    )


def build_seraphine_dawnshield_level(level: int) -> CombatantTemplate:
    """Compile Seraphine from Cleric base + Life Domain overlay; missing combat content fails closed."""
    return _build_seraphine(level)


def build_seraphine_dawnshield() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(1)


def build_seraphine_dawnshield_level_two() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(2)


def build_seraphine_dawnshield_level_three() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(3)


def build_seraphine_dawnshield_level_four() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(4)


def build_seraphine_dawnshield_level_five() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(5)


def build_seraphine_dawnshield_level_six() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(6)


def build_seraphine_dawnshield_level_seven() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(7)


def build_seraphine_dawnshield_level_eight() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(8)
