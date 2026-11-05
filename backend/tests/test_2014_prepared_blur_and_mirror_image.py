"""Prepared 2014 Blur reuses the universal modifier; Mirror Image stays blocked."""
from __future__ import annotations

import logging

from app.content.monster_innate_support_2014 import innate_timed_self_buffs_2014
from app.content.monster_prepared_spells_2014 import (
    prepared_defensive_spell_actions_2014,
    prepared_timed_self_buffs_2014,
    supports_prepared_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _synthetic_prepared(*spell_ids: str):
    """Test binding from explicit fake spell data without altering a pinned card."""
    try:
        archmage = next(
            card for card in load_monster_source_2014() if card.id == "archmage"
        )
        source = dict(archmage.spellcasting or {})
        source["source_complete"] = True
        source["spells"] = [
            {"id": spell_id, "name": spell_id, "level": 2}
            for spell_id in spell_ids
        ]
        return archmage.model_copy(update={
            "id": "synthetic-prepared-caster",
            "name": "Synthetic Prepared Caster",
            "spellcasting": source,
        })
    except Exception:
        logger.exception("Could not build synthetic prepared spell source.")
        raise


def test_prepared_blur_reuses_2014_innate_modifier_and_slot_spell_path() -> None:
    try:
        source = _synthetic_prepared("blur")
        before = source.model_dump_json()
        action, = prepared_defensive_spell_actions_2014(source)
        innate_source = next(
            card for card in load_monster_source_2014() if card.id == "steam-mephit"
        )
        innate = next(
            item for item in innate_timed_self_buffs_2014(innate_source)
            if item.id == "blur"
        )
        assert action.id == "blur"
        assert action.name == "Blur"
        assert action.level == 2
        assert action.action_cost == "action"
        assert action.target_policy == "self"
        assert action.duration_minutes == 1
        assert action.concentration is True
        assert action.modifier_effects == innate.modifier_effects
        assert not prepared_timed_self_buffs_2014(source)
        assert supports_prepared_spellcasting_2014(source) is True
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Prepared Blur universal binder regression failed.")
        raise


def test_unimplemented_mirror_image_stays_unbound_and_blocks_admission() -> None:
    try:
        source = _synthetic_prepared("mirror-image")
        before = source.model_dump_json()
        assert prepared_timed_self_buffs_2014(source) == []
        assert prepared_defensive_spell_actions_2014(source) == []
        assert supports_prepared_spellcasting_2014(source) is False
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Mirror Image fail-closed regression failed.")
        raise


def test_partial_prepared_blur_cannot_hide_unimplemented_mirror_image() -> None:
    try:
        source = _synthetic_prepared("blur", "mirror-image")
        assert [action.id for action in prepared_defensive_spell_actions_2014(source)] == ["blur"]
        assert prepared_timed_self_buffs_2014(source) == []
        assert supports_prepared_spellcasting_2014(source) is False
    except Exception:
        logger.exception("Partial prepared caster admission regression failed.")
        raise

def test_counterspell_remains_unbound_until_reaction_runtime_exists() -> None:
    try:
        source = _synthetic_prepared("counterspell")
        assert prepared_timed_self_buffs_2014(source) == []
        assert supports_prepared_spellcasting_2014(source) is False
    except Exception:
        logger.exception("Counterspell reaction fail-closed regression failed.")
        raise

def test_fire_shield_placeholder_is_not_treated_as_implemented() -> None:
    try:
        source = _synthetic_prepared("fire-shield")
        assert prepared_timed_self_buffs_2014(source) == []
        assert supports_prepared_spellcasting_2014(source) is False
    except Exception:
        logger.exception("Fire Shield fail-closed regression failed.")
        raise

def test_shield_reaction_does_not_use_defensive_spell_action() -> None:
    try:
        source = _synthetic_prepared("shield")
        assert prepared_defensive_spell_actions_2014(source) == []
        assert supports_prepared_spellcasting_2014(source) is False
    except Exception:
        logger.exception("Shield reaction fail-closed regression failed.")
        raise
