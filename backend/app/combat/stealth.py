from __future__ import annotations

import logging

from app.combat.conditions import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import (
    ActorVisibilityState,
    BattleEvent,
    BattlefieldState,
    CombatantState,
    ConditionKind,
    CoverLevel,
)

logger = logging.getLogger(__name__)
HIDE_DC = 15
HIDE_FEATURE = "hide"


def get_visibility_state(
    battlefield: BattlefieldState,
    actor: CombatantState,
) -> ActorVisibilityState:
    try:
        return battlefield.visibility_by_actor.get(
            actor.template.id, ActorVisibilityState()
        )
    except Exception as exc:
        logger.exception("Failed to read visibility for %s.", actor.template.name)
        raise RuntimeError("Visibility state could not be read.") from exc


def can_hide(actor: CombatantState, battlefield: BattlefieldState) -> bool:
    try:
        visibility = get_visibility_state(battlefield, actor)
        has_concealment = (
            visibility.heavily_obscured
            or visibility.cover in {CoverLevel.THREE_QUARTERS, CoverLevel.TOTAL}
        )
        return has_concealment and not visibility.enemy_line_of_sight
    except Exception as exc:
        logger.exception("Hide eligibility failed for %s.", actor.template.name)
        raise RuntimeError("Hide eligibility could not be resolved.") from exc


def break_hidden(state: CombatantState) -> None:
    try:
        if state.hidden:
            state.hidden = False
            state.hidden_dc = None
            state.conditions.discard(ConditionKind.INVISIBLE)
    except Exception as exc:
        logger.exception("Failed to reveal %s.", state.template.name)
        raise RuntimeError("Hidden state could not be ended.") from exc


def resolve_invisible_attack_sources(
    attacker: CombatantState,
    defender: CombatantState,
) -> tuple[int, int]:
    try:
        advantage = int(ConditionKind.INVISIBLE in attacker.conditions)
        disadvantage = int(ConditionKind.INVISIBLE in defender.conditions)
        return advantage, disadvantage
    except Exception as exc:
        logger.exception("Invisible attack effects could not be resolved.")
        raise RuntimeError("Invisible attack effects could not be resolved.") from exc


def take_hide_action(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    *,
    spend_action: bool = True,
    feature_id: str = HIDE_FEATURE,
) -> BattleEvent:
    try:
        if is_incapacitated(actor):
            raise ValueError("Incapacitated creatures cannot take the Hide action.")
        if actor.hidden:
            raise ValueError("Combatant is already hidden.")
        if spend_action and not actor.action_available:
            raise ValueError("Action is not available for Hide.")
        if not can_hide(actor, battlefield):
            raise ValueError("Hide requires concealment and no enemy line of sight.")

        check = roll_d20(dice, actor.template.skill_bonuses.get("stealth", 0))
        if spend_action:
            actor.action_available = False
        success = check.total >= HIDE_DC
        if success:
            actor.hidden = True
            actor.hidden_dc = check.total
            actor.conditions.add(ConditionKind.INVISIBLE)

        result = "succeeds" if success else "fails"
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="hide",
            actor_id=actor.template.id,
            actor_name=actor.template.name,
            check_roll=check,
            feature_id=feature_id,
            animation="hide",
            description=f"{actor.template.name} {result} on the Hide action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Hide action failed for %s.", actor.template.name)
        raise RuntimeError("Hide action could not be resolved.") from exc
