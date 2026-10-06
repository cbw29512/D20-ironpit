from __future__ import annotations

import pytest

from app.combat.resources import resource_state
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_zero_hp_prevention_2014 import (
    damage_threshold_zero_hp_replacements_2014,
    zero_hp_prevention_resources_2014,
)

_RELENTLESS = "Relentless (Recharges after a Short or Long Rest)"
_EXPECTED = {
    "boar": 7,
    "giant-boar": 10,
    "wereboar": 14,
}


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


@pytest.mark.parametrize(("monster_id", "threshold"), _EXPECTED.items())
def test_relentless_source_payload_compiles_to_one_shared_threshold_rule(
    monster_id: str,
    threshold: int,
) -> None:
    monster = _source(monster_id)
    rules = damage_threshold_zero_hp_replacements_2014(monster)
    resources = zero_hp_prevention_resources_2014(monster)

    assert len(rules) == 1
    rule = rules[0]
    assert (
        rule.source_name,
        rule.resource_id,
        rule.resource_cost,
        rule.max_trigger_damage,
        rule.replacement_hp,
    ) == (_RELENTLESS, "relentless", 1, threshold, 1)
    assert [(item.id, item.max_uses) for item in resources] == [("relentless", 1)]
    assert _RELENTLESS not in unsupported_traits_2014(monster)


@pytest.mark.parametrize(("monster_id", "threshold"), [("boar", 7), ("giant-boar", 10)])
def test_relentless_unlocks_and_resolves_through_shared_zero_hp_pipeline(
    monster_id: str,
    threshold: int,
) -> None:
    monster = _source(monster_id)
    assert basic_blockers_2014(monster) == ()
    template = compile_combatant(adapt_basic_monster_2014(monster))
    assert len(template.damage_threshold_zero_hp_replacements) == 1
    assert template.damage_threshold_zero_hp_replacements[0].max_trigger_damage == threshold

    state = build_combatant_state(template)
    state.current_hp = threshold
    assert apply_damage(state, threshold) == "damage_threshold_zero_hp_replacement"
    assert state.current_hp == 1
    assert state.is_dead is False
    assert resource_state(state, "relentless").current_uses == 0

    assert apply_damage(state, 1) == "dead"
    assert state.is_dead is True


@pytest.mark.parametrize(("monster_id", "threshold"), [("boar", 7), ("giant-boar", 10)])
def test_relentless_does_not_fire_above_threshold_or_on_non_damage_zero_hp(
    monster_id: str,
    threshold: int,
) -> None:
    template = compile_combatant(adapt_basic_monster_2014(_source(monster_id)))

    too_large = build_combatant_state(template)
    too_large.current_hp = threshold + 1
    assert apply_damage(too_large, threshold + 1) == "dead"
    assert resource_state(too_large, "relentless").current_uses == 1

    non_damage = build_combatant_state(template)
    assert reduce_to_zero_hit_points(non_damage) == "dead"
    assert resource_state(non_damage, "relentless").current_uses == 1


def test_wereboar_loses_only_the_relentless_portion_of_its_trait_blocker() -> None:
    monster = _source("wereboar")
    unsupported = set(unsupported_traits_2014(monster))
    assert _RELENTLESS not in unsupported
    assert "Shapechanger" in unsupported
    assert basic_blockers_2014(monster)
