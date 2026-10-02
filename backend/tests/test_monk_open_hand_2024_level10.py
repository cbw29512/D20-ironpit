from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.combat.tactical_actions import resolve_defensive_tactical_grant
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant


def test_2024_open_hand_monk_level10_heightened_focus_and_progression() -> None:
    template = build_kael_stillwater_2024(10)
    profile = build_kael_stillwater_2024_profile(10)
    fingerprint = build_kael_2024_combat_profiles(10)[-1]

    assert template.level == profile.level == fingerprint.level == 10
    assert (template.max_hp, template.speed_ft, template.initiative_bonus) == (83, 50, 9)
    assert (fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (83, 50, 9)
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 10

    flurry = next(item for item in template.bonus_attack_grants if item.id == "flurry-of-blows")
    assert flurry.attack_count == 3

    patient = next(
        item for item in template.bonus_tactical_action_grants
        if item.id == "patient-defense-focus"
    )
    assert (patient.temporary_hp_dice_count, patient.temporary_hp_dice_size) == (2, 8)


def test_heightened_focus_patient_defense_grants_rolled_temporary_hp() -> None:
    template = build_kael_stillwater_2024(10)
    state = build_combatant_state(template)
    begin_turn(state)
    member = EncounterCombatant(
        combatant_id="kael",
        side="heroes",
        position_ft=0,
        state=state,
    )

    event = resolve_defensive_tactical_grant(
        1,
        1,
        member,
        FixedDiceProvider([4, 5]),
    )

    assert event is not None
    assert event.feature_id == "patient-defense-focus"
    assert event.temporary_hp_before == 0
    assert event.temporary_hp_after == 9
    assert state.temporary_hp == 9
    assert next(item for item in state.resources if item.id == "focus-points").current_uses == 9


def test_level10_self_restoration_remains_explicitly_uncertified_pending_policy() -> None:
    profile = build_kael_stillwater_2024_profile(10)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["heightened-focus"].automated is True
    assert audits["self-restoration"].automated is False
