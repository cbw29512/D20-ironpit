from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.hero_combat_feature_registry import compile_progression_feature_fields
from app.content.equipment import build_longsword
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.friendly_condition_auras import FriendlyConditionImmunityAuraGrant
from app.domain.friendly_save_auras import FriendlySavingThrowAuraGrant
from app.domain.models import DamageType, OnHitDamage, WeaponAttack
from app.domain.post_hit_damage import ResourceBackedPostHitDamage
from app.domain.timed_self_buffs import TimedEmanationDamage, TimedFriendlyCoverAura, TimedSelfBuffAction
from app.domain.environment_context import TimedEnvironmentContextAura
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
# Printed weapon categories for the audited canonical loadout, independent of delivery.
_MELEE_WEAPON_IDS = ("longsword", "javelin")


def build_paladin_2024_attack(
    weapon_id: str,
    strength_modifier: int,
    level: int,
) -> WeaponAttack:
    try:
        weapon = build_longsword() if weapon_id == "longsword" else build_weapon(weapon_id)
        attack = WeaponAttack(
            id=f"aurelia-{weapon_id}",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + strength_modifier,
            damage_bonus=strength_modifier,
            attack_ability="strength",
            attack_ability_modifier=strength_modifier,
        )
        if level >= 11 and weapon_id in _MELEE_WEAPON_IDS:
            attack = attack.model_copy(update={
                "on_hit_damage": [
                    OnHitDamage(
                        source="Radiant Strikes",
                        dice_count=1,
                        dice_size=8,
                        damage_type=DamageType.RADIANT,
                    )
                ],
            })
        return attack
    except Exception:
        logger.exception(
            "Failed to build 2024 Paladin attack %s at level %s.",
            weapon_id,
            level,
        )
        raise


def build_paladin_2024_attack_action(level: int) -> AttackActionDefinition | None:
    try:
        if level < 5:
            return None
        choices = ["aurelia-longsword", "aurelia-javelin"]
        return AttackActionDefinition(
            id="extra-attack",
            name="Extra Attack",
            slots=[
                AttackActionSlot(attack_ids=choices),
                AttackActionSlot(attack_ids=choices),
            ],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to build 2024 Paladin Attack action at level %s.", level)
        raise


def build_paladin_2024_timed_self_buffs(
    level: int,
    charisma_modifier: int,
) -> list[TimedSelfBuffAction]:
    """Build source-centered timed Devotion aura benefits."""
    try:
        actions: list[TimedSelfBuffAction] = []
        if level >= 15:
            actions.append(TimedSelfBuffAction(
                id="smite-of-protection-2024",
                name="Smite of Protection",
                action_cost="bonus_action",
                duration_rounds=1,
                friendly_cover_aura=TimedFriendlyCoverAura(
                    radius_ft=30 if level >= 18 else 10,
                    cover_bonus=2,
                ),
                expiry_timing="source_turn_start",
            ))
        if level >= 20:
            actions.append(TimedSelfBuffAction(
                id="holy-nimbus-2024",
                name="Holy Nimbus",
                action_cost="bonus_action",
                resource_id="holy-nimbus",
                resource_cost=1,
                duration_rounds=100,
                saving_throw_advantage_grants=[
                    SavingThrowAdvantageGrant(
                        source_id="holy-nimbus-2024",
                        source_name="Holy Nimbus",
                        abilities=[
                            "strength", "dexterity", "constitution",
                            "intelligence", "wisdom", "charisma",
                        ],
                        source_creature_types=["fiend", "undead"],
                    ),
                ],
                environment_context_aura=TimedEnvironmentContextAura(
                    radius_ft=30,
                    context_tags=["sunlight"],
                ),
                start_turn_emanation_damage=TimedEmanationDamage(
                    trigger="enemy_turn_start",
                    radius_ft=30,
                    fixed_damage=charisma_modifier + proficiency_bonus(level),
                    damage_type=DamageType.RADIANT,
                ),
                inactive_while_source_incapacitated=True,
                expiry_timing="source_turn_start",
                priority=130,
                animation="holy-nimbus",
            ))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Paladin timed self buffs at level %s.", level)
        raise


def build_paladin_2024_progression(
    level: int,
    charisma_modifier: int,
) -> ProgressionCombatFeatures:
    try:
        aura_radius = 30 if level >= 18 else 10
        boon_fields = compile_progression_feature_fields(
            ["boon-combat-prowess"] if level >= 19 else [], level
        )
        return ProgressionCombatFeatures(
            friendly_saving_throw_aura=(
                FriendlySavingThrowAuraGrant(
                    source_id="aura-of-protection-2024",
                    source_name="Aura of Protection",
                    radius_ft=aura_radius,
                    flat_bonus=max(1, charisma_modifier),
                    inactive_while_incapacitated=True,
                )
                if level >= 6
                else None
            ),
            friendly_condition_immunity_auras=[
                *(
                    [FriendlyConditionImmunityAuraGrant(
                        source_id="aura-of-devotion-2024",
                        source_name="Aura of Devotion",
                        radius_ft=aura_radius,
                        condition_id="charmed",
                        inactive_while_incapacitated=True,
                    )]
                    if level >= 7 else []
                ),
                *(
                    [FriendlyConditionImmunityAuraGrant(
                        source_id="aura-of-courage-2024",
                        source_name="Aura of Courage",
                        radius_ft=aura_radius,
                        condition_id="frightened",
                        inactive_while_incapacitated=True,
                    )]
                    if level >= 10 else []
                ),
            ],
            **boon_fields,
            resource_backed_post_hit_damage=(
                ResourceBackedPostHitDamage(
                    source_id="divine-smite-2024",
                    source_name="Divine Smite",
                    trigger_attack_ids=[f"aurelia-{weapon_id}" for weapon_id in _MELEE_WEAPON_IDS],
                    action_cost="bonus_action",
                    free_resource_id="paladins-smite-free-cast",
                    post_hit_self_buff_action_id=(
                        "smite-of-protection-2024" if level >= 15 else None
                    ),
                    printed_spell_level=1,
                    max_slot_level=5,
                    base_dice_count=2,
                    dice_per_slot_above=1,
                    dice_size=8,
                    damage_type="radiant",
                    bonus_target_creature_types=["fiend", "undead"],
                    bonus_target_dice_count=1,
                    doubles_on_critical=True,
                )
                if level >= 2
                else None
            ),
        )
    except Exception:
        logger.exception(
            "Failed to build 2024 Paladin progression features at level %s.",
            level,
        )
        raise


def build_paladin_2024_resource_conversions(level: int) -> list[ResourceConversionAction]:
    """Build no-action printed Paladin resource exchanges."""
    try:
        if level < 20:
            return []
        return [ResourceConversionAction(
            id="restore-holy-nimbus-2024",
            name="Holy Nimbus (Restore Use)",
            action_cost="none",
            source_resource_id="spell-slot-5",
            source_cost=1,
            target_resource_id="holy-nimbus",
            target_gain=1,
            requires_target_empty=True,
            priority=120,
            source="D&D Beyond Basic Rules 2024: Oath of Devotion 20 — Holy Nimbus",
        )]
    except Exception:
        logger.exception("Failed to build 2024 Paladin resource conversions at level %s.", level)
        raise
