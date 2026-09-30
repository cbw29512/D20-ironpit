from __future__ import annotations

import logging

from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def build_wild_resurgence_2024(
    spell_slots: tuple[int, ...],
) -> list[ResourceConversionAction]:
    """Build both RAW Wild Resurgence exchanges from universal resource conversions."""
    try:
        actions: list[ResourceConversionAction] = []
        for spell_level, uses in enumerate(spell_slots, start=1):
            if not uses:
                continue
            actions.append(ResourceConversionAction(
                id=f"wild-resurgence-regain-wild-shape-slot-{spell_level}",
                name=f"Wild Resurgence (Spend Level {spell_level} Slot)",
                action_cost="none",
                source_resource_id=f"spell-slot-{spell_level}",
                source_cost=1,
                target_resource_id="wild-shape",
                target_gain=1,
                requires_target_empty=True,
                once_per_turn=True,
                once_per_turn_group="wild-resurgence-regain-wild-shape",
                priority=100 - spell_level,
                source="D&D Beyond Basic Rules 2024: Druid 5 — Wild Resurgence",
            ))
        actions.append(ResourceConversionAction(
            id="wild-resurgence-regain-level-1-slot",
            name="Wild Resurgence (Regain Level 1 Slot)",
            action_cost="none",
            source_resource_id="wild-shape",
            source_cost=1,
            additional_source_costs={"wild-resurgence-slot-restore": 1},
            target_resource_id="spell-slot-1",
            target_gain=1,
            target_allows_overflow=False,
            priority=80,
            source="D&D Beyond Basic Rules 2024: Druid 5 — Wild Resurgence",
        ))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Wild Resurgence.")
        raise
