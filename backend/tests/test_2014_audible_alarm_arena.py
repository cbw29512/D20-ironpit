"""2014 audible alarm reacts but cannot change the standard Iron Pit fight."""
from __future__ import annotations

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_audible_alert_2014 import arena_inert_audible_alert_reactions_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _shrieker():
    return next(m for m in load_monster_source_2014() if m.id == "shrieker")


def test_complete_audible_alarm_is_arena_inert_and_zero_offense_compiles():
    source = _shrieker()
    before = source.model_dump_json()
    assert source.attacks == [] and source.reaction_names == ["Shriek"]
    assert arena_inert_audible_alert_reactions_2014(source) == frozenset({"Shriek"})
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.id == "2014-shrieker"
    assert template.weapon_attack is None
    assert template.alternate_weapon_attacks == []
    assert source.model_dump_json() == before


@pytest.mark.parametrize("old,new", [
    ("bright light or a creature", "bright light or a creature deals 1d8 damage"),
    ("within 30 feet", "within 60 feet"),
    ("audible within 300 feet", "deafens creatures within 300 feet"),
    ("for 1d4 of the shrieker's turns", "for 1d6 of the shrieker's turns"),
    ("turns afterward.", "turns afterward. Each target must save or be Frightened."),
])
def test_added_or_altered_fight_effect_remains_blocked(old, new):
    source = _shrieker()
    assert old in source.source_reactions
    changed = source.model_copy(update={
        "source_reactions": source.source_reactions.replace(old, new)
    })
    assert not arena_inert_audible_alert_reactions_2014(changed)
    assert "source:reaction" in basic_blockers_2014(changed)
    assert "attack:none" in basic_blockers_2014(changed)


def test_missing_source_or_additional_unknown_reaction_remains_blocked():
    source = _shrieker()
    for changed in (
        source.model_copy(update={"source_reactions": ""}),
        source.model_copy(update={"reaction_names": ["Shriek", "Unknown"]}),
        source.model_copy(update={
            "source_reactions": source.source_reactions +
            "<p>The shrieker also poisons adjacent creatures.</p>",
        }),
    ):
        assert "source:reaction" in basic_blockers_2014(changed)
        assert "attack:none" in basic_blockers_2014(changed)


def test_source_proof_does_not_require_monster_id():
    source = _shrieker()
    renamed = source.model_copy(update={
        "id": "sonic-fungus",
        "name": "Sonic Fungus",
        "source_reactions": source.source_reactions.replace(
            "shrieker", "Sonic Fungus"
        ),
    })
    assert arena_inert_audible_alert_reactions_2014(renamed) == frozenset({"Shriek"})


def test_full_327_card_scan_exposes_attack_free_shrieker_once():
    from app.content.monster_roster_2014 import build_basic_2014_monsters

    roster = build_basic_2014_monsters()
    assert len(roster) == 245
    matches = [card for card in roster if card.id == "2014-shrieker"]
    assert len(matches) == 1
    assert matches[0].weapon_attack is None
    assert matches[0].alternate_weapon_attacks == []
    assert all(card.ruleset == "2014" for card in roster)
