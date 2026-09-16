from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import ConditionalAttackAdvantage, RollMode


def _attack():
    attack = build_goblin_warrior().weapon_attack
    return attack.model_copy(update={
        "conditional_attack_advantage": [ConditionalAttackAdvantage(trigger="round1_initiative_lead")],
        # This test isolates Ambusher roll mode from the 2024 Goblin Warrior's
        # separate advantage-triggered bonus-damage rider.
        "conditional_damage": [],
    })


def _states():
    attacker = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    attacker.initiative_total = 18
    target.initiative_total = 12
    return attacker, target


def test_ambusher_advantage_requires_round_one_initiative_win() -> None:
    attacker, target = _states()
    attack = _attack()
    assert conditional_attack_advantage_sources(attack, target, attacker=attacker, round_number=1) == 1
    assert conditional_attack_advantage_sources(attack, target, attacker=attacker, round_number=2) == 0
    target.initiative_total = 18
    assert conditional_attack_advantage_sources(attack, target, attacker=attacker, round_number=1) == 0


def test_ambusher_enters_canonical_attack_roll_mode() -> None:
    attacker, target = _states()
    event = resolve_attack(1, 1, attacker, target, _attack(), 5, FixedDiceProvider([3, 17, 4]))
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 17
