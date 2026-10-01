from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import proficiency_bonus
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.level_resources import orc_adrenaline_rush_uses
from app.content.monk_open_hand_2024_attacks import build_kael_unarmed_attack_2024
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout
from app.domain.progression import ProgressionCombatFeatures
from app.domain.traits import CombatTrait

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
                "intelligence": scores.modifier("intelligence"),
                "wisdom": wisdom,
                "charisma": scores.modifier("charisma"),
            },
            skill_bonuses={
                "acrobatics": dexterity + pb,
                "insight": wisdom + pb,
                "sleight-of-hand": dexterity + pb,
                "stealth": dexterity + pb,
            },
            combat_traits=[CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
            visual=VisualLoadout(
                armor="unarmored",
                main_hand="unarmed",
                body_style="humanoid",
            ),
            resources=[
                ResourceDefinition(
                    id="adrenaline-rush",
                    name="Adrenaline Rush",
                    max_uses=orc_adrenaline_rush_uses(level),
                ),
                ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
            ],
            source="D&D Beyond Basic Rules 2024: Monk 1, Orc, Criminal, Alert",
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael Stillwater at level %s.", level)
        raise
