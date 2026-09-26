from __future__ import annotations

import logging

from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.modifier_stack import add_modifier
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.spell_save_disadvantage import (
    choose_spell_save_disadvantage,
    spend_spell_save_disadvantage,
)
from app.combat.spell_choice import SpellChoice
from app.combat.spell_policy import spell_at_slot
from app.combat.targeting_wards import blocked_targeting_event, check_targeting_ward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def compile_spell_save_action(choice: SpellChoice) -> SavingThrowAction:
    """Compile one save spell choice into the universal SavingThrowAction shape."""
    try:
        spell = spell_at_slot(choice.action, choice.slot_level)
        target_range = spell.range_ft + (spell.area_radius_ft or 0)
        return SavingThrowAction(
            id=spell.id,
            name=spell.name,
            save_ability=spell.save_ability,
            dc=spell.dc,
            range_ft=target_range,
            area=spell.area,
            damage_dice_count=spell.damage_dice_count,
            damage_dice_size=spell.damage_dice_size,
            damage_bonus=spell.damage_bonus,
            damage_type=spell.damage_type,
            success_damage=spell.success_damage,
            damage_components=list(spell.damage_components),
            magical_effect=True,
            effect_tags=list(spell.effect_tags),
            requires_target_hearing=spell.requires_target_hearing,
            requires_target_sight=spell.requires_target_sight,
            failed_save_timed_effect=spell.failed_save_timed_effect,
            animation=spell.animation,
        )
    except Exception:
        logger.exception("Failed to compile save action for spell %s.", choice.action.id)
        raise


def resolve_spell_save_effect(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    choice: SpellChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve only a save spell's target effects, without casting or spending a slot."""
    try:
        scaled_spell = spell_at_slot(choice.action, choice.slot_level)
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        affected_states = [member.state for member in members]
        placement = choice.placement
        action = compile_spell_save_action(choice)
        events: list[BattleEvent] = []
        shared_damage_rolls: list[int] | list[list[int]] | None = None
        save_disadvantage = choose_spell_save_disadvantage(caster.state)

        for target_id in choice.target_ids:
            target = by_id[target_id]
            ward = (
                check_targeting_ward(caster, target, dice)
                if scaled_spell.area_radius_ft is None and scaled_spell.area is None
                else None
            )
            if ward is not None and not ward.succeeded:
                events.append(blocked_targeting_event(
                    sequence,
                    round_number,
                    caster,
                    target,
                    scaled_spell.name,
                    ward,
                ))
                sequence += 1
                continue

            disadvantage_sources: tuple[str, ...] = ()
            modifier_remaining = None
            if save_disadvantage is not None:
                modifier_remaining = spend_spell_save_disadvantage(caster.state, save_disadvantage)
                disadvantage_sources = (save_disadvantage.name,)
                save_disadvantage = None

            chain, sequence = resolve_save_event_chain(
                sequence,
                round_number,
                caster,
                target,
                action,
                0 if placement is not None else abs(caster.position_ft - target.position_ft),
                dice,
                setup,
                turn_key=turn_key,
                spend_action=False,
                shared_damage_rolls=shared_damage_rolls,
                affected_states=affected_states,
                spell_effect=True,
                save_disadvantage_sources=disadvantage_sources,
                resource_remaining_override=modifier_remaining,
            )
            event = chain[0]
            if ward is not None:
                event.description += (
                    f" {caster.state.template.name} succeeds against "
                    f"{ward.gate.source_effect_id}."
                )
            if event.save_succeeded is False and scaled_spell.failed_save_modifier_effects:
                for index, effect in enumerate(scaled_spell.failed_save_modifier_effects):
                    add_modifier(
                        target.state,
                        build_spell_modifier(
                            caster.combatant_id,
                            target.combatant_id,
                            scaled_spell.id,
                            effect,
                            index,
                            scaled_spell.name,
                            concentration_required=scaled_spell.concentration,
                            round_number=round_number,
                        ),
                    )
            events.extend(chain)
            if shared_damage_rolls is None and event.damage_components:
                shared_damage_rolls = [
                    list(component.rolls) for component in event.damage_components
                ]
        return events, sequence
    except Exception as exc:
        logger.exception("Save-spell effect resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Save-spell effect could not be resolved.") from exc
