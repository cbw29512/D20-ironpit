from app.combat.attacks import resolve_attack
from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import DamageRollComponent, DamageType


def _component(amount: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source="test",
        notation=str(amount),
        rolls=[amount],
        damage_type=damage_type,
        total=amount,
    )


def test_damage_type_enum_contains_all_thirteen_2024_types() -> None:
    assert {member.value for member in DamageType} == {
        "acid",
        "bludgeoning",
        "cold",
        "fire",
        "force",
        "lightning",
        "necrotic",
        "piercing",
        "poison",
        "psychic",
        "radiant",
        "slashing",
        "thunder",
    }


def test_resistance_halves_damage_and_rounds_down() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]

    assert adjusted_damage_amount(9, DamageType.FIRE, target) == 4


def test_vulnerability_doubles_damage() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_vulnerabilities = [DamageType.COLD]

    assert adjusted_damage_amount(9, DamageType.COLD, target) == 18


def test_immunity_reduces_matching_damage_to_zero() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_immunities = [DamageType.POISON]

    assert adjusted_damage_amount(9, DamageType.POISON, target) == 0


def test_resistance_applies_before_vulnerability_for_same_type() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]
    target.template.damage_vulnerabilities = [DamageType.FIRE]

    assert adjusted_damage_amount(9, DamageType.FIRE, target) == 8


def test_mixed_damage_is_adjusted_per_component() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]

    applied, components = apply_damage_defenses(
        target,
        [
            _component(7, DamageType.SLASHING),
            _component(8, DamageType.FIRE),
        ],
    )

    assert applied == 11
    assert [component.total for component in components] == [7, 8]
    assert [component.applied_total for component in components] == [7, 4]


def test_immune_critical_at_zero_causes_no_death_save_failure() -> None:
    attacker = build_combatant_state(build_goblin_warrior())
    defender = build_combatant_state(build_demo_fighter())
    apply_damage(defender, defender.current_hp)
    defender.template.damage_immunities = [DamageType.FIRE]
    fire_attack = attacker.template.weapon_attack.model_copy(deep=True)
    fire_attack.weapon.damage_type = DamageType.FIRE

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        fire_attack,
        5,
        FixedDiceProvider([20, 6, 6]),
    )

    assert event.critical is True
    assert event.damage_roll is not None
    assert event.damage_roll.total == 14
    assert event.damage_components[0].applied_total == 0
    assert defender.death_save_failures == 0
    assert defender.is_dead is False
