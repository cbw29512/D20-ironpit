from __future__ import annotations

import logging

from app.combat.conditions import apply_condition
from app.combat.dice import DiceProvider
from app.combat.unarmed_control import (
    resolve_control_save,
    unarmed_control_dc,
    validate_unarmed_control,
)
from app.domain.models import BattleEvent, CombatantState, ConditionType

logger = logging.getLogger(__name__)


def resolve_unarmed_grapple(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    dice: DiceProvider,
) -> list[BattleEvent]:
    """Resolve the Grapple option of one Unarmed Strike; caller owns the attack slot."""
    try:
        validate_unarmed_control(
            attacker,
            defender,
            distance_ft,
            require_free_hand=True,
        )
        dc = unarmed_control_dc(attacker)
        save_event, success = resolve_control_save(
            sequence, round_number, attacker, defender, "unarmed-grapple", dc, dice
        )
        events = [save_event]
        if not success and apply_condition(
            defender,
            ConditionType.GRAPPLED,
            attacker,
            escape_dc=dc,
        ):
            events.append(_grapple_event(sequence + 1, round_number, attacker, defender))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Unarmed Grapple failed.")
        raise RuntimeError("Unarmed Grapple could not be resolved.") from exc


def _grapple_event(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
) -> BattleEvent:
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="condition",
        actor_id=attacker.instance_id,
        actor_name=attacker.template.name,
        target_id=defender.instance_id,
        target_name=defender.template.name,
        condition=ConditionType.GRAPPLED,
        condition_active=True,
        feature_id="unarmed-grapple",
        animation="grapple",
        description=f"{defender.template.name} becomes Grappled.",
    )
