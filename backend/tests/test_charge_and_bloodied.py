from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.monsters_charge import build_boar
from app.domain.models import EncounterSelection, RollMode


def _boar_fixture(distance_ft: int):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-boar"],
    ))
    hero, boar = setup.heroes[0], setup.monsters[0]
    hero.position_ft = 0
    boar.position_ft = distance_ft
    hero.state.initiative_total = 10
    boar.state.initiative_total = 20
    return setup, hero, boar


def test_boar_charges_when_it_sweeps_initiative_and_has_twenty_feet_of_runup() -> None:
    setup, hero, boar = _boar_fixture(30)

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


def test_boar_that_does_not_win_initiative_uses_normal_melee_closing() -> None:
    setup, hero, boar = _boar_fixture(30)
    boar.state.initiative_total = hero.state.initiative_total

    events, _ = resolve_combat_turn(1, 1, boar, hero, setup, FixedDiceProvider([10, 3]))

    assert [event.event_type for event in events] == ["movement", "attack"]
    assert events[0].movement_ft == 25
    assert events[1].feature_id != "charge"
    assert events[1].weapon_id == "boar-gore-weapon"


def test_charge_is_not_reused_after_round_one() -> None:
    setup, hero, boar = _boar_fixture(30)

    events, _ = resolve_combat_turn(1, 2, boar, hero, setup, FixedDiceProvider([10, 3]))

    assert [event.event_type for event in events] == ["movement", "attack"]
    assert events[1].feature_id != "charge"


def test_initiative_sweep_assumes_precontact_charge_runup_from_melee_slot() -> None:
    setup, hero, boar = _boar_fixture(5)

    events, _ = resolve_combat_turn(1, 1, boar, hero, setup, FixedDiceProvider([15, 2, 3]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 1
    assert attacks[0].feature_id == "charge"
    assert attacks[0].damage_roll is not None
    assert attacks[0].damage_roll.notation == "1d6+1 + 1d6+0"
    assert not any(event.event_type == "movement" for event in events)


def test_bloodied_fury_supplies_advantage_on_melee_attack() -> None:
    attacker = build_combatant_state(build_boar())
    defender = build_combatant_state(build_commoner())
    attacker.current_hp = 6

    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([4, 15, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 15
    assert event.hit is True
