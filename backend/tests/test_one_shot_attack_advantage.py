import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import add_modifier, expire_source_turn_modifiers
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.modifiers import CombatModifier, ModifierKind


def _state():
    return build_combatant_state(build_karnok_stoneward().model_copy(deep=True))


def _next_attack_modifier(*, expires_round: int = 2) -> CombatModifier:
    return CombatModifier(
        id="caster:guiding-bolt:target:advantage",
        source_id="caster",
        source_effect_id="guiding-bolt",
        kind=ModifierKind.ATTACKS_AGAINST_ADVANTAGE,
        target_id="target",
        consume_on_attack_against=True,
        expires_source_turn_end_round=expires_round,
    )


def test_next_attack_advantage_is_consumed_by_the_attack_roll() -> None:
    attacker, defender = _state(), _state()
    defender.template.armor_class = 30
    add_modifier(defender, _next_attack_modifier())

    first = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([5, 15]), spend_action=False,
    )
    assert first.attack_roll is not None and first.attack_roll.mode.value == "advantage"
    assert defender.active_modifiers == []

    second = resolve_attack(
        2, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([10]), spend_action=False,
    )
    assert second.attack_roll is not None and second.attack_roll.mode.value == "normal"


def test_advantage_is_consumed_even_when_close_ranged_disadvantage_cancels_it() -> None:
    attacker, defender = _state(), _state()
    defender.template.armor_class = 30
    ranged = attacker.template.alternate_weapon_attacks[0]
    add_modifier(defender, _next_attack_modifier())

    event = resolve_attack(
        1, 1, attacker, defender, ranged, 5,
        FixedDiceProvider([10]), spend_action=False, close_enemy_active=True,
    )
    assert event.attack_roll is not None and event.attack_roll.mode.value == "normal"
    assert defender.active_modifiers == []


def test_unused_next_attack_advantage_expires_at_source_turn_end() -> None:
    defender = _state()
    modifier = _next_attack_modifier(expires_round=2)
    add_modifier(defender, modifier)

    assert expire_source_turn_modifiers([defender], "caster", 1) == 0
    assert defender.active_modifiers == [modifier]
    assert expire_source_turn_modifiers([defender], "caster", 2) == 1
    assert defender.active_modifiers == []


def test_only_attack_advantage_can_use_next_attack_consumption() -> None:
    with pytest.raises(ValueError, match="Only attack-advantage"):
        CombatModifier(
            id="bad", source_id="caster", source_effect_id="bad",
            kind=ModifierKind.SPEED, flat_bonus=5, consume_on_attack_against=True,
        )
