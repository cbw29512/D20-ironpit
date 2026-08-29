from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import (
    DamageType,
    EncounterSelection,
    OnHitDamage,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)


def _setup():
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-commoner"],
        starting_distance_ft=5,
    ))


def _venom_bite() -> WeaponAttack:
    return WeaponAttack(
        id="test-venom-bite",
        weapon=Weapon(
            id="test-venom-bite", name="Bite", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=4, damage_type=DamageType.PIERCING,
            animation="bite", reach_ft=5,
        ),
        attack_bonus=6,
        damage_bonus=4,
        on_hit_damage=[OnHitDamage(
            source="Venom", dice_count=1, dice_size=8,
            damage_type=DamageType.POISON,
        )],
    )


def test_mixed_hit_keeps_piercing_and_poison_components_separate() -> None:
    setup = _setup()
    hero, commoner = setup.heroes[0], setup.monsters[0]
    event = resolve_attack(
        1, 1, commoner.state, hero.state, _venom_bite(), 5,
        FixedDiceProvider([15, 3, 5]),
        actor_event_id=commoner.combatant_id, target_event_id=hero.combatant_id,
    )

    assert event.hit is True
    assert event.critical is False
    assert [component.damage_type for component in event.damage_components] == [
        DamageType.PIERCING, DamageType.POISON,
    ]
    assert [component.total for component in event.damage_components] == [7, 5]
    assert event.damage_roll is not None and event.damage_roll.total == 12


def test_critical_doubles_dice_for_every_on_hit_damage_component() -> None:
    setup = _setup()
    hero, commoner = setup.heroes[0], setup.monsters[0]
    event = resolve_attack(
        1, 1, commoner.state, hero.state, _venom_bite(), 5,
        FixedDiceProvider([20, 2, 3, 4, 5]),
        actor_event_id=commoner.combatant_id, target_event_id=hero.combatant_id,
    )

    assert event.critical is True
    assert [component.notation for component in event.damage_components] == ["2d4+4", "2d8+0"]
    assert [component.total for component in event.damage_components] == [9, 9]
    assert event.damage_roll is not None and event.damage_roll.total == 18


def test_type_specific_defenses_apply_after_components_are_rolled() -> None:
    setup = _setup()
    hero, commoner = setup.heroes[0], setup.monsters[0]
    hero.state.template.damage_resistances = [DamageType.PIERCING]
    hero.state.template.damage_immunities = [DamageType.POISON]
    event = resolve_attack(
        1, 1, commoner.state, hero.state, _venom_bite(), 5,
        FixedDiceProvider([15, 4, 8]),
        actor_event_id=commoner.combatant_id, target_event_id=hero.combatant_id,
    )

    assert [component.total for component in event.damage_components] == [8, 8]
    assert [component.applied_total for component in event.damage_components] == [4, 0]
    assert event.damage_roll is not None and event.damage_roll.total == 4
