from __future__ import annotations
from app.combat.action_economy import is_available, spend
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.saving_throws import resolve_save_action
from app.combat.spell_casting_resources import spell_cast_resource_text, spend_spell_cast_resource
from app.combat.spell_immunity import spell_affects_target
from app.combat.spell_modifiers import apply_failed_save_spell_modifiers, start_save_spell_concentration
from app.combat.spell_policy import SpellChoice
from app.combat.spell_reflection import reflection_target, spend_spell_reflection
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.spells import SpellSaveAction


def _effect_reach(choice: SpellChoice) -> int:
    spell = choice.action
    if spell.area is None: return spell.range_ft + (spell.area_radius_ft or 0)
    extent = spell.area.radius_ft or spell.area.length_ft or 0
    return spell.range_ft + extent if spell.area.origin == "point" else extent


def _target_type(target: EncounterCombatant) -> str:
    return (target.state.template.creature_type or "").lower()


def _spell_affects(spell: SpellSaveAction, target: EncounterCombatant) -> bool:
    return _target_type(target) not in spell.excluded_creature_types and spell_affects_target(target.state, spell.level)


def _target_save(spell: SpellSaveAction, target: EncounterCombatant, action: SavingThrowAction, dice):
    disadvantage = int(_target_type(target) in spell.save_disadvantage_creature_types)
    if not disadvantage: return None
    return resolve_saving_throw(target.state, action.save_ability, action.dc, dice,
                                magical_effect=True, disadvantage_sources=disadvantage)


def _target_damage_rolls(spell: SpellSaveAction, target: EncounterCombatant) -> list[int] | None:
    if _target_type(target) not in spell.maximize_damage_creature_types: return None
    return [spell.damage_dice_size] * spell.damage_dice_count


def _save_action(choice: SpellChoice) -> SavingThrowAction:
    spell = choice.action
    if choice.slot_level != spell.level: raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    return SavingThrowAction(
        id=spell.id, name=spell.name, save_ability=spell.save_ability, dc=spell.dc,
        range_ft=_effect_reach(choice), damage_dice_count=spell.damage_dice_count,
        damage_dice_size=spell.damage_dice_size, damage_bonus=spell.damage_bonus,
        damage_type=spell.damage_type, success_damage=spell.success_damage,
        failure_push_ft=spell.failure_push_ft, magical_effect=True, animation=spell.animation,
    )


def resolve_spell(
    sequence: int, round_number: int, caster: EncounterCombatant, setup: EncounterSetup,
    choice: SpellChoice, turn_key: str, dice,
) -> tuple[list[BattleEvent], int]:
    spell = choice.action
    if spell.action_cost == "reaction": raise ValueError("Reaction spells require their own trigger window.")
    if choice.slot_level != spell.level: raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if not is_available(caster.state, spell.action_cost): raise ValueError(f"{spell.action_cost} is unavailable for {spell.name}.")
    remaining = spend_spell_cast_resource(caster, choice, turn_key); spend(caster.state, spell.action_cost)
    members = [*setup.heroes, *setup.monsters]; by_id = {member.combatant_id: member for member in members}
    affected_states = [member.state for member in members]
    start_save_spell_concentration(caster.state, caster.combatant_id, spell, round_number, affected_states)
    placement = choice.placement
    detail = "" if placement is None else f" Area covers {len(placement.enemy_ids)} enemies and {len(placement.friendly_ids)} unprotected allies."
    cast_text = spell_cast_resource_text(choice)
    events = [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=caster.combatant_id, actor_name=caster.state.template.name,
        feature_id=spell.id, resource_remaining=remaining, animation=spell.animation,
        concentration_started_effect_id=spell.id if spell.concentration else None,
        description=f"{caster.state.template.name} casts {spell.name} using a {cast_text}.{detail}",
    )]; sequence += 1
    save_action = _save_action(choice)
    reflectable = spell.area is None and spell.area_radius_ft is None and len(choice.target_ids) == 1
    shared_damage_rolls: list[int] | None = None
    for target_id in choice.target_ids:
        target = by_id[target_id]
        if not _spell_affects(spell, target): continue
        precomputed = None; reflected_from = None
        if reflectable and target.state.template.spell_reflection_reaction is not None:
            precomputed = resolve_saving_throw(
                target.state, save_action.save_ability, save_action.dc, dice, magical_effect=True,
                disadvantage_sources=int(_target_type(target) in spell.save_disadvantage_creature_types),
            )
            if precomputed[1]:
                reflected = reflection_target(target, caster, setup)
                if reflected is not None:
                    spend_spell_reflection(target); reflected_from = target; target = reflected; precomputed = None
        if not _spell_affects(spell, target): continue
        if precomputed is None: precomputed = _target_save(spell, target, save_action, dice)
        maximized_rolls = _target_damage_rolls(spell, target)
        damage_rolls = maximized_rolls if maximized_rolls is not None else shared_damage_rolls
        event = resolve_save_action(
            sequence, round_number, caster, target, save_action,
            0 if placement is not None or reflected_from is not None else abs(caster.position_ft - target.position_ft),
            dice, spend_action=False, shared_damage_rolls=damage_rolls,
            affected_states=affected_states, setup=setup, precomputed_save=precomputed,
        )
        if event.save_succeeded is False and spell.failure_modifier_effects:
            apply_failed_save_spell_modifiers(target.combatant_id, target.state, caster.combatant_id, spell, round_number)
        if reflected_from is not None:
            event.description = f"{reflected_from.state.template.name} uses Spell Reflection; {spell.name} targets {target.state.template.name} instead. {event.description}"
        events.append(event)
        if maximized_rolls is None and shared_damage_rolls is None and event.damage_components:
            shared_damage_rolls = list(event.damage_components[0].rolls)
        sequence += 1
    return events, sequence
