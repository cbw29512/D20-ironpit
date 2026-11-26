"""Darkmantle Darkness Aura: exact source, universal moving-zone contract."""
from __future__ import annotations

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_darkness_aura_2014 import (
    darkness_aura_resources_2014, source_proven_darkness_aura_2014,
)
from scripts.browser_template_serializer import _suppression_zone


def _card():
    return next(card for card in load_monster_source_2014() if card.id == "darkmantle")


def test_darkness_aura_preserves_every_source_parameter_and_card_immutability() -> None:
    card = _card()
    snapshot = card.model_dump_json()
    action = source_proven_darkness_aura_2014(card)
    assert action is not None
    assert (action.name, action.id, action.level) == (
        "Darkness Aura (1/Day)", "darkness-aura", 0,
    )
    assert (action.cast_range_ft, action.radius_ft, action.duration_rounds) == (0, 15, 100)
    assert action.center_on_source and action.follows_source and action.concentration
    assert not action.is_spell
    assert action.obscuration_kind == "magical-darkness"
    assert action.dispel_light_spell_max_level == 2
    assert not any((action.deafens, action.blocks_verbal_spells,
                    action.thunder_immunity, action.expends_spell_slot))
    assert [(item.id, item.max_uses) for item in darkness_aura_resources_2014(card)] == [
        ("darkness-aura", 1),
    ]
    serialized = _suppression_zone(action)
    assert serialized["centerOnSource"] is True
    assert serialized["followsSource"] is True
    assert serialized["isSpell"] is False
    assert serialized["dispelLightSpellMaxLevel"] == 2
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    assert [item.id for item in template.suppression_zone_actions] == ["darkness-aura"]
    assert [(item.id, item.max_uses) for item in template.resources
            if item.id == "darkness-aura"] == [("darkness-aura", 1)]
    blockers = set(basic_blockers_2014(card))
    assert "source:extra-action" not in blockers
    assert "attack:incomplete" not in blockers
    assert card.model_dump_json() == snapshot


@pytest.mark.parametrize("old,new", [
    ("15-\N{SOFT HYPHEN}-foot radius", "20-foot radius"),
    ("moves with it", "remains in place"),
    ("up to 10 minutes", "up to 1 minute"),
    ("2nd level or lower", "3rd level or lower"),
])
def test_darkness_aura_source_changes_fail_closed(old: str, new: str) -> None:
    card = _card()
    assert old in card.source_actions
    altered = card.model_copy(update={"source_actions": card.source_actions.replace(old, new)})
    assert source_proven_darkness_aura_2014(altered) is None
    assert darkness_aura_resources_2014(altered) == []


def test_darkness_aura_binding_is_semantic_not_monster_named() -> None:
    card = _card().model_copy(update={"id": "anonymous", "name": "Anonymous"})
    assert source_proven_darkness_aura_2014(card) is not None
