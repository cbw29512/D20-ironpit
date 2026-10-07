import pytest

from app.combat.action_economy import is_available
from app.combat.condition_rules import condition_speed_is_zero, close_hit_is_automatic_critical
from app.combat.effect_removal import choose_effect_removal_action, resolve_effect_removal
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import expire_start_of_turn_conditions
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def fixture():
    armor = next(item for item in build_basic_2014_monsters() if item.name == 'Animated Armor')
    caster = armor.model_copy(update={
        'name': 'Caster', 'effect_tag_condition_grants': [],
        'effect_removal_actions': [dispel_magic_2014('intelligence')],
        'resources': [ResourceDefinition(id='spell-slot-3', name='Slot', max_uses=2)],
    })
    def member(id, side, template, position):
        return EncounterCombatant(combatant_id=id, side=side, position_ft=position, state=build_combatant_state(template))
    actor = member('caster', 'heroes', caster, 0)
    target = member('target', 'monsters', armor.model_copy(update={'name': 'Renamed construct'}), 30)
    setup = EncounterSetup(heroes=[actor], monsters=[target], hero_total_levels=6, monster_total_cr='1', ruleset='2014')
    return actor, target, setup


def test_dispel_uses_shared_stunned_without_buff_save_or_hp_change():
    actor, target, setup = fixture()
    before = target.state.template.model_dump()
    action, effect = choose_effect_removal_action(actor, setup, '1:caster')
    event = resolve_effect_removal(1, 2, actor, setup, action, effect, None, '1:caster')
    assert event.applied_condition_ids == ['stunned']
    assert event.hp_before == event.hp_after == target.state.template.max_hp
    assert event.ability_check_roll is None and event.saving_throw_roll is None
    assert target.state.is_alive and not target.state.is_dead and not target.state.is_unconscious
    assert not close_hit_is_automatic_critical(target.state)
    assert condition_speed_is_zero(target.state)
    assert all(not is_available(target.state, cost) for cost in ['action', 'bonus_action', 'reaction'])
    assert not actor.state.action_available and actor.state.resources[0].current_uses == 1
    timed = target.state.timed_effects[0]
    assert timed.expires_round == 12 and timed.repeat_save_dc is None and not timed.ends_on_damage
    assert timed.source_id == actor.combatant_id and timed.source_effect_id == action.id
    assert expire_start_of_turn_conditions(2, 11, actor, setup)[0] == []
    actor.state.is_dead = True
    assert expire_start_of_turn_conditions(2, 12, actor, setup)[0][0].removed_condition_ids == ['stunned']
    assert target.state.active_effect_ids == []
    assert target.state.template.model_dump() == before
    assert build_combatant_state(target.state.template).timed_effects == []


@pytest.mark.parametrize('reason', ['range', 'immune', 'ordinary', 'already_stunned', 'slot'])
def test_illegal_or_redundant_targets_do_not_spend(reason):
    actor, target, setup = fixture()
    if reason == 'range': target.position_ft = 121
    if reason == 'immune': target.state.template = target.state.template.model_copy(update={'condition_immunities': ['stunned']})
    if reason == 'ordinary': target.state.template = target.state.template.model_copy(update={'effect_tag_condition_grants': []})
    if reason == 'already_stunned': target.state.active_effect_ids.append('stunned')
    if reason == 'slot': actor.state.resources[0].current_uses = 0
    assert choose_effect_removal_action(actor, setup, '1:caster') is None
    assert actor.state.action_available


def test_stale_target_and_spent_slot_revalidate_before_mutation():
    for change in ['range', 'slot']:
        actor, target, setup = fixture()
        action, effect = choose_effect_removal_action(actor, setup, '1:caster')
        if change == 'range': target.position_ft = 121
        else: actor.state.resources[0].current_uses = 0
        with pytest.raises(ValueError):
            resolve_effect_removal(1, 1, actor, setup, action, effect, None, '1:caster')
        assert actor.state.action_available and target.state.timed_effects == []


def test_stunned_ends_concentration_and_owned_ally_effects():
    from app.domain.modifiers import CombatModifier, ConcentrationState, ModifierKind
    actor, target, setup = fixture()
    target.state.concentration = ConcentrationState(source_id='target', effect_id='buff', started_round=1)
    actor.state.active_modifiers.append(CombatModifier(
        id='buff', source_id='target', source_effect_id='buff', kind=ModifierKind.ARMOR_CLASS,
        flat_bonus=2, concentration_required=True,
    ))
    action, effect = choose_effect_removal_action(actor, setup, '1:caster')
    resolve_effect_removal(1, 1, actor, setup, action, effect, None, '1:caster')
    assert target.state.concentration is None and actor.state.active_modifiers == []
