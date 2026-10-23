"""2014 Harpy audible maintained control binds to universal save/effect primitives."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_audible_maintained_control_2014 import (
    semantic_audible_control_candidate_names_2014,
    source_proven_audible_maintained_controls_2014,
)
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source():
    return next(card for card in load_monster_source_2014() if card.id == "harpy")


def _member(cid, side, position, template):
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_printed_song_is_complete_declarative_control_and_card_stays_immutable():
    source = _source()
    before = source.model_dump_json()
    assert semantic_audible_control_candidate_names_2014(source) == ("Luring Song",)
    action, = source_proven_audible_maintained_controls_2014(source)
    rider = action.failed_save_timed_effect
    assert (action.id, action.name, action.range_ft, action.dc) == (
        "luring-song", "Luring Song", 300, 11,
    )
    assert action.target_scope == "all-other-creatures"
    assert action.area.radius_ft == 300
    assert action.requires_target_hearing and action.magical_effect
    assert action.required_target_creature_types == ["humanoid", "giant"]
    assert action.prohibited_target_source_effect_ids == ["luring-song"]
    assert rider.effect_id == "charmed"
    assert rider.additional_effect_ids == ["incapacitated"]
    assert rider.duration_rounds is None
    assert rider.repeat_save_timing == "target_turn_end"
    assert rider.damage_repeat_save_trigger == "other_than_effect_source"
    assert rider.repeat_save_before_damaging_terrain
    assert rider.source_maintenance_action_cost == "bonus_action"
    assert rider.turn_behavior == "forced_approach_source"
    assert rider.ends_if_source_incapacitated and rider.ends_if_source_dead
    assert rider.source_effect_immunity_on_end
    assert action.source_effect_immunity_on_success
    assert source.model_dump_json() == before
    assert basic_blockers_2014(source) == ()


def test_incomplete_printed_lifecycle_fails_closed():
    source = _source()
    mutant = source.model_copy(update={
        "source_actions": source.source_actions.replace(
            "The harpy must take a bonus action on its subsequent turns to continue singing.",
            "The harpy continues singing automatically.",
        )
    })
    assert semantic_audible_control_candidate_names_2014(mutant) == ("Luring Song",)
    assert source_proven_audible_maintained_controls_2014(mutant) == []
    assert "source:extra-action" in basic_blockers_2014(mutant)


def test_existing_matching_source_effect_blocks_other_source_until_song_ends():
    harpy_template = compile_combatant(adapt_basic_monster_2014(_source()))
    target_template = build_aurelia_brightshield_2014(1).model_copy(\n        update={"max_hp": 60, "creature_type": "humanoid"}\n    )
    first = _member("first-harpy", "monsters", 0, harpy_template)
    second = _member("second-harpy", "monsters", 5, harpy_template)
    target = _member("target", "heroes", 10, target_template)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[first, second],
        hero_total_levels=1,
        monster_total_cr="2",
        ruleset="2014",
    )
    action = next(item for item in first.state.template.saving_throw_actions
                  if item.id == "luring-song")
    resolve_save_action(
        1, 1, first, target, action, 10, FixedDiceProvider([1]), setup=setup,
    )
    assert {"charmed", "incapacitated"} <= set(target.state.active_effect_ids)
    assert not legal_save_action(
        action, target, 5, source_id=second.combatant_id, actor=second,
    )

    first.state.is_dead = True
    first.state.is_alive = False
    cleanup_disabled_source_effects(setup)
    assert "charmed" not in target.state.active_effect_ids
    assert "incapacitated" not in target.state.active_effect_ids
    assert not has_source_effect_immunity(target.state, action.id, first.combatant_id)
    assert legal_save_action(
        action, target, 5, source_id=second.combatant_id, actor=second,
    )
