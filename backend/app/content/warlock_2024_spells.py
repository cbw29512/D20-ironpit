from __future__ import annotations

import logging

from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellAttackAction, SpellSaveAction
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction
from app.domain.teleport_actions import TeleportAction

logger = logging.getLogger(__name__)


def eldritch_blast_2024(
    attack_bonus: int,
    level: int,
    damage_bonus: int = 0,
    range_ft: int = 120,
) -> SpellAttackAction:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Eldritch Blast character level must be between 1 and 20.")
        if range_ft < 1:
            raise ValueError("Eldritch Blast range must be positive.")
        return SpellAttackAction(
            id="eldritch-blast",
            name="Eldritch Blast",
            level=0,
            action_cost="action",
            attack_kind="ranged",
            range_ft=range_ft,
            attack_bonus=attack_bonus,
            damage_dice_count=1,
            damage_dice_size=10,
            damage_bonus=damage_bonus,
            damage_type="force",
            attack_count=1 + int(level >= 5) + int(level >= 11) + int(level >= 17),
            animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Eldritch Blast",
        )
    except Exception:
        logger.exception("Failed to build 2024 Eldritch Blast at level %s.", level)
        raise


def scorching_ray_2024(attack_bonus: int) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="scorching-ray",
            name="Scorching Ray",
            level=2,
            action_cost="action",
            attack_kind="ranged",
            range_ft=120,
            attack_bonus=attack_bonus,
            damage_dice_count=2,
            damage_dice_size=6,
            damage_type="fire",
            attack_count=3,
            attacks_per_slot_above=1,
            animation="spell-attack",
            source="D&D Beyond Basic Rules 2024: Scorching Ray",
        )
    except Exception:
        logger.exception("Failed to build 2024 Scorching Ray.")
        raise


def hex_2024() -> TargetedConcentrationDamageAction:
    try:
        return TargetedConcentrationDamageAction(
            id="hex",
            name="Hex",
            level=1,
            action_cost="bonus_action",
            range_ft=90,
            dice_count=1,
            dice_size=6,
            damage_type="necrotic",
            duration_rounds_by_slot={1: 600, 2: 2400, 3: 4800, 4: 4800, 5: 14400},
            retarget_after_target_zero=True,
            priority=10,
            animation="targeted-concentration",
            source="D&D Beyond Basic Rules 2024: Hex",
        )
    except Exception:
        logger.exception("Failed to build 2024 Hex.")
        raise


def charm_person_2024(save_dc: int) -> SpellSaveAction:
    try:
        return SpellSaveAction(
            id="charm-person",
            name="Charm Person",
            level=1,
            action_cost="action",
            range_ft=30,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            required_target_creature_types=["humanoid"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed",
                duration_rounds=600,
                expiry_timing="source_turn_end",
                ends_on_damage=True,
            ),
            concentration=False,
            allows_higher_slots=True,
            target_count=1,
            target_count_per_slot_above=1,
            save_advantage_if_fighting=True,
            animation="spell-save",
            source="D&D Beyond Basic Rules 2024: Charm Person",
        )
    except Exception:
        logger.exception("Failed to build 2024 Charm Person.")
        raise


def dimension_door_2024(pact_slot_level: int) -> TeleportAction:
    try:
        return TeleportAction(
            id="dimension-door",
            name="Dimension Door",
            level=4,
            action_cost="action",
            range_ft=500,
            passenger_count=1,
            passenger_range_ft=5,
            resource_id=f"spell-slot-{pact_slot_level}",
            expends_spell_slot=True,
            animation="dimension-door",
            source="D&D Beyond Basic Rules 2024: Dimension Door",
        )
    except Exception:
        logger.exception("Failed to build 2024 Dimension Door for pact slot %s.", pact_slot_level)
        raise
