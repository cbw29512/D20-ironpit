from __future__ import annotations

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.source_effect_immunity import has_source_effect_immunity, immunity_effect_id
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition

_CHROMATIC_IDS = (
    "adult-black-dragon", "adult-blue-dragon", "adult-green-dragon",
    "adult-red-dragon", "adult-white-dragon",
    "ancient-black-dragon", "ancient-blue-dragon", "ancient-green-dragon",
    "ancient-red-dragon", "ancient-white-dragon",
)


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    try:
        state = build_combatant_state(template.model_copy(deep=True))
        state.position = GridPosition(x=x, y=0)
        state.current_round = 1
        return EncounterCombatant(
            combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        raise


def _dragon(monster_id: str = "adult-black-dragon"):
    try:
        source = next(item for item in load_monster_source_2014() if item.id == monster_id)
        return compile_combatant(adapt_basic_monster_2014(source))
    except Exception:
        raise


def _presence_setup(monster_id: str = "adult-black-dragon"):
    try:
        dragon = _member(_dragon(monster_id), f"monster:{monster_id}", "monsters", 2)
        hero = _member(build_karnok_stoneward(), "hero:karnok", "heroes", 4)
        setup = EncounterSetup(
            heroes=[hero], monsters=[dragon], hero_total_levels=1, monster_total_cr="17",
            ruleset="2014",
            map_definition=BattleMapDefinition(id="frightful-presence", width_squares=24, height_squares=24),
        )
        action = next(item for item in dragon.state.template.saving_throw_actions if item.id == "frightful-presence")
        return dragon, hero, setup, action
    except Exception:
        raise


def test_chromatic_adult_ancient_dragons_are_single_family_unlocked() -> None:
    source = {item.id: item for item in load_monster_source_2014()}
    for monster_id in _CHROMATIC_IDS:
        assert basic_blockers_2014(source[monster_id]) == ()
    roster_ids = {item.id for item in build_basic_2014_monsters()}
    assert {f"2014-{item}" for item in _CHROMATIC_IDS} <= roster_ids
    assert len(roster_ids) == 201


def test_frightful_presence_binds_failed_save_frightened_and_match_immunity() -> None:
    action = next(item for item in _dragon().saving_throw_actions if item.id == "frightful-presence")
    rider = action.failed_save_timed_effect
    assert action.name == "Frightful Presence"
    assert action.save_ability == "wisdom"
    assert action.dc == 16
    assert action.source_effect_immunity_on_success is True
    assert rider is not None
    assert rider.effect_id == "frightened"
    assert rider.duration_rounds == 10
    assert rider.repeat_save_ability == "wisdom"
    assert rider.repeat_save_dc == 16
    assert rider.repeat_save_timing == "target_turn_end"
    assert rider.source_effect_immunity_on_end is True
    assert "frightened" in action.effect_tags


def test_failed_save_applies_frightened_and_prints_ability_name() -> None:
    dragon, hero, _setup, action = _presence_setup()
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["frightened"]
    assert "frightened" in hero.state.active_effect_ids
    assert "Frightful Presence" in event.description
    assert event.feature_id == "frightful-presence"


def test_successful_save_grants_match_scoped_source_immunity() -> None:
    dragon, hero, _setup, action = _presence_setup()
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([20]))
    assert event.save_succeeded is True
    assert "frightened" not in hero.state.active_effect_ids
    assert "Frightful Presence" in event.description
    assert has_source_effect_immunity(hero.state, action.id, dragon.combatant_id)
    immunity = next(
        item for item in hero.state.timed_effects
        if item.effect_id == immunity_effect_id(action.id, dragon.combatant_id)
    )
    assert immunity.expires_round is None
    assert immunity.expires_at_start_of_source_turn is False
    assert legal_save_action(action, hero, 10, source_id=dragon.combatant_id) is False
    other = _member(_dragon(), "monster:other-dragon", "monsters", 6)
    assert legal_save_action(action, hero, 10, source_id=other.combatant_id) is True


def test_repeat_save_success_ends_frightened_and_grants_match_immunity() -> None:
    dragon, hero, _setup, action = _presence_setup()
    resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert "frightened" in hero.state.active_effect_ids
    events, _ = resolve_target_condition_timing(2, 1, hero, "target_turn_end", FixedDiceProvider([20]))
    assert events[0].save_succeeded is True
    assert "frightened" not in hero.state.active_effect_ids
    assert has_source_effect_immunity(hero.state, action.id, dragon.combatant_id)
    immunity = next(
        item for item in hero.state.timed_effects
        if item.effect_id == immunity_effect_id(action.id, dragon.combatant_id)
    )
    assert immunity.expires_round is None
    assert legal_save_action(action, hero, 10, source_id=dragon.combatant_id) is False