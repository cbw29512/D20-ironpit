from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.dodge import DODGE_EFFECT_ID, apply_dodge_effect
from app.combat.encounter_movement import grant_dash_movement
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.modifier_stack import effective_speed
from app.combat.offensive_ranges import offensive_ranges_for_target
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.tactical_actions import BonusActionTacticalGrant

logger = logging.getLogger(__name__)

def _grants(member: EncounterCombatant) -> list[BonusActionTacticalGrant]:
    grants = list(member.state.template.bonus_tactical_action_grants)
    if (
        member.state.template.progression_features.cunning_action
        and not any(item.id == "cunning-action-dash" for item in grants)
    ):
        grants.append(BonusActionTacticalGrant(
            id="cunning-action-dash",
            name="Cunning Action",
            effects=["dash"],
            priority=50,
            use_policy="enable-offense",
        ))
    return grants

def choose_offensive_dash_grant(
    member: EncounterCombatant, setup: EncounterSetup, turn_key: str,
) -> BonusActionTacticalGrant | None:
    """Choose the cheapest declared Bonus Action Dash only when it enables offense."""
    try:
        if not is_available(member.state, "action") or not is_available(member.state, "bonus_action"):
            return None
        speed = effective_speed(member.state)
        if speed <= 0:
            return None
        candidates = [
            item for item in _grants(member)
            if item.use_policy == "enable-offense"
            and "dash" in item.effects
            and action_resource_available(member.state, item)
        ]
        if not candidates:
            return None
        normal_move = member.state.movement_remaining_ft
        dash_would_help = False
        for target in living_opponents(member, setup):
            distance = combatant_distance(member, target)
            for _, desired in offensive_ranges_for_target(member, target, turn_key):
                if distance <= desired + normal_move:
                    return None
                if distance <= desired + normal_move + speed:
                    dash_would_help = True
        if not dash_would_help:
            return None
        return min(candidates, key=lambda item: (
            item.resource_id is not None,
            item.priority,
            item.id,
        ))
    except Exception as exc:
        logger.exception("Failed to choose tactical Dash for %s.", member.combatant_id)
        raise RuntimeError("Tactical Dash choice could not be resolved.") from exc

def resolve_bonus_tactical_grant(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    grant: BonusActionTacticalGrant,
    dice: DiceProvider | None = None,
) -> BattleEvent:
    """Resolve one declared Bonus Action by composing standard tactical effects."""
    try:
        if not is_available(member.state, "bonus_action"):
            raise ValueError("Bonus Action is not available.")
        if not action_resource_available(member.state, grant):
            raise ValueError(f"Resource is unavailable for {grant.name}.")
        spend(member.state, "bonus_action")
        remaining = spend_action_resource(member.state, grant)
        movement = grant_dash_movement(member) if "dash" in grant.effects else 0
        if "disengage" in grant.effects:
            member.state.disengaged_this_turn = True
        if "dodge" in grant.effects:
            apply_dodge_effect(member.state)
        temporary_hp_before = member.state.temporary_hp
        temporary_hp_after = temporary_hp_before
        if grant.temporary_hp_dice_count:
            if dice is None:
                raise ValueError(f"{grant.name} Temporary HP requires a dice provider.")
            temporary_hp = sum(dice.roll(grant.temporary_hp_dice_size) for _ in range(grant.temporary_hp_dice_count))
            temporary_hp_after = grant_temporary_hit_points(member.state, temporary_hp)
        labels = ", ".join(effect.title() for effect in grant.effects)
        if grant.temporary_hp_dice_count:
            labels = f"{labels}, {grant.temporary_hp_dice_count}d{grant.temporary_hp_dice_size} Temporary HP"
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            feature_id=grant.id,
            resource_remaining=remaining,
            movement_ft=movement,
            temporary_hp_before=temporary_hp_before,
            temporary_hp_after=temporary_hp_after,
            applied_condition_ids=[DODGE_EFFECT_ID] if "dodge" in grant.effects else [],
            animation="movement" if "dash" in grant.effects else "dodge",
            description=f"{member.state.template.name} uses {grant.name}: {labels}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed tactical Bonus Action for %s.", member.combatant_id)
        raise RuntimeError("Tactical Bonus Action could not be resolved.") from exc

def use_offensive_dash(
    sequence: int, round_number: int, member: EncounterCombatant,
    setup: EncounterSetup, turn_key: str,
) -> BattleEvent | None:
    try:
        grant = choose_offensive_dash_grant(member, setup, turn_key)
        return resolve_bonus_tactical_grant(sequence, round_number, member, grant) if grant else None
    except Exception as exc:
        logger.exception("Failed offensive tactical Dash for %s.", member.combatant_id)
        raise RuntimeError("Offensive tactical Dash could not be resolved.") from exc

def resolve_defensive_tactical_grant(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    dice: DiceProvider | None = None,
) -> BattleEvent | None:
    """Use a declared defensive Bonus Action only when no earlier Bonus Action claimed the turn."""
    try:
        if not is_available(member.state, "bonus_action"):
            return None
        if is_incapacitated(member.state) or effective_speed(member.state) <= 0:
            return None
        if DODGE_EFFECT_ID in member.state.active_effect_ids:
            return None
        candidates = [
            item for item in _grants(member)
            if item.use_policy == "defensive-fallback"
            and "dodge" in item.effects
            and action_resource_available(member.state, item)
        ]
        if not candidates:
            return None
        grant = min(candidates, key=lambda item: (item.priority, item.id))
        return resolve_bonus_tactical_grant(sequence, round_number, member, grant, dice)
    except Exception as exc:
        logger.exception("Failed defensive tactical grant for %s.", member.combatant_id)
        raise RuntimeError("Defensive tactical grant could not be resolved.") from exc
