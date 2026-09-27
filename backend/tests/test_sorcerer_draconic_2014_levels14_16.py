from __future__ import annotations

from app.combat.effective_movement_modes import effective_movement_modes
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant


def _member(level: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=f"nyra-{level}",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_nyra_emberveil_2014(level)),
    )


def test_level_fourteen_dragon_wings_requires_activation_and_uses_universal_movement_grant() -> None:
    hero = build_nyra_emberveil_2014(14)
    member = _member(14)

    assert hero.movement_modes.walk_ft == 30
    assert hero.movement_modes.fly_ft == 0
    action = next(item for item in hero.timed_self_buff_actions if item.id == "dragon-wings")
    assert action.action_cost == "bonus_action"
    assert action.duration_rounds is None
    assert action.movement_mode_grants[0].mode == "fly"
    assert action.movement_mode_grants[0].match_current_speed is True

    assert effective_movement_modes(member.state).fly_ft == 0
    begin_turn(member.state)
    event = resolve_timed_self_buff(1, 1, member, action)
    assert event.feature_id == "dragon-wings"
    assert member.state.bonus_action_available is False
    assert effective_movement_modes(member.state).fly_ft == 30
    effect = next(item for item in member.state.timed_effects if item.source_effect_id == "dragon-wings")
    assert effect.expires_round is None
    assert effect.expiry_timing is None


def test_level_fifteen_keeps_dragon_wings_and_progression_resources() -> None:
    hero = build_nyra_emberveil_2014(15)

    assert hero.movement_modes.fly_ft == 0
    assert {item.id: item.max_uses for item in hero.resources}["sorcery-points"] == 15
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-8"] == 1
    assert any(item.id == "dragon-wings" for item in hero.timed_self_buff_actions)


def test_level_sixteen_constitution_asi_updates_hp_and_save() -> None:
    before = build_nyra_emberveil_2014(15)
    hero = build_nyra_emberveil_2014(16)
    profile = build_nyra_emberveil_2014_profile(16)

    assert profile.final_ability_scores.constitution == 16
    assert hero.max_hp > before.max_hp
    assert hero.saving_throw_bonuses["constitution"] == 8
    assert hero.movement_modes.fly_ft == 0
    assert any(item.id == "dragon-wings" for item in hero.timed_self_buff_actions)
