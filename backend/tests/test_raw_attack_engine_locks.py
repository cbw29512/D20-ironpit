from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.dodge import resolve_dodge_action
from app.combat.encounter_setup import build_encounter_setup
from app.combat.legendary_actions import resolve_legendary_actions_after_turn
from app.combat.modifier_stack import effective_armor_class
from app.combat.state import begin_turn
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection, RollMode


def _adjacent(setup) -> None:
    attacker, target = setup.monsters[0], setup.heroes[0]
    attacker.state.position = GridPosition(x=8, y=6)
    target.state.position = GridPosition(x=7, y=6)


def test_declared_multiattack_uses_printed_slot_order() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"], monster_ids=["2014-unicorn"], ruleset="2014",
    ))
    _adjacent(setup)
    unicorn = setup.monsters[0]
    begin_turn(unicorn.state)
    events, _ = resolve_attack_action(1, 1, unicorn, setup, FixedDiceProvider([10] * 12))
    attacks = [event for event in events if event.event_type == "attack"]
    assert [event.weapon_id for event in attacks] == ["2014-unicorn-hooves", "2014-unicorn-horn"]


def test_spent_dodge_action_cannot_also_attack() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"], monster_ids=["2014-unicorn"], ruleset="2014",
    ))
    _adjacent(setup)
    unicorn = setup.monsters[0]
    begin_turn(unicorn.state)
    resolve_dodge_action(1, 1, unicorn)
    try:
        resolve_attack_action(2, 1, unicorn, setup, FixedDiceProvider([15] * 8))
    except ValueError as exc:
        assert "not available" in str(exc)
    else:
        raise AssertionError("Dodge must consume the Action so Multiattack cannot fire.")


def test_normal_multiattack_miss_continues_remaining_slots() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l1"], monster_ids=["2014-brown-bear"], ruleset="2014",
    ))
    _adjacent(setup)
    bear = setup.monsters[0]
    begin_turn(bear.state)
    events, _ = resolve_attack_action(1, 1, bear, setup, FixedDiceProvider([2, 4, 4, 15, 4, 4]))
    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert attacks[0].hit is False
    assert attacks[0].turn_terminated is False
    assert attacks[1].weapon_id == "2014-brown-bear-claws"


def test_discarded_natural_20_is_not_a_critical() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    attacker, target = setup.heroes[0], setup.monsters[0]
    attacker.state.position = GridPosition(x=7, y=6)
    target.state.position = GridPosition(x=8, y=6)
    begin_turn(attacker.state)
    attack = attacker.state.template.weapon_attack
    event = resolve_attack(
        1, 1, attacker.state, target.state, attack, 5, FixedDiceProvider([20, 8, 4, 4, 4, 4]),
        other_disadvantage_sources=1, close_enemy_active=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.rolls == [20, 8]
    assert event.attack_roll.selected_roll == 8
    assert event.critical is False


def test_kept_die_at_expanded_crit_threshold_is_still_a_critical() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"], monster_ids=["2014-goblin"], ruleset="2014",
    ))
    attacker, target = setup.heroes[0], setup.monsters[0]
    attacker.state.position = GridPosition(x=7, y=6)
    target.state.position = GridPosition(x=8, y=6)
    begin_turn(attacker.state)
    event = resolve_attack(
        1, 1, attacker.state, target.state, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([20, 19, 4, 4, 4, 4, 4, 4]),
        other_disadvantage_sources=1, close_enemy_active=False,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.selected_roll == 19
    assert event.critical is True


def test_active_ac_buff_changes_effective_and_logged_ac() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"], monster_ids=["2014-unicorn"], ruleset="2014",
    ))
    hero, unicorn = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=12, y=6)
    unicorn.state.position = GridPosition(x=16, y=6)
    begin_turn(unicorn.state)
    events, _ = resolve_legendary_actions_after_turn(1, 1, hero, setup, FixedDiceProvider([20]))
    assert any("Shimmering Shield" in event.description for event in events)
    assert effective_armor_class(unicorn.state) == unicorn.state.template.armor_class + 2
    hero.state.position = GridPosition(x=15, y=6)
    begin_turn(hero.state)
    attack = resolve_attack(
        2, 1, hero.state, unicorn.state, hero.state.template.weapon_attack, 5,
        FixedDiceProvider([10, 4, 4, 4, 4]), close_enemy_active=False,
    )
    assert attack.target_ac == unicorn.state.template.armor_class + 2
