from app.combat.battlefield_objects import damage_battlefield_object
from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.save_actions import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    Ability,
    BattlefieldObjectDefinition,
    BattlefieldState,
    ConditionType,
    DamageType,
    RollMode,
    SaveAction,
    SaveFailureEffect,
)


def _web_definition() -> BattlefieldObjectDefinition:
    return BattlefieldObjectDefinition(
        id="test-web",
        name="Test Web",
        armor_class=10,
        max_hp=5,
        damage_vulnerabilities=[DamageType.FIRE],
        damage_immunities=[DamageType.POISON, DamageType.PSYCHIC],
    )


def _web_actor():
    action = SaveAction(
        id="test-web-action",
        name="Test Web Action",
        save_ability=Ability.DEXTERITY,
        dc=13,
        range_ft=60,
        failure_effects=[SaveFailureEffect(
            condition=ConditionType.RESTRAINED,
            object_definition=_web_definition(),
        )],
    )
    template = build_demo_fighter().model_copy(update={"save_actions": [action]})
    return build_combatant_state(template, "webber-1")


def test_failed_save_creates_object_linked_restrained_source() -> None:
    actor = _web_actor()
    target = build_combatant_state(build_goblin_warrior(), "target-1")
    battlefield = BattlefieldState(distance_ft=30)

    events = resolve_save_action(
        1, 1, actor, target, 30, actor.template.save_actions[0],
        FixedDiceProvider([5]), battlefield=battlefield,
    )

    assert [event.event_type for event in events] == [
        "saving_throw", "object_created", "condition"
    ]
    assert len(battlefield.objects) == 1
    obj = battlefield.objects[0]
    restrained = next(item for item in target.conditions if item.condition is ConditionType.RESTRAINED)
    assert restrained.linked_object_id == obj.instance_id
    assert obj.target_id == target.instance_id
    assert obj.current_hp == 5


def test_object_damage_obeys_immunity_vulnerability_and_ends_condition() -> None:
    actor = _web_actor()
    target = build_combatant_state(build_goblin_warrior(), "target-1")
    battlefield = BattlefieldState(distance_ft=30)
    resolve_save_action(
        1, 1, actor, target, 30, actor.template.save_actions[0],
        FixedDiceProvider([5]), battlefield=battlefield,
    )
    object_id = battlefield.objects[0].instance_id

    poison_events = damage_battlefield_object(
        4, 1, target, battlefield, object_id, DamageType.POISON, 10, [actor, target]
    )
    assert poison_events[0].damage_applied == 0
    assert battlefield.objects[0].current_hp == 5
    assert has_condition(target, ConditionType.RESTRAINED)

    fire_events = damage_battlefield_object(
        5, 1, target, battlefield, object_id, DamageType.FIRE, 3, [actor, target]
    )
    assert fire_events[0].damage_applied == 6
    assert [event.event_type for event in fire_events] == [
        "object_damage", "object_destroyed", "condition"
    ]
    assert battlefield.objects[0].is_destroyed is True
    assert not has_condition(target, ConditionType.RESTRAINED)


def test_destroying_one_of_two_objects_keeps_other_condition_source() -> None:
    actor = _web_actor()
    target = build_combatant_state(build_goblin_warrior(), "target-1")
    battlefield = BattlefieldState(distance_ft=30)
    action = actor.template.save_actions[0]

    resolve_save_action(
        1, 1, actor, target, 30, action,
        FixedDiceProvider([5]), battlefield=battlefield,
    )
    actor.action_available = True
    second_web_events = resolve_save_action(
        4, 2, actor, target, 30, action,
        FixedDiceProvider([5, 5]), battlefield=battlefield,
    )
    assert second_web_events[0].saving_throw is not None
    assert second_web_events[0].saving_throw.mode is RollMode.DISADVANTAGE
    assert len([item for item in target.conditions if item.condition is ConditionType.RESTRAINED]) == 2

    first, second = battlefield.objects
    first_events = damage_battlefield_object(
        7, 2, target, battlefield, first.instance_id, DamageType.SLASHING, 5, [actor, target]
    )
    assert first_events[-1].condition_active is True
    assert has_condition(target, ConditionType.RESTRAINED)

    second_events = damage_battlefield_object(
        10, 2, target, battlefield, second.instance_id, DamageType.SLASHING, 5, [actor, target]
    )
    assert second_events[-1].condition_active is False
    assert not has_condition(target, ConditionType.RESTRAINED)
