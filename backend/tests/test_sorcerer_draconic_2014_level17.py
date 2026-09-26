from __future__ import annotations

from app.combat.precombat_spells import choose_defensive_spell, prepare_defenses
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import build_combatant_state


def _member(combatant_id: str, template, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_level_seventeen_extended_spell_binds_generic_duration_modifier() -> None:
    hero = build_nyra_emberveil_2014(17)

    assert [item.id for item in hero.spell_duration_modifiers] == ["extended-spell"]
    modifier = hero.spell_duration_modifiers[0]
    assert modifier.resource_id == "sorcery-points"
    assert modifier.resource_cost == 1
    assert modifier.duration_multiplier == 2
    assert modifier.maximum_duration_minutes == 1440


def test_extended_spell_doubles_greater_invisibility_and_spends_one_point() -> None:
    nyra = _member("nyra", build_nyra_emberveil_2014(17), "heroes", 0)
    target = _member("target", build_nyra_emberveil_2014(1), "heroes", 5)
    enemy = _member("enemy", build_nyra_emberveil_2014(1), "monsters", 30)
    setup = EncounterSetup(heroes=[nyra, target], monsters=[enemy])

    choice = choose_defensive_spell(nyra, setup)
    assert choice is not None
    spell, slot_level, _ = choice
    assert spell.id == "greater-invisibility"
    assert slot_level == 4
    assert hero_modifier := nyra.state.template.spell_duration_modifiers[0]
    assert hero_modifier.id == "extended-spell"

    before = next(item.current_uses for item in nyra.state.resources if item.id == "sorcery-points")
    events, _ = prepare_defenses(setup)

    assert events
    assert nyra.state.concentration is not None
    assert nyra.state.concentration.effect_id == "greater-invisibility"
    assert nyra.state.concentration.expires_round == 21
    after = next(item.current_uses for item in nyra.state.resources if item.id == "sorcery-points")
    assert after == before - 1
