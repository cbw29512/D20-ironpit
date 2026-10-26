"""Printed 2014 armor-corrosion hit rider must fail closed until engine bound."""
from __future__ import annotations

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_armor_corrosion_2014 import (
    source_on_hit_armor_corrosion_2014,
)


def _gray():
    return next(m for m in load_monster_source_2014() if m.id == "gray-ooze")


def test_pinned_pseudopod_armor_effect_is_exact_and_not_prematurely_admitted():
    source = _gray()
    before = source.model_dump_json()
    assert len(source.attacks) == 1
    attack = source.attacks[0]
    profile = source_on_hit_armor_corrosion_2014(source, attack)
    assert profile is not None
    assert profile.source_name == attack.name == "Pseudopod"
    assert profile.required_armor_material == "metal"
    assert profile.requires_nonmagical_armor is True
    assert profile.penalty_per_hit == 1
    assert profile.destroys_at_armor_ac == 10
    assert profile.fight_only is True
    assert not attack.source_complete
    assert "attack:incomplete" in basic_blockers_2014(source)
    assert source.model_dump_json() == before


@pytest.mark.parametrize("old,new", [
    ("nonmagical metal armor", "magical metal armor"),
    ("permanent and cumulative −1 penalty", "permanent and cumulative −2 penalty"),
    ("reduces its AC to 10", "reduces its AC to 12"),
    ("plus 7 (2d6) acid damage", "plus 9 (2d8) acid damage"),
    ("reach 5 ft.", "reach 10 ft."),
])
def test_source_change_never_approves_a_different_armor_effect(old, new):
    source = _gray()
    assert old in source.source_actions
    altered = source.model_copy(update={
        "source_actions": source.source_actions.replace(old, new)
    })
    assert source_on_hit_armor_corrosion_2014(altered, source.attacks[0]) is None


def test_extra_unprinted_damage_or_incomplete_metadata_fails_closed():
    source = _gray()
    attack = source.attacks[0]
    changed = attack.model_copy(update={
        "on_hit_damage": [
            {**attack.on_hit_damage[0], "dice_size": 8},
        ],
    })
    assert source_on_hit_armor_corrosion_2014(source, changed) is None
    assert source_on_hit_armor_corrosion_2014(
        source, attack.model_copy(update={"source_complete": True})
    ) is None
    mut = source.model_copy(update={"source_actions": source.source_actions.replace(
        "reduces its AC to 10.</p>",
        "reduces its AC to 10. It also poisons the wielder.</p>",
    )})
    assert source_on_hit_armor_corrosion_2014(mut, attack) is None
