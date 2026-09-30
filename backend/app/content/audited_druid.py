from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.character_math import saving_throw_bonuses
from app.content.druid_2024_spells import build_faerie_fire_2024, build_longstrider_2024, build_poison_spray_2024
from app.content.druid_combat_levels import DRUID_COMBAT_LEVELS
from app.content.healing_spell_effects import build_cure_wounds, build_healing_word
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.replacement_form_actions import ReplacementFormAction
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _sickle(proficiency_bonus: int, strength_modifier: int) -> WeaponAttack:
    weapon = build_weapon("sickle").model_copy(update={"mastery_property": None})
    return WeaponAttack(
        id="thalen-sickle",
        weapon=weapon,
        attack_bonus=proficiency_bonus + strength_modifier,
        damage_bonus=strength_modifier,
        attack_ability="strength",
        attack_ability_modifier=strength_modifier,
    )


def _wild_shape(level: int) -> list[ReplacementFormAction]:
    try:
        if level < 2:
            return []
        return [ReplacementFormAction(
            id="wild-shape", name="Wild Shape", action_cost="bonus_action",
            form_template_id="srd-wolf", resource_id="wild-shape", resource_cost=1,
            voluntary_revert_action="bonus_action", hp_mode="retain_owner",
            temporary_hp_on_enter=level, retain_creature_type=True,
            retain_spellcasting=False, source="D&D Beyond Basic Rules 2024: Druid — Wild Shape",
        )]
    except Exception:
        logger.exception("Failed to build 2024 Wild Shape at Druid level %s.", level)
        raise


def build_thalen_greenbough_level(level: int) -> CombatantTemplate:
    """Compile the certified 2024 Land-Druid progression."""
    try:
        if level not in {1, 2}:
            raise ValueError("2024 Thalen runtime currently supports Druid levels 1 through 2.")
        profile = build_thalen_greenbough_profile(level)
        row = DRUID_COMBAT_LEVELS[level]
        scores = profile.final_ability_scores
        wisdom_modifier = scores.modifier("wisdom")
        pb = row.proficiency_bonus
        armor = get_armor("leather")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            scores.modifier("dexterity"),
            [],
            wielding_shield=True,
            shield_trained=True,
        )
        if armor_class != row.armor_class:
            raise ValueError(
                f"2024 Druid level 1 AC drifted: compiled {armor_class}, spine {row.armor_class}."
            )
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype="Druid",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="Humanoid",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=row.max_hp,
            speed_ft=35,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_sickle(pb, scores.modifier("strength")),
            spell_attack_actions=[
                build_poison_spray_2024(pb + wisdom_modifier, level),
            ],
            spell_save_actions=[build_faerie_fire_2024(8 + pb + wisdom_modifier)] if level >= 2 else [],
            defensive_spell_actions=[build_longstrider_2024()],
            healing_actions=[
                build_healing_word(wisdom_modifier),
                build_cure_wounds(wisdom_modifier),
            ],
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="fey-ancestry",
                        source_name="Fey Ancestry",
                        abilities=_ABILITIES,
                        required_effect_tags=["charm"],
                    ),
                ],
            ),
            saving_throw_bonuses=saving_throw_bonuses(
                scores, level, ("intelligence", "wisdom"),
            ),
            skill_bonuses={
                "athletics": scores.modifier("strength"),
                "acrobatics": scores.modifier("dexterity"),
                "nature": scores.modifier("intelligence") + pb + wisdom_modifier,
                "survival": wisdom_modifier + pb,
                "insight": wisdom_modifier + pb,
                "religion": scores.modifier("intelligence") + pb,
                "perception": wisdom_modifier + pb,
            },
            resources=[
                ResourceDefinition(id="spell-slot-1", name="Spell Slot 1", max_uses=row.spell_slots[0]),
                *(
                    [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=row.wild_shape_uses)]
                    if row.wild_shape_uses else []
                ),
            ],
            replacement_form_actions=_wild_shape(level),
            weapon_masteries=[],
            visual=VisualLoadout(
                armor="leather",
                main_hand="sickle",
                off_hand="wooden-shield",
                body_style="humanoid",
            ),
            source=(
                "D&D Beyond Basic Rules 2024: Wood Elf, Acolyte, Druid, Primal Order: Magician, "
                "Poison Spray, Healing Word, Cure Wounds, Longstrider, Faerie Fire, Wild Shape, Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Thalen Greenbough at Druid level %s.", level)
        raise
