from app.combat.dice import FixedDiceProvider
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    state = build_combatant_state(build_demo_fighter())
    member = EncounterCombatant(combatant_id="fighter", side="heroes", position_ft=0, state=state)
    setup = EncounterSetup(
        heroes=[member],
        monsters=[],
        hero_total_levels=1,
        monster_total_cr="0",
    )
    return member, setup


def test_second_wind_uses_shared_healing_resolution() -> None:
    fighter, setup = _setup()
    fighter.state.current_hp = 4

    choice = choose_healing_action(fighter, setup, "2:fighter")
    assert choice is not None
    action, target = choice
    assert action.id == "second-wind"
    assert action.action_cost == "bonus_action"
    assert target is fighter

    event = resolve_healing(1, 2, fighter, target, action, FixedDiceProvider([5]), "2:fighter")

    assert event.event_type == "healing"
    assert event.healing_roll is not None
    assert event.healing_roll.total == 6
    assert fighter.state.current_hp == 10
    assert fighter.state.bonus_action_available is False
    assert event.resource_remaining == 1
    assert fighter.state.resources[0].current_uses == 1


def test_second_wind_healing_cannot_exceed_max_hp() -> None:
    fighter, _setup_state = _setup()
    fighter.state.current_hp = 6
    action = next(item for item in fighter.state.template.healing_actions if item.id == "second-wind")

    event = resolve_healing(
        1, 1, fighter, fighter, action, FixedDiceProvider([10]), "1:fighter",
    )

    assert event.healing_roll is not None
    assert event.healing_roll.total == 11
    assert fighter.state.current_hp == fighter.state.template.max_hp == 12


def test_shared_healing_policy_waits_until_half_hp_or_lower() -> None:
    fighter, setup = _setup()
    fighter.state.current_hp = 7
    assert choose_healing_action(fighter, setup, "1:fighter") is None

    fighter.state.current_hp = 6
    choice = choose_healing_action(fighter, setup, "1:fighter")
    assert choice is not None
    assert choice[0].id == "second-wind"
