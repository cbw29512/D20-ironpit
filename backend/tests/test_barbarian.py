from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage
from app.combat.damage_taken import resolve_damage_taken
from app.combat.dice import FixedDiceProvider
from app.combat.lifecycle import begin_actor_turn, end_actor_turn
from app.combat.saving_throws import resolve_saving_throw, saving_throw_bonus
from app.combat.state import build_combatant_state
from app.content.barbarian import build_demo_barbarian
from app.content.low_cr_monsters import build_bandit
from app.domain.models import AbilityKind, ConditionKind, DamageRollComponent, DamageType, RollMode


def test_barbarian_template_is_classic_and_raw() -> None:
    template = build_demo_barbarian()

    assert template.armor_class == 15
    assert template.max_hp == 15
    assert template.weapon_attack.weapon.name == "Greataxe"
    assert template.weapon_attack.weapon.dice_size == 12
    assert template.weapon_attack.ability is AbilityKind.STRENGTH
    assert template.alternate_weapon_attacks[0].weapon.name == "Handaxe"
    assert template.weapon_masteries == ["greataxe", "handaxe"]
    assert template.resources[0].id == "rage" and template.resources[0].max_uses == 2
    assert saving_throw_bonus(build_combatant_state(template), AbilityKind.STRENGTH) == 5
    assert saving_throw_bonus(build_combatant_state(template), AbilityKind.CONSTITUTION) == 5


def test_enter_rage_spends_bonus_action_and_one_use() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())

    event = enter_rage(1, 1, barbarian)

    assert barbarian.raging is True
    assert barbarian.bonus_action_available is False
    assert barbarian.resources[0].current_uses == 1
    assert barbarian.temporary_damage_resistances == {
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    }
    assert event.effect_changes[0].effect_id == "rage"
    assert event.resource_remaining == 1


def test_heavy_armor_blocks_rage() -> None:
    template = build_demo_barbarian().model_copy(update={"wearing_heavy_armor": True})
    barbarian = build_combatant_state(template)

    try:
        enter_rage(1, 1, barbarian)
    except ValueError as exc:
        assert "Heavy armor" in str(exc)
    else:
        raise AssertionError("Rage must be blocked by Heavy armor.")


def test_rage_grants_strength_save_advantage_only() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    enter_rage(1, 1, barbarian)

    strength = resolve_saving_throw(
        barbarian, AbilityKind.STRENGTH, 20, FixedDiceProvider([4, 15])
    )
    dexterity = resolve_saving_throw(
        barbarian, AbilityKind.DEXTERITY, 20, FixedDiceProvider([15])
    )

    assert strength.roll is not None and strength.roll.mode is RollMode.ADVANTAGE
    assert strength.roll.selected_roll == 15 and strength.roll.total == 20
    assert dexterity.roll is not None and dexterity.roll.mode is RollMode.NORMAL


def test_rage_adds_two_strength_damage_and_is_not_doubled_on_crit() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    bandit = build_combatant_state(build_bandit())
    enter_rage(1, 1, barbarian)

    event = resolve_attack(
        2,
        1,
        barbarian,
        bandit,
        barbarian.template.weapon_attack,
        5,
        FixedDiceProvider([20, 4, 5]),
    )

    rage = next(component for component in event.damage_components if component.source == "Rage")
    assert event.critical is True
    assert rage.rolls == [] and rage.total == 2
    assert event.damage_roll is not None and event.damage_roll.total == 14
    assert event.damage_applied == 14


def test_rage_resistance_halves_physical_damage_rounding_down() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    bandit = build_combatant_state(build_bandit())
    enter_rage(1, 1, barbarian)

    event = resolve_attack(
        2,
        1,
        bandit,
        barbarian,
        bandit.template.weapon_attack,
        5,
        FixedDiceProvider([15, 5]),
    )

    assert event.damage_roll is not None and event.damage_roll.total == 6
    assert event.damage_applied == 3
    assert barbarian.current_hp == 12
    assert "Resistance reduces applied damage to 3" in event.description


def test_resistance_groups_same_damage_type_before_rounding() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    enter_rage(1, 1, barbarian)
    components = [
        DamageRollComponent(source="A", notation="1", rolls=[], total=1, damage_type=DamageType.SLASHING),
        DamageRollComponent(source="B", notation="1", rolls=[], total=1, damage_type=DamageType.SLASHING),
    ]

    applied, resisted, _, _ = resolve_damage_taken(barbarian, components)

    assert applied == 1
    assert resisted == {DamageType.SLASHING}


def test_attack_roll_extends_rage_even_when_attack_misses() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    bandit = build_combatant_state(build_bandit())
    enter_rage(1, 1, barbarian)
    end_actor_turn(2, 1, barbarian, (barbarian, bandit))
    begin_actor_turn(3, 2, barbarian, (barbarian, bandit))
    assert barbarian.rage_extension_required is True

    event = resolve_attack(
        4,
        2,
        barbarian,
        bandit,
        barbarian.template.weapon_attack,
        5,
        FixedDiceProvider([1]),
    )
    end_events, _ = end_actor_turn(5, 2, barbarian, (barbarian, bandit))

    assert event.hit is False
    assert barbarian.raging is True
    assert barbarian.rage_extension_required is False
    assert not any(change.effect_id == "rage" for item in end_events for change in item.effect_changes)


def test_unextended_rage_expires_at_end_of_next_turn() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    bandit = build_combatant_state(build_bandit())
    enter_rage(1, 1, barbarian)
    end_actor_turn(2, 1, barbarian, (barbarian, bandit))
    begin_actor_turn(3, 2, barbarian, (barbarian, bandit))

    events, _ = end_actor_turn(4, 2, barbarian, (barbarian, bandit))

    assert barbarian.raging is False
    assert barbarian.temporary_damage_resistances == set()
    assert any(change.effect_id == "rage" and change.operation == "remove" for event in events for change in event.effect_changes)


def test_incapacitation_ends_active_rage_at_turn_start() -> None:
    barbarian = build_combatant_state(build_demo_barbarian())
    bandit = build_combatant_state(build_bandit())
    enter_rage(1, 1, barbarian)
    barbarian.conditions.add(ConditionKind.INCAPACITATED)

    events, _ = begin_actor_turn(2, 2, barbarian, (barbarian, bandit))

    assert barbarian.raging is False
    assert any(change.effect_id == "rage" and change.operation == "remove" for event in events for change in event.effect_changes)
