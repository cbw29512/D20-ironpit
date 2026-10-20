"""Source-only contract; never marks the 2014 Sea Hag playable."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_visual_disguise_2014 import source_proven_visual_disguise_2014


def _card():
    return next(card for card in load_monster_source_2014() if card.id == "sea-hag")


def test_full_illusion_action_is_preserved_as_immutable_source_facts():
    card = _card()
    original = card.model_dump_json()
    fact = source_proven_visual_disguise_2014(card)
    assert fact is not None
    assert fact.source_name == "Illusory Appearance"
    assert fact.activation_cost == "action"
    assert fact.magical_illusion and fact.conceals_true_form
    assert fact.ends_on_owner_bonus_action and fact.ends_if_owner_dead
    assert fact.physical_inspection_inconsistent
    assert (fact.investigation_action_cost, fact.investigation_ability,
            fact.investigation_skill, fact.investigation_dc) == (
                "action", "intelligence", "investigation", 16
            )
    assert fact.investigation_reveals_true_form is False
    assert original == card.model_dump_json()
    with pytest.raises(FrozenInstanceError):
        fact.investigation_dc = 99


@pytest.mark.parametrize("original,replacement", [
    ("magical illusion", "nonmagical costume"),
    ("a bonus action to end it", "an action to end it"),
    ("or if she dies", "or if she is frightened"),
    ("fail to hold up to physical inspection", "remain real to the touch"),
    ("DC 16 Intelligence (Investigation)", "DC 16 Wisdom (Perception)"),
    ("take an action to visually inspect", "use a bonus action to visually inspect"),
    ("discern that the hag is disguised", "learn the hag's true appearance"),
])
def test_no_printed_outcome_or_economy_can_change_silently(original, replacement):
    card = _card()
    assert original in card.source_actions, original
    modified = card.model_copy(update={
        "source_actions": card.source_actions.replace(original, replacement),
    })
    assert source_proven_visual_disguise_2014(modified) is None
    assert source_proven_visual_disguise_2014(card) is not None


def test_dc_is_source_owned_and_mutation_of_card_identity_is_irrelevant():
    card = _card()
    modified = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "DC 16 Intelligence (Investigation)",
            "DC 18 Intelligence (Investigation)",
        ),
        "id": "renamed-illusion-source",
        "name": "Other Name",
    })
    assert source_proven_visual_disguise_2014(modified).investigation_dc == 18
    assert source_proven_visual_disguise_2014(card).investigation_dc == 16


@pytest.mark.parametrize("dc", ["0", "41"])
def test_invalid_source_dc_fails_closed(dc):
    card = _card()
    changed = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "DC 16 Intelligence (Investigation)",
            f"DC {dc} Intelligence (Investigation)",
        ),
    })
    assert source_proven_visual_disguise_2014(changed) is None


def test_heading_or_unprinted_continuation_cannot_supply_missing_ability():
    card = _card()
    assert source_proven_visual_disguise_2014(
        card.model_copy(update={"action_names": ["Claws", "Death Glare"]}),
    ) is None
    assert source_proven_visual_disguise_2014(
        card.model_copy(update={
            "source_actions": card.source_actions + "<p>An added Rider: grants +5 AC.</p>",
        }),
    ) is None
