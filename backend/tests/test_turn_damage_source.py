import logging
from types import SimpleNamespace

from app.combat.state import build_combatant_state
from app.combat.turn_damage import clear_turn_damage
from app.combat.zero_hp import apply_damage
from app.content.monsters import build_commoner

logger = logging.getLogger(__name__)


def test_canonical_damage_records_only_identified_source() -> None:
    try:
        state = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))
        apply_damage(state, 7, source_id="attacker-a")
        apply_damage(state, 5, source_id="attacker-a")
        apply_damage(state, 3, source_id="attacker-b")
        apply_damage(state, 2)

        assert state.damage_taken_this_turn_by_source == {
            "attacker-a": 12,
            "attacker-b": 3,
        }
    except Exception:
        logger.exception("Canonical damage source ledger regression failed.")
        raise


def test_turn_damage_clear_resets_type_and_source_ledgers() -> None:
    try:
        state = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))
        apply_damage(state, 6, source_id="attacker-a")
        state.damage_taken_this_turn_by_type = {"fire": 6}
        setup = SimpleNamespace(
            heroes=[SimpleNamespace(state=state)],
            monsters=[],
        )

        clear_turn_damage(setup)

        assert state.damage_taken_this_turn_by_type == {}
        assert state.damage_taken_this_turn_by_source == {}
    except Exception:
        logger.exception("Turn damage source ledger reset regression failed.")
        raise
