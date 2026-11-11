"""Universal source proofs for repeated-choice 2014 Multiattack policies."""
from __future__ import annotations

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_multiattack_2014 import multiattack_blockers_2014
from app.content.monster_multiattack_variants_2014 import source_variants_2014
from app.content.monster_source_damage_or_grapple_2014 import source_proven_damage_or_grapple_2014
from app.content.monster_source_2014 import load_monster_source_2014


AT_MOST_ONCE = {"vampire", "vampire-spawn", "wereboar", "wererat"}
SAME_ATTACK = {"werebear", "weretiger"}
FAMILY = AT_MOST_ONCE | SAME_ATTACK


def _cards():
    return {card.id: card for card in load_monster_source_2014()}


def test_327_card_semantic_scan_finds_and_wires_the_complete_policy_family():
    cards = _cards()
    assert len(cards) == 327
    applicable = {
        card.id for card in cards.values()
        if isinstance(card.multiattack_policy, dict) and (
            "at_most_once_attack_ids" in card.multiattack_policy
            or "same_attack_as_previous_slots" in card.multiattack_policy
        )
    }
    assert applicable == FAMILY
    assert all(source_variants_2014(cards[card_id]) for card_id in applicable)
    assert all(not multiattack_blockers_2014(cards[card_id]) for card_id in applicable)


@pytest.mark.parametrize("card_id", sorted(AT_MOST_ONCE))
def test_at_most_once_variants_preserve_both_orders_and_two_nonlimited_attacks(card_id):
    card = _cards()[card_id]
    before = card.model_dump()
    variants = source_variants_2014(card)
    limited = {f"2014-{card.id}-{item}" for item in card.multiattack_policy["at_most_once_attack_ids"]}
    # Three printed base orders remain; a source-verified alternate Grapple
    # adds both one-slot replacements and the legal two-Grapple sequence.
    grapple_alternatives = source_proven_damage_or_grapple_2014(card)
    assert len(variants) == (8 if grapple_alternatives else 3)
    if grapple_alternatives:
        assert len(grapple_alternatives) == 1
        grapple_id = grapple_alternatives[0].id
        assert sum(
            any(grapple_id in slot.attack_ids for slot in variant.slots)
            for variant in variants
        ) == 5
        assert sum(
            all(slot.attack_ids == [grapple_id] for slot in variant.slots)
            for variant in variants
        ) == 1
    assert all(variant.attack_kind is None for variant in variants)
    assert all(len(variant.slots) == 2 for variant in variants)
    assert all(
        sum(bool(set(slot.attack_ids) & limited) for slot in variant.slots) <= 1
        for variant in variants
    )
    assert card.model_dump() == before


@pytest.mark.parametrize("card_id,expected_kinds", [
    ("werebear", ["melee", "melee"]),
    ("weretiger", ["melee", "ranged", "melee"]),
])
def test_same_attack_variants_preserve_printed_mode_and_never_mix_slots(card_id, expected_kinds):
    card = _cards()[card_id]
    variants = source_variants_2014(card)
    assert [variant.attack_kind.value for variant in variants] == expected_kinds
    assert all(variant.slots[0].attack_ids == variant.slots[1].attack_ids for variant in variants)
    runtime = compile_combatant(adapt_monster_mechanics_2014(card))
    assert [variant.attack_kind.value for variant in runtime.attack_action.variants] == expected_kinds


@pytest.mark.parametrize("card_id", sorted(FAMILY))
def test_mutated_printed_rule_fails_closed_instead_of_trusting_policy_data(card_id):
    card = _cards()[card_id]
    mutated = card.model_copy(update={
        "source_actions": card.source_actions.replace("two ", "three ", 1),
    })
    assert source_variants_2014(mutated) == []
    assert multiattack_blockers_2014(mutated) == ["multiattack:complex"]


def test_form_gated_multiattack_headings_are_source_visible():
    cards = _cards()
    for card_id in ("wereboar", "wererat", "weretiger"):
        assert "Multiattack (Humanoid or Hybrid Form Only)" in cards[card_id].action_names
        assert source_variants_2014(cards[card_id])
