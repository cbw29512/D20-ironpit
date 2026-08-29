from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monsters_fixed_damage import build_fixed_damage_monsters


def _monster(monster_id: str):
    return next(item for item in build_fixed_damage_monsters() if item.id == monster_id)


def test_fixed_damage_critical_stays_fixed_and_rolls_no_damage_dice() -> None:
    attacker = build_combatant_state(_monster("srd-bat"))
    defender = build_combatant_state(build_demo_fighter())

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([20]),
    )

    assert event.critical is True
    assert event.hit is True
    assert event.damage_roll is not None
    assert event.damage_roll.notation == "1"
    assert event.damage_roll.rolls == []
    assert event.damage_roll.total == 1
    assert event.damage_components[0].total == 1
    assert defender.current_hp == defender.template.max_hp - 1


def test_fixed_damage_templates_store_zero_damage_dice() -> None:
    for monster in build_fixed_damage_monsters():
        attack = monster.weapon_attack
        assert attack.weapon.dice_count == 0
        assert attack.fixed_damage == 1
