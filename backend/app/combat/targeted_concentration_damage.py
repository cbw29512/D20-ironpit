from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier, remove_source_modifiers
from app.combat.pit_policy import target_order
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction

logger = logging.getLogger(__name__)


def _slot_resource(member: EncounterCombatant, action: TargetedConcentrationDamageAction, turn_key: str):
    if not slot_spell_available(
        member.state, turn_key, spell_level=action.level, action_cost=action.action_cost,
    ):
        return None
    candidates = []
    for resource in member.state.resources:
        if not resource.id.startswith("spell-slot-") or resource.current_uses <= 0:
            continue
        try:
            level = int(resource.id.removeprefix("spell-slot-"))
        except ValueError:
            continue
        if level >= action.level:
            candidates.append((level, resource))
    return min(candidates, key=lambda item: item[0]) if candidates else None


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
    if combatant_id is None:
        return None
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == combatant_id),
        None,
    )


def _legal_target(
    member: EncounterCombatant,
    setup: EncounterSetup,
    action: TargetedConcentrationDamageAction,
) -> EncounterCombatant | None:
    return next(
        (
            target for target in target_order(member, setup)
            if combatant_distance(member, target) <= action.range_ft
        ),
        None,
    )


def _modifier_effect(action: TargetedConcentrationDamageAction) -> SpellModifierEffect:
    return SpellModifierEffect(
        kind="bonus-damage",
        dice_count=action.dice_count,
        dice_size=action.dice_size,
        damage_type=action.damage_type,
    )


def _active_target(
    member: EncounterCombatant,
    action: TargetedConcentrationDamageAction,
    setup: EncounterSetup,
) -> EncounterCombatant | None:
    modifier = next(
        (
            item for item in member.state.active_modifiers
            if item.source_id == member.combatant_id
            and item.source_effect_id == action.id
            and item.concentration_required
        ),
        None,
    )
    return _member_by_id(setup, modifier.target_id if modifier is not None else None)


def resolve_targeted_concentration_damage(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> BattleEvent | None:
    """Cast or retarget one declared hostile-target concentration damage spell."""
    try:
        if not is_available(member.state, "bonus_action"):
            return None
        for action in member.state.template.targeted_concentration_damage_actions:
            active = member.state.concentration
            if active is not None and active.effect_id != action.id:
                continue

            target = _active_target(member, action, setup) if active is not None else None
            if target is not None and target.state.current_hp > 0 and not target.state.is_dead:
                continue
            if active is not None and not action.retarget_after_target_zero:
                continue

            new_target = _legal_target(member, setup, action)
            if new_target is None:
                continue

            affected = [entry.state for entry in [*setup.heroes, *setup.monsters]]
            resource_remaining = None
            if active is None:
                selected = _slot_resource(member, action, turn_key)
                if selected is None:
                    continue
                slot_level, resource = selected
                mark_slot_spell_cast(
                    member.state, turn_key, spell_level=action.level, action_cost=action.action_cost,
                )
                resource.current_uses -= 1
                resource_remaining = resource.current_uses
                start_concentration(
                    member.state,
                    member.combatant_id,
                    action.id,
                    round_number,
                    affected,
                    expires_round=round_number + action.duration_rounds(slot_level),
                    slot_level=slot_level,
                )
                verb = "casts"
            else:
                remove_source_modifiers(
                    [member.state], member.combatant_id, action.id, concentration_only=True,
                )
                verb = "moves"

            modifier = build_spell_modifier(
                member.combatant_id,
                new_target.combatant_id,
                action.id,
                _modifier_effect(action),
                0,
                action.name,
                concentration_required=True,
                round_number=round_number,
            )
            add_modifier(member.state, modifier)
            spend(member.state, "bonus_action")
            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                target_id=new_target.combatant_id,
                target_name=new_target.state.template.name,
                feature_id=action.id,
                resource_remaining=resource_remaining,
                animation=action.animation,
                description=(
                    f"{member.state.template.name} {verb} {action.name} on "
                    f"{new_target.state.template.name}."
                ),
            )
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Targeted concentration damage resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Targeted concentration damage could not be resolved.") from exc
