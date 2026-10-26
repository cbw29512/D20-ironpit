from __future__ import annotations

import logging

from app.content.shared_zone_spells_2014 import wall_of_fire_2014

logger = logging.getLogger(__name__)


def test_wall_of_fire_2014_declares_exact_ring_zone_windows() -> None:
    try:
        spell = wall_of_fire_2014(21)

        assert spell.id == "wall-of-fire"
        assert spell.level == 4
        assert spell.action_cost == "action"
        assert spell.cast_range_ft == 120
        assert spell.radius_ft == 10
        assert spell.duration_rounds == 10
        assert spell.concentration is True
        assert spell.save_ability == "dexterity"
        assert spell.dc == 21
        assert spell.triggers == ["appear", "enter", "end_turn"]
        assert spell.save_triggers == ["appear"]
        assert spell.once_per_turn is True
        assert spell.damage_dice_count == 5
        assert spell.damage_dice_size == 8
        assert spell.damage_type == "fire"
        assert spell.success_damage == "half"
        assert spell.upcast_dice_per_level == 1
    except Exception:
        logger.exception("2014 Wall of Fire declaration regression failed.")
        raise


def test_wall_of_fire_2014_builder_is_dc_parameterized_and_resource_neutral() -> None:
    try:
        low = wall_of_fire_2014(12)
        high = wall_of_fire_2014(21)

        assert low.dc == 12
        assert high.dc == 21
        assert low.resource_id is None
        assert high.resource_id is None
        assert low.expends_spell_slot is False
        assert high.expends_spell_slot is False
        assert low.target_policy == high.target_policy == "enemies"
        assert low.save_context == high.save_context == "spell"
    except Exception:
        logger.exception("2014 Wall of Fire parameterization regression failed.")
        raise
