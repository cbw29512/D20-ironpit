from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import proficiency_bonus, saving_throw_bonuses
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.sorcerer_draconic_2024_features import build_sorcerer_2024_features
from app.content.sorcerer_draconic_2024_math import nyra_2024_armor_class, nyra_2024_hit_points
from app.content.sorcerer_draconic_2024_profile import build_nyra_emberveil_2024_profile
from app.content.sorcerer_draconic_2024_runtime_support import (
    build_nyra_2024_auto_hits,
    build_nyra_2024_conversions,
    build_nyra_2024_defenses,
    build_nyra_2024_dispel,
    build_nyra_2024_distant,
    build_nyra_2024_heightened,
    build_nyra_2024_initiative_refills,
    build_nyra_2024_resources,
    build_nyra_2024_self_buffs,
    build_nyra_2024_spell_attacks,
    build_nyra_2024_spell_saves,
    nyra_2024_resistances,
)
from app.content.weapon_catalog import build_weapon
from app.domain.models import CombatantTemplate, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def build_nyra_emberveil_2024(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Nyra runtime currently certifies levels 1 through 20.")
        profile = build_nyra_emberveil_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        save_dc = 8 + pb + cha
        dagger = build_weapon("dagger").model_copy(update={"mastery_property": None})
        return CombatantTemplate(
            id=canonical_template_id("sorcerer", level),
            name=HERO_BY_CLASS["sorcerer"].hero_name,
            archetype="Sorcerer",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=nyra_2024_armor_class(level, dex, cha),
            max_hp=nyra_2024_hit_points(level, scores.modifier("constitution")),
            speed_ft=30,
            movement_modes={"walk_ft": 30, "fly_ft": 0},
            initiative_bonus=dex,
            starts_with_heroic_inspiration=True,
            weapon_attack=WeaponAttack(
                id="nyra-2024-dagger",
                weapon=dagger,
                attack_bonus=pb + dex,
                damage_bonus=dex,
                attack_ability="dexterity",
                attack_ability_modifier=dex,
            ),
            spell_attack_actions=build_nyra_2024_spell_attacks(level, pb + cha, cha),
            auto_hit_spell_actions=build_nyra_2024_auto_hits(),
            spell_save_actions=build_nyra_2024_spell_saves(level, save_dc, cha),
            defensive_spell_actions=build_nyra_2024_defenses(level),
            effect_removal_actions=([build_nyra_2024_dispel()] if level >= 9 else []),
            resource_conversion_actions=build_nyra_2024_conversions(level),
            spell_save_disadvantage_options=build_nyra_2024_heightened(level),
            spell_range_modifiers=build_nyra_2024_distant(level),
            timed_self_buff_actions=build_nyra_2024_self_buffs(level),
            progression_features=build_sorcerer_2024_features(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("constitution", "charisma")),
            skill_bonuses={
                "arcana": intel + pb,
                "persuasion": cha + pb,
                "insight": wis + pb,
                "religion": intel + pb,
                "deception": cha + pb,
                "intimidation": cha + pb,
                "investigation": intel + pb,
                "history": intel + pb,
            },
            damage_resistances=nyra_2024_resistances(level),
            resources=build_nyra_2024_resources(level),
            initiative_resource_refill_grants=build_nyra_2024_initiative_refills(level),
            visual=VisualLoadout(armor="unarmored", main_hand="arcane-focus", body_style="humanoid"),
            source="D&D Beyond Basic Rules 2024: Human; Acolyte; Sorcerer; Draconic Sorcery; Equipment",
        )
    except Exception:
        logger.exception("Failed to build 2024 Nyra Emberveil runtime at level %s.", level)
        raise
