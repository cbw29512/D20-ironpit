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


def test_source_proof_fails_closed_when_each_required_clause_is_missing():
    """A same-named action is insufficient without all pinned RAW predicates."""
    monster = _chain_devil()
    source = monster.source_actions
    for phrase in (
        "chains aren't being worn or carried",
        "within 60 feet",
        "animated chain is an object",
        "reverts to its inanimate state",
    ):
        assert phrase in source.casefold()
        mutated = monster.model_copy(
            update={"source_actions": source.replace(
                source[source.casefold().index(phrase):source.casefold().index(phrase) + len(phrase)],
                "[omitted source clause]",
                1,
            )}
        )
        assert not supports_animate_chains_arena_unavailable_2014(mutated), phrase


def test_arena_classification_never_removes_printed_action():
    """Keep the printed monster card complete even when the action cannot run."""
    monster = _chain_devil()
    original_actions = monster.source_actions
    original_names = tuple(monster.action_names)
    assert supports_animate_chains_arena_unavailable_2014(monster)
    assert "source:extra-action" not in basic_blockers_2014(monster)
    assert monster.source_actions == original_actions
    assert tuple(monster.action_names) == original_names
    assert any(name.casefold().startswith("animate chains") for name in original_names)
