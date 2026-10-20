"""Banshee's printed visual fear Action reuses universal all-creature, sight and condition rules."""
from __future__ import annotations

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_save_actions import resolve_area_save
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_visual_save_bindings_2014 import source_proven_visual_saves_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "banshee")


def _member(cid, side, x, template):
    actor = EncounterCombatant(
        combatant_id=cid, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    actor.state.position = GridPosition(x=x, y=1)
    return actor


def _battle():
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    banshee = _member("banshee", "monsters", 1, template)
    living = build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60})
    ally = _member("living-friend", "monsters", 2, living.model_copy(update={"kind": "monster"}))
    undead = _member("undead-friend", "monsters", 3, living.model_copy(update={
        "creature_type": "undead", "kind": "monster",
    }))
    construct = _member("construct-friend", "monsters", 4, living.model_copy(update={
        "creature_type": "construct", "kind": "monster",
    }))
    foe = _member("visible-foe", "heroes", 5, living)
    blind = _member("blind-foe", "heroes", 6, living)
    blind.state.active_effect_ids.append("blinded")
    setup = EncounterSetup(
        heroes=[foe, blind], monsters=[banshee, ally, undead, construct],
        hero_total_levels=2, monster_total_cr="4", ruleset="2014",
        map_definition=BattleMapDefinition(id="banshee-visage", width_squares=15, height_squares=12),
    )
    action = next(item for item in banshee.state.template.saving_throw_actions
                  if item.id == "horrifying-visage")
    return banshee, ally, undead, construct, foe, blind, setup, action


def test_printed_visual_fear_is_source_proven_and_fully_parameterized():
    source = _source()
    action, = source_proven_visual_saves_2014(source)
    assert (action.name, action.save_ability, action.dc) == ("Horrifying Visage", "wisdom", 13)
    assert action.target_scope == "all-other-creatures"
    assert action.area.radius_ft == 60 and action.requires_target_to_see_source
    assert action.excluded_target_creature_types == ["undead"]
    assert action.source_effect_immunity_on_success
    assert action.failed_save_timed_effect.effect_id == "frightened"
    assert action.failed_save_timed_effect.duration_rounds == 10
    assert action.failed_save_timed_effect.repeat_save_timing == "target_turn_end"
    assert action.failed_save_timed_effect.repeat_save_disadvantage_while_source_visible
    assert action.failed_save_timed_effect.source_effect_immunity_on_end
    assert basic_blockers_2014(source) == ()
    for previous, changed in (
        ("Each non-undead creature", "Each enemy creature"),
        ("that can see her", "that can hear her"),
        ("with disadvantage", "with advantage"),
        ("for 1 minute", "for 2 minutes"),
        ("24 hours", "1 hour"),
    ):
        mutant = source.model_copy(update={"source_actions": source.source_actions.replace(previous, changed)})
        assert source_proven_visual_saves_2014(mutant) == []
        assert "source:extra-action" in basic_blockers_2014(mutant)


def test_visage_targets_friendly_creatures_but_not_undead_or_blind_creatures():
    banshee, ally, undead, construct, foe, blind, setup, action = _battle()
    placements = legal_area_save_placements(banshee, setup, action)
    assert len(placements) == 1
    ids = set(placements[0].target_ids)
    assert ids == {"visible-foe", "living-friend", "construct-friend"}
    assert not ids & {"banshee", "undead-friend", "blind-foe"}
    # Independently fail the first source-position eligible target(s).
    events, _ = resolve_area_save(
        1, 1, banshee, setup, action, placements[0],
        FixedDiceProvider([1, 1, 1]),
    )
    assert {event.target_id for event in events} == ids
    assert all(event.save_succeeded is False for event in events)
    assert "frightened" in ally.state.active_effect_ids
    assert "frightened" in foe.state.active_effect_ids
    assert "frightened" in construct.state.active_effect_ids
    assert "frightened" not in undead.state.active_effect_ids
    assert "frightened" not in blind.state.active_effect_ids
    assert banshee.state.template.source_trait_names == ["Detect Life", "Incorporeal Movement"]


def test_visage_repeat_disadvantage_ends_with_lost_sight_and_grants_immunity():
    banshee, ally, undead, construct, foe, blind, setup, action = _battle()
    initial = next(p for p in legal_area_save_placements(banshee, setup, action)
                   if "visible-foe" in p.target_ids)
    resolve_area_save(1, 1, banshee, setup, action, initial, FixedDiceProvider([1, 1, 1]))
    effect = next(e for e in foe.state.timed_effects if e.source_effect_id == action.id)
    assert effect.repeat_save_disadvantage_while_source_visible
    # Still seeing the source: 20 and 1 means Disadvantage picks 1, so Frightened remains.
    events, _ = resolve_target_condition_timing(
        10, 1, foe, "target_turn_end", FixedDiceProvider([20, 1]), setup,
    )
    assert events[0].save_succeeded is False
    assert "frightened" in foe.state.active_effect_ids
    # Blinded now: only one die rolled; success ends Frightened and grants fight-local immunity.
    foe.state.active_effect_ids.append("blinded")
    events, _ = resolve_target_condition_timing(
        11, 2, foe, "target_turn_end", FixedDiceProvider([20]), setup,
    )
    assert events[0].save_succeeded is True
    assert "frightened" not in foe.state.active_effect_ids
    assert has_source_effect_immunity(foe.state, action.id, banshee.combatant_id)
    assert not any("horrifying-visage" == e.effect_id for e in foe.state.timed_effects)
