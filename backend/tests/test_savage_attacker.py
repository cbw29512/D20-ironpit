from app.combat.attacks import resolve_attack
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.pregens import build_brom_ironmark
from app.domain.models import RollMode
from app.domain.traits import CombatTrait


def _savage_brom():
    template = build_brom_ironmark().model_copy(deep=True)
    template.combat_traits.append(CombatTrait.SAVAGE_ATTACKER)
    return build_combatant_state(template)


def test_savage_attacker_rolls_weapon_dice_twice_and_uses_better_result() -> None:
    attacker = _savage_brom()

    total, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([2, 11]),
        False,
        RollMode.NORMAL,
        "round-1:hero-1",
    )

    assert total.total == 14
    assert components[0].rolls == [11]
    assert components[0].source == "Greataxe (Savage Attacker)"


def test_savage_attacker_is_used_only_once_for_the_same_turn_key() -> None:
    attacker = _savage_brom()
    attack = attacker.template.weapon_attack

    first, _ = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([2, 11]), False, RollMode.NORMAL, "turn-a"
    )
    second, second_components = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([4]), False, RollMode.NORMAL, "turn-a"
    )
    third, _ = resolve_weapon_damage(
        attacker, attack, FixedDiceProvider([1, 8]), False, RollMode.NORMAL, "turn-b"
    )

    assert first.total == 14
    assert second.total == 7
    assert second_components[0].source == "Greataxe"
    assert third.total == 11


def test_savage_attacker_on_critical_compares_the_critical_weapon_dice_sets() -> None:
    attacker = _savage_brom()

    total, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([1, 1, 10, 10]),
        True,
        RollMode.NORMAL,
        "turn-critical",
    )

    assert total.total == 23
    assert components[0].notation == "2d12+3"
    assert components[0].rolls == [10, 10]


def test_savage_attacker_does_not_roll_conditional_bonus_damage_twice() -> None:
    template = build_goblin_warrior().model_copy(deep=True)
    template.combat_traits.append(CombatTrait.SAVAGE_ATTACKER)
    attacker = build_combatant_state(template)

    total, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([1, 6, 4]),
        False,
        RollMode.ADVANTAGE,
        "turn-goblin",
    )

    assert total.total == 12
    assert [component.rolls for component in components] == [[6], [4]]
    assert components[1].source == "Advantage bonus damage"


def test_combatant_without_feat_rolls_weapon_damage_once() -> None:
    attacker = build_combatant_state(build_brom_ironmark())

    total, components = resolve_weapon_damage(
        attacker,
        attacker.template.weapon_attack,
        FixedDiceProvider([5]),
        False,
        RollMode.NORMAL,
        "turn-a",
    )

    assert total.total == 8
    assert components[0].source == "Greataxe"


def test_miss_does_not_consume_savage_attacker_for_later_hit_on_same_turn() -> None:
    attacker = _savage_brom()
    defender = build_combatant_state(build_goblin_warrior())

    miss = resolve_attack(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([1]),
        spend_action=False,
        turn_key="turn-a",
    )
    hit = resolve_attack(
        2,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 2, 12]),
        spend_action=False,
        turn_key="turn-a",
    )

    assert miss.hit is False
    assert hit.hit is True
    assert hit.damage_components[0].source == "Greataxe (Savage Attacker)"
    assert hit.damage_components[0].rolls == [12]
