from __future__ import annotations

import pytest

from app.combat.ally_context import has_adjacent_active_ally
from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.dice import FixedDiceProvider
from app.combat.once_per_turn_hit_damage import once_per_turn_weapon_hit_bonus_damages
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_once_per_turn_traits_2014 import martial_advantage_rider_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _member(monster_id: str, side: str, position_ft: int) -> EncounterCombatant:
    template = compile_combatant(adapt_basic_monster_2014(_source(monster_id)))
    return EncounterCombatant(
        combatant_id=monster_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_hobgoblin_martial_advantage_reuses_pack_tactics_adjacency() -> None:
    source = _source("hobgoblin")
    assert source.trait_names == ["Martial Advantage"]
    assert unsupported_traits_2014(source) == ()
    assert basic_blockers_2014(source) == ()

    hobgoblin = _member("hobgoblin", "monsters", 0)
    ally = _member("commoner", "monsters", 10)
    target = _member("commoner", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[hobgoblin, ally],
        hero_total_levels=1, monster_total_cr="1/2", ruleset="2014",
    )
    rider = hobgoblin.state.template.progression_features.once_per_turn_weapon_hit_damage_rider
    assert rider is not None
    assert (rider.source_name, rider.dice_count, rider.dice_size) == ("Martial Advantage", 2, 6)
    assert rider.requires_active_ally_adjacent_to_target is True

    adjacent = has_adjacent_active_ally(hobgoblin, target, setup)
    assert adjacent is True
    attack = hobgoblin.state.template.weapon_attack
    first = once_per_turn_weapon_hit_bonus_damages(
        hobgoblin.state, attack, "1:hobgoblin", target.state, adjacent,
    )
    assert first == [("Martial Advantage", 2, 6, 0, attack.weapon.damage_type)]
    assert once_per_turn_weapon_hit_bonus_damages(
        hobgoblin.state, attack, "1:hobgoblin", target.state, adjacent,
    ) == []


def test_martial_advantage_rejects_distant_or_incapacitated_ally() -> None:
    hobgoblin = _member("hobgoblin", "monsters", 0)
    ally = _member("commoner", "monsters", 20)
    target = _member("commoner", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[hobgoblin, ally],
        hero_total_levels=1, monster_total_cr="1/2", ruleset="2014",
    )
    attack = hobgoblin.state.template.weapon_attack
    assert has_adjacent_active_ally(hobgoblin, target, setup) is False
    assert once_per_turn_weapon_hit_bonus_damages(
        hobgoblin.state, attack, "2:hobgoblin", target.state, False,
    ) == []

    ally.position_ft = 10
    ally.state.active_effect_ids.append("stunned")
    assert has_adjacent_active_ally(hobgoblin, target, setup) is False
    assert once_per_turn_weapon_hit_bonus_damages(
        hobgoblin.state, attack, "3:hobgoblin", target.state, False,
    ) == []


@pytest.mark.parametrize("missing_text", ["Once per turn, ", "weapon "])
def test_martial_advantage_source_binding_fails_closed_when_semantics_are_missing(missing_text: str) -> None:
    source = _source("hobgoblin")
    assert source.source_traits is not None
    altered = source.model_copy(
        update={"source_traits": source.source_traits.replace(missing_text, "", 1)},
        deep=True,
    )
    with pytest.raises(ValueError, match="unsupported Martial Advantage wording"):
        martial_advantage_rider_2014(altered)


def test_martial_advantage_flows_through_shared_hit_damage_pipeline() -> None:
    hobgoblin = _member("hobgoblin", "monsters", 0)
    ally = _member("commoner", "monsters", 10)
    target = _member("guard", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[hobgoblin, ally],
        hero_total_levels=1, monster_total_cr="1/2", ruleset="2014",
    )
    attack = hobgoblin.state.template.weapon_attack
    affected = [hobgoblin.state, ally.state, target.state]

    first = resolve_attack_hit_damage(
        hobgoblin.state,
        target.state,
        attack,
        FixedDiceProvider([1, 5, 6]),
        critical=False,
        attack_mode=RollMode.NORMAL,
        turn_key="1:hobgoblin",
        bonus_damage=None,
        affected_states=affected,
        sneak_attack_ally_available=False,
        setup=setup,
    )
    martial = next(item for item in first.damage_components if item.source == "Martial Advantage")
    assert martial.rolls == [5, 6]
    assert martial.damage_type == attack.weapon.damage_type

    second = resolve_attack_hit_damage(
        hobgoblin.state,
        target.state,
        attack,
        FixedDiceProvider([1]),
        critical=False,
        attack_mode=RollMode.NORMAL,
        turn_key="1:hobgoblin",
        bonus_damage=None,
        affected_states=affected,
        sneak_attack_ally_available=False,
        setup=setup,
    )
    assert all(item.source != "Martial Advantage" for item in second.damage_components)

    ally.position_ft = 20
    third = resolve_attack_hit_damage(
        hobgoblin.state,
        target.state,
        attack,
        FixedDiceProvider([1]),
        critical=False,
        attack_mode=RollMode.NORMAL,
        turn_key="2:hobgoblin",
        bonus_damage=None,
        affected_states=affected,
        sneak_attack_ally_available=False,
        setup=setup,
    )
    assert all(item.source != "Martial Advantage" for item in third.damage_components)
