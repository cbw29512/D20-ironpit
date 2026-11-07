"""2014 Engulf is a source-typed Multiattack combination, not a name resolver."""
from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import cleanup_grapples, release_grapple
from app.combat.multiattack_hit_grapple import resolve_hit_grapple
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_engulf_source_2014 import source_engulf_profile_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "shambling-mound")


def _setup():
    source = _source()
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    hero = build_demo_fighter().model_copy(update={"max_hp": 100, "armor_class": 10})
    mound = EncounterCombatant(
        combatant_id="mound", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5,
        state=build_combatant_state(hero),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[mound], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    return source, mound, target, setup


def test_printed_engulf_source_compiles_without_identity_dispatch():
    source = _source()
    snapshot = source.model_dump_json()
    proof = source_engulf_profile_2014(source)
    assert proof is not None
    assert proof.attack_id == "slam" and proof.required_hits == 2
    assert proof.grapple_escape_dc == 14
    assert (proof.damage_dice_count, proof.damage_dice_size, proof.damage_bonus) == (2, 8, 4)
    assert (proof.save_ability, proof.save_dc) == ("constitution", 14)
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    assert template.attack_action.hit_grapple.attack_id == "2014-shambling-mound-slam"
    assert template.source_turn_relation_damages[-1].required_grapple_condition_id == "engulfed"
    assert source.model_dump_json() == snapshot
    renamed = source.model_copy(update={"id": "renamed-mound", "name": "Renamed Mound"})
    assert source_engulf_profile_2014(renamed) == proof


@pytest.mark.parametrize("old,new", [
    ("both attacks hit", "one attack hits"),
    ("escape DC 14", "escape DC 15"),
    ("unable to breathe", "able to breathe"),
    ("DC 14 Constitution", "DC 15 Constitution"),
    ("2d8 + 4", "2d8 + 5"),
    ("only one creature engulfed", "two creatures engulfed"),
])
def test_drift_in_full_source_fails_closed(old, new):
    source = _source()
    assert old in source.source_actions
    changed = source.model_copy(update={
        "source_actions": source.source_actions.replace(old, new),
    })
    assert source_engulf_profile_2014(changed) is None


def test_two_same_target_hits_required_and_escape_deletes_all_owned_conditions():
    source, mound, target, setup = _setup()
    slam_id = mound.state.template.attack_action.hit_grapple.attack_id
    assert resolve_hit_grapple(1, 1, mound, setup, [(slam_id, "target")]) == ([], 1)
    assert target.state.grapple_sources == []
    other = EncounterCombatant(
        combatant_id="other", side="heroes", position_ft=5,
        state=build_combatant_state(target.state.template),
    )
    setup.heroes.append(other)
    assert resolve_hit_grapple(1, 1, mound, setup, [
        (slam_id, "target"), (slam_id, "other"),
    ]) == ([], 1)
    events, seq = resolve_hit_grapple(1, 1, mound, setup, [
        (slam_id, "target"), (slam_id, "target"),
    ])
    assert seq == 2 and len(events) == 1 and events[0].feature_id == "Engulf"
    assert {"grappled", "restrained", "blinded", "unable-to-breathe", "engulfed"}.issubset(
        set(target.state.active_effect_ids)
    )
    assert target.state.swallowed is None  # No fictional outside total cover.
    assert target.state.grapple_sources[0].escape_dc == 14
    assert target.state.grapple_sources[0].moves_with_source is True
    assert resolve_hit_grapple(2, 1, mound, setup, [
        (slam_id, "other"), (slam_id, "other"),
    ]) == ([], 2)
    release_grapple(target.state, mound.combatant_id)
    assert not {"grappled", "restrained", "blinded", "unable-to-breathe", "engulfed"} & set(
        target.state.active_effect_ids
    )


def test_start_of_owner_turn_damage_requires_engulf_marker_and_ends_on_release():
    _, mound, target, setup = _setup()
    slam = mound.state.template.attack_action.hit_grapple.attack_id
    resolve_hit_grapple(1, 1, mound, setup, [(slam, "target"), (slam, "target")])
    hp = target.state.current_hp
    passed, _ = resolve_source_turn_relation_damage(
        2, 2, mound, setup, FixedDiceProvider([20]),
    )
    assert passed[0].save_succeeded is True
    assert target.state.current_hp == hp
    failed, _ = resolve_source_turn_relation_damage(
        3, 3, mound, setup, FixedDiceProvider([1, 8, 8]),
    )
    assert failed[0].save_succeeded is False
    assert target.state.current_hp == hp - 20
    mound.position_ft = 50
    cleanup_grapples(setup)
    assert target.state.grapple_sources  # This linked relationship moves with source.
    release_grapple(target.state, mound.combatant_id)
    assert resolve_source_turn_relation_damage(
        4, 4, mound, setup, FixedDiceProvider([1]),
    ) == ([], 4)
