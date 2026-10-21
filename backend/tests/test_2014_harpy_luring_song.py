"""2014 Harpy Luring Song whole-card and combat integration regressions."""
from __future__ import annotations

from app.combat.area_save_actions import resolve_area_save
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import legal_save_action
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.source_maintenance import resolve_source_maintenance
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_luring_song_2014 import source_proven_luring_song_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "harpy")


def _member(cid, side, x, template):
    actor = EncounterCombatant(
        combatant_id=cid, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    actor.state.position = GridPosition(x=x, y=1)
    return actor


def _battle():
    harpy_template = compile_combatant(adapt_basic_monster_2014(_source()))
    harpy = _member("source", "monsters", 1, harpy_template)
    other = _member("other-source", "monsters", 2, harpy_template)
    base = build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 60})
    ally = _member("humanoid-ally", "monsters", 3, base.model_copy(update={"kind": "monster"}))
    human = _member("human", "heroes", 4, base)
    giant = _member("giant", "heroes", 5, base.model_copy(update={"creature_type": "giant"}))
    beast = _member("beast", "heroes", 6, base.model_copy(update={"creature_type": "beast"}))
    deaf = _member("deaf", "heroes", 7, base)
    deaf.state.active_effect_ids.append("deafened")
    setup = EncounterSetup(
        heroes=[human, giant, beast, deaf],
        monsters=[harpy, other, ally],
        hero_total_levels=4, monster_total_cr="3", ruleset="2014",
        map_definition=BattleMapDefinition(id="harpy-song", width_squares=24, height_squares=16),
    )
    action = next(item for item in harpy.state.template.saving_throw_actions
                  if item.id == "luring-song")
    return harpy, other, ally, human, giant, beast, deaf, setup, action


def test_luring_song_is_whole_clause_proven_and_fully_parameterized():
    source = _source()
    action, = source_proven_luring_song_2014(source)
    rider = action.failed_save_timed_effect
    assert (action.name, action.action_cost, action.dc) == ("Luring Song", "action", 11)
    assert action.range_ft == action.area.radius_ft == 300
    assert action.target_scope == "all-other-creatures" and action.max_targets == 20
    assert action.requires_target_hearing and action.magical_effect
    assert action.required_target_creature_types == ["humanoid", "giant"]
    assert action.source_effect_immunity_on_success
    assert rider.effect_id == "charmed"
    assert rider.additional_effect_ids == ["incapacitated"]
    assert rider.turn_behavior == "forced_approach_source"
    assert rider.repeat_save_timing == "target_turn_end"
    assert rider.damage_repeat_save_trigger == "other_than_effect_source"
    assert rider.repeat_save_before_damaging_terrain
    assert rider.ends_if_source_incapacitated
    assert rider.source_maintenance_action_cost == "bonus_action"
    assert rider.source_effect_immunity_on_repeat_save_success
    assert not rider.source_effect_immunity_on_end
    assert rider.exclusive_source_effect_group_id == "audible-luring-song"
    assert basic_blockers_2014(source) == ()
    for previous, changed in (
        ("Every humanoid and giant", "Every creature"),
        ("DC 11 Wisdom", "DC 12 Wisdom"),
        ("bonus action on its subsequent turns", "action on its subsequent turns"),
        ("ignores the songs of other harpies", "hears every other song"),
        ("source other than the harpy", "any source"),
        ("next 24 hours", "next 1 hour"),
    ):
        mutant = source.model_copy(update={
            "source_actions": source.source_actions.replace(previous, changed),
        })
        assert source_proven_luring_song_2014(mutant) == []
        assert "source:extra-action" in basic_blockers_2014(mutant)


def test_song_targets_only_hearing_humanoids_and_giants_then_groups_conditions():
    harpy, _other, ally, human, giant, beast, deaf, setup, action = _battle()
    placement, = legal_area_save_placements(harpy, setup, action)
    assert set(placement.target_ids) == {"humanoid-ally", "human", "giant"}

    events, _ = resolve_area_save(
        1, 1, harpy, setup, action, placement, FixedDiceProvider([1, 1, 1]),
    )

    assert {event.target_id for event in events} == set(placement.target_ids)
    for target in (ally, human, giant):
        assert {"charmed", "incapacitated"} <= set(target.state.active_effect_ids)
        primary = next(effect for effect in target.state.timed_effects
                       if effect.effect_id == "charmed")
        secondary = next(effect for effect in target.state.timed_effects
                         if effect.effect_id == "incapacitated")
        assert primary.source_effect_id == secondary.source_effect_id == action.id
        assert primary.source_maintenance_action_cost == "bonus_action"
        assert secondary.source_maintenance_action_cost == "none"
    assert "charmed" not in beast.state.active_effect_ids
    assert "charmed" not in deaf.state.active_effect_ids


def test_song_continues_once_ignores_competitors_and_grants_immunity_only_on_save():
    harpy, other, _ally, human, giant, _beast, _deaf, setup, action = _battle()
    placement, = legal_area_save_placements(harpy, setup, action)
    resolve_area_save(1, 1, harpy, setup, action, placement, FixedDiceProvider([1, 1, 1]))

    other_action = next(item for item in other.state.template.saving_throw_actions
                        if item.id == "luring-song")
    assert not legal_save_action(
        other_action, human, 10, source_id=other.combatant_id, actor=other,
    )

    harpy.state.turns_started = 1
    events, _ = resolve_source_maintenance(10, 2, harpy, setup)
    assert [event.feature_id for event in events] == ["luring-song"]
    assert harpy.state.bonus_action_available is False

    events, _ = resolve_target_condition_timing(
        20, 2, human, "target_turn_end", FixedDiceProvider([20]), setup,
    )
    assert events[0].save_succeeded is True
    assert "charmed" not in human.state.active_effect_ids
    assert "incapacitated" not in human.state.active_effect_ids
    assert has_source_effect_immunity(human.state, action.id, harpy.combatant_id)

    harpy.state.active_effect_ids.append("incapacitated")
    cleanup_disabled_source_effects(setup)
    assert "charmed" not in giant.state.active_effect_ids
    assert not has_source_effect_immunity(giant.state, action.id, harpy.combatant_id)
