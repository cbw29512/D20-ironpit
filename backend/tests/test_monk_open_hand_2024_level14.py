from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024


def test_2024_open_hand_monk_level14_advances_speed_focus_hp_and_all_saves() -> None:
    level13 = build_kael_stillwater_2024(13)
    template = build_kael_stillwater_2024(14)
    profile = build_kael_stillwater_2024_profile(14)
    fingerprint = build_kael_2024_combat_profiles(14)[-1]

    assert template.level == profile.level == fingerprint.level == 14
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (16, 115, 55, 10)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (16, 115, 55, 10)
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 14
    assert fingerprint.save_proficiencies == (
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    )
    assert level13.saving_throw_bonuses["constitution"] == 3
    assert template.saving_throw_bonuses == {
        "strength": 6,
        "dexterity": 10,
        "constitution": 8,
        "intelligence": 5,
        "wisdom": 6,
        "charisma": 5,
    }


def test_2024_disciplined_survivor_reuses_failed_save_reroll_with_focus() -> None:
    template = build_kael_stillwater_2024(14)
    grants = template.progression_features.saving_throw_proficiency_grants
    rerolls = template.progression_features.failed_save_reroll_grants

    assert len(grants) == 1
    assert grants[0].source_id == "disciplined-survivor"
    assert grants[0].abilities == ["constitution", "intelligence", "wisdom", "charisma"]
    assert len(rerolls) == 1
    assert rerolls[0].source_id == "disciplined-survivor"
    assert rerolls[0].source_name == "Disciplined Survivor"
    assert (rerolls[0].resource_id, rerolls[0].resource_cost) == ("focus-points", 1)

    state = build_combatant_state(template)
    roll, succeeded = resolve_saving_throw(
        state,
        "constitution",
        20,
        FixedDiceProvider([1, 20]),
    )
    assert succeeded is True
    assert roll is not None
    assert roll.total == 28
    assert roll.revisions[-1].source_effect_id == "disciplined-survivor"
    assert roll.revisions[-1].accepted == "replacement"
    assert "Disciplined Survivor" in roll.notation
    assert next(item for item in state.resources if item.id == "focus-points").current_uses == 13


def test_2024_disciplined_survivor_must_use_the_replacement_roll() -> None:
    state = build_combatant_state(build_kael_stillwater_2024(14))
    roll, succeeded = resolve_saving_throw(
        state,
        "constitution",
        30,
        FixedDiceProvider([10, 1]),
    )

    assert succeeded is False
    assert roll is not None
    assert roll.selected_roll == 1
    assert roll.total == 9
    assert roll.revisions[-1].original_total == 18
    assert roll.revisions[-1].replacement_total == 9
    assert roll.revisions[-1].accepted == "replacement"


def test_2024_open_hand_monk_level14_audit_and_registry_are_certified() -> None:
    profile = build_kael_stillwater_2024_profile(14)
    audits = {item.feature_id: item for item in profile.feature_audits}
    registry = build_certified_hero_registry()

    disciplined = audits["disciplined-survivor"]
    assert disciplined.combat_relevant is True
    assert disciplined.automated is True
    assert "1 Focus Point" in (disciplined.notes or "")
    assert registry[("monk", 14, "canonical")] == ("Kael Stillwater", "kael-stillwater-l14")
