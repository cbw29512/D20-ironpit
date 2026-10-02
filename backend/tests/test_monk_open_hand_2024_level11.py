from __future__ import annotations

from app.combat.bonus_action_follow_up import resolve_bonus_action_follow_up
from app.combat.state import begin_turn, build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant


def test_2024_open_hand_monk_level11_scales_martial_arts_and_focus() -> None:
    template = build_kael_stillwater_2024(11)
    profile = build_kael_stillwater_2024_profile(11)
    fingerprint = build_kael_2024_combat_profiles(11)[-1]

    assert template.level == profile.level == fingerprint.level == 11
    assert (template.max_hp, template.speed_ft, template.initiative_bonus) == (91, 50, 9)
    assert (fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (91, 50, 9)
    assert template.weapon_attack.weapon.dice_size == 10
    assert template.progression_features.martial_arts_die_size == 10
    assert fingerprint.attacks[0].dice_size == 10
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 11


def test_2024_open_hand_monk_level11_scales_martial_arts_healing_riders() -> None:
    template = build_kael_stillwater_2024(11)

    wholeness = next(item for item in template.healing_actions if item.id == "wholeness-of-body")
    assert wholeness.dice_size == 10

    metabolism = next(
        item for item in template.initiative_resource_refill_grants
        if item.source_id == "uncanny-metabolism"
    )
    assert metabolism.healing_rider is not None
    assert metabolism.healing_rider.dice_count == 1
    assert metabolism.healing_rider.dice_size == 10
    assert metabolism.healing_rider.healing_bonus == 11

    patient = next(
        item for item in template.bonus_tactical_action_grants
        if item.id == "patient-defense-focus"
    )
    assert (patient.temporary_hp_dice_count, patient.temporary_hp_dice_size) == (2, 10)

    flurry = next(item for item in template.bonus_attack_grants if item.id == "flurry-of-blows")
    assert flurry.attack_count == 3


def test_2024_open_hand_monk_level11_fleet_step_is_source_audited_and_registry_ready() -> None:
    profile = build_kael_stillwater_2024_profile(11)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["fleet-step"].combat_relevant is True
    assert audits["fleet-step"].automated is True
    assert "free Dash" in (audits["fleet-step"].notes or "")

    registry = build_certified_hero_registry()
    assert registry[("monk", 11, "canonical")] == ("Kael Stillwater", "kael-stillwater-l11")


def test_2024_open_hand_monk_level11_fleet_step_follows_other_bonus_action() -> None:
    template = build_kael_stillwater_2024(11)
    state = build_combatant_state(template)
    begin_turn(state)
    member = EncounterCombatant(
        combatant_id="kael",
        side="heroes",
        position_ft=0,
        state=state,
    )
    state.bonus_action_available = False
    before = state.movement_remaining_ft

    event = resolve_bonus_action_follow_up(
        1,
        1,
        member,
        "wholeness-of-body",
        "1:kael",
    )

    assert event is not None
    assert event.feature_id == "fleet-step"
    assert event.movement_ft == 50
    assert state.movement_remaining_ft == before + 50
    assert state.dash_uses_this_turn == 1
    assert state.feature_last_turn_keys["fleet-step"] == "1:kael"

    assert resolve_bonus_action_follow_up(
        2,
        1,
        member,
        "martial-arts",
        "1:kael",
    ) is None


def test_2024_open_hand_monk_level11_fleet_step_does_not_chain_from_step_of_wind() -> None:
    template = build_kael_stillwater_2024(11)
    state = build_combatant_state(template)
    begin_turn(state)
    member = EncounterCombatant(
        combatant_id="kael",
        side="heroes",
        position_ft=0,
        state=state,
    )
    state.bonus_action_available = False

    assert resolve_bonus_action_follow_up(
        1,
        1,
        member,
        "step-of-the-wind-dash",
        "1:kael",
    ) is None
