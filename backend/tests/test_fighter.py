from app.combat.dice import FixedDiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.gladiators import build_mara_stone


def test_second_wind_heals_and_spends_one_bonus_action_use() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.current_hp = 4

    event = use_second_wind(1, 2, fighter, FixedDiceProvider([5]))

    assert event.event_type == "healing"
    assert event.healing_roll is not None
    assert event.healing_roll.total == 6
    assert fighter.current_hp == 10
    assert fighter.bonus_action_available is False
    assert event.resource_remaining == 1
    assert fighter.resources[0].current_uses == 1


def test_second_wind_healing_cannot_exceed_max_hp() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.current_hp = 10

    event = use_second_wind(1, 1, fighter, FixedDiceProvider([10]))

    assert event.healing_roll is not None
    assert event.healing_roll.total == 11
    assert fighter.current_hp == fighter.template.max_hp == 12


def test_level_five_second_wind_scales_healing_and_uses() -> None:
    fighter = build_combatant_state(build_mara_stone())
    fighter.current_hp = 20

    event = use_second_wind(4, 3, fighter, FixedDiceProvider([7]))

    assert event.healing_roll is not None
    assert event.healing_roll.notation == "1d10+5"
    assert event.healing_roll.total == 12
    assert fighter.current_hp == 32
    assert event.resource_remaining == 2
    assert fighter.resources[0].max_uses == 3


def test_arena_policy_waits_until_half_hp_or_lower() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.current_hp = 7
    assert should_use_second_wind(fighter) is False

    fighter.current_hp = 6
    assert should_use_second_wind(fighter) is True
