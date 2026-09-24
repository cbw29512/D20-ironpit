from __future__ import annotations

import logging

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_2014_level1_spells import (
    bless_2014,
    cure_wounds_2014,
    guiding_bolt_2014,
    healing_word_2014,
    inflict_wounds_2014,
    sacred_flame_2014,
    shield_of_faith_2014,
)
from app.content.cleric_2014_level4_spells import death_ward_2014, guardian_of_faith_2014
from app.content.cleric_2014_level5_spells import mass_cure_wounds_2014
from app.content.cleric_2014_divine_intervention import divine_intervention_full_heal_2014
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime_support import (
    build_cleric_progression_2014,
    build_cleric_resources_2014,
    build_seraphine_weapon_attack,
    seraphine_light_crossbow,
    seraphine_warhammer,
)
from app.content.shared_spells_2014 import (
    aid_2014,
    beacon_of_hope_2014,
    lesser_restoration_2014,
    sanctuary_2014,
    spiritual_weapon_2014,
)
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def build_seraphine_dawnshield_2014(level: int) -> CombatantTemplate:
    """Compile the currently certified RAW 2014 Life Cleric runtime."""
    try:
        if level not in range(1, 12):
            raise ValueError("2014 Life Cleric runtime is currently certified through level 11.")
        profile = build_seraphine_dawnshield_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        wisdom_modifier = scores.modifier("wisdom")
        spell_attack = pb + wisdom_modifier
        save_dc = 8 + spell_attack
        armor = get_armor("scale-mail")
        armor_class = compile_worn_armor_class(
            armor.base_ac,
            armor.category,
            scores.modifier("dexterity"),
            [],
            wielding_shield=True,
            shield_trained=True,
        )
        return CombatantTemplate(
            id=profile.template_id,
            name=profile.character_name,
            archetype=profile.class_name,
            level=level,
            kind="character",
            ruleset="2014",
            ability_scores=scores,
            armor_class=armor_class,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")) + level,
            speed_ft=25,
            initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=build_seraphine_weapon_attack(seraphine_warhammer(), scores, level),
            alternate_weapon_attacks=[
                build_seraphine_weapon_attack(seraphine_light_crossbow(), scores, level)
            ],
            spell_save_actions=[sacred_flame_2014(save_dc, level)],
            spell_attack_actions=[
                guiding_bolt_2014(spell_attack),
                inflict_wounds_2014(spell_attack),
                *([inflict_wounds_2014(spell_attack, 5)] if level >= 9 else []),
                *([inflict_wounds_2014(spell_attack, 6)] if level >= 11 else []),
            ],
            persistent_spell_attack_actions=(
                [spiritual_weapon_2014(spell_attack, wisdom_modifier)] if level >= 3 else []
            ),
            persistent_hazard_actions=(
                [guardian_of_faith_2014(save_dc)] if level >= 7 else []
            ),
            defensive_spell_actions=[
                bless_2014(),
                shield_of_faith_2014(),
                *([sanctuary_2014(save_dc)] if level >= 2 else []),
                *([aid_2014()] if level >= 3 else []),
                *([beacon_of_hope_2014()] if level >= 5 else []),
                *([death_ward_2014()] if level >= 7 else []),
            ],
            healing_actions=[
                healing_word_2014(wisdom_modifier, 3),
                cure_wounds_2014(wisdom_modifier, 3),
                *([mass_cure_wounds_2014(wisdom_modifier)] if level >= 9 else []),
                *([divine_intervention_full_heal_2014(level)] if level >= 10 else []),
            ],
            condition_removal_actions=(
                [lesser_restoration_2014()] if level >= 3 else []
            ),
            saving_throw_bonuses=saving_throw_bonuses(
                scores,
                level,
                ("wisdom", "charisma"),
            ),
            skill_bonuses={
                "insight": wisdom_modifier + pb,
                "religion": scores.modifier("intelligence") + pb,
                "medicine": wisdom_modifier + pb,
                "persuasion": scores.modifier("charisma") + pb,
            },
            weapon_masteries=[],
            damage_resistances=[DamageType.POISON],
            combat_traits=[CombatTrait.LIFE_DOMAIN],
            resources=build_cleric_resources_2014(level),
            progression_features=build_cleric_progression_2014(level),
            visual=VisualLoadout(
                armor="scale-mail",
                main_hand="warhammer",
                off_hand="shield",
                body_style="humanoid",
            ),
            source=(
                "D&D Basic Rules 2014: Hill Dwarf, Acolyte, Cleric, Life Domain, "
                "Bless, Cure Wounds, Guiding Bolt, Healing Word, Inflict Wounds, "
                "Sacred Flame, Shield of Faith, Aid, Lesser Restoration, Spiritual Weapon, "
                "Beacon of Hope, Death Ward, Guardian of Faith, Mass Cure Wounds, Divine Intervention, Equipment"
            ),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Seraphine Dawnshield at level %s.", level)
        raise
