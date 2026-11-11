"""Source-neutral creature-space entry: Python combat, card schema, and source pins."""
from __future__ import annotations

import logging

from app.combat.creature_space_entry import resolve_creature_space_entry
from app.combat.dice import FixedDiceProvider
from app.combat.grid_reaction_movement import move_toward_on_grid
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_fire_form_entry_2014 import fire_form_space_entry_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _scene(target_side: str = "heroes"):
    try:
        card = next(m for m in load_monster_source_2014() if m.id == "fire-elemental")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        target = EncounterCombatant(
            combatant_id="target", side=target_side, position_ft=0,
            state=build_combatant_state(build_goblin_warrior().model_copy(
                update={"max_hp": 100},
            )),
        )
        owner.state.position = GridPosition(x=0, y=0)
        target.state.position = GridPosition(x=1, y=1)
        setup = EncounterSetup(
            heroes=[target] if target_side == "heroes" else [],
            monsters=[owner, *([target] if target_side == "monsters" else [])],
            ruleset="2014", hero_total_levels=2, monster_total_cr="5",
            map_definition=BattleMapDefinition(
                id="entry", width_squares=8, height_squares=8,
            ),
        )
        return card, template, owner, target, setup
    except Exception:
        logger.exception("Creature-space entry combat setup failed.")
        raise


def test_source_bound_passive_compiles_hostile_space_ability_without_mutation():
    try:
        card, template, *_ = _scene()
        before = card.model_dump_json()
        assert fire_form_space_entry_2014(card) is not None
        assert template.source_allows_hostile_overlap
        action = next(a for a in template.timed_self_buff_actions if a.name == "Fire Form")
        assert action.activation_timing == "passive"
        assert action.creature_space_entry_damage is not None
        spec = action.creature_space_entry_damage
        assert (spec.dice_count, spec.dice_size, spec.damage_type.value) == (1, 10, "fire")
        assert spec.recurring_damage.tick_timing == "target_turn_start"
        assert "Fire Form" not in unsupported_traits_2014(card)
        row = template_row(template)
        passive = next(a for a in row["timed_self_buff_actions"] if a["name"] == "Fire Form")
        assert passive["creatureSpaceEntryDamage"]["recurringDamage"]["effectId"] == "burning"
        assert row["source_allows_hostile_overlap"] is True
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Fire Form source and browser schema binding failed.")
        raise


def test_first_entry_deals_typed_damage_and_attaches_nonstacking_burning():
    try:
        _, _, owner, target, setup = _scene()
        owner.state.position = GridPosition(x=1, y=1)
        events, count = resolve_creature_space_entry(
            1, 1, owner, setup, FixedDiceProvider([7]), "1:owner",
        )
        assert count == 2 and len(events) == 1
        assert target.state.current_hp == 93
        assert events[0].feature_id == "Fire Form"
        effects = [e for e in target.state.timed_effects if e.effect_id == "burning"]
        assert len(effects) == 1
        assert (effects[0].start_of_turn_dice_count, effects[0].start_of_turn_dice_size) == (1, 10)
        repeated, _ = resolve_creature_space_entry(
            2, 1, owner, setup, FixedDiceProvider([9]), "1:owner",
        )
        assert not repeated and target.state.current_hp == 93
        next_turn, _ = resolve_creature_space_entry(
            2, 2, owner, setup, FixedDiceProvider([4]), "2:owner",
        )
        assert len(next_turn) == 1 and target.state.current_hp == 89
        assert len([e for e in target.state.timed_effects if e.effect_id == "burning"]) == 1
    except Exception:
        logger.exception("Universal per-target entry and burning lifecycle failed.")
        raise


def test_entering_allied_square_still_triggers_the_printed_creature_clause():
    try:
        _, _, owner, ally, setup = _scene("monsters")
        owner.state.position = ally.state.position.model_copy(deep=True)
        result, _ = resolve_creature_space_entry(
            1, 1, owner, setup, FixedDiceProvider([6]), "1:owner",
        )
        assert len(result) == 1 and ally.state.current_hp == 94
    except Exception:
        logger.exception("Source-declared ally-space ignition failed.")
        raise


def test_real_grid_step_enters_enemy_square_and_triggers_fire_form():
    try:
        _, _, owner, target, setup = _scene()
        events, _, moved = move_toward_on_grid(
            1, 1, owner, target, setup, 0, FixedDiceProvider([7]), turn_key="1:owner",
        )
        assert moved is not None and owner.state.position == target.state.position
        assert target.state.current_hp == 93
        assert any(e.feature_id == "Fire Form" for e in events)
    except Exception:
        logger.exception("Real grid space-entry integration failed.")
        raise


def test_source_mutation_and_monster_rename_proof():
    try:
        card, *_ = _scene()
        renamed = card.model_copy(update={"id": "generic-fire", "name": "Generic Fire"})
        assert fire_form_space_entry_2014(renamed) == fire_form_space_entry_2014(card)
        for previous, changed in (
            ("first time it enters", "every time it enters"),
            ("catches fire", "feels warm"),
            ("1 inch", "2 inches"),
        ):
            modified = card.model_copy(update={
                "source_traits": card.source_traits.replace(previous, changed),
            })
            assert modified.source_traits != card.source_traits
            assert fire_form_space_entry_2014(modified) is None
            assert "Fire Form" in unsupported_traits_2014(modified)
    except Exception:
        logger.exception("Renamed source and tamper resistance failed.")
        raise
