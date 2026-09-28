from __future__ import annotations

from app.combat.ability_checks import resolve_ability_check_outcome
from app.combat.dice import FixedDiceProvider
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.barbarian_level18_profile import build_rokhan_stonefury_level18_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry
from app.domain.models import RollMode


def test_level18_binds_indomitable_might_to_universal_total_floors() -> None:
    profile = build_rokhan_stonefury_level18_profile()
    template = build_rokhan_stonefury_level(18)
    features = template.progression_features

    assert profile.level == 18
    assert profile.subclass_id == "path-berserker"
    assert template.max_hp == 221
    assert template.rage_damage_bonus == 4
    assert {item.id: item.max_uses for item in template.resources}["rage"] == 6
    assert [(item.source_id, item.ability) for item in features.ability_check_minimums] == [
        ("indomitable-might", "strength"),
    ]
    assert [(item.source_id, item.ability) for item in features.saving_throw_minimums] == [
        ("indomitable-might", "strength"),
    ]
    assert ("barbarian", 18, "canonical") in build_certified_hero_registry()


def test_level18_strength_check_uses_strength_score_as_total_floor() -> None:
    state = build_combatant_state(build_rokhan_stonefury_level(18))
    raw = roll_d20(FixedDiceProvider([1]), modifier=5, mode=RollMode.NORMAL)

    revised, succeeded = resolve_ability_check_outcome(state, "strength", raw, 19)

    assert succeeded is True
    assert revised.total == 20
    revision = revised.revisions[-1]
    assert revision.source_effect_id == "indomitable-might"
    assert revision.kind == "total_replacement"
    assert (revision.original_total, revision.replacement_total) == (6, 20)


def test_level18_strength_save_uses_strength_score_as_total_floor() -> None:
    state = build_combatant_state(build_rokhan_stonefury_level(18))

    revised, succeeded = resolve_saving_throw(
        state,
        "strength",
        19,
        FixedDiceProvider([1]),
    )

    assert revised is not None
    assert succeeded is True
    assert revised.total == 20
    revision = revised.revisions[-1]
    assert revision.source_effect_id == "indomitable-might"
    assert revision.kind == "total_replacement"
    assert (revision.original_total, revision.replacement_total) == (12, 20)


def test_indomitable_might_does_not_floor_other_saves_or_leak_into_2014_saves() -> None:
    level18 = build_rokhan_stonefury_level(18)
    state = build_combatant_state(level18)
    dex_roll, dex_success = resolve_saving_throw(state, "dexterity", 19, FixedDiceProvider([1]))
    assert dex_roll is not None
    assert dex_success is False
    assert dex_roll.total == 2
    assert not any(item.source_effect_id == "indomitable-might" for item in dex_roll.revisions)

    legacy = build_rokhan_stonefury_2014(18)
    assert legacy.progression_features.ability_check_minimums
    assert legacy.progression_features.saving_throw_minimums == []
