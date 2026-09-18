from app.combat.dice import SeededDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import build_combatant_state
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.demo import build_goblin_warrior
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _encounter(template, level: int):
    hero = EncounterCombatant(
        combatant_id="hero-1",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(template),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[hero],
        monsters=[enemy],
        hero_total_levels=level,
        monster_total_cr="1/4",
    )
    return hero, enemy, setup


def test_python_turn_keeps_rage_ahead_of_adrenaline_rush() -> None:
    hero, enemy, setup = _encounter(build_rokhan_stonefury_level(6), 6)

    events, _ = resolve_combat_turn(
        1, 1, hero, enemy, setup, SeededDiceProvider(7),
    )

    features = [event.feature_id for event in events if event.feature_id]
    assert "rage" in features
    assert "adrenaline-rush" not in features
    assert hero.state.bonus_action_available is False


def test_python_turn_keeps_second_wind_ahead_of_adrenaline_rush_when_bloodied() -> None:
    hero, enemy, setup = _encounter(build_karnok_stoneward_level(4), 4)
    hero.state.current_hp = hero.state.template.max_hp // 2

    events, _ = resolve_combat_turn(
        1, 1, hero, enemy, setup, SeededDiceProvider(11),
    )

    features = [event.feature_id for event in events if event.feature_id]
    assert "second-wind" in features
    assert "adrenaline-rush" not in features
    assert hero.state.bonus_action_available is False
