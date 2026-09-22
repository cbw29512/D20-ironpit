from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import add_modifier
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.modifiers import CombatModifier, ModifierKind


def test_level14_diamond_soul_grants_all_save_proficiencies_and_reroll() -> None:
    hero = build_kael_stillwater_2014(14)
    assert hero.speed_ft == 55
    assert hero.saving_throw_bonuses == {
        "strength": 6,
        "dexterity": 10,
        "constitution": 7,
        "intelligence": 5,
        "wisdom": 8,
        "charisma": 4,
    }

    grants = hero.progression_features.saving_throw_proficiency_grants
    assert len(grants) == 1
    assert grants[0].source_id == "diamond-soul"
    assert grants[0].abilities == ["constitution", "intelligence", "wisdom", "charisma"]

    rerolls = hero.progression_features.failed_save_reroll_grants
    assert len(rerolls) == 1
    assert rerolls[0].source_id == "diamond-soul"
    assert rerolls[0].source_name == "Diamond Soul"
    assert (rerolls[0].resource_id, rerolls[0].resource_cost) == ("ki", 1)

    state = build_combatant_state(hero)
    roll, succeeded = resolve_saving_throw(
        state, "constitution", 20, FixedDiceProvider([1, 20]),
    )
    assert succeeded is True
    assert roll is not None
    assert roll.total == 27
    assert roll.revisions[-1].source_effect_id == "diamond-soul"
    assert roll.revisions[-1].accepted == "replacement"
    assert "Diamond Soul" in roll.notation
    assert next(item for item in state.resources if item.id == "ki").current_uses == 13


def test_diamond_soul_must_accept_second_result_even_when_worse() -> None:
    state = build_combatant_state(build_kael_stillwater_2014(14))
    roll, succeeded = resolve_saving_throw(
        state, "constitution", 30, FixedDiceProvider([10, 1]),
    )
    assert succeeded is False
    assert roll is not None
    assert roll.selected_roll == 1
    assert roll.total == 8
    assert roll.revisions[-1].original_total == 17
    assert roll.revisions[-1].replacement_total == 8
    assert roll.revisions[-1].accepted == "replacement"
    assert next(item for item in state.resources if item.id == "ki").current_uses == 13


def test_diamond_soul_rerolls_only_d20_and_preserves_existing_bonus_die() -> None:
    state = build_combatant_state(build_kael_stillwater_2014(14))
    add_modifier(state, CombatModifier(
        id="test-save-d4",
        source_id="test",
        source_effect_id="test-save-d4",
        kind=ModifierKind.SAVING_THROW_BONUS_DIE,
        dice_count=1,
        dice_size=4,
    ))

    # Initial d20=1, existing d4=4, Diamond Soul replacement d20=20.
    roll, succeeded = resolve_saving_throw(
        state, "constitution", 25, FixedDiceProvider([1, 4, 20]),
    )
    assert succeeded is True
    assert roll is not None
    assert roll.rolls == [20, 4]
    assert roll.total == 31
    revision = roll.revisions[-1]
    assert revision.original_rolls == [1, 4]
    assert revision.replacement_rolls == [20, 4]


def test_level14_profile_fingerprint_and_registry_match() -> None:
    profile = build_kael_stillwater_2014_profile(14)
    fingerprint = build_kael_2014_combat_profile(14)
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }

    assert profile.level == 14
    diamond = next(item for item in profile.feature_audits if item.feature_id == "diamond-soul")
    assert diamond.combat_relevant is True
    assert diamond.automated is True
    assert fingerprint.save_proficiencies == (
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    )
    assert fingerprint.speed_ft == 55
    assert registry[("monk", 14, "canonical-2014")] == (
        "Kael Stillwater", "kael-stillwater-2014-l14",
    )
