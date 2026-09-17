from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.modifier_stack import saving_throw_flat_bonus
from app.combat.paladin_auras_2014 import sync_paladin_auras_2014
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(level: int, ally_position: int = 5) -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    paladin = _member(build_aurelia_brightshield_2014(level), "aurelia", "heroes", 0)
    ally = _member(build_kael_stillwater_2014(1), "kael", "heroes", ally_position)
    enemy = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "commoner", "monsters", 30)
    return EncounterSetup(
        heroes=[paladin, ally], monsters=[enemy], hero_total_levels=level + 1,
        monster_total_cr="0", ruleset="2014",
    ), paladin, ally


def test_aura_of_protection_applies_inside_ten_feet_and_updates_save_math() -> None:
    setup, paladin, ally = _setup(6)
    sync_paladin_auras_2014(setup)

    assert saving_throw_flat_bonus(ally.state) == 2
    assert saving_throw_flat_bonus(paladin.state) == 0
    roll, succeeded = resolve_saving_throw(ally.state, "wisdom", 12, FixedDiceProvider([8]))
    assert roll is not None
    assert roll.modifier == 4
    assert succeeded is True


def test_aura_of_protection_is_removed_when_ally_leaves_range() -> None:
    setup, _, ally = _setup(6)
    sync_paladin_auras_2014(setup)
    assert saving_throw_flat_bonus(ally.state) == 2

    ally.position_ft = 15
    sync_paladin_auras_2014(setup)
    assert saving_throw_flat_bonus(ally.state) == 0


def test_devotion_and_courage_grant_dynamic_condition_immunity() -> None:
    setup, _, ally = _setup(10)
    sync_paladin_auras_2014(setup)
    assert condition_is_immune(ally.state, "charmed") is True
    assert condition_is_immune(ally.state, "frightened") is True

    ally.position_ft = 15
    sync_paladin_auras_2014(setup)
    assert condition_is_immune(ally.state, "charmed") is False
    assert condition_is_immune(ally.state, "frightened") is False


def test_incapacitated_or_dead_paladin_stops_granting_auras() -> None:
    setup, paladin, ally = _setup(10)
    paladin.state.is_unconscious = True
    sync_paladin_auras_2014(setup)
    assert saving_throw_flat_bonus(ally.state) == 0
    assert condition_is_immune(ally.state, "charmed") is False

    paladin.state.is_unconscious = False
    paladin.state.is_dead = True
    paladin.state.is_alive = False
    paladin.state.current_hp = 0
    sync_paladin_auras_2014(setup)
    assert saving_throw_flat_bonus(ally.state) == 0
    assert condition_is_immune(ally.state, "frightened") is False


def test_multiple_paladin_protection_auras_use_only_the_strongest_bonus() -> None:
    setup, first, ally = _setup(6)
    stronger = _member(build_aurelia_brightshield_2014(8), "aurelia-8", "heroes", 5)
    setup.heroes.insert(1, stronger)
    setup.hero_total_levels += 8

    sync_paladin_auras_2014(setup)
    assert first.state.template.progression_features.aura_of_protection_2014_bonus == 2
    assert stronger.state.template.progression_features.aura_of_protection_2014_bonus == 3
    assert saving_throw_flat_bonus(ally.state) == 3
    assert saving_throw_flat_bonus(first.state) == 1
    assert saving_throw_flat_bonus(stronger.state) == 0
