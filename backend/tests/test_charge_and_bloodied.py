from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monsters_charge import build_boar
from app.domain.models import EncounterSelection, RollMode


def test_boar_charges_instead_of_dodging_when_twenty_feet_of_runup_exists() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-boar"],
        starting_distance_ft=30,
    ))
    hero, boar = setup.heroes[0], setup.monsters[0]

    events, _ = resolve_combat_turn(
        1, 1, boar, hero, setup, FixedDiceProvider([15, 2, 3])
    )

    assert [event.event_type for event in events[:2]] == ["movement", "attack"]
    assert events[0].movement_ft == 25
    attack = events[1]
    assert attack.feature_id == "charge"
    assert attack.hit is True
    assert attack.damage_roll is not None
    assert attack.damage_roll.notation == "1d6+1 + 1d6+0"
    assert attack.damage_roll.total == 6
    assert attack.applied_condition_ids == ["prone"]
    assert "dodge" not in boar.state.active_effect_ids


def test_boar_without_twenty_feet_of_runup_dodges_while_closing() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-boar"],
        starting_distance_ft=15,
    ))
    hero, boar = setup.heroes[0], setup.monsters[0]

    events, _ = resolve_combat_turn(1, 1, boar, hero, setup, FixedDiceProvider([10]))

    assert [event.event_type for event in events] == ["feature", "movement"]
    assert events[0].feature_id == "dodge"
    assert events[1].movement_ft == 10
    assert not any(event.feature_id == "charge" for event in events)


def test_bloodied_fury_supplies_advantage_on_melee_attack() -> None:
    attacker = build_combatant_state(build_boar())
    defender = build_combatant_state(build_demo_fighter())
    attacker.current_hp = 6

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([4, 15, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 15
    assert event.hit is True
