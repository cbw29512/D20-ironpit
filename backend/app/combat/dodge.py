from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import is_incapacitated
from app.combat.grapple import speed_is_zero
from app.combat.modifier_stack import effective_speed
from app.domain.models import BattleEvent, CombatantState, EncounterCombatant

logger = logging.getLogger(__name__)
DODGE_EFFECT_ID = "dodge"


def dodge_benefits_active(state: CombatantState) -> bool:
    """Return whether the creature currently receives the RAW Dodge benefits."""
    try:
        return bool(
            DODGE_EFFECT_ID in state.active_effect_ids
            and not is_incapacitated(state)
            and not speed_is_zero(state)
            and effective_speed(state) > 0
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Dodge benefits for %s.", state.template.name)
        raise RuntimeError("Dodge benefits could not be evaluated.") from exc


def dodge_dex_save_advantage_sources(state: CombatantState, ability: str) -> int:
    """Feed Dodge into the shared saving-throw Advantage primitive."""
    try:
        return 1 if ability == "dexterity" and dodge_benefits_active(state) else 0
    except Exception as exc:
        logger.exception("Failed to evaluate Dodge save Advantage for %s.", state.template.name)
        raise RuntimeError("Dodge saving-throw Advantage could not be evaluated.") from exc


def resolve_dodge_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
) -> BattleEvent:
    """Spend the creature's Action and activate Dodge until its next turn starts."""
    try:
        if not is_available(actor.state, "action"):
            raise ValueError("Action is not available for Dodge.")
        spend(actor.state, "action")
        if DODGE_EFFECT_ID not in actor.state.active_effect_ids:
            actor.state.active_effect_ids.append(DODGE_EFFECT_ID)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            applied_condition_ids=[DODGE_EFFECT_ID],
            feature_id=DODGE_EFFECT_ID,
            animation="dodge",
            description=f"{actor.state.template.name} takes the Dodge action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve Dodge for %s.", actor.combatant_id)
        raise RuntimeError("Dodge action could not be resolved.") from exc
