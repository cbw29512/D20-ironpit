"""Moving magical darkness follows its source in the Python fight state."""
from __future__ import annotations

from app.combat.state import begin_turn, build_combatant_state
from app.combat.suppression_zone_cast import (
    cast_suppression_zone, choose_suppression_zone_action,
)
from app.combat.suppression_zone_effects import sync_suppression_zone_effects
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=7)
    return member


def test_darkness_aura_uses_once_and_moves_with_source() -> None:
    card = next(card for card in load_monster_source_2014() if card.id == "darkmantle")
    caster = _member(
        compile_combatant(adapt_monster_mechanics_2014(card)), "caster", "monsters", 1,
    )
    target = _member(build_commoner(), "target", "heroes", 3)
    setup = EncounterSetup(
        heroes=[target], monsters=[caster], ruleset="2014", hero_total_levels=1,
        monster_total_cr=card.challenge_rating, map_definition=build_standard_iron_pit_map(),
    )
    begin_turn(caster.state)
    selected = choose_suppression_zone_action(caster, setup, "1:caster")
    assert selected is not None
    action, center = selected
    assert center == caster.state.position
    event, _ = cast_suppression_zone(1, 1, caster, setup, action, center, "1:caster")
    assert event.description == "Darkmantle uses Darkness Aura (1/Day)."
    assert event.resource_remaining == 0
    assert caster.state.concentration is not None
    assert target.state.active_effect_ids.count("magical-darkness") == 1
    assert setup.suppression_zones[0].follows_source

    caster.state.position = GridPosition(x=8, y=7)
    sync_suppression_zone_effects(setup, 1)
    assert setup.suppression_zones[0].position == caster.state.position
    assert "magical-darkness" not in target.state.active_effect_ids
    assert "magical-darkness" in caster.state.active_effect_ids

    begin_turn(caster.state)
    caster.state.concentration = None
    assert choose_suppression_zone_action(caster, setup, "2:caster") is None
