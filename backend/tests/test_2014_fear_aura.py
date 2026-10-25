from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_condition_aura_source_corrections_2014 import (
    corrected_condition_aura_source_2014,
)
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _timed_self_buff

logger = logging.getLogger(__name__)


def _pit_fiend():
    try:
        return next(
            monster for monster in load_monster_source_2014()
            if monster.id == "pit-fiend"
        )
    except Exception:
        logger.exception("Pinned 2014 Pit Fiend source is missing.")
        raise


def test_pinned_source_correction_binds_generic_fear_aura_parameters() -> None:
    try:
        card = _pit_fiend()
        corrected = corrected_condition_aura_source_2014(card.source_traits)
        assert corrected != card.source_traits

        action, = condition_auras_from_source(card.source_traits, "2014")
        aura = action.hostile_start_turn_condition_aura
        assert action.name == "Fear Aura"
        assert action.activation_timing == "passive"
        assert aura is not None
        assert (aura.radius_ft, aura.save_ability, aura.save_dc) == (20, "wisdom", 21)
        assert aura.condition_id == "frightened"
        assert aura.condition_expiry_timing == "target_turn_start"
        assert aura.success_immunity is True
        assert aura.source_is_magical is False
        assert aura.requires_source_not_incapacitated is True
        assert aura.effect_tags == ["fear"]

        unsupported = unsupported_traits_2014(card)
        assert "Fear Aura" not in unsupported
        assert "Innate Spellcasting" in unsupported
    except Exception:
        logger.exception("Pinned 2014 Fear Aura source binding regression failed.")
        raise


def test_source_correction_fails_closed_on_ingest_drift() -> None:
    try:
        card = _pit_fiend()
        assert condition_auras_from_source(card.source_traits + " drift", "2014") == []
    except Exception:
        logger.exception("Fear Aura source-correction drift regression failed.")
        raise


def test_generic_fear_aura_parser_is_not_source_identity_keyed() -> None:
    try:
        renamed = (
            "Dread Aura. Any creature hostile to the renamed fiend that starts its turn "
            "within 25 feet of the renamed fiend must make a DC 17 Wisdom saving throw, "
            "unless the renamed fiend is incapacitated. On a failed save, the creature "
            "is frightened until the start of its next turn. If a creature's saving "
            "throw is successful, the creature is immune to the renamed fiend's Dread "
            "Aura for the next 24 hours."
        )
        action, = condition_auras_from_source(renamed, "2014")
        aura = action.hostile_start_turn_condition_aura
        assert action.name == "Dread Aura"
        assert aura is not None
        assert (aura.radius_ft, aura.save_dc) == (25, 17)
        assert aura.requires_source_not_incapacitated is True
    except Exception:
        logger.exception("Generic Fear Aura source renaming regression failed.")
        raise


def test_real_source_serializes_through_generic_browser_bridge() -> None:
    card = _pit_fiend()
    action, = condition_auras_from_source(card.source_traits, "2014")

    row = _timed_self_buff(action)
    aura = row["hostileStartTurnConditionAura"]

    assert row["name"] == "Fear Aura"
    assert row["activationTiming"] == "passive"
    assert aura["radius_ft"] == 20
    assert aura["save_ability"] == "wisdom"
    assert aura["save_dc"] == 21
    assert aura["condition_id"] == "frightened"
    assert aura["success_immunity"] is True
    assert aura["source_is_magical"] is False
    assert aura["requires_source_not_incapacitated"] is True
    assert aura["condition_expiry_timing"] == "target_turn_start"
