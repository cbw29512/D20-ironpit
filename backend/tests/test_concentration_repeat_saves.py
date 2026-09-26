from __future__ import annotations

from app.combat.concentration_repeat_saves import (
    choose_concentration_repeat_save,
    resolve_concentration_repeat_save,
)
from app.combat.dice import FixedDiceProvider
from app.combat.replacement_forms import enter_replacement_form
from app.combat.state import build_combatant_state
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.concentration_repeat_saves import ConcentrationRepeatSaveAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import ConcentrationState
from app.domain.spells import SpellSaveAction


def _repeat_spell() -> SpellSaveAction:
    return SpellSaveAction(
        id="storm-pulse",
        name="Storm Pulse",
        level=3,
        action_cost="action",
        range_ft=120,
        area_radius_ft=5,
        save_ability="dexterity",
        dc=12,
        damage_dice_count=3,
        damage_dice_size=10,
        damage_type="lightning",
        success_damage="half",
        upcast_dice_per_level=1,
        concentration=True,
        duration_minutes=10,
    )


def _repeat_action() -> ConcentrationRepeatSaveAction:
    return ConcentrationRepeatSaveAction(
        id="storm-pulse-repeat",
        name="Storm Pulse",
        source_spell_id="storm-pulse",
        priority=80,
        source="test universal concentration repeat-save action",
    )


def _target() -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(update={
        "saving_throw_bonuses": {"dexterity": 0},
    })
    return EncounterCombatant(
        combatant_id="target",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(template),
    )


def test_repeat_save_uses_stored_slot_without_spending_another_slot() -> None:
    base = build_thalen_greenbough_2014(2)
    template = base.model_copy(update={
        "spell_save_actions": [_repeat_spell()],
        "concentration_repeat_save_actions": [_repeat_action()],
        "resources": [
            ResourceDefinition(id="spell-slot-4", name="Spell Slot 4", max_uses=1),
        ],
    })
    caster = EncounterCombatant(
        combatant_id="caster",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )
    caster.state.concentration = ConcentrationState(
        source_id="caster",
        effect_id="storm-pulse",
        started_round=1,
        expires_round=101,
        slot_level=4,
    )
    target = _target()
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[target],
        hero_total_levels=2,
        monster_total_cr="1",
        starting_distance_ft=30,
    )

    choice = choose_concentration_repeat_save(caster, setup)
    assert choice is not None
    assert choice.spell_choice.slot_level == 4

    events, _ = resolve_concentration_repeat_save(
        1,
        2,
        caster,
        setup,
        choice,
        "2:caster",
        FixedDiceProvider([1, 10, 10, 10, 10]),
    )

    assert caster.state.action_available is False
    assert caster.state.concentration is not None
    assert caster.state.concentration.effect_id == "storm-pulse"
    assert caster.state.resources[0].current_uses == 1
    save_event = next(event for event in events if event.event_type == "saving_throw")
    assert save_event.damage_components[0].rolls == [10, 10, 10, 10]
    assert save_event.damage_roll is not None
    assert save_event.damage_roll.total == 40


def test_repeat_save_reads_original_template_while_replacement_form_blocks_spellcasting() -> None:
    base = build_thalen_greenbough_2014(2)
    template = base.model_copy(update={
        "spell_save_actions": [_repeat_spell()],
        "concentration_repeat_save_actions": [_repeat_action()],
    })
    state = build_combatant_state(template)
    state.concentration = ConcentrationState(
        source_id="caster",
        effect_id="storm-pulse",
        started_round=1,
        expires_round=101,
        slot_level=3,
    )
    wolf = canonical_wild_shape_template_2014(2)
    active_form = compile_replacement_form_template(template, wolf)
    enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=active_form,
        action_cost="action",
        resource_id="wild-shape",
    )
    state.action_available = True
    assert state.template.spell_save_actions == []

    caster = EncounterCombatant(
        combatant_id="caster",
        side="heroes",
        position_ft=0,
        state=state,
    )
    target = _target()
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[target],
        hero_total_levels=2,
        monster_total_cr="1",
        starting_distance_ft=30,
    )

    choice = choose_concentration_repeat_save(caster, setup)

    assert choice is not None
    assert choice.action.id == "storm-pulse-repeat"
    assert choice.spell_choice.action.id == "storm-pulse"
    assert choice.spell_choice.slot_level == 3
