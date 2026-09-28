from __future__ import annotations

import pytest

from app.combat.area_save_actions import choose_area_save
from app.combat.bonus_save_actions import resolve_bonus_save_action
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_turn_support import save_choice
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_berserker_endgame_profile import build_rokhan_stonefury_level14_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.save_effects import FailedSaveTimedEffect


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    try:
        state = build_combatant_state(template.model_copy(deep=True))
        state.position = GridPosition(x=x, y=0)
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=x * 5,
            state=state,
        )
    except Exception:
        raise


def _resource(member: EncounterCombatant, resource_id: str):
    try:
        return next(item for item in member.state.resources if item.id == resource_id)
    except StopIteration as exc:
        raise AssertionError(f"Missing resource {resource_id}.") from exc


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterCombatant, EncounterSetup]:
    try:
        hero = _member(build_rokhan_stonefury_level(14), "hero:rokhan-l14", "heroes", 1)
        enemy_a = _member(build_karnok_stoneward(), "monster:a", "monsters", 2)
        enemy_b = _member(build_karnok_stoneward(), "monster:b", "monsters", 5)
        setup = EncounterSetup(
            heroes=[hero],
            monsters=[enemy_a, enemy_b],
            hero_total_levels=14,
            monster_total_cr="0",
            ruleset="2024",
            map_definition=BattleMapDefinition(
                id="barbarian14-intimidating-presence",
                width_squares=12,
                height_squares=8,
            ),
        )
        return hero, enemy_a, enemy_b, setup
    except Exception:
        raise


def test_level14_profile_binds_intimidating_presence_to_universal_primitives() -> None:
    profile = build_rokhan_stonefury_level14_profile()
    template = build_rokhan_stonefury_level(14)
    action = next(item for item in template.saving_throw_actions if item.id == "intimidating-presence")
    conversion = next(
        item for item in template.resource_conversion_actions
        if item.id == "restore-intimidating-presence"
    )
    resource = next(item for item in template.resources if item.id == "intimidating-presence")

    assert profile.level == 14
    assert action.name == "Intimidating Presence"
    assert action.action_cost == "bonus_action"
    assert action.save_ability == "wisdom"
    assert action.dc == 18
    assert action.area is not None
    assert action.area.shape == "emanation"
    assert action.area.origin == "self"
    assert action.area.radius_ft == 30
    assert action.resource_id == "intimidating-presence"
    assert action.failed_save_timed_effect is not None
    assert action.failed_save_timed_effect.effect_id == "frightened"
    assert action.failed_save_timed_effect.duration_rounds == 10
    assert action.failed_save_timed_effect.repeat_save_ability == "wisdom"
    assert action.failed_save_timed_effect.repeat_save_dc == 18
    assert action.failed_save_timed_effect.repeat_save_timing == "target_turn_end"
    assert resource.max_uses == 1
    assert conversion.action_cost == "none"
    assert conversion.source_resource_id == "rage"
    assert conversion.source_cost == 1
    assert conversion.target_resource_id == "intimidating-presence"
    assert conversion.target_gain == 1
    assert ("barbarian", 14, "canonical") in build_certified_hero_registry()


def test_bonus_action_presence_frightens_targets_and_preserves_normal_action() -> None:
    hero, enemy_a, enemy_b, setup = _setup()

    events, sequence = resolve_bonus_save_action(
        1,
        1,
        hero,
        setup,
        FixedDiceProvider([1, 1]),
    )

    assert sequence == 3
    assert len(events) == 2
    assert all(event.feature_id == "intimidating-presence" for event in events)
    assert all(event.applied_condition_ids == ["frightened"] for event in events)
    assert hero.state.bonus_action_available is False
    assert hero.state.action_available is True
    assert _resource(hero, "intimidating-presence").current_uses == 0
    for enemy in (enemy_a, enemy_b):
        assert "frightened" in enemy.state.active_effect_ids
        effect = next(
            item for item in enemy.state.timed_effects
            if item.source_effect_id == "intimidating-presence"
        )
        assert effect.expires_round == 11
        assert effect.expiry_timing == "source_turn_start"
        assert effect.repeat_save_ability == "wisdom"
        assert effect.repeat_save_dc == 18
        assert effect.repeat_save_timing == "target_turn_end"

    repeat_events, _ = resolve_target_condition_timing(
        10,
        1,
        enemy_a,
        "target_turn_end",
        FixedDiceProvider([20]),
    )
    assert repeat_events[0].save_succeeded is True
    assert repeat_events[0].removed_condition_ids == ["frightened"]
    assert "frightened" not in enemy_a.state.active_effect_ids


def test_depleted_presence_spends_rage_to_restore_only_when_legal_target_exists() -> None:
    hero, enemy_a, enemy_b, setup = _setup()
    presence = _resource(hero, "intimidating-presence")
    rage = _resource(hero, "rage")
    presence.current_uses = 0
    rage.current_uses = 2

    events, _ = resolve_bonus_save_action(
        1,
        1,
        hero,
        setup,
        FixedDiceProvider([20, 20]),
    )

    assert events[0].feature_id == "restore-intimidating-presence"
    assert rage.current_uses == 1
    assert presence.current_uses == 0
    assert hero.state.action_available is True
    assert hero.state.bonus_action_available is False
    assert all("frightened" not in enemy.state.active_effect_ids for enemy in (enemy_a, enemy_b))

    no_target_hero = _member(build_rokhan_stonefury_level(14), "hero:no-target", "heroes", 1)
    no_target_presence = _resource(no_target_hero, "intimidating-presence")
    no_target_rage = _resource(no_target_hero, "rage")
    no_target_presence.current_uses = 0
    no_target_rage.current_uses = 2
    empty_setup = EncounterSetup(
        heroes=[no_target_hero],
        monsters=[],
        hero_total_levels=14,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=setup.map_definition,
    )
    no_events, _ = resolve_bonus_save_action(
        1,
        1,
        no_target_hero,
        empty_setup,
        FixedDiceProvider([]),
    )
    assert no_events == []
    assert no_target_rage.current_uses == 2
    assert no_target_presence.current_uses == 0


def test_bonus_action_save_is_not_rediscovered_as_main_action() -> None:
    hero, _, _, setup = _setup()

    assert choose_area_save(hero, setup) is None
    assert save_choice(hero, setup) is None


def test_repeat_save_rider_requires_complete_repeat_metadata() -> None:
    with pytest.raises(ValueError, match="ability, DC, and timing"):
        FailedSaveTimedEffect(
            effect_id="frightened",
            repeat_save_ability="wisdom",
        )
