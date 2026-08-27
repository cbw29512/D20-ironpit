import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.conditions import apply_condition, has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import attempt_escape_grapple
from app.combat.prone import stand_from_prone
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_beasts import build_giant_crab, build_wolf
from app.domain.models import BattlefieldState, ConditionType, RollMode


def test_wolf_bite_applies_prone_to_medium_target() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    events = resolve_attack_action(
        1, 1, wolf, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([15, 3])
    )

    assert [event.event_type for event in events] == ["attack", "condition"]
    assert events[1].condition is ConditionType.PRONE
    assert has_condition(fighter, ConditionType.PRONE)


def test_prone_attack_modifiers_follow_distance() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(wolf, ConditionType.PRONE, fighter)
    events = resolve_attack_action(
        1, 1, wolf, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([18, 5])
    )
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE

    goblin = build_combatant_state(build_goblin_warrior())
    prone_fighter = build_combatant_state(build_demo_fighter())
    apply_condition(prone_fighter, ConditionType.PRONE, goblin)
    events = resolve_attack_action(
        1, 1, goblin, prone_fighter, BattlefieldState(distance_ft=10), FixedDiceProvider([18, 7])
    )
    assert events[0].weapon_id == "shortbow"
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE


def test_melee_attack_against_prone_target_has_advantage() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PRONE, wolf)
    events = resolve_attack_action(
        1, 1, wolf, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([4, 17, 2])
    )
    assert events[0].attack_roll.mode is RollMode.ADVANTAGE
    assert events[0].attack_roll.selected_roll == 17


def test_standing_from_prone_costs_half_speed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PRONE)
    begin_turn(fighter)
    event = stand_from_prone(1, 1, fighter)

    assert event is not None
    assert event.movement_ft == 15
    assert fighter.movement_remaining_ft == 15
    assert not has_condition(fighter, ConditionType.PRONE)


def test_giant_crab_claw_applies_grapple_with_escape_dc() -> None:
    crab = build_combatant_state(build_giant_crab(), "crab-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    events = resolve_attack_action(
        1, 1, crab, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([15, 3])
    )

    assert [event.event_type for event in events] == ["attack", "condition"]
    grapple = next(item for item in fighter.conditions if item.condition is ConditionType.GRAPPLED)
    assert grapple.source_id == "crab-1"
    assert grapple.escape_dc == 11
    begin_turn(fighter)
    assert fighter.movement_remaining_ft == 0


def test_grappled_attacker_only_avoids_disadvantage_against_grappler() -> None:
    crab = build_combatant_state(build_giant_crab(), "crab-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    apply_condition(fighter, ConditionType.GRAPPLED, crab, escape_dc=11)

    vs_crab = resolve_attack_action(
        1, 1, fighter, crab, BattlefieldState(distance_ft=5), FixedDiceProvider([12, 4])
    )
    fighter.action_available = True
    vs_other = resolve_attack_action(
        3, 1, fighter, goblin, BattlefieldState(distance_ft=5), FixedDiceProvider([12, 4])
    )

    assert vs_crab[0].attack_roll.mode is RollMode.NORMAL
    assert vs_other[0].attack_roll.mode is RollMode.DISADVANTAGE


def test_escape_grapple_spends_action_and_restores_movement_on_success() -> None:
    crab = build_combatant_state(build_giant_crab(), "crab-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    apply_condition(fighter, ConditionType.GRAPPLED, crab, escape_dc=11)
    begin_turn(fighter)

    events = attempt_escape_grapple(1, 2, fighter, FixedDiceProvider([9]))

    assert [event.event_type for event in events] == ["ability_check", "condition"]
    assert events[0].test_success is True
    assert events[0].test_dc == 11
    assert fighter.action_available is False
    assert fighter.movement_remaining_ft == 30
    assert not has_condition(fighter, ConditionType.GRAPPLED)


def test_escape_grapple_failure_keeps_condition() -> None:
    crab = build_combatant_state(build_giant_crab(), "crab-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    apply_condition(fighter, ConditionType.GRAPPLED, crab, escape_dc=11)
    begin_turn(fighter)

    events = attempt_escape_grapple(1, 2, fighter, FixedDiceProvider([1]))

    assert len(events) == 1
    assert events[0].test_success is False
    assert fighter.action_available is False
    assert fighter.movement_remaining_ft == 0
    assert has_condition(fighter, ConditionType.GRAPPLED)


def test_overlapping_grapples_end_one_source_at_a_time() -> None:
    crab_one = build_combatant_state(build_giant_crab(), "crab-1")
    crab_two = build_combatant_state(build_giant_crab(), "crab-2")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    apply_condition(fighter, ConditionType.GRAPPLED, crab_one, escape_dc=11)
    apply_condition(fighter, ConditionType.GRAPPLED, crab_two, escape_dc=11)
    begin_turn(fighter)

    events = attempt_escape_grapple(1, 2, fighter, FixedDiceProvider([9]))
    grapples = [item for item in fighter.conditions if item.condition is ConditionType.GRAPPLED]

    assert events[0].target_id == "crab-1"
    assert len(grapples) == 1
    assert grapples[0].source_id == "crab-2"
    assert fighter.movement_remaining_ft == 0
    assert has_condition(fighter, ConditionType.GRAPPLED)


def test_unimplemented_condition_still_fails_closed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    with pytest.raises(ValueError, match="not fully implemented"):
        apply_condition(fighter, ConditionType.CHARMED)
