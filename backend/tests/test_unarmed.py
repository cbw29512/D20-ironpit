import pytest

from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.unarmed import resolve_unarmed_grapple, resolve_unarmed_shove
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_monsters import build_ogre
from app.domain.models import Ability, BattlefieldState, ConditionType


def _free_hand_fighter():
    template = build_demo_fighter().model_copy(update={"free_hands": 1})
    return build_combatant_state(template, "fighter-1")


def test_unarmed_grapple_uses_target_choice_and_exact_dc() -> None:
    fighter = _free_hand_fighter()
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    events = resolve_unarmed_grapple(
        1, 1, fighter, goblin, 5, FixedDiceProvider([10])
    )

    assert [event.event_type for event in events] == ["saving_throw", "condition"]
    assert events[0].test_ability is Ability.DEXTERITY
    assert events[0].test_dc == 13
    assert events[0].saving_throw.modifier == 2
    assert events[0].test_success is False
    grapple = next(item for item in goblin.conditions if item.condition is ConditionType.GRAPPLED)
    assert grapple.source_id == "fighter-1"
    assert grapple.escape_dc == 13


def test_unarmed_grapple_success_does_not_apply_condition() -> None:
    fighter = _free_hand_fighter()
    goblin = build_combatant_state(build_goblin_warrior())

    events = resolve_unarmed_grapple(
        1, 1, fighter, goblin, 5, FixedDiceProvider([11])
    )

    assert len(events) == 1
    assert events[0].test_success is True
    assert not has_condition(goblin, ConditionType.GRAPPLED)


def test_unarmed_grapple_requires_free_hand() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    with pytest.raises(ValueError, match="free hand"):
        resolve_unarmed_grapple(1, 1, fighter, goblin, 5, FixedDiceProvider([1]))


def test_unarmed_shove_can_knock_target_prone() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    events = resolve_unarmed_shove(
        1, 1, fighter, goblin, BattlefieldState(distance_ft=5), FixedDiceProvider([5])
    )

    assert [event.event_type for event in events] == ["saving_throw", "condition"]
    assert events[0].test_dc == 13
    assert events[0].test_success is False
    assert has_condition(goblin, ConditionType.PRONE)


def test_unarmed_shove_can_push_target_five_feet() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_unarmed_shove(
        1, 1, fighter, goblin, battlefield, FixedDiceProvider([5]), outcome="push"
    )

    assert events[1].event_type == "forced_movement"
    assert events[1].movement_ft == 5
    assert battlefield.distance_ft == 10


def test_unarmed_control_rejects_target_more_than_one_size_larger() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    ogre = build_combatant_state(build_ogre())

    with pytest.raises(ValueError, match="too large"):
        resolve_unarmed_shove(
            1, 1, goblin, ogre, BattlefieldState(distance_ft=5), FixedDiceProvider([1])
        )
