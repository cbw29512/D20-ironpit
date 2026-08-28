from __future__ import annotations

import logging

from app.combat.card_effects import dodge_effect_change
from app.combat.conditions import effective_speed_ft, is_incapacitated, require_activity
from app.combat.sight import can_see_combatant
from app.domain.models import AbilityKind, BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)
DODGE = "dodge"


def has_dodge_benefits(state: CombatantState) -> bool:
    try:
        return bool(
            state.dodging
            and not is_incapacitated(state)
            and effective_speed_ft(state) > 0
        )
    except Exception as exc:
        logger.exception("Failed to resolve Dodge benefits for %s.", state.template.name)
        raise RuntimeError("Dodge benefits could not be resolved.") from exc


def dodge_attack_disadvantage(
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState | None,
) -> int:
    try:
        return int(
            has_dodge_benefits(defender)
            and can_see_combatant(defender, attacker, battlefield)
        )
    except Exception as exc:
        logger.exception("Failed to resolve Dodge attack effect for %s.", defender.template.name)
        raise RuntimeError("Dodge attack effect could not be resolved.") from exc


def dodge_save_advantage(state: CombatantState, ability: AbilityKind) -> int:
    try:
        return int(ability is AbilityKind.DEXTERITY and has_dodge_benefits(state))
    except Exception as exc:
        logger.exception("Failed to resolve Dodge save effect for %s.", state.template.name)
        raise RuntimeError("Dodge save effect could not be resolved.") from exc


def take_dodge_action(
    sequence: int,
    round_number: int,
    actor: CombatantState,
) -> BattleEvent:
    try:
        require_activity(actor, "Action")
        if not actor.action_available:
            raise ValueError("Action is not available for Dodge.")
        actor.action_available = False
        actor.dodging = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="dodge",
            actor_id=actor.template.id,
            actor_name=actor.template.name,
            feature_id=DODGE,
            effect_changes=[dodge_effect_change(actor, "apply")],
            animation="dodge",
            description=f"{actor.template.name} takes the Dodge action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Dodge failed for %s.", actor.template.name)
        raise RuntimeError("Dodge could not be resolved.") from exc
