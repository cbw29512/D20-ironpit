from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import RollMode, WeaponAttackKind


def test_natural_twenty_critical_can_end_duel() -> None:
    # Fighter initiative 15, goblin 10, fighter attack 20, then 7 and 6 on doubled d8 damage dice.
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([15, 10, 20, 7, 6]),
    )
    attack = next(event for event in battle.events if event.event_type == "attack")
    assert attack.critical is True
    assert attack.damage_roll is not None
    assert attack.damage_roll.total == 16
    assert battle.winner_id == "aldric-vane-l1"
    assert battle.monster.current_hp == 0


def test_natural_one_always_misses() -> None:
    # Goblin wins initiative. It rolls a natural 1, so the attack misses even after its +4 bonus.
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([5, 18, 1, 12, 4, 10, 3, 9, 2, 20, 6, 6]),
    )
    first_attack = next(event for event in battle.events if event.event_type == "attack")
    assert first_attack.actor_id == "srd-goblin-warrior"
    assert first_attack.attack_roll is not None
    assert first_attack.attack_roll.rolls == [1]
    assert first_attack.hit is False


def test_default_demo_remains_five_foot_melee() -> None:
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([15, 10, 20, 7, 6]),
    )
    first_attack = next(event for event in battle.events if event.event_type == "attack")

    assert battle.battlefield.distance_ft == 5
    assert battle.monster.template.weapon.attack_kind is WeaponAttackKind.MELEE
    assert battle.monster.template.alternate_weapons[0].attack_kind is WeaponAttackKind.RANGED
    assert first_attack.attack_roll is not None
    assert first_attack.attack_roll.mode is RollMode.NORMAL
