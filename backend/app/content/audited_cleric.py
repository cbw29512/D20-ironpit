from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.cleric_divine_intervention import build_divine_intervention_damage, build_divine_intervention_healing
from app.content.cleric_life_domain import AID, DISPEL_MAGIC, LESSER_RESTORATION, disciple_of_life_bonus
from app.content.cleric_runtime_support import (
    ability_modifier,
    build_cleric_resources,
    build_mace_attack,
    cleric_features,
    cleric_source,
)
from app.content.healing_spell_effects import (
    build_cure_wounds, build_healing_word, build_mass_cure_wounds, build_mass_healing_word,
)
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.offensive_spell_effects import build_guiding_bolt, build_inflict_wounds, build_sacred_flame
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.character_builds import AbilityScores
from app.domain.progression import AbilityScaledDamageRider, ProgressionCombatFeatures, SlotHealingSelfRider
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _build_seraphine(level: int) -> CombatantTemplate:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Seraphine Cleric level {level} must be between 1 and 20.")
    features = cleric_features(level)
    unsupported = unsupported_hero_engine_features(features)
    if unsupported:
        raise ValueError(f"Seraphine Cleric level {level} awaits combat support for: {', '.join(unsupported)}")
    row = CLERIC_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["cleric"]
    wisdom_modifier = ability_modifier(row.wisdom)
    intelligence_modifier = 2
    charisma_modifier = ability_modifier(row.charisma)
    save_dc = 8 + row.proficiency_bonus + wisdom_modifier
    spell_attack_bonus = row.proficiency_bonus + wisdom_modifier
    life_bonus = disciple_of_life_bonus(1) if "disciple-of-life" in features else 0
    healing = [build_cure_wounds(wisdom_modifier, life_bonus)]
    if level >= 2:
        healing.append(build_healing_word(wisdom_modifier, life_bonus))
    if level >= 5:
        healing.append(build_mass_healing_word(
            wisdom_modifier,
            disciple_of_life_bonus(3) if "disciple-of-life" in features else 0,
        ))
    if level >= 9:
        healing.append(build_mass_cure_wounds(
            wisdom_modifier,
            disciple_of_life_bonus(5) if "disciple-of-life" in features else 0,
        ))
    if level >= 11:
        healing.append(build_mass_cure_wounds(
            wisdom_modifier,
            disciple_of_life_bonus(6) if "disciple-of-life" in features else 0,
            6,
        ))
    if level >= 10:
        healing.append(build_divine_intervention_healing(
            wisdom_modifier,
            disciple_of_life_bonus(5) if "disciple-of-life" in features else 0,
        ))
    defenses = [BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)]
    if level >= 3:
        defenses.insert(0, AID.model_copy(deep=True))
    save_spells = [build_sacred_flame(
        save_dc, level, wisdom_modifier if "blessed-strikes" in features else 0,
    )]
    if level >= 4:
        save_spells.append(build_inflict_wounds(save_dc))
    if level >= 9:
        save_spells.append(build_inflict_wounds(save_dc, 5))
    if level >= 11:
        save_spells.append(build_inflict_wounds(save_dc, 6))
    traits = [CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE]
    if "disciple-of-life" in features:
        traits.append(CombatTrait.LIFE_DOMAIN)
    return CombatantTemplate(
        id=canonical_template_id("cleric", level), name=hero.hero_name, archetype=hero.class_name,
        level=level, kind="character",
        ability_scores=AbilityScores(
            strength=10, dexterity=10, constitution=10, intelligence=14,
            wisdom=row.wisdom, charisma=row.charisma,
        ),
        armor_class=row.armor_class, max_hp=row.max_hp,
        speed_ft=30, initiative_bonus=0, weapon_attack=build_mace_attack(row.proficiency_bonus),
        saving_throw_actions=[build_divine_intervention_damage(save_dc)] if level >= 10 else [],
        spell_save_actions=save_spells, spell_attack_actions=[build_guiding_bolt(spell_attack_bonus)],
        defensive_spell_actions=defenses, healing_actions=healing,
        condition_removal_actions=[LESSER_RESTORATION.model_copy(deep=True)] if level >= 3 else [],
        effect_removal_actions=[DISPEL_MAGIC.model_copy(deep=True)] if level >= 5 else [],
        progression_features=ProgressionCombatFeatures(
            turning_failure_damage=(AbilityScaledDamageRider(
                source_id="sear-undead", ability="wisdom", dice_size=8, damage_type="radiant",
            ) if level >= 5 else None),
            slot_healing_other_self_rider=(SlotHealingSelfRider(
                source_id="blessed-healer", flat_bonus=2, per_slot_level=1,
            ) if level >= 6 else None),
        ),
        saving_throw_bonuses={
            "strength": 0, "dexterity": 0, "constitution": 0, "intelligence": intelligence_modifier,
            "wisdom": row.proficiency_bonus + wisdom_modifier,
            "charisma": row.proficiency_bonus + charisma_modifier,
        },
        skill_bonuses={
            "athletics": 0, "acrobatics": 0,
            "arcana": row.proficiency_bonus + intelligence_modifier,
            "history": row.proficiency_bonus + intelligence_modifier,
            "medicine": row.proficiency_bonus + wisdom_modifier,
            "persuasion": row.proficiency_bonus + charisma_modifier,
        },
        combat_traits=traits,
        visual=VisualLoadout(armor="chain-shirt", main_hand="mace", off_hand="shield", body_style="humanoid"),
        resources=build_cleric_resources(level), source=cleric_source(level),
    )


def build_seraphine_dawnshield_level(level: int) -> CombatantTemplate:
    """Compile Seraphine from Cleric base + Life Domain overlay; missing combat content fails closed."""
    try:
        return _build_seraphine(level)
    except Exception:
        logger.exception("Failed to build Seraphine Dawnshield at Cleric level %s.", level)
        raise


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
