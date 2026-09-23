from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.level_resources import cleric_2014_channel_divinity_uses
from app.content.spell_slot_progression import spell_slot_resources
from app.content.shared_spells_2014 import aid_2014, lesser_restoration_2014, sanctuary_2014, spiritual_weapon_2014
from app.content.cleric_2014_level1_spells import (
    bless_2014,
    cure_wounds_2014,
    guiding_bolt_2014,
    healing_word_2014,
    inflict_wounds_2014,
    sacred_flame_2014,
    shield_of_faith_2014,
)
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _attack(weapon: Weapon, scores: AbilityScores, level: int) -> WeaponAttack:
    try:
        ability = "dexterity" if weapon.attack_kind is WeaponAttackKind.RANGED else "strength"
        modifier = scores.modifier(ability)
        return WeaponAttack(
            id=f"seraphine-2014-{weapon.id}", weapon=weapon,
            attack_bonus=proficiency_bonus(level) + modifier,
            damage_bonus=modifier, attack_ability=ability, attack_ability_modifier=modifier,
        )
    except Exception:
        logger.exception("Failed to compile Seraphine's 2014 %s attack.", weapon.id)
        raise


def _warhammer() -> Weapon:
    return Weapon(
        id="warhammer", name="Warhammer", attack_kind=WeaponAttackKind.MELEE,
        dice_count=1, dice_size=8, damage_type=DamageType.BLUDGEONING,
        animation="blunt-strike", reach_ft=5, mastery_property=None, versatile=True,
    )


def _light_crossbow() -> Weapon:
    return Weapon(
        id="light-crossbow", name="Light Crossbow", attack_kind=WeaponAttackKind.RANGED,
        dice_count=1, dice_size=8, damage_type=DamageType.PIERCING,
        animation="projectile", normal_range_ft=80, long_range_ft=320,
        projectile="bolt", mastery_property=None, two_handed=True,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    resources = [
        ResourceDefinition(id=resource_id, name=f"Level {resource_id.split('-')[-1]} Spell Slot", max_uses=uses)
        for resource_id, uses in spell_slot_resources("cleric", level).items()
    ]
    channel_uses = cleric_2014_channel_divinity_uses(level)
    if channel_uses:
        resources.append(ResourceDefinition(id="channel-divinity", name="Channel Divinity", max_uses=channel_uses))
    return resources


def build_seraphine_dawnshield_2014(level: int) -> CombatantTemplate:
    """Compile the currently certified RAW 2014 Life Cleric runtime."""
    try:
        if level not in range(1, 5):
            raise ValueError("2014 Life Cleric runtime is currently certified through level 4.")
        profile = build_seraphine_dawnshield_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        wisdom_modifier = scores.modifier("wisdom")
        spell_attack = pb + wisdom_modifier
        save_dc = 8 + spell_attack
        armor = get_armor("scale-mail")
        armor_class = compile_worn_armor_class(
            armor.base_ac, armor.category, scores.modifier("dexterity"), [],
            wielding_shield=True, shield_trained=True,
        )
        progression = ProgressionCombatFeatures(
            saving_throw_advantage_grants=[SavingThrowAdvantageGrant(
                source_id="dwarven-resilience",
                source_name="Dwarven Resilience",
                abilities=_ABILITIES,
                against_effect_tags=["poison", "poisoned"],
            )],
        )
        life_bonus = 3
        return CombatantTemplate(
            id=profile.template_id, name=profile.character_name, archetype=profile.class_name,
            level=level, kind="character", ruleset="2014", ability_scores=scores,
            armor_class=armor_class,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")) + level,
            speed_ft=25, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(_warhammer(), scores, level),
            alternate_weapon_attacks=[_attack(_light_crossbow(), scores, level)],
            spell_save_actions=[sacred_flame_2014(save_dc)],
            spell_attack_actions=[guiding_bolt_2014(spell_attack), inflict_wounds_2014(spell_attack)],
            persistent_spell_attack_actions=(
                [spiritual_weapon_2014(spell_attack, wisdom_modifier)]
                if level >= 3 else []
            ),
            defensive_spell_actions=[
                bless_2014(),
                shield_of_faith_2014(),
                *([sanctuary_2014(save_dc)] if level >= 2 else []),
                *([aid_2014()] if level >= 3 else []),
            ],
            healing_actions=[
                healing_word_2014(wisdom_modifier, life_bonus),
                cure_wounds_2014(wisdom_modifier, life_bonus),
            ],
            condition_removal_actions=(
                [lesser_restoration_2014()] if level >= 3 else []
            ),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses={
                "insight": wisdom_modifier + pb,
                "religion": scores.modifier("intelligence") + pb,
                "medicine": wisdom_modifier + pb,
                "persuasion": scores.modifier("charisma") + pb,
            },
            weapon_masteries=[], damage_resistances=[DamageType.POISON],
            combat_traits=[CombatTrait.LIFE_DOMAIN],
            resources=_resources(level),
            progression_features=progression,
            visual=VisualLoadout(armor="scale-mail", main_hand="warhammer", off_hand="shield", body_style="humanoid"),
            source=("D&D Basic Rules 2014: Hill Dwarf, Acolyte, Cleric, Life Domain, "
                    "Bless, Cure Wounds, Guiding Bolt, Healing Word, Inflict Wounds, "
                    "Sacred Flame, Shield of Faith, Aid, Lesser Restoration, Spiritual Weapon, Equipment"),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Seraphine Dawnshield at level %s.", level)
        raise
