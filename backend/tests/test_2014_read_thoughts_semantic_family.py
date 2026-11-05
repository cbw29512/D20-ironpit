"""Read Thoughts classification is source-semantic and fails closed."""
from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import (
    verified_nonactionable_action_2014,
)
from app.content.monster_read_thoughts_neutral_2014 import (
    semantic_read_thoughts_action_labels_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _doppelganger():
    return next(row for row in load_monster_source_2014() if row.id == "doppelganger")


def test_full_roster_scan_finds_exactly_one_semantic_clause() -> None:
    monsters = load_monster_source_2014()
    matches = [
        (monster.id, label)
        for monster in monsters
        for label in semantic_read_thoughts_action_labels_2014(monster)
    ]
    assert len(monsters) == 327
    assert matches == [("doppelganger", "Read Thoughts")]


def test_exact_clause_clears_the_last_doppelganger_blocker() -> None:
    monster = _doppelganger()
    before = monster.model_dump_json()
    assert verified_nonactionable_action_2014(monster, "Read Thoughts")
    assert basic_blockers_2014(monster) == ()
    assert monster.model_dump_json() == before


def test_card_and_action_rename_do_not_select_classification() -> None:
    monster = _doppelganger()
    renamed_source = (monster.source_actions or "").replace(
        "<strong>Read Thoughts.</strong>", "<strong>Probe Surface Mind.</strong>",
    )
    renamed = monster.model_copy(update={
        "id": "synthetic-thought-reader",
        "name": "Synthetic Thought Reader",
        "action_names": [
            "Probe Surface Mind" if name == "Read Thoughts" else name
            for name in monster.action_names
        ],
        "source_actions": renamed_source,
    })
    assert semantic_read_thoughts_action_labels_2014(renamed) == ("Probe Surface Mind",)
    assert verified_nonactionable_action_2014(renamed, "Probe Surface Mind")
    assert basic_blockers_2014(renamed) == ()


def test_outcome_changing_or_source_value_mutations_fail_closed() -> None:
    monster = _doppelganger()
    original = monster.source_actions or ""
    for altered in (
        original.replace("within 60 feet", "within 30 feet"),
        original.replace("3 feet of wood", "1 foot of wood"),
        original.replace(
            "checks against the target.",
            "checks against the target and has advantage on attack rolls against it.",
        ),
    ):
        mutant = monster.model_copy(update={"source_actions": altered})
        assert not verified_nonactionable_action_2014(mutant, "Read Thoughts")
        assert "source:extra-action" in basic_blockers_2014(mutant)
