"""Source-derived proof for 2014 hurled-object reaction binding."""
from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_rock_catching_2014 import (
    source_hurled_object_qualifiers_2014,
    supports_rock_catching_reaction_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _stone_giant():
    return next(monster for monster in load_monster_source_2014()
                if monster.id == "stone-giant")


def test_source_reaction_requires_exact_2014_dc() -> None:
    monster = _stone_giant()
    assert supports_rock_catching_reaction_2014(monster)
    assert "source:reaction" not in basic_blockers_2014(monster)
    altered = monster.model_copy(update={
        "source_reactions": monster.source_reactions.replace("DC 10", "DC 11"),
    })
    assert not supports_rock_catching_reaction_2014(altered)
    assert "source:reaction" in basic_blockers_2014(altered)


def test_hurled_object_qualifier_requires_source_action_proof() -> None:
    monster = _stone_giant()
    rocks = [attack for attack in monster.attacks if attack.name == "Rock"]
    assert len(rocks) == 1
    attack = rocks[0]
    assert [tag.value for tag in source_hurled_object_qualifiers_2014(monster, attack)] == ["hurled-object"]
    altered = monster.model_copy(update={"source_actions": ""})
    assert source_hurled_object_qualifiers_2014(altered, attack) == []


def test_source_record_is_immutable_during_binding() -> None:
    monster = _stone_giant()
    original = monster.model_dump_json()
    assert supports_rock_catching_reaction_2014(monster)
    assert monster.model_dump_json() == original
