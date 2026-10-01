from __future__ import annotations

import logging

from app.domain.combatants import ResourceDefinition
from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)

# Source-audited 2024 Druid combat spells whose Material components, if any,
# have no specified cost and are not consumed. Beast Spells may retain these.
BEAST_SPELL_ACTION_IDS = [
    "poison-spray", "fire-bolt", "starry-wisp",
    "faerie-fire", "burning-hands", "fireball", "blight", "cone-of-cold",
    "thunderclap", "thunderwave", "sunburst",
    "longstrider", "blur", "aid", "freedom-of-movement", "foresight", "barkskin",
    "healing-word", "cure-wounds", "mass-cure-wounds", "heal",
    "lesser-restoration", "dispel-magic", "wall-of-stone",
]


def druid_endgame_resources(level: int) -> list[ResourceDefinition]:
    try:
        resources: list[ResourceDefinition] = []
        if level >= 19:
            resources.append(ResourceDefinition(id="boon-of-fate", name="Boon of Fate", max_uses=1))
        if level >= 20:
            resources.append(ResourceDefinition(
                id="nature-magician-conversion",
                name="Nature Magician",
                max_uses=1,
            ))
        return resources
    except Exception:
        logger.exception("Failed to build 2024 Druid endgame resources at level %s.", level)
        raise


def druid_boon_of_fate(level: int) -> list[ResourceBackedD20OutcomeAdjustment]:
    try:
        if level < 19:
            return []
        return [ResourceBackedD20OutcomeAdjustment(
            source_id="boon-of-fate",
            source_name="Boon of Fate",
            resource_id="boon-of-fate",
            dice_count=2,
            dice_size=4,
            range_ft=60,
            test_kinds=["attack", "saving_throw", "ability_check"],
            can_add=True,
            can_subtract=True,
        )]
    except Exception:
        logger.exception("Failed to build 2024 Druid Boon of Fate at level %s.", level)
        raise


def druid_endgame_initiative_refills(level: int) -> list[InitiativeResourceRefillGrant]:
    try:
        grants: list[InitiativeResourceRefillGrant] = []
        if level >= 19:
            grants.append(InitiativeResourceRefillGrant(
                source_id="boon-of-fate",
                source_name="Boon of Fate",
                resource_id="boon-of-fate",
                when_at_or_below=0,
                restore_to_max=True,
            ))
        if level >= 20:
            grants.append(InitiativeResourceRefillGrant(
                source_id="evergreen-wild-shape",
                source_name="Evergreen Wild Shape",
                resource_id="wild-shape",
                when_at_or_below=0,
                restore_amount=1,
            ))
        return grants
    except Exception:
        logger.exception("Failed to build 2024 Druid initiative refills at level %s.", level)
        raise


def nature_magician_conversions(level: int) -> list[ResourceConversionAction]:
    """Expose all legal Wild Shape -> even-level spell-slot exchanges at Druid 20."""
    try:
        if level < 20:
            return []
        return [
            ResourceConversionAction(
                id=f"nature-magician-level-{slot_level}",
                name=f"Nature Magician (Create Level {slot_level} Slot)",
                action_cost="none",
                source_resource_id="wild-shape",
                source_cost=slot_level // 2,
                additional_source_costs={"nature-magician-conversion": 1},
                target_resource_id=f"spell-slot-{slot_level}",
                target_gain=1,
                target_allows_overflow=True,
                automation="when-target-empty",
                priority=100 + slot_level,
                source="D&D Beyond Basic Rules 2024: Druid 20 — Archdruid, Nature Magician",
            )
            for slot_level in (2, 4, 6, 8)
        ]
    except Exception:
        logger.exception("Failed to build 2024 Nature Magician conversions at level %s.", level)
        raise
