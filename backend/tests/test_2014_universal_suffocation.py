"""2014 source-owned breath deprivation through universal Grapple and zero-HP."""
from __future__ import annotations

import pytest

from app.combat.breathing import (
    resolve_breathing_start_turn, suffocation_blocks_recovery, unable_to_breathe,
)
from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import release_grapple
from app.combat.saving_throw_effects import apply_save_effects
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.combat.zero_hp_stabilization import stabilize_at_zero
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.content.monster_breath_lifecycle_source_2014 import source_breath_hold_rounds_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row


def _catalog():
    cards = {c.id: c for c in load_monster_source_2014()}
    assert len(cards) == 327
    return cards


def _fight(victim_card="goblin", *, character=False, constitution=14):
    cards = _catalog()
    source = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(
            compile_combatant(adapt_monster_mechanics_2014(cards["water-elemental"]))
        ),
    )
    template = compile_combatant(adapt_monster_mechanics_2014(cards[victim_card]))
    scores = template.ability_scores.model_copy(update={"constitution": constitution})
    template = template.model_copy(update={
        "kind": "character" if character else "monster",
        "ability_scores": scores,
    })
    victim = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=0,
        state=build_combatant_state(template),
    )
    setup = EncounterSetup(
        heroes=[victim], monsters=[source], ruleset="2014",
        hero_total_levels=0, monster_total_cr="5",
    )
    action = next(a for a in source.state.template.saving_throw_actions if a.id == "whelm")
    apply_save_effects(source, victim, action, False, None, 1, setup=setup)
    return source, victim, setup


def _ticks(victim, setup, count):
    seen = []
    seq = 1
    for number in range(1, count + 1):
        events, seq = resolve_breathing_start_turn(seq, number, victim, setup)
        seen.extend(events)
    return seen


def test_327_card_hold_breath_source_is_validated_and_exported():
    cards = _catalog()
    # A standard 2014 Crocodile explicitly holds its breath for 15 minutes.
    crocodile = cards["crocodile"]
    assert source_breath_hold_rounds_2014(crocodile) == 150
    # 2014 Giant Octopus prints an additional out-of-water qualifier.
    # The exact full paragraph is accepted without inventing a new resolver.
    assert source_breath_hold_rounds_2014(cards["giant-octopus"]) == 600
    template = compile_combatant(adapt_monster_mechanics_2014(crocodile))
    assert template.breath_hold_rounds == 150
    assert template_row(template)["breath_hold_rounds"] == 150
    assert definition_from_template(template).breath_hold_rounds == 150
    for card in cards.values():
        result = source_breath_hold_rounds_2014(card)
        assert result is None or result > 0
    mutated = crocodile.model_copy(update={
        "source_traits": crocodile.source_traits.replace(
            "can hold its breath for 15 minutes.",
            "can hold its breath for 15 minutes and resists magic.",
        )
    })
    assert mutated.source_traits != crocodile.source_traits
    with pytest.raises(ValueError, match="Unsupported 2014 Hold Breath"):
        source_breath_hold_rounds_2014(mutated)


def test_whelm_countdown_uses_2014_constitution_and_printeffect():
    owner, victim, setup = _fight(character=True)
    assert unable_to_breathe(victim.state)
    assert victim.state.breath_hold_rounds_remaining is None
    assert victim.state.breath_survival_rounds_remaining is None

    assert _ticks(victim, setup, 29) == []
    assert victim.state.breath_hold_rounds_remaining == 1
    warning = _ticks(victim, setup, 1)
    assert len(warning) == 1 and "Whelm" in warning[0].description
    assert _ticks(victim, setup, 2) == []
    expired = _ticks(victim, setup, 1)
    assert len(expired) == 1 and "Whelm" in expired[0].description
    assert victim.state.current_hp == 0 and victim.state.is_unconscious
    assert not victim.state.is_stable
    assert suffocation_blocks_recovery(victim.state)

    # 2014 suffocation prevents ordinary healing, stabilization and natural-20
    # recovery while the same Grapple still denies breathing.
    assert restore_hit_points(victim.state, 4) == 0
    assert stabilize_at_zero(victim.state) == "unchanged"
    victim.state.death_save_successes = 2
    resolve_death_save(5, 34, "victim", victim.state, FixedDiceProvider([20]))
    assert victim.state.current_hp == 0 and not victim.state.is_stable
    assert victim.state.death_save_successes == 2

    release_grapple(victim.state, owner.combatant_id)
    assert not suffocation_blocks_recovery(victim.state)
    assert victim.state.breath_hold_rounds_remaining is None
    assert restore_hit_points(victim.state, 3) == 3


def test_water_breather_never_counts_down_and_ordinary_release_resets():
    owner, frog, setup = _fight("frog")
    assert frog.state.grapple_sources and not unable_to_breathe(frog.state)
    assert not _ticks(frog, setup, 100)
    assert frog.state.breath_hold_rounds_remaining is None

    owner, victim, setup = _fight()
    assert _ticks(victim, setup, 8) == []
    assert victim.state.breath_hold_rounds_remaining == 22
    release_grapple(victim.state, owner.combatant_id)
    assert victim.state.breath_hold_rounds_remaining is None
    assert not unable_to_breathe(victim.state)
    # A new source effect begins its own fresh budget after release.
    action = next(a for a in owner.state.template.saving_throw_actions if a.id == "whelm")
    apply_save_effects(owner, victim, action, False, None, 1, setup=setup)
    assert _ticks(victim, setup, 1) == []
    assert victim.state.breath_hold_rounds_remaining == 29


def test_synthetic_no_air_and_edition_isolation():
    owner, victim, setup = _fight()
    victim.state.template = victim.state.template.model_copy(update={"needs_air": False})
    assert not unable_to_breathe(victim.state)
    assert not _ticks(victim, setup, 20)
    victim.state.template = victim.state.template.model_copy(update={
        "needs_air": True, "ruleset": "2024",
    })
    with pytest.raises(ValueError, match="2024 suffocation"):
        resolve_breathing_start_turn(1, 1, victim, setup)
