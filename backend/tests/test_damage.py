from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import RollMode


def test_goblin_normal_hit_does_not_get_advantage_bonus_damage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )

    assert total.total == 6
    assert len(components) == 1
    assert components[0].notation == "1d6+2"


def test_goblin_advantage_hit_adds_one_d4_damage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4, 3]),
        critical=False,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 9
    assert [component.notation for component in components] == ["1d6+2", "1d4+0"]
    assert components[1].source == "Advantage bonus damage"


def test_goblin_advantage_critical_doubles_base_and_bonus_damage_dice() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    total, components = resolve_weapon_damage(
        goblin,
        goblin.template.weapon_attack,
        FixedDiceProvider([4, 5, 2, 3]),
        critical=True,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 16
    assert [component.notation for component in components] == ["2d6+2", "2d4+0"]


def test_longsword_has_no_goblin_advantage_bonus_damage() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    total, components = resolve_weapon_damage(
        fighter,
        fighter.template.weapon_attack,
        FixedDiceProvider([7]),
        critical=False,
        attack_mode=RollMode.ADVANTAGE,
    )

    assert total.total == 10
    assert len(components) == 1
    assert components[0].source == "Longsword"
