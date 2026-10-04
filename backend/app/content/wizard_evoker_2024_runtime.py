from __future__ import annotations

import logging

from app.content.bard_2024_spells import build_greater_invisibility_2024
from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.threshold_spell_effects import build_power_word_kill_2024
from app.content.wizard_evoker_2024_bound_spells import (
    build_elian_2024_auto_hits,
    build_elian_2024_spell_attacks,
    build_elian_2024_spell_saves,
)
from app.content.wizard_evoker_2024_features import build_wizard_evoker_2024_features
from app.content.wizard_evoker_2024_profile import build_elian_starweaver_2024_profile
from app.content.wizard_evoker_2024_runtime_support import (
    build_elian_2024_dispel,
    build_elian_2024_initiative_refills,
    build_elian_2024_resources,
    build_elian_2024_weapon,
)
from app.domain.models import CombatantTemplate, VisualLoadout

logger = logging.getLogger(__name__)


def build_elian_starweaver_2024(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Elian runtime currently certifies levels 1 through 20.")
        profile = build_elian_starweaver_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        save_dc = 8 + pb + intel
        arcana = intel + (pb * 2 if level >= 2 else pb)
        return CombatantTemplate(
            id=canonical_template_id("wizard", level),
            name=HERO_BY_CLASS["wizard"].hero_name,
            archetype="Wizard",
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=10 + dex,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            movement_modes={"walk_ft": 30},
            initiative_bonus=dex,
            starts_with_heroic_inspiration=True,
            weapon_attack=build_elian_2024_weapon(level, scores),
            spell_attack_actions=build_elian_2024_spell_attacks(level, pb + intel, intel),
            auto_hit_spell_actions=build_elian_2024_auto_hits(level, intel),
            spell_save_actions=build_elian_2024_spell_saves(level, save_dc, intel),
            defensive_spell_actions=([build_greater_invisibility_2024()] if level >= 8 else []),
            effect_removal_actions=([build_elian_2024_dispel()] if level >= 9 else []),
            hp_threshold_instant_death_actions=([build_power_word_kill_2024()] if level >= 17 else []),
            progression_features=build_wizard_evoker_2024_features(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("intelligence", "wisdom")),
            skill_bonuses={
                "arcana": arcana,
                "history": intel + pb,
                "investigation": intel + pb,
                "insight": wis + pb,
                "religion": intel + pb,
                "medicine": wis + pb,
                "nature": intel + pb,
                "perception": wis + pb,
            },
            resources=build_elian_2024_resources(level),
            initiative_resource_refill_grants=build_elian_2024_initiative_refills(level),
            visual=VisualLoadout(armor="unarmored", main_hand="arcane-focus", body_style="humanoid"),
            source="D&D Beyond Basic Rules 2024: Human; Sage; Wizard; Evoker; Equipment",
        )
    except Exception:
        logger.exception("Failed to build 2024 Elian Starweaver runtime at level %s.", level)
        raise
