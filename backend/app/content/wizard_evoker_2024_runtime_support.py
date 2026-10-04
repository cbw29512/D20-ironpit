from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.weapon_catalog import build_weapon
from app.content.wizard_combat_levels import WIZARD_COMBAT_LEVELS
from app.domain.effect_removal import EffectRemovalAction
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.models import ResourceDefinition, WeaponAttack

logger = logging.getLogger(__name__)


def build_elian_2024_weapon(level: int, scores) -> WeaponAttack:
    try:
        weapon = build_weapon("dagger").model_copy(update={"mastery_property": None})
        dexterity = scores.modifier("dexterity")
        return WeaponAttack(
            id="elian-2024-dagger",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Elian's 2024 dagger at level %s.", level)
        raise


def build_elian_2024_resources(level: int):
    try:
        row = WIZARD_COMBAT_LEVELS[level]
        resources = [
            ResourceDefinition(id=f"spell-slot-{spell_level}", name=f"Spell Slot {spell_level}", max_uses=uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if level >= 19:
            resources.append(ResourceDefinition(id="boon-of-fate", name="Boon of Fate", max_uses=1))
        if level >= 20:
            resources.extend([
                ResourceDefinition(id="signature-spell-fireball", name="Signature Spells: Fireball", max_uses=1),
                ResourceDefinition(
                    id="signature-spell-lightning-bolt",
                    name="Signature Spells: Lightning Bolt",
                    max_uses=1,
                ),
            ])
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Elian resources at level %s.", level)
        raise


def build_elian_2024_dispel() -> EffectRemovalAction:
    try:
        return EffectRemovalAction(
            id="dispel-magic",
            name="Dispel Magic",
            level=3,
            action_cost="action",
            range_ft=120,
            casting_ability="intelligence",
            target_mode="enemy",
            auto_remove_max_level=3,
            resource_id="spell-slot-3",
            resource_cost=1,
            expends_spell_slot=True,
            animation="dispel-magic",
        )
    except Exception:
        logger.exception("Failed to build 2024 Wizard Dispel Magic.")
        raise


def build_elian_2024_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
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
        logger.exception("Failed to build 2024 Elian initiative refills at level %s.", level)
        raise
