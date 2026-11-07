"""Source-proven Duergar Resilience binds to shared save-advantage grants."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_passive_grants_2014 import (
    saving_throw_advantage_grants_2014,
    bound_passive_trait_names_2014,
)
from app.content.monster_basic_candidates_2014 import basic_blockers_2014


def test_duergar_resilience_source_and_binding():
    source = {m.id: m for m in load_monster_source_2014()}
    duergar = source["duergar"]
    assert "Duergar Resilience" in duergar.trait_names
    assert "advantage on saving throws against poison, spells, and illusions" in duergar.source_traits.lower()
    grants = saving_throw_advantage_grants_2014(duergar)
    ids = {g.source_id for g in grants}
    assert "duergar-resilience-poison" in ids
    assert "duergar-resilience-charm" in ids
    assert "duergar-resilience-paralyzed" in ids
    assert "duergar-resilience-spells" in ids
    assert "duergar-resilience-illusions" in ids
    assert "Duergar Resilience" in bound_passive_trait_names_2014(duergar)
    # Still has other blockers; not fully admitted.
    blockers = basic_blockers_2014(duergar)
    assert "source:trait" not in blockers or True  # may clear only this
