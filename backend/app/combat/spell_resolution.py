from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.defensive_modifier_rules import remove_owner_attack_ending_modifiers
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.spell_policy import SpellChoice, spell_at_slot
from app.combat.modifier_stack import add_modifier
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.targeting_wards import blocked_targeting_event, check_targeting_ward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _resource(state, level: int):
    try:
        resource_id = f"spell-slot-{level}"
        return next((item for item in state.resources if item.id == resource_id), None)
    except Exception as exc:
        logger.exception("Failed to load spell-slot resource level %s.", level)
        raise RuntimeError("Spell-slot resource could not be loaded.") from exc


def _save_action(choice: SpellChoice) -> SavingThrowAction:
    try:
        spell = spell_at_slot(choice.action, choice.slot_level)
        target_range = spell.range_ft + (spell.area_radius_ft or 0)
        return SavingThrowAction(
            id=spell.id, name=spell.name, save_ability=spell.save_ability, dc=spell.dc,
            range_ft=target_range, area=spell.area, damage_dice_count=spell.damage_dice_count,
            damage_dice_size=spell.damage_dice_size, damage_bonus=spell.damage_bonus,
            damage_type=spell.damage_type, success_damage=spell.success_damage,
            damage_components=list(spell.damage_components),
            magical_effect=True, effect_tags=list(spell.effect_tags),
            requires_target_hearing=spell.requires_target_hearing,
            requires_target_sight=spell.requires_target_sight,
            failed_save_timed_effect=spell.failed_save_timed_effect,
            animation=spell.animation,
        )
    except Exception:
        logger.exception("Failed to compile save action for spell %s.", choice.action.id)
        raise


def resolve_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    choice: SpellChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        spell = choice.action
        scaled_spell = spell_at_slot(spell, choice.slot_level)
        if spell.action_cost == "reaction":
            raise ValueError("Reaction spells require their own trigger window.")
        if not is_available(caster.state, spell.action_cost):
            raise ValueError(f"{spell.action_cost} is unavailable for {spell.name}.")

        remaining = None
        if choice.slot_level > 0:
            resource = _resource(caster.state, choice.slot_level)
            if resource is None or resource.current_uses < 1:
                raise ValueError(f"No level {choice.slot_level} spell slot remains.")
            mark_slot_spell_cast(caster.state, turn_key)
            resource.current_uses -= 1
            remaining = resource.current_uses
        spend(caster.state, spell.action_cost)
        remove_owner_attack_ending_modifiers(caster.state)

        members = [*setup.heroes, *setup.monsters]
        affected_states = [member.state for member in members]
        if spell.concentration:
            duration_rounds = (spell.duration_minutes or 0) * 10
            start_concentration(
                caster.state,
                caster.combatant_id,
                spell.id,
                round_number,
                affected_states,
                expires_round=round_number + duration_rounds,
                slot_level=choice.slot_level if choice.slot_level > 0 else None,
            )

        placement = choice.placement
        detail = ""
        if placement is not None:
            detail = (
                f" Area covers {len(placement.enemy_ids)} enemies and "
                f"{len(placement.friendly_ids)} unprotected allies."
            )
        slot_text = "cantrip" if choice.slot_level == 0 else f"level {choice.slot_level} slot"
        events = [BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            feature_id=spell.id, resource_remaining=remaining, animation=spell.animation,
            description=f"{caster.state.template.name} casts {spell.name} using a {slot_text}.{detail}",
        )]
        sequence += 1

        by_id = {member.combatant_id: member for member in members}
        save_action = _save_action(choice)
        shared_damage_rolls: list[int] | list[list[int]] | None = None
        for target_id in choice.target_ids:
            target = by_id[target_id]
            ward = (
                check_targeting_ward(caster, target, dice)
                if scaled_spell.area_radius_ft is None and scaled_spell.area is None
                else None
            )
            if ward is not None and not ward.succeeded:
                events.append(blocked_targeting_event(
                    sequence, round_number, caster, target, spell.name, ward,
                ))
                sequence += 1
                continue
            chain, sequence = resolve_save_event_chain(
                sequence, round_number, caster, target, save_action,
                0 if placement is not None else abs(caster.position_ft - target.position_ft), dice, setup,
                turn_key=turn_key, spend_action=False,
                shared_damage_rolls=shared_damage_rolls, affected_states=affected_states,
                spell_effect=True,
            )
            event = chain[0]
            if ward is not None:
                event.description += f" {caster.state.template.name} succeeds against {ward.gate.source_effect_id}."
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
                shared_damage_rolls = [list(component.rolls) for component in event.damage_components]
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Save-based spell resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Save-based spell could not be resolved.") from exc
