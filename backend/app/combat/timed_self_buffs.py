from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.modifier_stack import add_modifier
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_self_buff_policy import (
    choose_timed_self_buff_action,
    timed_self_buff_active,
    timed_self_buff_resource,
)
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def resolve_timed_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
    *,
    spend_action_cost: bool = True,
    affected_states=None,
    setup=None,
    turn_key: str | None = None,
) -> BattleEvent:
    """Spend source-defined economy/resources and apply one source-owned timed buff."""
    try:
        resource = timed_self_buff_resource(member, action)
        if spend_action_cost and not is_available(member.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if action.resource_id is not None and (resource is None or resource.current_uses < action.resource_cost):
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if timed_self_buff_active(member, action):
            raise ValueError(f"{action.name} is already active.")
        if setup is not None:
            from app.combat.suppression_zone_geometry import verbal_casting_blocked
            if action.resource_id and action.resource_id.startswith("spell-slot-") and verbal_casting_blocked(member, setup):
                raise ValueError(f"{action.name} cannot be cast inside a Silence effect.")
        if turn_key and action.resource_id and action.resource_id.startswith("spell-slot-"):
            from app.combat.spellcasting import mark_slot_spell_cast
            mark_slot_spell_cast(member.state, turn_key)

        if spend_action_cost:
            spend(member.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost
        applied: list[str] = []
        defenses_attached = False
        expires_round = (
            round_number + action.duration_rounds
            if action.duration_rounds is not None else None
        )
        expiry_timing = action.expiry_timing if action.duration_rounds is not None else None
        expires_at_source_start = expiry_timing == "source_turn_start"
        for condition_id in action.condition_ids:
            condition = apply_timed_condition(
                member.state,
                condition_id,
                member.combatant_id,
                source_effect_id=action.id,
                source_template=member.state.template,
                applied_round=round_number,
                expires_round=expires_round,
                expiry_timing=expiry_timing,
                expires_at_start_of_source_turn=expires_at_source_start,
                owned_damage_resistances=action.damage_resistances if not defenses_attached else [],
                owned_debuff_counters=action.debuff_counters if not defenses_attached else [],
                owned_movement_mode_grants=action.movement_mode_grants if not defenses_attached else [],
                ends_if_source_incapacitated=action.ends_if_source_incapacitated,
                ends_if_source_dead=action.ends_if_source_dead,
                use_default_poison_recovery=False,
            )
            if condition is not None:
                applied.append(condition)
                defenses_attached = True
        if not defenses_attached and (
            action.damage_resistances
            or action.debuff_counters
            or action.saving_throw_advantage_grants
            or action.movement_mode_grants
            or action.friendly_save_advantage_aura is not None
            or action.friendly_cover_aura is not None
            or action.hostile_start_turn_condition_aura is not None
            or action.start_turn_emanation_damage is not None
            or action.melee_hit_retaliation is not None
            or action.spell_save_dc_bonus
            or action.spell_attack_advantage
        ):
            apply_timed_condition(
                member.state,
                action.id,
                member.combatant_id,
                source_effect_id=action.id,
                source_template=member.state.template,
                applied_round=round_number,
                expires_round=expires_round,
                expiry_timing=expiry_timing,
                expires_at_start_of_source_turn=expires_at_source_start,
                owned_damage_resistances=action.damage_resistances,
                owned_debuff_counters=action.debuff_counters,
                owned_movement_mode_grants=action.movement_mode_grants,
                ends_if_source_incapacitated=action.ends_if_source_incapacitated,
                ends_if_source_dead=action.ends_if_source_dead,
                use_default_poison_recovery=False,
            )

        if action.concentration:
            start_concentration(
                member.state,
                member.combatant_id,
                action.id,
                round_number,
                affected_states,
                expires_round=expires_round,
            )

        for grant in action.saving_throw_advantage_grants:
            for ability in grant.abilities:
                add_modifier(member.state, CombatModifier(
                    id=f"{member.combatant_id}:{action.id}:save-advantage:{ability}",
                    source_id=member.combatant_id,
                    source_effect_id=action.id,
                    source_name=grant.source_name,
                    kind=ModifierKind.SAVING_THROW_ADVANTAGE,
                    save_ability=ability,
                    requires_magical_effect=grant.requires_magical_effect,
                    requires_spell_effect=grant.requires_spell_effect,
                    source_creature_types=list(grant.source_creature_types),
                    required_effect_tags=list(grant.required_effect_tags),
                ))

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            target_id=member.combatant_id,
            target_name=member.state.template.name,
            applied_condition_ids=applied,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            animation=action.animation,
            concentration_started_effect_id=action.id if action.concentration else None,
            description=f"{member.state.template.name} uses {action.name}.",
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Timed self-buff resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff could not be resolved.") from exc
