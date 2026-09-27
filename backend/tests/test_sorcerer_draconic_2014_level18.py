from __future__ import annotations

from app.combat.state import begin_turn
from app.combat.concentration import end_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.combat.state import build_combatant_state


def _member(combatant_id: str, level: int, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(build_nyra_emberveil_2014(level)),
    )


def _setup() -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    source = _member("nyra-18", 18, "heroes", 0)
    target = _member("enemy", 1, "monsters", 30)
    return EncounterSetup(heroes=[source], monsters=[target], hero_total_levels=18, monster_total_cr="0", ruleset="2014"), source, target


def test_level_eighteen_draconic_presence_is_resource_backed_concentration_aura() -> None:
    hero = build_nyra_emberveil_2014(18)
    assert len(hero.timed_self_buff_actions) == 1
    action = hero.timed_self_buff_actions[0]

    assert action.id == "draconic-presence-fear"
    assert action.resource_id == "sorcery-points"
    assert action.resource_cost == 5
    assert action.duration_rounds == 10
    assert action.concentration is True
    aura = action.hostile_start_turn_condition_aura
    assert aura is not None
    assert aura.radius_ft == 60
    assert aura.save_ability == "wisdom"
    assert aura.save_dc == 19
    assert aura.condition_id == "frightened"
    assert aura.success_immunity_rounds == 14400


def test_draconic_presence_failure_applies_frightened_until_concentration_ends() -> None:
    setup, source, target = _setup()
    begin_turn(source.state)
    action = source.state.template.timed_self_buff_actions[0]
    before = next(item.current_uses for item in source.state.resources if item.id == "sorcery-points")

    event = resolve_timed_self_buff(
        1, 1, source, action,
        affected_states=[source.state, target.state],
    )
    assert event.concentration_started_effect_id == action.id
    assert source.state.concentration is not None
    after = next(item.current_uses for item in source.state.resources if item.id == "sorcery-points")
    assert after == before - 5

    events, _ = resolve_target_turn_start_emanations(
        2, 1, target, setup, FixedDiceProvider([1]),
    )
    assert len(events) == 1
    assert events[0].save_succeeded is False
    assert "frightened" in target.state.active_effect_ids

    assert end_concentration(source.state, [source.state, target.state]) is True
    assert "frightened" not in target.state.active_effect_ids


def test_draconic_presence_success_grants_source_specific_24_hour_immunity() -> None:
    setup, source, target = _setup()
    begin_turn(source.state)
    action = source.state.template.timed_self_buff_actions[0]
    resolve_timed_self_buff(
        1, 1, source, action,
        affected_states=[source.state, target.state],
    )

    events, next_sequence = resolve_target_turn_start_emanations(
        2, 1, target, setup, FixedDiceProvider([20]),
    )
    assert len(events) == 1
    assert events[0].save_succeeded is True
    immunity_id = f"{action.id}:success-immunity:{source.combatant_id}"
    immunity = next(effect for effect in target.state.timed_effects if effect.effect_id == immunity_id)
    assert immunity.expires_round == 14401

    repeated, sequence = resolve_target_turn_start_emanations(
        next_sequence, 2, target, setup, FixedDiceProvider([1]),
    )
    assert repeated == []
    assert sequence == next_sequence
