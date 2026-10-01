from __future__ import annotations

from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.dice import FixedDiceProvider
from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.state import build_combatant_state
from app.combat.tactical_actions import resolve_bonus_tactical_grant, use_offensive_dash
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _resource(member: EncounterCombatant, resource_id: str):
    return next(item for item in member.state.resources if item.id == resource_id)


def test_2024_monk_level_two_profile_and_runtime_match_raw_delta() -> None:
    profile = build_kael_stillwater_2024_profile(2)
    monk = build_kael_stillwater_2024(2)

    assert profile.level == monk.level == 2
    assert {"monks-focus", "unarmored-movement", "uncanny-metabolism"}.issubset(
        {item.feature_id for item in profile.feature_audits}
    )
    assert monk.max_hp == 17
    assert monk.speed_ft == 40
    assert {item.id: item.max_uses for item in monk.resources} == {
        "focus": 2,
        "uncanny-metabolism": 1,
    }
    grants = {item.id: item for item in monk.bonus_attack_grants}
    assert grants["flurry-of-blows"].attack_count == 2
    assert grants["flurry-of-blows"].resource_id == "focus"
    assert grants["flurry-of-blows"].resource_cost == 1
    tactics = {item.id: item for item in monk.bonus_tactical_action_grants}
    assert tactics["step-of-the-wind-dash"].effects == ["dash"]
    assert tactics["step-of-the-wind-dash"].resource_id is None
    assert tactics["patient-defense-focus"].effects == ["disengage", "dodge"]
    assert tactics["patient-defense-focus"].resource_id == "focus"
    assert tactics["step-of-the-wind-focus"].jump_distance_multiplier == 2
    refill = monk.initiative_resource_refill_grants[0]
    assert refill.source_id == "uncanny-metabolism"
    assert refill.resource_id == "focus"
    assert refill.restore_to_max is True
    assert refill.usage_resource_id == "uncanny-metabolism"
    assert refill.healing_rider is not None
    assert (refill.healing_rider.dice_count, refill.healing_rider.dice_size, refill.healing_rider.healing_bonus) == (1, 6, 2)


def test_flurry_of_blows_reuses_bonus_attack_grant_and_spends_one_focus() -> None:
    monk = _member(build_kael_stillwater_2024(2), "monk", "heroes", 0)
    target_template = build_karnok_stoneward_level(2).model_copy(update={"armor_class": 1, "max_hp": 100})
    target = _member(target_template, "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[monk], monsters=[target], hero_total_levels=2, monster_total_cr="2", ruleset="2024",
    )

    events, sequence = resolve_bonus_attack_grant(
        1, 1, monk, setup, FixedDiceProvider([10, 4, 10, 4]), "1:monk",
    )

    assert sequence == 3
    assert [event.feature_id for event in events] == ["flurry-of-blows", "flurry-of-blows"]
    assert monk.state.bonus_action_available is False
    assert monk.state.action_available is True
    assert _resource(monk, "focus").current_uses == 1


def test_step_of_the_wind_free_dash_uses_universal_tactical_action() -> None:
    monk = _member(build_kael_stillwater_2024(2), "monk", "heroes", 0)
    target = _member(build_karnok_stoneward_level(2), "target", "monsters", 70)
    setup = EncounterSetup(
        heroes=[monk], monsters=[target], hero_total_levels=2, monster_total_cr="2", ruleset="2024",
    )
    monk.state.movement_remaining_ft = 40

    event = use_offensive_dash(1, 1, monk, setup, "1:monk")

    assert event is not None
    assert event.feature_id == "step-of-the-wind-dash"
    assert event.movement_ft == 40
    assert monk.state.movement_remaining_ft == 80
    assert monk.state.bonus_action_available is False
    assert _resource(monk, "focus").current_uses == 2


def test_patient_defense_composes_disengage_and_dodge_without_named_resolver() -> None:
    monk = _member(build_kael_stillwater_2024(2), "monk", "heroes", 0)
    grant = next(
        item for item in monk.state.template.bonus_tactical_action_grants
        if item.id == "patient-defense-focus"
    )

    event = resolve_bonus_tactical_grant(1, 1, monk, grant)

    assert event.feature_id == "patient-defense-focus"
    assert monk.state.disengaged_this_turn is True
    assert "dodge" in monk.state.active_effect_ids
    assert monk.state.bonus_action_available is False
    assert _resource(monk, "focus").current_uses == 1


def test_uncanny_metabolism_refills_focus_heals_and_consumes_long_rest_use() -> None:
    monk = _member(build_kael_stillwater_2024(2), "monk", "heroes", 0)
    target = _member(build_karnok_stoneward_level(2), "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[monk], monsters=[target], hero_total_levels=2, monster_total_cr="2", ruleset="2024",
    )
    _resource(monk, "focus").current_uses = 0
    monk.state.current_hp = 8

    events, sequence = resolve_initiative_resource_refills(1, setup, FixedDiceProvider([4]))

    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "uncanny-metabolism"
    assert events[0].healing_roll is not None
    assert events[0].healing_roll.total == 6
    assert monk.state.current_hp == 14
    assert _resource(monk, "focus").current_uses == 2
    assert _resource(monk, "uncanny-metabolism").current_uses == 0

    again, next_sequence = resolve_initiative_resource_refills(sequence, setup, FixedDiceProvider([6]))
    assert again == []
    assert next_sequence == sequence
    assert monk.state.current_hp == 14
