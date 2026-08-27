from __future__ import annotations

import logging
from typing import Literal

from app.combat.conditions import apply_condition
from app.combat.dice import DiceProvider
from app.combat.unarmed_control import (
    resolve_control_save,
    unarmed_control_dc,
    validate_unarmed_control,
)
from app.domain.models import BattleEvent, BattlefieldState, CombatantState, ConditionType

logger = logging.getLogger(__name__)


def resolve_unarmed_shove(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
    outcome: Literal["prone", "push"] = "prone",
) -> list[BattleEvent]:
    """Resolve the Shove option of one Unarmed Strike; caller owns the attack slot."""
    try:
        validate_unarmed_control(
            attacker,
            defender,
            battlefield.distance_ft,
            require_free_hand=False,
        )
        dc = unarmed_control_dc(attacker)
        save_event, success = resolve_control_save(
            sequence, round_number, attacker, defender, "unarmed-shove", dc, dice
        )
        if success:
            return [save_event]
        effect = (
            _prone_event(sequence + 1, round_number, attacker, defender)
            if outcome == "prone"
            else _push_event(sequence + 1, round_number, attacker, defender, battlefield)
        )
        return [save_event, effect]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Unarmed Shove failed.")
        raise RuntimeError("Unarmed Shove could not be resolved.") from exc


def _prone_event(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
) -> BattleEvent:
    apply_condition(defender, ConditionType.PRONE, attacker)
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="condition",
        actor_id=attacker.instance_id,
        actor_name=attacker.template.name,
        target_id=defender.instance_id,
        target_name=defender.template.name,
        condition=ConditionType.PRONE,
        condition_active=True,
        feature_id="unarmed-shove",
        animation="shove-prone",
        description=f"{defender.template.name} is knocked Prone.",
    )


def _push_event(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState,
) -> BattleEvent:
    before = battlefield.distance_ft
    battlefield.distance_ft += 5
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="forced_movement",
        actor_id=attacker.instance_id,
        actor_name=attacker.template.name,
        target_id=defender.instance_id,
        target_name=defender.template.name,
        distance_before_ft=before,
        distance_after_ft=battlefield.distance_ft,
        movement_ft=5,
        feature_id="unarmed-shove",
        animation="push",
        description=f"{defender.template.name} is shoved 5 ft. away.",
    )
