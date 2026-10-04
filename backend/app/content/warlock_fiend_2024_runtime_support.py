from __future__ import annotations

import logging

from app.content.druid_2024_land_spells import build_blight_2024, build_burning_hands_2024
from app.content.druid_2024_spells import build_poison_spray_2024
from app.content.offensive_spell_effects import build_fireball_2024
from app.content.warlock_2024_control_spells import (
    command_2024,
    geas_2024,
    hold_person_2024,
    suggestion_2024,
)
from app.content.warlock_2024_spells import (
    charm_person_2024,
    eldritch_blast_2024,
    scorching_ray_2024,
)
from app.domain.effect_removal import EffectRemovalAction
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.models import ResourceDefinition
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def warlock_2024_eldritch_range(level: int) -> int:
    return 120 + (30 * level if level >= 2 else 0)


def build_varek_2024_spell_attacks(level: int, attack_bonus: int, damage_bonus: int):
    try:
        attacks = [
            eldritch_blast_2024(
                attack_bonus, level,
                damage_bonus=damage_bonus if level >= 2 else 0,
                range_ft=warlock_2024_eldritch_range(level),
            ),
        ]
        if level >= 3:
            attacks.append(scorching_ray_2024(attack_bonus))
        if level >= 10:
            attacks.append(build_poison_spray_2024(attack_bonus, level))
        return attacks
    except Exception:
        logger.exception("Failed to build 2024 Varek spell attacks at level %s.", level)
        raise


def build_varek_2024_spell_saves(level: int, save_dc: int):
    try:
        actions = [charm_person_2024(save_dc)]
        if level >= 3:
            actions.extend([
                build_burning_hands_2024(save_dc),
                command_2024(save_dc),
                suggestion_2024(save_dc),
            ])
        if level >= 5:
            actions.extend([build_fireball_2024(save_dc), hold_person_2024(save_dc)])
        if level >= 7:
            actions.append(build_blight_2024(save_dc))
        if level >= 9:
            actions.append(geas_2024(save_dc))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Varek spell saves at level %s.", level)
        raise


def build_varek_2024_dispel(pact_slot_level: int) -> EffectRemovalAction:
    try:
        return EffectRemovalAction(
            id="dispel-magic",
            name="Dispel Magic",
            level=3,
            action_cost="action",
            range_ft=120,
            casting_ability="charisma",
            target_mode="enemy",
            auto_remove_max_level=3,
            resource_id=f"spell-slot-{pact_slot_level}",
            resource_cost=1,
            expends_spell_slot=True,
            animation="dispel-magic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Warlock Dispel Magic.")
        raise


def build_varek_2024_resources(level: int, pact_slots: int, pact_slot_level: int, charisma_modifier: int):
    try:
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{pact_slot_level}",
                name=f"Pact Magic Slot {pact_slot_level}",
                max_uses=pact_slots,
            ),
        ]
        if level >= 2:
            resources.append(ResourceDefinition(id="magical-cunning", name="Magical Cunning", max_uses=1))
        if level >= 6:
            resources.append(ResourceDefinition(
                id="dark-ones-own-luck",
                name="Dark One's Own Luck",
                max_uses=max(1, charisma_modifier),
            ))
        for arcanum_level, unlock in ((6, 11), (7, 13), (8, 15), (9, 17)):
            if level >= unlock:
                resources.append(ResourceDefinition(
                    id=f"mystic-arcanum-{arcanum_level}",
                    name=f"Mystic Arcanum ({arcanum_level}th Level)",
                    max_uses=1,
                ))
        if level >= 14:
            resources.append(ResourceDefinition(id="hurl-through-hell", name="Hurl Through Hell", max_uses=1))
        if level >= 19:
            resources.append(ResourceDefinition(id="boon-of-fate", name="Boon of Fate", max_uses=1))
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Varek resources at level %s.", level)
        raise


def build_varek_2024_conversions(level: int, pact_slot_level: int) -> list[ResourceConversionAction]:
    try:
        if level < 14:
            return []
        return [ResourceConversionAction(
            id="hurl-through-hell-restore",
            name="Hurl Through Hell",
            action_cost="none",
            source_resource_id=f"spell-slot-{pact_slot_level}",
            source_cost=1,
            target_resource_id="hurl-through-hell",
            target_gain=1,
            requires_target_empty=True,
            automation="when-target-empty",
            source="D&D Beyond Basic Rules 2024: Hurl Through Hell",
        )]
    except Exception:
        logger.exception("Failed to build 2024 Hurl Through Hell conversion at level %s.", level)
        raise


def build_varek_2024_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    try:
        if level < 19:
            return []
        return [InitiativeResourceRefillGrant(
            source_id="boon-of-fate",
            source_name="Boon of Fate",
            resource_id="boon-of-fate",
            when_at_or_below=0,
            restore_to_max=True,
        )]
    except Exception:
        logger.exception("Failed to build 2024 Varek initiative refills at level %s.", level)
        raise
