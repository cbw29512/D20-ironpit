"""Wall-creation exclusions follow printed source and never grant fake combat damage."""
from __future__ import annotations

import logging

from app.combat.save_zone_landing import choose_damaging_save_zone
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.arena_wall_spell_policy import is_arena_unavailable_wall_effect
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.monster_arena_action_policy_2014 import (
    arena_unavailable_recharge_ids_2014,
    arena_unavailable_wall_action_labels_2014,
)
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_barrier_2014 import source_barrier_parameters_2014
from app.content.monsters import build_commoner
from app.content.shared_zone_spells_2014 import wall_of_fire_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def _ice():
    try:
        monsters = load_monster_source_2014()
        assert len(monsters) == 327
        return next(item for item in monsters if item.id == "ice-devil")
    except Exception:
        logger.exception("Failed to read pinned 2014 wall source.")
        raise


def test_exact_printed_wall_is_neutral_without_deleting_card_or_recharge():
    try:
        ice = _ice()
        before = ice.model_dump_json()
        assert source_barrier_parameters_2014(ice) is not None
        assert arena_unavailable_wall_action_labels_2014(ice) == {"wall of ice"}
        assert "wall-of-ice" in arena_unavailable_recharge_ids_2014(ice)
        assert basic_blockers_2014(ice) == ()
        assert "Wall of Ice (Recharge 6)" in ice.action_names
        assert ice.model_dump_json() == before
        named_other = ice.model_copy(update={"id": "renamed-ice", "name": "Another Creature"})
        assert arena_unavailable_wall_action_labels_2014(named_other) == {"wall of ice"}
        assert basic_blockers_2014(named_other) == ()
    except Exception:
        logger.exception("Arena wall printed-source classification failed.")
        raise



def test_ice_devil_keeps_three_melee_attacks_without_creating_wall_state():
    """Banning a wall must never ban the creature's source combat damage."""
    try:
        ice = _ice()
        untouched = ice.model_dump_json()
        template = compile_combatant(adapt_basic_monster_2014(ice))
        assert template.attack_action is not None
        # Compiled attack IDs are universally namespaced by edition and source card.
        expected_ids = {
            name: attack_id_2014(ice, name) for name in ("bite", "claws", "tail")
        }
        assert [slot.attack_ids for slot in template.attack_action.slots] == [
            [expected_ids["bite"]], [expected_ids["claws"]], [expected_ids["tail"]],
        ]
        attacks = [
            item for item in [template.weapon_attack, *template.alternate_weapon_attacks]
            if item is not None
        ]
        assert {attack.id for attack in attacks} == set(expected_ids.values())
        assert all(attack.weapon.attack_kind.value == "melee" for attack in attacks)
        assert all(attack.attack_bonus == 10 for attack in attacks)
        # The wall-only Recharge is not a selectable Action or fight resource.
        assert not template.persistent_barrier_actions
        assert not any(resource.id == "wall-of-ice" for resource in template.resources)
        assert ice.model_dump_json() == untouched
    except Exception:
        logger.exception("Ice Devil non-wall melee fight regression failed.")
        raise


def test_wall_source_mutation_reinstates_real_blockers():
    try:
        ice = _ice()
        for old, new in (
            ("30 hit points", "40 hit points"),
            ("17 Constitution", "16 Constitution"),
            ("5d6", "6d6"),
        ):
            assert old in ice.source_actions
            changed = ice.model_copy(update={
                "source_actions": ice.source_actions.replace(old, new),
            })
            assert arena_unavailable_wall_action_labels_2014(changed) == frozenset()
            assert "wall-of-ice" not in arena_unavailable_recharge_ids_2014(changed)
            assert "source:extra-action" in basic_blockers_2014(changed)
            assert "mechanic:recharge" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Source-mutation fail-closed wall proof failed.")
        raise


def test_wall_spells_remain_reference_data_but_are_not_fight_choices():
    try:
        assert is_arena_unavailable_wall_effect("wall-of-ice")
        assert is_arena_unavailable_wall_effect("wall-of-fire")
        assert is_arena_unavailable_wall_effect("wall-of-stone")
        assert not is_arena_unavailable_wall_effect("fireball")
        wall = wall_of_fire_2014(18)
        assert wall.name == "Wall of Fire" and wall.damage_dice_count == 5
        caster = EncounterCombatant(
            combatant_id="caster", side="heroes", position_ft=5,
            state=build_combatant_state(build_seraphine_dawnshield_level(9)),
        )
        enemy = EncounterCombatant(
            combatant_id="enemy", side="monsters", position_ft=30,
            state=build_combatant_state(build_commoner()),
        )
        caster.state.position = GridPosition(x=1, y=7)
        enemy.state.position = GridPosition(x=6, y=7)
        setup = EncounterSetup(
            heroes=[caster], monsters=[enemy], ruleset="2024",
            hero_total_levels=9, monster_total_cr="0",
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(caster.state)
        original = caster.state.template.persistent_save_zone_actions
        caster.state.template = caster.state.template.model_copy(update={
            "persistent_save_zone_actions": [wall, *original],
        })
        result = choose_damaging_save_zone(caster, setup, "1:caster")
        assert result is None or result[0].id != "wall-of-fire"
        assert wall.id == "wall-of-fire"
        assert not setup.save_zones
    except Exception:
        logger.exception("Wall combat selection exclusion failed.")
        raise
