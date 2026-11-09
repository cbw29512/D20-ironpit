"""Source-proven water breathing and a generic failed-save Grapple exception."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.saving_throw_effects import apply_save_effects
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_breathing_media_2014 import source_can_breathe_water_2014
from app.domain.capability_effects import GrappleEffectDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row


def _sources():
    cards = {card.id: card for card in load_monster_source_2014()}
    assert len(cards) == 327
    return cards


def _template(card):
    return compile_combatant(adapt_monster_mechanics_2014(card))


def test_327_card_audit_proves_all_and_only_40_printed_water_breathers():
    cards = _sources()
    found = {id for id, card in cards.items() if source_can_breathe_water_2014(card)}
    expected = {
        id for id, card in cards.items()
        if {"Amphibious", "Water Breathing", "Limited Amphibiousness"} & set(card.trait_names)
    }
    assert found == expected and len(found) == 40
    for id in ("frog", "chuul", "gold-dragon-wyrmling", "sahuagin", "giant-octopus"):
        assert id in found
        template = _template(cards[id])
        assert template.can_breathe_water
        assert template_row(template)["can_breathe_water"] is True
    for id in ("water-elemental", "air-elemental", "magmin"):
        assert id not in found
        assert not _template(cards[id]).can_breathe_water
    assert "can_breathe_water" not in template_row(_template(cards["magmin"]))


def test_changed_trait_rider_is_not_silently_accepted_or_fabricated():
    cards = _sources()
    frog = cards["frog"]
    changed = frog.model_copy(update={
        "source_traits": frog.source_traits.replace(
            "can breathe air and water.", "can breathe air and water and gains resistance."
        )
    })
    assert not source_can_breathe_water_2014(changed)
    renamed = frog.model_copy(update={"name": "Synthetic Amphibian", "id": "synthetic-123"})
    assert source_can_breathe_water_2014(renamed)
    fake = cards["magmin"].model_copy(update={
        "trait_names": [*cards["magmin"].trait_names, "Amphibious"]
    })
    assert not source_can_breathe_water_2014(fake)


def test_exception_requires_breath_prevention_in_generic_grapple_definition():
    with pytest.raises(ValidationError, match="requires breathing prevention"):
        GrappleEffectDefinition(
            escape_dc=14, breathing_exempt_medium="water",
        )


def test_real_water_elemental_whelm_grapples_both_but_only_blocks_air_breathing():
    cards = _sources()
    source = EncounterCombatant(
        combatant_id="source", side="monsters", position_ft=0,
        state=build_combatant_state(_template(cards["water-elemental"])),
    )
    targets = [
        EncounterCombatant(
            combatant_id=card_id, side="heroes", position_ft=0,
            state=build_combatant_state(_template(cards[card_id])),
        )
        for card_id in ("frog", "goblin")
    ]
    setup = EncounterSetup(
        heroes=targets, monsters=[source], ruleset="2014",
        hero_total_levels=0, monster_total_cr="5",
    )
    action = next(a for a in source.state.template.saving_throw_actions if a.id == "whelm")
    assert action.grapple_prevents_breathing
    assert action.grapple_breathing_exempt_medium == "water"
    browser = template_row(source.state.template)
    save = next(a for a in browser["saving_throw_actions"] if a["id"] == "whelm")
    assert save["grappleBreathingExemptMedium"] == "water"

    frog, goblin = targets
    assert frog.state.template.can_breathe_water and not goblin.state.template.can_breathe_water
    for target in targets:
        result = apply_save_effects(source, target, action, False, None, 1, setup=setup)
        assert result.applied_conditions == ["grappled", "restrained"]
    assert not frog.state.grapple_sources[0].prevents_breathing
    assert goblin.state.grapple_sources[0].prevents_breathing
    assert frog.state.grapple_sources[0].source_id == source.combatant_id
    assert goblin.state.grapple_sources[0].source_id == source.combatant_id
