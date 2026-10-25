"""Generic staged-effect removal capability and 327-card source coverage."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.combat.condition_removal_policy import _effect_allows_removal
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_staged_disease_2014 import staged_disease_candidates_2014
from app.domain.actions import ConditionRemovalAction
from app.domain.timed_effects import TimedEffect
from app.domain.delayed_effect_transition import DelayedTimedEffectTransition
from app.combat.timed_effect_transition import activate_due_transitions
from app.content.monster_source_staged_disease_2014 import source_bound_staged_disease_2014
from scripts.browser_template_serializer import _removal
from scripts.report_staged_disease_bindings_2014 import render, report


def _action(action_id: str, level: int, tags: list[str]) -> ConditionRemovalAction:
    return ConditionRemovalAction(
        id=action_id, name=action_id, action_cost="action",
        removable_conditions=["poisoned"] if not tags else [],
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
    assert data["stage_wired_python_card_count"] == 1
    assert data["stage_wired_browser_card_count"] == 1
    assert data["wired_python_card_count"] == 0
    assert data["remaining_card_count"] == 1
    assert "100-round acid/moisture" in data["exceptions"][0]["reason"]
    expected = (
        Path(__file__).resolve().parents[2]
        / "docs" / "generated" / "STAGED_DISEASE_BINDINGS_2014.json"
    ).read_text(encoding="utf-8")
    assert expected == render()


def test_delayed_transition_activates_once_on_declared_target_turn() -> None:
    rule = DelayedTimedEffectTransition(
        target_turns=10, cannot_regain_hit_points=True,
        removal_effect_tag="disease", minimum_removal_spell_level=6,
        removal_action_exceptions=["heal"],
    )
    effect = TimedEffect(
        effect_id="diseased", source_id="source", source_effect_id="Tentacle",
        activates_target_turn_count=10, pending_transition=rule,
        removal_effect_tag="disease",
    )
    state = SimpleNamespace(
        turns_started=9, timed_effects=[effect], template=SimpleNamespace(name="Target")
    )
    target = SimpleNamespace(combatant_id="target", state=state)
    events, sequence = activate_due_transitions(1, 9, target)
    assert events == [] and sequence == 1
    state.turns_started = 10
    events, sequence = activate_due_transitions(sequence, 10, target)
    assert len(events) == 1 and sequence == 2
    assert effect.cannot_regain_hit_points
    assert effect.minimum_removal_spell_level == 6
    assert effect.removal_action_exceptions == ["heal"]
    assert effect.pending_transition is None
    assert activate_due_transitions(sequence, 11, target) == ([], sequence)


def test_source_binding_is_semantic_and_keeps_unresolved_attack_incomplete() -> None:
    card = next(card for card in load_monster_source_2014() if card.id == "aboleth")
    original = next(attack for attack in card.attacks if not attack.source_complete)
    bound = source_bound_staged_disease_2014(card, original)
    assert bound.source_complete is False
    assert bound.on_hit_save_effect["delayed_transition"]["target_turns"] == 10
    assert bound.on_hit_save_effect["delayed_transition"]["minimum_removal_spell_level"] == 6
    assert original.on_hit_save_effect is None

