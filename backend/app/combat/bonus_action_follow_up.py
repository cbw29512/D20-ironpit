from __future__ import annotations

import logging

from app.combat.activation_movement import resolve_activation_movement
from app.combat.dodge import DODGE_EFFECT_ID, apply_dodge_effect
from app.combat.modifier_stack import effective_speed
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_bonus_action_follow_up(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    triggering_feature_id: str | None,
    turn_key: str,
    dice=None,
) -> BattleEvent | None:
    """Resolve one declared tactical follow-up after another Bonus Action."""
    try:
        if not triggering_feature_id or member.state.bonus_action_available:
            return None
        rules = member.state.template.progression_features.bonus_action_follow_up_tactical_grants
        for rule in rules:
            if member.state.feature_last_turn_keys.get(rule.source_id) == turn_key:
                continue
            if triggering_feature_id in rule.excluded_trigger_ids:
                continue
            grant = next(
                (item for item in member.state.template.bonus_tactical_action_grants
                 if item.id == rule.tactical_grant_id),
                None,
            )
            if grant is None:
                raise ValueError(f"{rule.source_name} references missing tactical grant {rule.tactical_grant_id}.")
            if grant.resource_id is not None:
                raise ValueError(f"{rule.source_name} follow-up tactical grant must be resource-free.")

            movement = effective_speed(member.state) if "dash" in grant.effects else 0
            if movement:
                member.state.movement_remaining_ft += movement
                member.state.dash_uses_this_turn += 1
            if "disengage" in grant.effects:
                member.state.disengaged_this_turn = True
            if "dodge" in grant.effects:
                apply_dodge_effect(member.state)

            temporary_hp_before = member.state.temporary_hp
            temporary_hp_after = temporary_hp_before
            if grant.temporary_hp_dice_count:
                if dice is None:
                    raise ValueError(f"{rule.source_name} Temporary HP requires a dice provider.")
                amount = sum(
                    dice.roll(grant.temporary_hp_dice_size)
                    for _ in range(grant.temporary_hp_dice_count)
                )
                temporary_hp_after = grant_temporary_hit_points(member.state, amount)

            member.state.feature_last_turn_keys[rule.source_id] = turn_key
            labels = ", ".join(effect.title() for effect in grant.effects)
            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                feature_id=rule.source_id,
                movement_ft=movement,
                temporary_hp_before=temporary_hp_before if grant.temporary_hp_dice_count else None,
                temporary_hp_after=temporary_hp_after if grant.temporary_hp_dice_count else None,
                applied_condition_ids=[DODGE_EFFECT_ID] if "dodge" in grant.effects else [],
                animation="movement" if "dash" in grant.effects else "dodge",
                description=(
                    f"{member.state.template.name} uses {rule.source_name} to use "
                    f"{grant.name}: {labels}."
                ),
            )
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed Bonus Action follow-up for %s.", member.combatant_id)
        raise RuntimeError("Bonus Action follow-up could not be resolved.") from exc



def resolve_bonus_action_follow_up_movement(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    triggering_feature_id: str | None,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve one declared movement grant after a matching Bonus Action trigger."""
    try:
        if not triggering_feature_id or member.state.bonus_action_available:
            return [], sequence
        rules = member.state.template.progression_features.bonus_action_follow_up_movement_grants
        for rule in rules:
            if triggering_feature_id not in rule.required_trigger_ids:
                continue
            if member.state.feature_last_turn_keys.get(rule.source_id) == turn_key:
                continue
            events, next_sequence = resolve_activation_movement(
                sequence,
                round_number,
                member,
                setup,
                dice,
                speed_fraction=rule.speed_fraction,
                desired_distance_ft=rule.desired_distance_ft,
                turn_key=turn_key,
                provokes_opportunity_attacks=rule.provokes_opportunity_attacks,
            )
            if not events:
                return [], sequence
            for event in events:
                if event.event_type == "movement":
                    event.feature_id = rule.source_id
                    event.description = f"{rule.source_name}: {event.description}"
            member.state.feature_last_turn_keys[rule.source_id] = turn_key
            return events, next_sequence
        return [], sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed Bonus Action follow-up movement for %s.", member.combatant_id)
        raise RuntimeError("Bonus Action follow-up movement could not be resolved.") from exc
