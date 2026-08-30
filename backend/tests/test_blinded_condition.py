from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters_wolves import build_wolf
from app.domain.models import RollMode


def test_blinded_attacker_has_disadvantage() -> None:
    attacker = build_combatant_state(build_karnok_stoneward())
    defender = build_combatant_state(build_wolf())
    attacker.active_effect_ids.append("blinded")

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([17, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 3


def test_attack_against_blinded_defender_has_advantage() -> None:
    attacker = build_combatant_state(build_wolf())
    defender = build_combatant_state(build_karnok_stoneward())
    defender.active_effect_ids.append("blinded")

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([3, 17, 2]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 17


def test_blinded_attacker_against_blinded_defender_rolls_normally() -> None:
    attacker = build_combatant_state(build_karnok_stoneward())
    defender = build_combatant_state(build_wolf())
    attacker.active_effect_ids.append("blinded")
    defender.active_effect_ids.append("blinded")

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([12, 3, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL
    assert event.attack_roll.selected_roll == 12
