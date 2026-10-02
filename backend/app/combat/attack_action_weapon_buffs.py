from __future__ import annotations

import logging

from app.combat.modifier_stack import add_modifier
from app.combat.resources import resource_available, spend_resource
from app.combat.timed_conditions import apply_timed_condition
from app.domain.attack_action_weapon_buffs import AttackActionWeaponBuff
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def _active(member: EncounterCombatant, action: AttackActionWeaponBuff) -> bool:
    return any(
        effect.source_id == member.combatant_id and effect.source_effect_id == action.id
        for effect in member.state.timed_effects
    )


def resolve_attack_action_weapon_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
) -> BattleEvent | None:
    """Activate the first legal declared weapon buff as part of taking the Attack action."""
    try:
        for action in member.state.template.attack_action_weapon_buffs:
            if _active(member, action):
                continue
            if not resource_available(member.state, action.resource_id, action.resource_cost):
                continue
            if not any(
                attack.weapon.id == action.weapon_id
                for attack in [member.state.template.weapon_attack, *member.state.template.alternate_weapon_attacks]
            ):
                raise ValueError(f"{action.name} weapon {action.weapon_id} is absent from the combat loadout.")

            remaining = spend_resource(member.state, action.resource_id, action.resource_cost)
            apply_timed_condition(
                member.state,
                action.id,
                member.combatant_id,
                source_effect_id=action.id,
                source_template=member.state.template,
                applied_round=round_number,
                expires_round=round_number + action.duration_rounds,
                expiry_timing="source_turn_start",
                source_is_magical=action.source_is_magical,
                use_default_poison_recovery=False,
            )
            if action.attack_roll_bonus:
                add_modifier(member.state, CombatModifier(
                    id=f"{member.combatant_id}:{action.id}:attack",
                    source_id=member.combatant_id,
                    source_effect_id=action.id,
                    source_name=action.name,
                    source_is_magical=action.source_is_magical,
                    kind=ModifierKind.ATTACK_ROLL_FLAT,
                    flat_bonus=action.attack_roll_bonus,
                    weapon_id=action.weapon_id,
                    expires_source_turn_end_round=round_number + action.duration_rounds,
                ))
            if action.damage_type_choice is not None:
                add_modifier(member.state, CombatModifier(
                    id=f"{member.combatant_id}:{action.id}:damage-type",
                    source_id=member.combatant_id,
                    source_effect_id=action.id,
                    source_name=action.name,
                    source_is_magical=action.source_is_magical,
                    kind=ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE,
                    damage_type=action.damage_type_choice,
                    weapon_id=action.weapon_id,
                    expires_source_turn_end_round=round_number + action.duration_rounds,
                ))

            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                target_id=member.combatant_id,
                target_name=member.state.template.name,
                feature_id=action.id,
                resource_remaining=remaining,
                animation=action.animation,
                description=f"{member.state.template.name} uses {action.name} on {action.weapon_id}.",
            )
        return None
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Attack-action weapon buff failed for %s.", member.combatant_id)
        raise RuntimeError("Attack-action weapon buff could not be resolved.") from exc
