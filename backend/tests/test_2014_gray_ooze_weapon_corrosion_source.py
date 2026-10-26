"""Prove the pinned Gray Ooze Corrode Metal clause before engine wiring."""
from __future__ import annotations

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_weapon_corrosion_2014 import source_weapon_corrosion_2014


def _source():
    return next(m for m in load_monster_source_2014() if m.id == "gray-ooze")


def test_full_printed_corrode_metal_trait_proves_immutable_weapon_profile():
    source = _source()
    before = source.model_dump_json()
    profile = source_weapon_corrosion_2014(source)
    assert profile is not None
    assert profile.source_name == "Corrode Metal"
    assert profile.damage_penalty_per_hit == 1
    assert profile.unusable_at_penalty == 5
    assert profile.requires_nonmagical_metal_weapon
    # Admission still requires a universal hit hook and the Pseudopod armor rider.
    assert "source:trait" in basic_blockers_2014(source)
    assert source.model_dump_json() == before


@pytest.mark.parametrize("old,new", [
    ("nonmagical weapon made of metal", "magical weapon made of metal"),
    ("permanent and cumulative −1 penalty", "permanent and cumulative −2 penalty"),
    ("drops to −5", "drops to −3"),
    ("Nonmagical ammunition", "All ammunition"),
    ("2-inch-thick", "4-inch-thick"),
])
def test_incomplete_or_changed_source_corrosion_never_binds(old, new):
    source = _source()
    assert old in source.source_traits
    changed = source.model_copy(update={
        "source_traits": source.source_traits.replace(old, new),
    })
    assert source_weapon_corrosion_2014(changed) is None


def test_unheaded_combat_rider_blocks_full_source_proof():
    source = _source()
    changed = source.model_copy(update={
        "source_traits": source.source_traits.replace(
            "in 1 round. </p>", "in 1 round. Enemies take 1d6 poison damage.</p>"
        ),
    })
    assert changed.source_traits != source.source_traits
    assert source_weapon_corrosion_2014(changed) is None
    assert source_weapon_corrosion_2014(
        source.model_copy(update={"trait_names": []})
    ) is None
