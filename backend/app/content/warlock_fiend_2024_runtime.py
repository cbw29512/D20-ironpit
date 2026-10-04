from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.warlock_2024_spells import dimension_door_2024, hex_2024
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.content.warlock_fiend_2024_features import build_warlock_fiend_2024_features
from app.content.warlock_fiend_2024_profile import build_varek_ashenmark_2024_profile
from app.content.warlock_fiend_2024_arcanum import (
    build_varek_2024_arcanum_saves,
    build_varek_2024_power_word_stun,
    build_varek_2024_threshold_death,
)
from app.content.warlock_fiend_2024_runtime_support import (
    build_varek_2024_conversions,
    build_varek_2024_dispel,
    build_varek_2024_initiative_refills,
    build_varek_2024_resources,
    build_varek_2024_spell_attacks,
    build_varek_2024_spell_saves,
)
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def build_varek_ashenmark_2024(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Varek runtime currently certifies levels 1 through 20.")
        profile = build_varek_ashenmark_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        row = WARLOCK_COMBAT_LEVELS[level]
        save_dc = 8 + pb + cha
        dagger = build_weapon("dagger").model_copy(update={"mastery_property": None})
        return CombatantTemplate(
            id=canonical_template_id("warlock", level),
            name=HERO_BY_CLASS["warlock"].hero_name,
            archetype="Warlock",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=11 + dex,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            movement_modes={"walk_ft": 30},
            initiative_bonus=dex,
            starts_with_heroic_inspiration=True,
            weapon_attack=WeaponAttack(
                id="varek-2024-dagger",
                weapon=dagger,
                attack_bonus=pb + dex,
                damage_bonus=dex,
                attack_ability="dexterity",
                attack_ability_modifier=dex,
            ),
            spell_attack_actions=build_varek_2024_spell_attacks(level, pb + cha, cha),
            spell_save_actions=build_varek_2024_spell_saves(level, save_dc),
            targeted_concentration_damage_actions=[hex_2024()],
            progression_features=build_warlock_fiend_2024_features(
                level, row.pact_slot_level, pb, cha,
            ),
            saving_throw_actions=build_varek_2024_arcanum_saves(level, save_dc),
            hp_threshold_instant_death_actions=build_varek_2024_threshold_death(level),
            hp_threshold_condition_actions=(
                [build_varek_2024_power_word_stun(save_dc)] if level >= 15 else []
            ),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses={
                "arcana": intel + pb,
                "history": intel + pb,
                "insight": wis + pb,
                "religion": intel + pb,
                "deception": cha + pb,
                "persuasion": cha + pb,
                "investigation": intel + pb,
                "intimidation": cha + pb,
            },
            resources=build_varek_2024_resources(level, row.pact_slots, row.pact_slot_level, cha),
            resource_conversion_actions=build_varek_2024_conversions(level, row.pact_slot_level),
            teleport_actions=([dimension_door_2024(row.pact_slot_level)] if level >= 8 else []),
            effect_removal_actions=([build_varek_2024_dispel(row.pact_slot_level)] if level >= 6 else []),
            initiative_resource_refill_grants=build_varek_2024_initiative_refills(level),
            visual=VisualLoadout(armor="leather-armor", main_hand="arcane-focus", body_style="humanoid"),
            source="D&D Beyond Basic Rules 2024: Human; Acolyte; Warlock; Fiend Patron; Equipment",
        )
    except Exception:
        logger.exception("Failed to build 2024 Varek Ashenmark runtime at level %s.", level)
        raise
