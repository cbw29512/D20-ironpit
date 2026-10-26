"""2014 Rust Monster: preserve printed gear-only Action without gear mutation."""
from __future__ import annotations

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_equipment_only_action_2014 import (
    verified_arena_inert_equipment_action_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _source():
    return next(m for m in load_monster_source_2014() if m.id == "rust-monster")


def test_complete_source_only_corrosion_action_admits_rust_monster():
    source = _source()
    before = source.model_dump_json()
    assert source.action_names == ["Bite", "Antennae"]
    assert verified_arena_inert_equipment_action_2014(source, "Antennae")
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.id == "2014-rust-monster"
    assert template.weapon_attack is not None
    assert template.weapon_attack.weapon.name == "Bite"
    assert template.weapon_attack.weapon.damage_type.value == "piercing"
    assert template.saving_throw_actions == []
    assert not any(action.id == "antennae" for action in template.timed_self_buff_actions)
    assert source.model_dump_json() == before


@pytest.mark.parametrize("old,new", [
    ("nonmagical ferrous metal object", "magical ferrous metal creature"),
    ("DC 11 Dexterity saving throw", "DC 11 Constitution saving throw"),
    ("permanent and cumulative −1 penalty", "temporary and cumulative −2 penalty"),
    ("it rusts as described in the Rust Metal trait",
     "the wielder also takes 1d8 necrotic damage"),
])
def test_unapproved_action_semantics_remain_blocked(old, new):
    source = _source()
    assert old in source.source_actions
    changed = source.model_copy(update={
        "source_actions": source.source_actions.replace(old, new),
    })
    assert not verified_arena_inert_equipment_action_2014(changed, "Antennae")
    assert "source:extra-action" in basic_blockers_2014(changed)


def test_additional_combat_rider_fails_closed():
    source = _source()
    changed = source.model_copy(update={
        "source_actions": source.source_actions.replace(
            "as described in the Rust Metal trait.</p>",
            "as described in the Rust Metal trait. It also poisons the wielder.</p>",
        ),
    })
    assert "source:extra-action" in basic_blockers_2014(changed)
    assert not verified_arena_inert_equipment_action_2014(source, "Bite")


def test_equipment_only_proof_does_not_dispatch_on_monster_id():
    source = _source()
    renamed = source.model_copy(update={
        "id": "renamed-object-eater",
        "name": "Gear Eater",
        "source_actions": source.source_actions.replace(
            "rust monster", "gear eater"
        ),
    })
    assert verified_arena_inert_equipment_action_2014(renamed, "Antennae")
    assert not verified_arena_inert_equipment_action_2014(source, "Not An Action")
