"""Printed reverse-visibility gates and live repeat-save disadvantage are source-neutral."""
from __future__ import annotations

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.timed_condition_saves import resolve_repeat_save
from app.combat.state import build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import _compile_save
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting
from app.domain.timed_effects import TimedEffect


def _member(cid: str, side: str, x: int):
    state = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    state.position = GridPosition(x=x, y=1)
    return EncounterCombatant(combatant_id=cid, side=side, position_ft=x * 5, state=state)


def _pair():
    source = _member("source-renamed", "monsters", 1)
    target = _member("target", "heroes", 2)
    setup = EncounterSetup(
        heroes=[target], monsters=[source], hero_total_levels=1,
        monster_total_cr="1", ruleset="2014",
        map_definition=BattleMapDefinition(id="reverse-sight-test", width_squares=12, height_squares=12),
    )
    return source, target, setup


def test_reverse_sight_is_card_data_and_filters_area_before_action_spend():
    source, target, setup = _pair()
    definition = SaveCapabilityDefinition(
        id="renamed-gaze", name="Renamed Gaze", save_ability="wisdom",
        dc=13, range_ft=60,
        target_scope="all-other-creatures",
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=60),
        requires_target_to_see_source=True,
    )
    action = _compile_save(definition)
    assert action.requires_target_to_see_source
    assert legal_area_save_placements(source, setup, action)[0].target_ids == ("target",)
    target.state.active_effect_ids.append("blinded")
    assert legal_area_save_placements(source, setup, action) == []
    assert source.state.action_available
    # Ordinary area saves must NOT acquire reverse visibility requirements.
    unguarded = SavingThrowAction.model_validate({
        **action.model_dump(), "requires_target_to_see_source": False,
    })
    assert legal_area_save_placements(source, setup, unguarded)[0].target_ids == ("target",)


def test_source_visible_repeat_save_has_disadvantage_only_while_target_can_see_source():
    source, target, setup = _pair()
    effect = TimedEffect(
        effect_id="frightened", source_id=source.combatant_id,
        source_effect_id="renamed-gaze",
        repeat_save_ability="wisdom", repeat_save_dc=12,
        repeat_save_timing="target_turn_end",
        repeat_save_disadvantage_while_source_visible=True,
    )
    visible_roll, _, _ = resolve_repeat_save(target, effect, FixedDiceProvider([19, 2]), 1, setup)
    assert len(visible_roll.rolls) == 2
    assert visible_roll.selected_roll == 2

    target.state.active_effect_ids.append("blinded")
    hidden_roll, _, _ = resolve_repeat_save(target, effect, FixedDiceProvider([19]), 1, setup)
    assert len(hidden_roll.rolls) == 1

    # Non-gated repeat saves remain normal even with the source visible.
    target.state.active_effect_ids.remove("blinded")
    ordinary = effect.model_copy(update={"repeat_save_disadvantage_while_source_visible": False})
    normal_roll, _, _ = resolve_repeat_save(target, ordinary, FixedDiceProvider([19]), 1, setup)
    assert len(normal_roll.rolls) == 1
