"""2014 Barbed Hide uses existing grapple/typed-damage effects on source turn."""
from __future__ import annotations

from app.combat.grapple import apply_grapple, release_grapple
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_grappler_damage_2014 import source_turn_grappler_damage_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row


class FixedDice:
    def roll(self, size: int) -> int:
        assert size == 10
        return 7


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "barbed-devil")


def _setup():
    devil = compile_combatant(adapt_basic_monster_2014(_source()))
    fighter = build_demo_fighter()
    monster = EncounterCombatant(
        combatant_id="devil", side="monsters", position_ft=0,
        state=build_combatant_state(devil),
    )
    heroes = [
        EncounterCombatant(
            combatant_id=f"hero-{i}", side="heroes", position_ft=5,
            state=build_combatant_state(fighter),
        ) for i in range(2)
    ]
    setup = EncounterSetup(
        heroes=heroes, monsters=[monster], hero_total_levels=2,
        monster_total_cr="5", ruleset="2014",
    )
    return monster, heroes, setup


def test_barbed_hide_source_verified_immutable_and_exported():
    source = _source()
    snapshot = source.model_dump_json()
    specs = source_turn_grappler_damage_2014(source)
    assert len(specs) == 1
    assert (specs[0].source_name, specs[0].target_relation,
            specs[0].dice_count, specs[0].dice_size, specs[0].damage_type) == (
                "Barbed Hide", "creatures_grappling_source", 1, 10, DamageType.PIERCING,
            )
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template_row(template)["source_turn_relation_damages"] == [specs[0].model_dump(mode="json")]
    assert source.model_dump_json() == snapshot
    drift = source.model_copy(update={
        "source_traits": source.source_traits.replace("grappling it", "adjacent to it"),
    })
    assert source_turn_grappler_damage_2014(drift) == []
    assert "source:trait" in basic_blockers_2014(drift)


def test_source_turn_only_current_grapplers_get_damage_and_released_one_does_not():
    monster, heroes, setup = _setup()
    first, second = heroes
    start = first.state.current_hp
    assert resolve_source_turn_relation_damage(1, 1, monster, setup, FixedDice()) == ([], 1)
    apply_grapple(monster.state, first.combatant_id, 12, 10)
    apply_grapple(monster.state, second.combatant_id, 12, 10)
    events, sequence = resolve_source_turn_relation_damage(1, 1, monster, setup, FixedDice())
    assert sequence == 3
    assert len(events) == 2
    assert all(e.feature_id == "Barbed Hide" for e in events)
    assert first.state.current_hp == start - 7
    assert second.state.current_hp == start - 7
    assert all(e.hp_after == start - 7 for e in events)
    assert resolve_source_turn_relation_damage(3, 1, first, setup, FixedDice()) == ([], 3)
    release_grapple(monster.state, first.combatant_id)
    events, sequence = resolve_source_turn_relation_damage(3, 2, monster, setup, FixedDice())
    assert len(events) == 1 and events[0].target_id == second.combatant_id and sequence == 4
    first.state.is_dead = True
    assert all(e.target_id != first.combatant_id for e in events)


def test_source_turn_damage_respects_type_defenses_and_disappears_after_grapple_ends():
    monster, heroes, setup = _setup()
    target, other = heroes
    target.state.template = target.state.template.model_copy(update={
        "damage_immunities": [DamageType.PIERCING],
    })
    apply_grapple(monster.state, target.combatant_id, 12, 10)
    before = target.state.current_hp
    events, _ = resolve_source_turn_relation_damage(4, 2, monster, setup, FixedDice())
    assert len(events) == 1 and target.state.current_hp == before
    assert events[0].damage_components[0].applied_total == 0
    target.position_ft = 40
    assert resolve_source_turn_relation_damage(5, 3, monster, setup, FixedDice()) == ([], 5)
    monster.state.is_dead = True
    assert resolve_source_turn_relation_damage(6, 3, monster, setup, FixedDice()) == ([], 6)
    fresh = build_combatant_state(monster.state.template)
    assert fresh.grapple_sources == []
