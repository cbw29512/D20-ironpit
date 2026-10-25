"""Generic staged-effect removal capability and 327-card source coverage."""
from types import SimpleNamespace

import pytest

from app.combat.condition_removal_policy import _effect_allows_removal
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_staged_disease_2014 import staged_disease_candidates_2014
from app.domain.actions import ConditionRemovalAction
from app.domain.timed_effects import TimedEffect
from scripts.browser_template_serializer import _removal
from scripts.report_staged_disease_bindings_2014 import render, report


def _action(action_id: str, level: int, tags: list[str]) -> ConditionRemovalAction:
    return ConditionRemovalAction(
        id=action_id, name=action_id, action_cost="action",
        removal_effect_tags=tags, spell_level=level,
    )


def _target(effect: TimedEffect):
    return SimpleNamespace(state=SimpleNamespace(timed_effects=[effect]))


def test_staged_effect_removal_honors_tag_level_and_explicit_exception() -> None:
    dormant = TimedEffect(
        effect_id="renamed-disease", source_id="renamed-source",
        removal_effect_tag="disease",
    )
    onset = dormant.model_copy(update={
        "minimum_removal_spell_level": 6,
        "removal_action_exceptions": ["heal"],
    })
    lesser = _action("lesser-restoration", 2, ["disease"])
    greater = _action("greater-restoration", 6, ["disease"])
    heal = _action("heal", 0, [])

    assert _effect_allows_removal(_target(dormant), dormant.effect_id, lesser)
    assert not _effect_allows_removal(_target(onset), onset.effect_id, lesser)
    assert _effect_allows_removal(_target(onset), onset.effect_id, greater)
    assert _effect_allows_removal(_target(onset), onset.effect_id, heal)


def test_invalid_level_gate_without_effect_tag_fails_closed() -> None:
    with pytest.raises(ValueError):
        TimedEffect(
            effect_id="bad", source_id="source",
            minimum_removal_spell_level=6,
        )


def test_browser_serialization_preserves_removal_capability() -> None:
    row = _removal(_action("renamed-cure", 6, ["disease"]))
    assert row["removalEffectTags"] == ["disease"]
    assert row["spellLevel"] == 6


def test_all_327_cards_are_scanned_and_aboleth_remains_explicitly_blocked() -> None:
    cards = load_monster_source_2014()
    assert [card.id for card in staged_disease_candidates_2014(cards)] == ["aboleth"]
    data = report()
    assert data["source_cards_scanned"] == 327
    assert data["applicable_card_count"] == 1
    assert data["wired_python_card_count"] == 0
    assert data["remaining_card_count"] == 1
    assert "100-round acid/moisture" in data["exceptions"][0]["reason"]
    assert render().endswith("\n")
