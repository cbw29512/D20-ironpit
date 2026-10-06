from __future__ import annotations

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_catalog import load_monster_rows
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2024 import bind_monster_source_traits_2024
from app.content.monster_trait_source_audit import trait_issues
from app.content.demo import build_demo_fighter
from app.domain.timed_self_buffs import TimedSelfBuffAction


@pytest.mark.parametrize("edition,name,dc,radius,immunity", [
    ("2014", "Ghast", 10, 5, True), ("2014", "Hezrou", 14, 10, True),
    ("2024", "Ghast", 10, 5, True), ("2024", "Hezrou", 16, 10, False),
])
def test_source_edition_values_are_independent(edition, name, dc, radius, immunity):
    if edition == "2014":
        source = next(m for m in load_monster_source_2014() if m.name == name).source_traits
    else:
        source = next(m for m in load_monster_rows() if m["name"] == name)["traits"]
    action, = condition_auras_from_source(source, edition)
    aura = action.hostile_start_turn_condition_aura
    assert action.activation_timing == "passive"
    assert action.duration_rounds is None and action.resource_id is None
    assert (aura.save_dc, aura.radius_ft, aura.success_immunity) == (dc, radius, immunity)
    assert aura.condition_id == "poisoned" and aura.save_ability == "constitution"
    assert aura.condition_duration_rounds is None
    assert aura.condition_expiry_timing == "target_turn_start"
    assert aura.source_is_magical is False
    assert aura.effect_tags == ["poison"]


def test_passive_schema_requires_explicit_target_lifetime_and_no_activation_cost():
    source = next(m for m in load_monster_source_2014() if m.name == "Hezrou")
    action, = condition_auras_from_source(source.source_traits, "2014")
    data = action.model_dump()
    for invalid in ({"resource_id": "spell-slot-1"}, {"concentration": True}, {"duration_rounds": 1}, {"condition_ids": ["invisible"]}):
        with pytest.raises(ValueError):
            TimedSelfBuffAction.model_validate({**data, **invalid})
    data["hostile_start_turn_condition_aura"]["condition_expiry_timing"] = None
    with pytest.raises(ValueError):
        TimedSelfBuffAction.model_validate(data)


def test_binding_unlocks_hezrou_but_preserves_ghast_unrelated_blocker():
    hezrou = next(m for m in load_monster_source_2014() if m.name == "Hezrou")
    ghast = next(m for m in load_monster_source_2014() if m.name == "Ghast")
    assert basic_blockers_2014(hezrou) == ()
    assert unsupported_traits_2014(ghast) == ("Turning Defiance",)
    template = compile_combatant(adapt_basic_monster_2014(hezrou))
    assert template.timed_self_buff_actions == condition_auras_from_source(hezrou.source_traits, "2014")


def test_ability_name_is_only_a_source_label_and_unknown_success_fails_closed():
    source = next(m for m in load_monster_rows() if m["name"] == "Ghast")["traits"]
    action, = condition_auras_from_source(source.replace("Stench", "Rotten Aura"), "2024")
    assert action.name == "Rotten Aura" and action.hostile_start_turn_condition_aura.condition_id == "poisoned"
    with pytest.raises(ValueError):
        condition_auras_from_source(source.replace("for 24 hours.", "and takes damage."), "2024")


@pytest.mark.parametrize("name", ["Ghast", "Hezrou"])
def test_2024_binding_is_idempotent_and_source_audit_rejects_missing_or_wrong_aura(name):
    row = next(m for m in load_monster_rows() if m["name"] == name)
    template = build_demo_fighter().model_copy(update={"kind": "monster", "name": name, "ruleset": "2024"})
    template = bind_monster_source_traits_2024(template)
    assert bind_monster_source_traits_2024(template) == template
    assert not any("passive-condition-aura" in issue for issue in trait_issues(template, row))
    missing = template.model_copy(update={"timed_self_buff_actions": []})
    assert "trait-runtime-mismatch:passive-condition-aura" in trait_issues(missing, row)
    wrong = template.model_copy(deep=True)
    wrong.timed_self_buff_actions[0].hostile_start_turn_condition_aura.save_dc += 1
    assert "trait-runtime-mismatch:passive-condition-aura" in trait_issues(wrong, row)
