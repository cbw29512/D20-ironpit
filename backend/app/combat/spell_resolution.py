from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.defensive_modifier_rules import remove_owner_attack_ending_modifiers
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.spell_policy import SpellChoice
from app.combat.spellcasting import available_free_spell_cast, consume_free_spell_cast, mark_slot_spell_cast
from app.combat.spell_damage_bonus import matching_spell_damage_bonuses
from app.combat.targeting_wards import blocked_targeting_event, check_targeting_ward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _resource(state, level: int):
    resource_id = f"spell-slot-{level}"
    return next((item for item in state.resources if item.id == resource_id), None)


def _save_action(choice: SpellChoice, caster_state) -> SavingThrowAction:
    try:
        spell = choice.action
        if choice.slot_level < spell.level:
            raise ValueError("Spell cast level cannot be below the spell's printed level.")
        if spell.level == 0 and choice.slot_level != 0:
            raise ValueError("Cantrips cannot expend spell slots.")
        upcast_levels = choice.slot_level - spell.level
        if spell.damage_components and upcast_levels and spell.upcast_dice_per_level:
            raise ValueError("Split-component spell upcasting requires explicit component scaling data.")

        target_range = spell.range_ft + (spell.area_radius_ft or 0)
        damage_bonus = spell.damage_bonus
        damage_dice_count = spell.damage_dice_count + (
            upcast_levels * spell.upcast_dice_per_level
        )
        components = [component.model_copy(deep=True) for component in spell.damage_components]
        used_sources: set[str] = set()

        if components:
            adjusted = []
            for component in components:
                matches = matching_spell_damage_bonuses(
                    caster_state,
                    spell.id,
                    component.damage_type,
                    excluded_source_ids=used_sources,
                )
                used_sources.update(source_id for source_id, _, _ in matches)
                adjusted.append(component.model_copy(update={
                    "damage_bonus": component.damage_bonus
                    + sum(amount for _, _, amount in matches),
                }))
            components = adjusted
        elif spell.damage_type is not None:
            matches = matching_spell_damage_bonuses(
                caster_state,
                spell.id,
                spell.damage_type,
            )
            damage_bonus += sum(amount for _, _, amount in matches)

        return SavingThrowAction(
            id=spell.id,
            name=spell.name,
            save_ability=spell.save_ability,
            dc=spell.dc,
            range_ft=target_range,
            damage_dice_count=damage_dice_count,
            damage_dice_size=spell.damage_dice_size,
            damage_bonus=damage_bonus,
            damage_type=spell.damage_type,
            damage_components=components,
            success_damage=spell.success_damage,
            magical_effect=True,
            animation=spell.animation,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to compile runtime save spell %s at cast level %s.",
            choice.action.id,
            choice.slot_level,
        )
        raise RuntimeError("Runtime save spell could not be compiled.") from exc


def resolve_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    choice: SpellChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    spell = choice.action
    if spell.action_cost == "reaction":
        raise ValueError("Reaction spells require their own trigger window.")
    if choice.slot_level < spell.level:
        raise ValueError("Spell cast level cannot be below the spell's printed level.")
    if spell.level == 0 and choice.slot_level != 0:
        raise ValueError("Cantrips cannot expend spell slots.")
    if not is_available(caster.state, spell.action_cost):
        raise ValueError(f"{spell.action_cost} is unavailable for {spell.name}.")

    remaining = None
    free_grant = available_free_spell_cast(caster.state, spell.id) if choice.slot_level > 0 else None
    if free_grant is not None:
        remaining = consume_free_spell_cast(caster.state, free_grant)
    elif choice.slot_level > 0:
        resource = _resource(caster.state, choice.slot_level)
        if resource is None or resource.current_uses < 1:
            raise ValueError(f"No level {choice.slot_level} spell slot remains.")
        mark_slot_spell_cast(caster.state, turn_key)
        resource.current_uses -= 1
        remaining = resource.current_uses
    spend(caster.state, spell.action_cost)
    remove_owner_attack_ending_modifiers(caster.state)

    placement = choice.placement
    detail = ""
    if placement is not None:
        detail = (
            f" Area covers {len(placement.enemy_ids)} enemies and "
            f"{len(placement.friendly_ids)} unprotected allies."
        )
    slot_text = (
        "cantrip"
        if choice.slot_level == 0
        else (
            f"{free_grant.source_name} without expending a spell slot"
            if free_grant is not None
            else f"level {choice.slot_level} slot"
        )
    )
    events = [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=caster.combatant_id, actor_name=caster.state.template.name,
        feature_id=spell.id, resource_remaining=remaining, animation=spell.animation,
        description=f"{caster.state.template.name} casts {spell.name} using a {slot_text}.{detail}",
    )]
    sequence += 1

    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    affected_states = [member.state for member in members]
    save_action = _save_action(choice, caster.state)
    shared_damage_rolls: list[int] | None = None
    shared_damage_component_rolls: list[list[int]] | None = None
    for target_id in choice.target_ids:
        target = by_id[target_id]
        ward = check_targeting_ward(caster, target, dice) if spell.area_radius_ft is None else None
        if ward is not None and not ward.succeeded:
            events.append(blocked_targeting_event(
                sequence, round_number, caster, target, spell.name, ward,
            ))
            sequence += 1
            continue
        chain, sequence = resolve_save_event_chain(
            sequence, round_number, caster, target, save_action,
            abs(caster.position_ft - target.position_ft), dice, setup,
            turn_key=turn_key, spend_action=False,
            shared_damage_rolls=shared_damage_rolls,
            shared_damage_component_rolls=shared_damage_component_rolls,
            affected_states=affected_states,
        )
        event = chain[0]
        if ward is not None:
            event.description += f" {caster.state.template.name} succeeds against {ward.gate.source_effect_id}."
        events.extend(chain)
        if event.damage_components:
            if save_action.damage_components and shared_damage_component_rolls is None:
                shared_damage_component_rolls = [
                    list(component.rolls) for component in event.damage_components
                ]
            elif not save_action.damage_components and shared_damage_rolls is None:
                shared_damage_rolls = list(event.damage_components[0].rolls)
    return events, sequence
