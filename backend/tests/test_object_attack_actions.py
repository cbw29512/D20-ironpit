from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.save_actions import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.turn_execution import execute_turn
from app.content.demo import build_demo_fighter
from app.content.gladiators import build_mara_stone
from app.content.srd_spiders import build_giant_spider
from app.domain.models import BattlefieldState, ConditionType, RollMode


def _web_target(fighter_template):
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(fighter_template, "fighter-1")
    battlefield = BattlefieldState(distance_ft=30)
    resolve_save_action(
        1,
        1,
        spider,
        fighter,
        30,
        spider.template.save_actions[0],
        FixedDiceProvider([5]),
        battlefield=battlefield,
    )
    return spider, fighter, battlefield


def test_restrained_fighter_attacks_and_destroys_linked_web() -> None:
    spider, fighter, battlefield = _web_target(build_demo_fighter())

    events, _ = execute_turn(
        4,
        1,
        fighter,
        spider,
        battlefield,
        FixedDiceProvider([15, 12, 2]),
    )

    object_attack = next(event for event in events if event.event_type == "object_attack")
    assert object_attack.attack_roll is not None
    assert object_attack.attack_roll.mode is RollMode.DISADVANTAGE
    assert object_attack.weapon_id == "longsword"
    assert battlefield.objects[0].is_destroyed is True
    assert not has_condition(fighter, ConditionType.RESTRAINED)
    assert not any(event.event_type == "attack" for event in events)


def test_extra_attack_redirects_to_enemy_after_web_breaks() -> None:
    spider, fighter, battlefield = _web_target(build_mara_stone())
    hp_before = spider.current_hp

    events, _ = execute_turn(
        4,
        1,
        fighter,
        spider,
        battlefield,
        FixedDiceProvider([15, 12, 1, 15, 4]),
    )

    event_types = [event.event_type for event in events]
    creature_attack = next(event for event in events if event.event_type == "attack")
    assert event_types.index("object_destroyed") < event_types.index("attack")
    assert creature_attack.target_id == spider.instance_id
    assert creature_attack.weapon_id == "longsword"
    assert spider.current_hp < hp_before
    assert not has_condition(fighter, ConditionType.RESTRAINED)
