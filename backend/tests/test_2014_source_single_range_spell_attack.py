"""2014 source-only spell range: one printed maximum maps to both legal range bands."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_attack_source_corrections_2014 import corrected_attack_range_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _horned_devil():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "horned-devil")
    except Exception:
        logger.exception("Unable to find the pinned 2014 Horned Devil source.")
        raise


def test_horned_devil_source_spell_range_admits_complete_monster() -> None:
    try:
        source = _horned_devil()
        before = source.model_dump_json()
        hurl = next(a for a in source.attacks if a.name == "Hurl Flame")
        assert hurl.kind == "ranged"
        assert (hurl.attack_bonus, hurl.damage.average,
                hurl.damage.dice_count, hurl.damage.dice_size,
                hurl.damage.type) == (7, 14, 4, 6, "fire")
        assert corrected_attack_range_2014(source, hurl) == (150, 150)
        assert basic_blockers_2014(source) == ()
        runtime = compile_combatant(adapt_basic_monster_2014(source))
        attack = next(
            a for a in [runtime.weapon_attack, *runtime.alternate_weapon_attacks]
            if a.weapon.name == "Hurl Flame"
        )
        assert attack.weapon.normal_range_ft == 150
        assert attack.weapon.long_range_ft == 150
        assert attack.attack_bonus == 7
        assert attack.weapon.dice_count == 4 and attack.weapon.dice_size == 6
        assert runtime.attack_action is not None
        assert len(runtime.attack_action.slots) == 3
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Horned Devil 2014 range/certification regression.")
        raise


def test_range_source_missing_or_mismatched_fails_closed() -> None:
    try:
        source = _horned_devil()
        hurl = next(a for a in source.attacks if a.name == "Hurl Flame")
        absent = source.model_copy(update={"source_actions": None})
        assert corrected_attack_range_2014(absent, hurl) == (
            hurl.normal_range_ft, hurl.long_range_ft,
        )
        assert "attack:range" in basic_blockers_2014(absent)
        mismatched = hurl.model_copy(update={"attack_bonus": hurl.attack_bonus + 1})
        with pytest.raises(ValueError, match="source differs"):
            corrected_attack_range_2014(source, mismatched)
        conflicting = hurl.model_copy(update={
            "normal_range_ft": 90, "long_range_ft": None,
        })
        with pytest.raises(ValueError, match="contradicts"):
            corrected_attack_range_2014(source, conflicting)
    except Exception:
        logger.exception("2014 ranged-spell fail-closed source tests failed.")
        raise


def test_weapon_longbow_uses_its_existing_printed_range_bands() -> None:
    try:
        scout = next(m for m in load_monster_source_2014() if m.id == "scout")
        longbow = next(a for a in scout.attacks if a.name == "Longbow")
        assert corrected_attack_range_2014(scout, longbow) == (150, 600)
    except Exception:
        logger.exception("2014 longbow range semantics unexpectedly changed.")
        raise
