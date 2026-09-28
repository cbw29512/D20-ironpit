from __future__ import annotations

from app.combat.attack_roll_resolution import resolve_attack_roll
from app.combat.brutal_strike import (
    BRUTAL_STRIKE_FEATURE_ID,
    BRUTAL_STRIKE_PENDING_KEY,
    brutal_strike_attack_sources,
    clear_brutal_strike_pending,
)
from app.combat.dice import FixedDiceProvider
from app.combat.reckless_attack import RECKLESS_ATTACK_EFFECT_ID
from app.combat.state import build_combatant_state
from app.content.barbarian_progression import build_rokhan_stonefury_level


def _barbarian(level: int = 9):
    state = build_combatant_state(build_rokhan_stonefury_level(level))
    state.active_effect_ids.append(RECKLESS_ATTACK_EFFECT_ID)
    return state


def test_brutal_strike_choice_is_spent_even_when_the_chosen_attack_misses() -> None:
    state = _barbarian()
    attack = state.template.weapon_attack
    adjusted, disadvantaged = brutal_strike_attack_sources(
        state, attack, "1:rokhan", reckless_advantage=1, disadvantage_sources=0,
    )
    assert adjusted == 0
    assert disadvantaged is False
    assert state.feature_last_turn_keys[BRUTAL_STRIKE_FEATURE_ID] == "1:rokhan"
    assert state.feature_last_turn_keys[BRUTAL_STRIKE_PENDING_KEY] == "1:rokhan"

    assert clear_brutal_strike_pending(state, "1:rokhan") is True
    adjusted_again, _ = brutal_strike_attack_sources(
        state, attack, "1:rokhan", reckless_advantage=1, disadvantage_sources=0,
    )
    assert adjusted_again == 1
    assert BRUTAL_STRIKE_PENDING_KEY not in state.feature_last_turn_keys


def test_python_blocks_brutal_strike_on_long_range_strength_attack_disadvantage() -> None:
    attacker = _barbarian()
    defender = _barbarian()
    thrown = next(
        item for item in attacker.template.alternate_weapon_attacks
        if item.id == "rokhan-handaxe-thrown"
    )
    result = resolve_attack_roll(
        attacker,
        defender,
        thrown,
        30,
        FixedDiceProvider([14, 9]),
        defender_event_id="target",
        attacker_event_id="rokhan",
        round_number=1,
        turn_key="1:rokhan",
        advantage_sources=0,
        other_disadvantage_sources=0,
        close_enemy_active=False,
    )
    assert result.brutal_strike_disadvantage is True
    assert BRUTAL_STRIKE_FEATURE_ID not in attacker.feature_last_turn_keys
    assert BRUTAL_STRIKE_PENDING_KEY not in attacker.feature_last_turn_keys
