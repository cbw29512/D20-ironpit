from __future__ import annotations

from app.combat.debuff_counters import difficult_terrain_multiplier
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.druid_land_2014_audits import build_druid_land_2014_feature_audits
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.saving_throw_context import SavingThrowContext


def test_level_six_lands_stride_uses_universal_passive_counter() -> None:
    hero = build_thalen_greenbough_2014(6)
    state = build_combatant_state(hero)

    assert hero.level == 6
    assert hero.max_hp == 45
    assert len(hero.progression_features.passive_debuff_counter_grants) == 1
    grant = hero.progression_features.passive_debuff_counter_grants[0]
    assert grant.source_id == "lands-stride"
    assert grant.source_name == "Land's Stride"
    assert grant.counter.debuff_id == "difficult-terrain"
    assert grant.counter.source_scope == "nonmagical"

    assert difficult_terrain_multiplier(state, source_is_magical=False) == 1
    assert difficult_terrain_multiplier(state, source_is_magical=True) == 2


def test_level_six_lands_stride_grants_advantage_only_against_magical_plant_impediments() -> None:
    state = build_combatant_state(build_thalen_greenbough_2014(6))

    roll, _ = resolve_saving_throw(
        state,
        "dexterity",
        99,
        FixedDiceProvider([3, 17]),
        SavingThrowContext(
            magical_effect=True,
            effect_tags=frozenset({"plant-impediment"}),
        ),
    )
    assert roll is not None
    assert roll.mode == "advantage"
    assert roll.rolls == [3, 17]

    ordinary = build_combatant_state(build_thalen_greenbough_2014(6))
    roll, _ = resolve_saving_throw(
        ordinary,
        "dexterity",
        99,
        FixedDiceProvider([10]),
        SavingThrowContext(
            magical_effect=False,
            effect_tags=frozenset({"plant-impediment"}),
        ),
    )
    assert roll is not None
    assert roll.mode == "normal"
    assert roll.rolls == [10]


def test_level_six_lands_stride_audit_is_certified() -> None:
    audit = next(
        item for item in build_druid_land_2014_feature_audits(6)
        if item.feature_id == "lands-stride"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True
