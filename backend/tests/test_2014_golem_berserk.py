from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_targeting import select_nearest_target
from app.combat.start_turn_timed_self_buffs import resolve_start_turn_timed_self_buff
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.content.capability_compiler import compile_combatant
from app.content.monster_berserk_2014 import berserk_self_buffs_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _sources():
    return {monster.id: monster for monster in load_monster_source_2014()}


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_2014_golems_bind_same_berserk_buff_with_source_hp_thresholds() -> None:
    source = _sources()
    flesh = berserk_self_buffs_2014(source["flesh-golem"])
    clay = berserk_self_buffs_2014(source["clay-golem"])

    assert len(flesh) == len(clay) == 1
    assert flesh[0].id == clay[0].id == "berserk"
    assert flesh[0].name == clay[0].name == "Berserk"
    assert flesh[0].start_turn_max_current_hp == 40
    assert clay[0].start_turn_max_current_hp == 60
    for action in (*flesh, *clay):
        assert action.activation_timing == "start_turn"
        assert (action.start_turn_roll_die_size, action.start_turn_roll_minimum) == (6, 6)
        assert action.ends_at_full_hp is True
        assert action.target_policy == "nearest_visible_creature"


def test_flesh_golem_berserk_uses_existing_self_buff_state_and_nearest_creature_policy() -> None:
    source = _sources()["flesh-golem"]
    template = compile_combatant(adapt_basic_monster_2014(source))
    actor = _member(template, "flesh", "monsters", 10)
    ally = _member(template, "ally", "monsters", 15)
    enemy = _member(template, "enemy", "heroes", 30)
    setup = EncounterSetup(
        heroes=[enemy], monsters=[actor, ally],
        hero_total_levels=1, monster_total_cr="5", ruleset="2014",
    )
    actor.state.current_hp = 40

    failed = resolve_start_turn_timed_self_buff(
        1, 1, actor, setup, FixedDiceProvider([5]),
    )
    assert failed is not None
    assert failed.feature_id == "berserk"
    assert failed.feature_roll is not None and failed.feature_roll.total == 5
    assert "berserk" not in actor.state.active_effect_ids

    activated = resolve_start_turn_timed_self_buff(
        2, 2, actor, setup, FixedDiceProvider([6]),
    )
    assert activated is not None
    assert activated.feature_roll is not None and activated.feature_roll.total == 6
    assert "berserk" in actor.state.active_effect_ids
    assert select_nearest_target(actor, setup) is ally

    healed = restore_hit_points(actor.state, template.max_hp)
    assert healed == template.max_hp - 40
    assert "berserk" not in actor.state.active_effect_ids
    assert select_nearest_target(actor, setup) is enemy
