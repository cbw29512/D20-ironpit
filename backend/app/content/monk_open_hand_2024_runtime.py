from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import proficiency_bonus
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.monk_open_hand_2024_attacks import build_kael_unarmed_attack_2024
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def build_kael_stillwater_2024(level: int = 1) -> CombatantTemplate:
    """Build the certified 2024 Open Hand Monk foundation without 2014 Martial Arts leakage."""
    try:
        if level != 1:
            raise ValueError("The current 2024 Monk runtime tranche supports level 1 only.")
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
            max_hp=8 + constitution,
            speed_ft=30,
            initiative_bonus=dexterity + pb,
            starts_with_heroic_inspiration=True,
            progression_features=ProgressionCombatFeatures(
                martial_arts_bonus_attack=True,
                martial_arts_die_size=6,
            ),
            weapon_attack=unarmed,
            bonus_attack_grants=[
                BonusAttackGrant(
                    id="martial-arts",
                    name="Martial Arts",
                    attack_ids=[unarmed.id],
                    attack_count=1,
                    priority=90,
                ),
            ],
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
            visual=VisualLoadout(
                armor="unarmored",
                main_hand="unarmed",
                body_style="humanoid",
            ),
            source="D&D Beyond Basic Rules 2024: Monk 1, Human, Criminal, Alert, Skilled",
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael Stillwater at level %s.", level)
        raise
