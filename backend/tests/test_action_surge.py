import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.fighter import use_action_surge
from app.combat.state import begin_turn, build_combatant_state
from app.combat.turn_execution import execute_turn
from app.content.gladiators import build_mara_stone, build_vera_ash
from app.content.srd_monsters import build_ogre
from app.domain.models import BattlefieldState


def test_action_surge_restores_action_and_spends_resource() -> None:
    fighter = build_combatant_state(build_mara_stone())
    fighter.action_available = False

    event = use_action_surge(3, 1, fighter)
    resource = next(item for item in fighter.resources if item.id == "action-surge")

    assert event.event_type == "feature"
    assert event.feature_id == "action-surge"
    assert fighter.action_available is True
    assert fighter.action_surge_used_this_turn is True
    assert resource.current_uses == 0


def test_level_twenty_action_surge_is_limited_to_once_per_turn() -> None:
    fighter = build_combatant_state(build_vera_ash())
    resource = next(item for item in fighter.resources if item.id == "action-surge")

    fighter.action_available = False
    use_action_surge(1, 1, fighter)
    fighter.action_available = False
    with pytest.raises(RuntimeError, match="Action Surge could not be resolved"):
        use_action_surge(2, 1, fighter)

    begin_turn(fighter)
    fighter.action_available = False
    use_action_surge(3, 2, fighter)
    assert resource.current_uses == 0


def test_arena_turn_uses_action_surge_for_second_attack_action() -> None:
    fighter = build_combatant_state(build_mara_stone())
    ogre = build_combatant_state(build_ogre())
    battlefield = BattlefieldState(starting_distance_ft=5, distance_ft=5)

    events, sequence = execute_turn(
        1,
        1,
        fighter,
        ogre,
        battlefield,
        FixedDiceProvider([4, 1, 4, 1, 4, 1, 4, 1]),
        fighter_features=True,
    )

    assert [event.event_type for event in events] == [
        "attack", "attack", "feature", "attack", "attack"
    ]
    assert events[2].feature_id == "action-surge"
    assert sequence == 6
    assert ogre.current_hp == 48
