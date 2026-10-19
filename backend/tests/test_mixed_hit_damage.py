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


def _ritual_sickle() -> WeaponAttack:
    return WeaponAttack(
        id="test-ritual-sickle",
        weapon=Weapon(
            id="test-ritual-sickle", name="Ritual Sickle", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=4, damage_type=DamageType.SLASHING,
            animation="slash", reach_ft=5,
        ),
        attack_bonus=3,
        damage_bonus=1,
        on_hit_damage=[OnHitDamage(
            source="Necrotic", dice_count=0, dice_size=2, damage_bonus=1,
            damage_type=DamageType.NECROTIC,
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


def test_fixed_typed_on_hit_damage_does_not_double_on_critical() -> None:
    setup = _setup()
    hero, commoner = setup.heroes[0], setup.monsters[0]
    event = resolve_attack(
        1, 1, commoner.state, hero.state, _ritual_sickle(), 5,
        FixedDiceProvider([20, 2, 3]),
        actor_event_id=commoner.combatant_id, target_event_id=hero.combatant_id,
    )

    assert event.critical is True
    assert [component.notation for component in event.damage_components] == ["2d4+1", "1"]
    assert [component.total for component in event.damage_components] == [6, 1]
    assert event.damage_roll is not None and event.damage_roll.total == 7


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


def test_renamed_card_attack_uses_same_typed_damage_and_defense_primitives() -> None:
    """Source labels may change; AC, rolls and typed defenses alone decide combat."""
    original = _venom_bite()
    renamed = original.model_copy(deep=True)
    renamed.id = "synthetic-anonymous-attack"
    renamed.weapon.id = "synthetic-anonymous-weapon"
    renamed.weapon.name = "Completely Different Label"
    renamed.on_hit_damage[0].source = "An Unrelated Effect Label"

    def resolve(attack: WeaponAttack):
        setup = _setup()
        hero, attacker = setup.heroes[0], setup.monsters[0]
        hero.state.template.damage_resistances = [DamageType.PIERCING]
        hero.state.template.damage_vulnerabilities = [DamageType.POISON]
        starting_hp = hero.state.current_hp
        event = resolve_attack(
            1, 1, attacker.state, hero.state, attack, 5,
            FixedDiceProvider([15, 4, 2]),
            actor_event_id=attacker.combatant_id,
            target_event_id=hero.combatant_id,
        )
        return event, starting_hp

    original_event, original_hp = resolve(original)
    renamed_event, renamed_hp = resolve(renamed)
    for event, before in ((original_event, original_hp), (renamed_event, renamed_hp)):
        assert event.hit is True
        assert [part.damage_type for part in event.damage_components] == [
            DamageType.PIERCING, DamageType.POISON,
        ]
        assert [part.total for part in event.damage_components] == [8, 2]
        # Piercing resistance halves 8 to 4; poison vulnerability doubles 2 to 4.
        assert [part.applied_total for part in event.damage_components] == [4, 4]
        assert event.damage_roll is not None and event.damage_roll.total == 8
        assert event.hp_after == before - 8
    assert renamed_event.attack_id != original_event.attack_id


def test_missed_mixed_type_attack_rolls_no_damage_and_spends_its_action() -> None:
    setup = _setup()
    hero, attacker = setup.heroes[0], setup.monsters[0]
    starting_hp = hero.state.current_hp
    event = resolve_attack(
        1, 1, attacker.state, hero.state, _venom_bite(), 5,
        FixedDiceProvider([1]),
        actor_event_id=attacker.combatant_id,
        target_event_id=hero.combatant_id,
    )
    assert event.hit is False
    assert event.turn_terminated is True  # Locked Pit natural-1 rule.
    assert event.damage_components == []
    assert hero.state.current_hp == starting_hp


def test_one_bite_typed_components_are_one_damage_event_for_a_monster() -> None:
    """Do not skip poison merely because piercing would individually reach 0 HP."""
    from app.combat.attack_legality import attack_allowed_against

    setup = _setup()
    hero, monster = setup.heroes[0], setup.monsters[0]
    monster.state.current_hp = 5
    event = resolve_attack(
        1, 1, hero.state, monster.state, _venom_bite(), 5,
        FixedDiceProvider([15, 4, 2]),
        actor_event_id=hero.combatant_id,
        target_event_id=monster.combatant_id,
    )
    assert event.hit is True
    assert [part.damage_type for part in event.damage_components] == [
        DamageType.PIERCING, DamageType.POISON,
    ]
    assert [part.applied_total for part in event.damage_components] == [8, 2]
    assert event.damage_roll is not None and event.damage_roll.total == 10
    assert monster.state.current_hp == 0 and monster.state.is_dead
    assert not attack_allowed_against(_venom_bite(), hero.combatant_id, monster.state)


def test_one_bite_zeroes_pregen_without_extra_failed_save_from_poison() -> None:
    setup = _setup()
    hero, monster = setup.heroes[0], setup.monsters[0]
    hero.state.current_hp = 5
    # Test ordinary dying, rather than this hero's Relentless Endurance.
    for resource in hero.state.resources:
        if resource.id == "relentless-endurance":
            resource.current_uses = 0
    event = resolve_attack(
        1, 1, monster.state, hero.state, _venom_bite(), 5,
        FixedDiceProvider([15, 4, 2]),
        actor_event_id=monster.combatant_id,
        target_event_id=hero.combatant_id,
    )
    assert [part.applied_total for part in event.damage_components] == [8, 2]
    assert hero.state.current_hp == 0 and hero.state.is_unconscious
    assert not hero.state.is_dead
    assert hero.state.death_save_failures == 0


def test_separate_later_damage_at_zero_causes_a_failed_save() -> None:
    from app.combat.zero_hp import apply_damage

    setup = _setup()
    hero = setup.heroes[0]
    hero.state.current_hp = 0
    hero.state.is_unconscious = True
    outcome = apply_damage(hero.state, 2, damage_types={DamageType.POISON})
    assert outcome == "unconscious"
    assert hero.state.death_save_failures == 1
    assert not hero.state.is_dead

