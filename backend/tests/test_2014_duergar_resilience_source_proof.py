"""Source-proof and binding tests for 2014 Duergar Resilience family.

Reuses existing SavingThrowAdvantageGrant. No name dispatch.
Mutation of printed clause fails closed.
"""
from __future__ import annotations

import pytest

from app.content.monster_contextual_save_defenses import contextual_save_defenses_from_source, contextual_save_defenses_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _duergar():
    for row in load_monster_source_2014():
        if row.id == "duergar":
            return row
    raise AssertionError("Duergar source missing")


def test_duergar_resilience_binds_existing_advantage_grants():
    monster = _duergar()
    actions, grants = contextual_save_defenses_2014(monster)
    assert not actions
    source_ids = {g.source_id for g in grants}
    assert "duergar-resilience-poison" in source_ids
    assert "duergar-resilience-spell" in source_ids
    assert "duergar-resilience-illusion" in source_ids
    assert "duergar-resilience-charmed" in source_ids
    assert "duergar-resilience-paralyzed" in source_ids
    spell_grant = next(g for g in grants if g.source_id.endswith("-spell"))
    assert spell_grant.requires_spell_effect is True
    poison_grant = next(g for g in grants if g.source_id.endswith("-poison"))
    assert "poison" in poison_grant.required_effect_tags


def test_duergar_resilience_mutation_fails_closed():
    monster = _duergar()
    mutated = monster.source_traits.replace(
        "advantage on saving throws against poison, spells, and illusions",
        "advantage on saving throws against fire",
    )
    actions, grants = contextual_save_defenses_from_source(mutated, "2014")
    resilience_ids = [g.source_id for g in grants if "resilience" in g.source_id]
    assert not resilience_ids


def test_renamed_source_still_binds():
    monster = _duergar()
    renamed = monster.source_traits.replace("Duergar Resilience", "Underdark Fortitude")
    actions, grants = contextual_save_defenses_from_source(renamed, "2014")
    assert any("underdark-fortitude" in g.source_id for g in grants)
