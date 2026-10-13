from __future__ import annotations

from app.content.monster_animate_chains_2014 import supports_animate_chains_arena_unavailable_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _chain_devil():
    return next(m for m in load_monster_source_2014() if m.id == "chain-devil")


def test_source_proof_matches_pinned_2014():
    monster = _chain_devil()
    assert supports_animate_chains_arena_unavailable_2014(monster)


def test_extra_action_blocker_clears():
    monster = _chain_devil()
    blockers = basic_blockers_2014(monster)
    assert "source:extra-action" not in blockers


def test_mutated_source_fails_proof():
    monster = _chain_devil()
    mutated = monster.model_copy(update={"source_actions": "Animate Chains. Choose chains."})
    assert not supports_animate_chains_arena_unavailable_2014(mutated)
