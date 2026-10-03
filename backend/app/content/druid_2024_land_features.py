from __future__ import annotations

import logging

from app.domain.persistent_beneficial_zones import PersistentBeneficialZoneAction

logger = logging.getLogger(__name__)


def build_natures_sanctuary_2024() -> PersistentBeneficialZoneAction:
    """Compile 2024 Arid Nature's Sanctuary onto the universal beneficial-zone primitive."""
    try:
        return PersistentBeneficialZoneAction(
            id="natures-sanctuary",
            name="Nature's Sanctuary",
            action_cost="action",
            resource_id="wild-shape",
            resource_cost=1,
            cast_range_ft=120,
            duration_rounds=10,
            shape="cube",
            length_ft=15,
            move_action_cost="bonus_action",
            move_distance_ft=60,
            move_range_ft=120,
            cover_bonus=2,
            saving_throw_abilities=["dexterity"],
            ally_damage_resistances=["fire"],
            include_source_for_defense=True,
            end_if_source_incapacitated=True,
            end_if_source_dead=True,
            animation="natures-sanctuary",
            source="D&D Beyond Basic Rules 2024: Circle of the Land — Nature's Sanctuary (Arid)",
        )
    except Exception:
        logger.exception("Failed to build 2024 Nature's Sanctuary.")
        raise
