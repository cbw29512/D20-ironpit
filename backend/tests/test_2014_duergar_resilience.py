"""Source-proof and binding tests for 2014 Duergar Resilience."""
from __future__ import annotations

import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import (
    saving_throw_advantage_grants_2014,
    bound_passive_trait_names_2014,
    _source_proves_duergar_resilience,
)


def _duergar():
    return next(m for m in load_monster_source_2014() if m.id == "duergar")


def test_source_proves_exact_clause():
    monster = _duergar()
    assert _source_proves_duergar_resilience(monster)
    assert "Duergar Resilience" in bound_passive_trait_names_2014(monster)


def test_source_mutation_fails_closed():
    monster = _duergar()
    mutated = monster.model_copy(update={"source_traits": (monster.source_traits or "").replace("poison", "fire")})
    assert not _source_proves_duergar_resilience(mutated)
    assert "Duergar Resilience" not in bound_passive_trait_names_2014(mutated)


def test_grants_are_composed():
    monster = _duergar()
    grants = saving_throw_advantage_grants_2014(monster)
    sources = {g.source_name for g in grants}
    assert "Duergar Resilience" in sources
    spell_grant = next(g for g in grants if g.source_id == "duergar-resilience-spells")
    assert spell_grant.requires_spell_effect
    tag_grants = [g for g in grants if g.source_id.startswith("duergar-resilience-") and g.source_id != "duergar-resilience-spells"]
    tags = {t for g in tag_grants for t in g.required_effect_tags}
    assert {"poison", "illusion", "charmed", "paralyzed"} <= tags


def test_rename_neutrality():
    monster = _duergar()
    renamed = monster.model_copy(update={"name": "Renamed Duergar", "id": "renamed-duergar"})
    # Source proof is text-based; rename of card does not affect clause match.
    assert _source_proves_duergar_resilience(renamed)
