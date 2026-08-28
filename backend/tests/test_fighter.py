from app.combat.dice import FixedDiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter


def test_level_one_fighter_has_required_style_and_three_masteries() -> None:
    fighter = build_demo_fighter()

    assert fighter.fighting_style == "defense"
    assert fighter.armor_class == 19
    assert len(fighter.weapon_masteries) == 3
    assert set(fighter.weapon_masteries) == {"longsword", "javelin", "handaxe"}


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


def test_arena_policy_waits_until_half_hp_or_lower() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.current_hp = 7
    assert should_use_second_wind(fighter) is False

    fighter.current_hp = 6
    assert should_use_second_wind(fighter) is True
