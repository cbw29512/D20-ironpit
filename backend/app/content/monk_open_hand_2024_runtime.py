from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import proficiency_bonus
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.monk_open_hand_2024_actions import (
    build_monk_attack_damage_reduction,
    build_monk_bonus_attacks,
    build_monk_tactical_actions,
)
from app.content.monk_open_hand_2024_attacks import build_kael_extra_attack_2024, build_kael_unarmed_attack_2024
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_resources import build_monk_initiative_refills, build_monk_resources
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import ResourceBackedOnHitSaveRider

logger = logging.getLogger(__name__)


def build_kael_stillwater_2024(level: int = 1) -> CombatantTemplate:
    """Build the certified persistent 2024 Open Hand Monk using shared combat primitives."""
    try:
        if level not in {1, 2, 3, 4, 5}:
            raise ValueError("The current 2024 Monk runtime tranche supports levels 1-5 only.")
        profile = build_kael_stillwater_2024_profile(level)
        scores = profile.final_ability_scores
        if scores is None:
            raise ValueError("2024 Kael profile is missing final ability scores.")
        hero = HERO_BY_CLASS["monk"]
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        constitution = scores.modifier("constitution")
        strength = scores.modifier("strength")
        intelligence = scores.modifier("intelligence")
        unarmed = build_kael_unarmed_attack_2024(level, scores)
        return CombatantTemplate(
            id=canonical_template_id("monk", level),
            name=hero.hero_name,
            archetype=hero.class_name,
            level=level,
            kind="character",
            ruleset="2024",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=10 + dexterity + wisdom,
            max_hp=(8 + constitution) + (5 + constitution) * (level - 1),
            speed_ft=30 + (10 if level >= 2 else 0),
            initiative_bonus=dexterity + pb,
            starts_with_heroic_inspiration=True,
            progression_features=ProgressionCombatFeatures(
                martial_arts_bonus_attack=True,
                martial_arts_die_size=8 if level >= 5 else 6,
                resource_backed_on_hit_save_rider=(
                    ResourceBackedOnHitSaveRider(
                        source_id="stunning-strike",
                        source_name="Stunning Strike",
                        trigger_attack_ids=[unarmed.id],
                        resource_id="focus-points",
                        resource_cost=1,
                        save_ability="constitution",
                        save_dc=8 + pb + wisdom,
                        once_per_turn=True,
                        failed_condition_id="stunned",
                        failed_condition_expiry_timing="source_turn_start",
                        successful_save_speed_multiplier=0.5,
                        successful_save_next_attack_advantage=True,
                    )
                    if level >= 5 else None
                ),
            ),
            weapon_attack=unarmed,
            attack_action=build_kael_extra_attack_2024(level, unarmed.id),
            bonus_attack_grants=build_monk_bonus_attacks(level, unarmed, pb, wisdom),
            bonus_tactical_action_grants=build_monk_tactical_actions(level),
            attack_damage_reduction_reaction=build_monk_attack_damage_reduction(level),
            resources=build_monk_resources(level),
            initiative_resource_refill_grants=build_monk_initiative_refills(level),
            saving_throw_bonuses={
                "strength": strength + pb,
                "dexterity": dexterity + pb,
                "constitution": constitution,
                "intelligence": intelligence,
                "wisdom": wisdom,
                "charisma": scores.modifier("charisma"),
            },
            skill_bonuses={
                "athletics": strength,
                "acrobatics": dexterity + pb,
                "history": intelligence + pb,
                "insight": wisdom + pb,
                "nature": intelligence + pb,
                "perception": wisdom + pb,
                "religion": intelligence + pb,
                "sleight-of-hand": dexterity + pb,
                "stealth": dexterity + pb,
            },
            visual=VisualLoadout(armor="unarmored", main_hand="unarmed", body_style="humanoid"),
            source=f"D&D Beyond Basic Rules 2024: Monk {level}, Human, Criminal, Alert, Skilled",
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael Stillwater at level %s.", level)
        raise
