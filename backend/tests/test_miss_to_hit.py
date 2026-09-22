from __future__ import annotations

from app.combat.miss_to_hit import resolve_miss_to_hit
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level


def test_first_miss_converts_once_per_turn_and_recharges_next_turn() -> None:
    state = build_combatant_state(build_mara_quickstep_level(19))

    assert resolve_miss_to_hit(state, False, "1:mara") == (True, True)
    assert resolve_miss_to_hit(state, False, "1:mara") == (False, False)
    assert resolve_miss_to_hit(state, False, "2:mara") == (True, True)


def test_hit_and_missing_turn_key_do_not_spend_capability() -> None:
    state = build_combatant_state(build_mara_quickstep_level(19))

    assert resolve_miss_to_hit(state, True, "1:mara") == (True, False)
    assert resolve_miss_to_hit(state, False, None) == (False, False)
    assert state.feature_last_turn_keys == {}
