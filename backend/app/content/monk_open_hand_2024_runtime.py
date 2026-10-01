from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import proficiency_bonus
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.monk_open_hand_2024_attacks import build_kael_unarmed_attack_2024
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_2024_resource_rules import monk_focus_points
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.initiative_resources import InitiativeHealingRider, InitiativeResourceRefillGrant
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout
from app.domain.tactical_actions import BonusActionTacticalGrant
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def build_kael_stillwater_2024(level: int = 1) -> CombatantTemplate:
    """Build the certified 2024 Open Hand Monk foundation without 2014 Martial Arts leakage."""
    try:
        if level not in {1, 2}:
            raise ValueError("The current 2024 Monk runtime tranche supports levels 1-2 only.")
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
                martial_arts_die_size=6,
            ),
            weapon_attack=unarmed,
            bonus_attack_grants=[
                *(
                    [
                        BonusAttackGrant(
                            id="flurry-of-blows",
                            name="Flurry of Blows",
                            attack_ids=[unarmed.id],
                            attack_count=2,
                            resource_id="focus-points",
                            resource_cost=1,
                            priority=80,
                        ),
                    ]
                    if level >= 2 else []
                ),
                BonusAttackGrant(
                    id="martial-arts",
                    name="Martial Arts",
                    attack_ids=[unarmed.id],
                    attack_count=1,
                    priority=90,
                ),
            ],
            bonus_tactical_action_grants=(
                [
                    BonusActionTacticalGrant(
                        id="step-of-the-wind-dash",
                        name="Step of the Wind",
                        effects=["dash"],
                        priority=40,
                        use_policy="enable-offense",
                    ),
                    BonusActionTacticalGrant(
                        id="patient-defense-disengage",
                        name="Patient Defense",
                        effects=["disengage"],
                        priority=100,
                        use_policy="manual",
                    ),
                    BonusActionTacticalGrant(
                        id="patient-defense-focus",
                        name="Patient Defense",
                        effects=["disengage", "dodge"],
                        resource_id="focus-points",
                        resource_cost=1,
                        priority=90,
                        use_policy="defensive-fallback",
                    ),
                    BonusActionTacticalGrant(
                        id="step-of-the-wind-focus",
                        name="Step of the Wind",
                        effects=["disengage", "dash"],
                        resource_id="focus-points",
                        resource_cost=1,
                        priority=100,
                        use_policy="manual",
                        jump_distance_multiplier=2,
                    ),
                ]
                if level >= 2 else []
            ),
            resources=(
                [
                    ResourceDefinition(id="focus-points", name="Focus Points", max_uses=monk_focus_points(level)),
                    ResourceDefinition(id="uncanny-metabolism", name="Uncanny Metabolism", max_uses=1),
                ]
                if level >= 2 else []
            ),
            initiative_resource_refill_grants=(
                [
                    InitiativeResourceRefillGrant(
                        source_id="uncanny-metabolism",
                        source_name="Uncanny Metabolism",
                        resource_id="focus-points",
                        when_at_or_below=monk_focus_points(level) - 1,
                        restore_to_max=True,
                        usage_resource_id="uncanny-metabolism",
                        usage_resource_cost=1,
                        healing_rider=InitiativeHealingRider(
                            dice_count=1,
                            dice_size=6,
                            healing_bonus=level,
                        ),
                    ),
                ]
                if level >= 2 else []
            ),
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
            source=f"D&D Beyond Basic Rules 2024: Monk {level}, Human, Criminal, Alert, Skilled",
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael Stillwater at level %s.", level)
        raise
