from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.heroic_inspiration import (
    grant_heroic_warrior_inspiration,
    reroll_failed_attack_with_heroic_inspiration,
)
from app.combat.rolls import roll_d20
from app.combat.state import build_combatant_state, refresh_start_of_turn
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.models import RollMode


def _level_ten_state():
    return build_combatant_state(build_karnok_stoneward_level(10))


def test_heroic_warrior_grants_one_inspiration_at_turn_start_only_when_missing() -> None:
    state = _level_ten_state()
    assert state.heroic_inspiration is False
    assert grant_heroic_warrior_inspiration(state) is True
    assert state.heroic_inspiration is True
    assert grant_heroic_warrior_inspiration(state) is False
    assert state.heroic_inspiration is True


def test_shared_start_turn_refresh_grants_inspiration_even_while_downed() -> None:
    state = _level_ten_state()
    state.current_hp = 0
    state.is_unconscious = True
    state.reaction_available = False
    refresh_start_of_turn(state)
    assert state.reaction_available is True
    assert state.heroic_inspiration is True


def test_normal_failed_attack_rerolls_one_die_and_spends_inspiration() -> None:
    state = _level_ten_state()
    state.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([5]), modifier=9)
    rerolled, used = reroll_failed_attack_with_heroic_inspiration(
        state, original, 17, FixedDiceProvider([8]),
    )
    assert used is True
    assert rerolled.rolls == [8]
    assert rerolled.selected_roll == 8
    assert rerolled.total == 17
    assert "Heroic Inspiration" in rerolled.notation
    assert state.heroic_inspiration is False


def test_heroic_inspiration_must_keep_a_worse_replacement_roll() -> None:
    state = _level_ten_state()
    state.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([7]), modifier=9)
    rerolled, used = reroll_failed_attack_with_heroic_inspiration(
        state, original, 17, FixedDiceProvider([1]),
    )
    assert used is True
    assert rerolled.selected_roll == 1
    assert rerolled.total == 10
    assert state.heroic_inspiration is False


def test_advantage_replaces_only_one_die_and_recomputes_selected_roll() -> None:
    state = _level_ten_state()
    state.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([4, 7]), modifier=9, mode=RollMode.ADVANTAGE)
    rerolled, used = reroll_failed_attack_with_heroic_inspiration(
        state, original, 17, FixedDiceProvider([10]),
    )
    assert used is True
    assert rerolled.rolls == [10, 7]
    assert rerolled.selected_roll == 10
    assert rerolled.total == 19


def test_disadvantage_spends_only_when_one_die_replacement_can_recover_the_attack() -> None:
    recoverable = _level_ten_state()
    recoverable.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([7, 18]), modifier=9, mode=RollMode.DISADVANTAGE)
    rerolled, used = reroll_failed_attack_with_heroic_inspiration(
        recoverable, original, 17, FixedDiceProvider([10]),
    )
    assert used is True
    assert rerolled.rolls == [10, 18]
    assert rerolled.selected_roll == 10
    assert rerolled.total == 19
    assert recoverable.heroic_inspiration is False

    impossible = _level_ten_state()
    impossible.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([7, 6]), modifier=9, mode=RollMode.DISADVANTAGE)
    unchanged, used = reroll_failed_attack_with_heroic_inspiration(
        impossible, original, 17, FixedDiceProvider([20]),
    )
    assert used is False
    assert unchanged == original
    assert impossible.heroic_inspiration is True


def test_successful_attack_does_not_spend_heroic_inspiration() -> None:
    state = _level_ten_state()
    state.heroic_inspiration = True
    original = roll_d20(FixedDiceProvider([8]), modifier=9)
    unchanged, used = reroll_failed_attack_with_heroic_inspiration(
        state, original, 17, FixedDiceProvider([1]),
    )
    assert used is False
    assert unchanged == original
    assert state.heroic_inspiration is True


def test_attack_resolution_uses_heroic_inspiration_before_damage_resolution() -> None:
    attacker = _level_ten_state()
    defender = build_combatant_state(build_karnok_stoneward_level(9))
    attacker.heroic_inspiration = True
    attacker.feature_last_turn_keys["savage-attacker"] = "1:attacker"
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([5, 8, 3, 3]),
        actor_event_id="attacker", target_event_id="defender",
        spend_action=False, turn_key="1:attacker",
    )
    assert event.hit is True
    assert event.attack_roll is not None
    assert event.attack_roll.rolls == [8]
    assert event.attack_roll.total == 17
    assert "Heroic Inspiration" in event.attack_roll.notation
    assert "Heroic Inspiration rerolls one d20" in event.description
    assert attacker.heroic_inspiration is False
