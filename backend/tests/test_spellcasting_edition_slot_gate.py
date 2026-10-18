"""Edition-isolation regressions for the shared slot-per-turn gate."""
import logging

import pytest

from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast, slot_spell_available, spell_turn_legal, record_spell_turn
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("edition,second_cast_legal", [("2014", True), ("2024", False)])
def test_slot_gate_uses_combatant_edition(edition: str, second_cast_legal: bool) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": edition})
        state = build_combatant_state(template)
        key = "1:caster"
        assert slot_spell_available(state, key)
        mark_slot_spell_cast(state, key)
        assert slot_spell_available(state, key) is second_cast_legal
        if second_cast_legal:
            mark_slot_spell_cast(state, key)
        else:
            with pytest.raises(ValueError, match="already been expended"):
                mark_slot_spell_cast(state, key)
        assert slot_spell_available(state, "2:caster")
        assert slot_spell_available(build_combatant_state(template), key)
    except Exception:
        logger.exception("Spellcasting edition gate regression failed for %s", edition)
        raise


def test_missing_turn_key_fails_closed() -> None:
    try:
        state = build_combatant_state(build_seraphine_dawnshield())
        with pytest.raises(ValueError, match="active turn key"):
            slot_spell_available(state, "")
    except Exception:
        logger.exception("Missing-turn-key spellcasting regression failed")
        raise

@pytest.mark.parametrize("edition,expected", [("2014", (1,)), ("2024", ())])
def test_slot_level_selection_respects_edition_after_expenditure(edition: str, expected: tuple[int, ...]) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": edition})
        state = build_combatant_state(template)
        key = "1:caster"
        # Explicit fixture resource: the test isolates turn legality from spell preparation.
        from app.domain.runtime import ResourceState
        state.resources = [ResourceState(id="spell-slot-1", name="Level 1 Slot", current_uses=2, max_uses=2)]
        mark_slot_spell_cast(state, key)
        assert legal_slot_levels(state, key, 1) == expected
        assert legal_slot_levels(state, "2:caster", 1) == (1,)
    except Exception:
        logger.exception("Edition-specific slot-level selection failed for %s", edition)
        raise

@pytest.mark.parametrize("ruleset", ["2014", "2024"])
def test_first_spell_records_before_its_own_slot_expenditure(ruleset: str) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": ruleset})
        state = build_combatant_state(template)
        turn_key = "1:caster"
        assert spell_turn_legal(state, turn_key, "action", 1)
        record_spell_turn(state, turn_key, "action", 1)
        mark_slot_spell_cast(state, turn_key)
        assert slot_spell_available(state, turn_key) is (ruleset == "2014")
        assert slot_spell_available(build_combatant_state(template), turn_key)
        if ruleset == "2024":
            assert not spell_turn_legal(state, turn_key, "action", 1)
    except Exception:
        logger.exception("First spell cast ordering regression failed for %s", ruleset)
        raise


@pytest.mark.parametrize("first_cost,first_level,second_cost,second_level,allowed", [
    ("bonus_action", 1, "action", 0, True),
    ("bonus_action", 1, "action", 1, False),
    ("bonus_action", 1, "bonus_action", 1, False),
    ("bonus_action", 0, "bonus_action", 0, False),
    ("bonus_action", 1, "reaction", 0, False),
    ("action", 1, "bonus_action", 1, False),
    ("action", 0, "bonus_action", 1, True),
    ("action", 1, "action", 1, True),
])
def test_2014_bonus_action_spell_turn_order(first_cost, first_level, second_cost, second_level, allowed) -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": "2014"})
        state = build_combatant_state(template)
        record_spell_turn(state, "1:caster", first_cost, first_level)
        assert spell_turn_legal(state, "1:caster", second_cost, second_level) is allowed
        assert spell_turn_legal(state, "2:caster", second_cost, second_level)
    except Exception:
        logger.exception("2014 bonus-action spell order regression failed")
        raise

def test_2014_duplicate_bonus_spell_rejected_without_mutation() -> None:
    try:
        template = build_seraphine_dawnshield().model_copy(update={"ruleset": "2014"})
        state = build_combatant_state(template)
        record_spell_turn(state, "1:caster", "bonus_action", 0)
        before = dict(state.feature_last_turn_keys)
        with pytest.raises(ValueError, match="conflicts"):
            record_spell_turn(state, "1:caster", "bonus_action", 1)
        assert state.feature_last_turn_keys == before
        assert spell_turn_legal(state, "1:caster", "action", 0)
        assert not spell_turn_legal(state, "1:caster", "action", 1)
        assert spell_turn_legal(state, "2:caster", "bonus_action", 1)
        assert spell_turn_legal(build_combatant_state(template), "1:caster", "bonus_action", 1)
    except Exception:
        logger.exception("Duplicate bonus-action spell regression failed")
        raise


@pytest.mark.parametrize("invalid_level", [True, False, 1.0, -1, 10])
def test_spell_turn_gate_rejects_invalid_spell_levels(invalid_level) -> None:
    try:
        state = build_combatant_state(build_seraphine_dawnshield().model_copy(update={"ruleset": "2014"}))
        with pytest.raises(ValueError, match="Spell level"):
            spell_turn_legal(state, "1:caster", "action", invalid_level)
    except Exception:
        logger.exception("Spell level schema parity regression failed")
        raise
