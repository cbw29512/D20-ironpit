from app.combat.attacks import resolve_attack
from app.combat.conditions import apply_condition, has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.recharge import get_recharge_state, roll_recharges
from app.combat.save_actions import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.turn_execution import execute_turn
from app.content.demo import build_demo_fighter
from app.content.srd_spiders import build_giant_spider
from app.domain.models import BattlefieldState, ConditionType, DamageType


def test_giant_spider_matches_srd_combat_stats() -> None:
    spider = build_giant_spider()

    assert spider.challenge_rating == "1"
    assert spider.armor_class == 14
    assert spider.max_hp == 26
    assert spider.speed_ft == 30
    assert spider.initiative_bonus == 3
    assert spider.weapon_attack.attack_bonus == 5
    assert spider.save_actions[0].dc == 13
    assert spider.save_actions[0].range_ft == 60


def test_giant_spider_bite_deals_piercing_and_poison_damage() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")

    event = resolve_attack(
        1,
        1,
        spider,
        fighter,
        spider.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4, 3, 5]),
    )

    assert event.hit is True
    assert event.damage_applied == 15
    assert [component.damage_type for component in event.damage_components] == [
        DamageType.PIERCING,
        DamageType.POISON,
    ]
    assert event.damage_components[0].notation == "1d8+3"
    assert event.damage_components[1].notation == "2d6+0"


def test_giant_spider_web_creates_exact_restrained_object_and_spends_recharge() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    battlefield = BattlefieldState(distance_ft=30)
    web = spider.template.save_actions[0]

    events = resolve_save_action(
        1,
        1,
        spider,
        fighter,
        30,
        web,
        FixedDiceProvider([5]),
        battlefield=battlefield,
    )

    assert [event.event_type for event in events] == [
        "saving_throw",
        "object_created",
        "condition",
    ]
    assert has_condition(fighter, ConditionType.RESTRAINED)
    obj = battlefield.objects[0]
    assert obj.definition.armor_class == 10
    assert obj.definition.max_hp == 5
    assert obj.definition.damage_vulnerabilities == [DamageType.FIRE]
    assert obj.definition.damage_immunities == [DamageType.POISON, DamageType.PSYCHIC]
    recharge = get_recharge_state(spider, web.id)
    assert recharge is not None
    assert recharge.available is False


def test_giant_spider_web_recharges_only_on_five_or_six() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    recharge = get_recharge_state(spider, "giant-spider-web")
    assert recharge is not None
    recharge.available = False

    failed = roll_recharges(1, 2, spider, FixedDiceProvider([4]))
    assert failed[0].test_success is False
    assert recharge.available is False

    restored = roll_recharges(2, 3, spider, FixedDiceProvider([6]))
    assert restored[0].test_success is True
    assert recharge.available is True


def test_spider_turn_closes_then_webs_unrestrained_target() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    battlefield = BattlefieldState(distance_ft=30)

    events, _ = execute_turn(
        1, 1, spider, fighter, battlefield, FixedDiceProvider([5])
    )

    assert [event.event_type for event in events] == [
        "movement", "saving_throw", "object_created", "condition"
    ]
    assert has_condition(fighter, ConditionType.RESTRAINED)
    assert battlefield.distance_ft == 5


def test_spider_rechecks_web_range_after_normal_closing_movement() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    battlefield = BattlefieldState(distance_ft=70)

    events, _ = execute_turn(
        1, 1, spider, fighter, battlefield, FixedDiceProvider([5])
    )

    assert events[0].event_type == "movement"
    assert events[0].distance_before_ft == 70
    assert events[0].distance_after_ft == 40
    assert any(event.feature_id == "giant-spider-web" for event in events)
    assert has_condition(fighter, ConditionType.RESTRAINED)
    assert battlefield.distance_ft == 40


def test_spider_turn_bites_target_already_restrained() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    apply_condition(fighter, ConditionType.RESTRAINED, spider)
    battlefield = BattlefieldState(distance_ft=5)

    events, _ = execute_turn(
        1, 2, spider, fighter, battlefield,
        FixedDiceProvider([5, 15, 4, 3, 5]),
    )

    attack = next(event for event in events if event.event_type == "attack")
    assert attack.weapon_id == "giant-spider-bite"
    assert not any(event.feature_id == "giant-spider-web" for event in events)


def test_spider_turn_cannot_use_web_before_recharge() -> None:
    spider = build_combatant_state(build_giant_spider(), "spider-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    recharge = get_recharge_state(spider, "giant-spider-web")
    assert recharge is not None
    recharge.available = False
    battlefield = BattlefieldState(distance_ft=30)

    events, _ = execute_turn(
        1, 2, spider, fighter, battlefield,
        FixedDiceProvider([4, 15, 4, 3, 5]),
    )

    assert events[0].event_type == "recharge"
    assert events[0].test_success is False
    assert any(event.event_type == "movement" for event in events)
    assert next(event for event in events if event.event_type == "attack").weapon_id == "giant-spider-bite"
    assert not any(event.feature_id == "giant-spider-web" for event in events[1:])
