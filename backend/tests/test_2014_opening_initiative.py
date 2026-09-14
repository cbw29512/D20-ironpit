from __future__ import annotations

from app.combat.conditional_damage import conditional_damage_active, round1_initiative_lead
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.attacks import resolve_attack
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import ConditionalDamage, RollMode


def _states():
    attacker = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    attacker.initiative_total = 18
    target.initiative_total = 12
    return attacker, target


def _opening_attack():
    attack = build_goblin_warrior().weapon_attack
    rider = ConditionalDamage(
        trigger="round1_initiative_lead",
        mode="add",
        dice_count=2,
        dice_size=6,
        damage_type=attack.weapon.damage_type,
    )
    return attack.model_copy(update={"conditional_damage": [rider]})


def test_round1_initiative_lead_requires_strict_round_one_win() -> None:
    attacker, target = _states()
    assert round1_initiative_lead(attacker, target, 1)
    assert not round1_initiative_lead(attacker, target, 2)
    target.initiative_total = attacker.initiative_total
    assert not round1_initiative_lead(attacker, target, 1)


def test_opening_initiative_damage_uses_target_specific_initiative() -> None:
    attacker, target = _states()
    rider = _opening_attack().conditional_damage[0]
    assert conditional_damage_active(rider, attacker, target, RollMode.NORMAL, 1)
    target.initiative_total = 20
    assert not conditional_damage_active(rider, attacker, target, RollMode.NORMAL, 1)


def test_opening_initiative_damage_enters_canonical_attack_damage() -> None:
    attacker, target = _states()
    event = resolve_attack(1, 1, attacker, target, _opening_attack(), 5, FixedDiceProvider([19, 4, 3, 2]))
    assert event.hit
    assert any(part.source == "Opening initiative bonus damage" for part in event.damage_components)
