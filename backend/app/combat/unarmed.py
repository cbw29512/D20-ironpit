from __future__ import annotations

import logging
from typing import Literal

from app.combat.conditions import apply_condition
from app.combat.d20_tests import ability_modifier, choose_best_save, resolve_saving_throw
from app.combat.dice import DiceProvider
from app.domain.models import (
    Ability,
    BattleEvent,
    BattlefieldState,
    CombatantState,
    ConditionType,
    SizeCategory,
)

logger = logging.getLogger(__name__)
_SIZE_ORDER = list(SizeCategory)
_SAVE_OPTIONS = (Ability.STRENGTH, Ability.DEXTERITY)


def _validate_unarmed_control(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    require_free_hand: bool,
) -> None:
    if distance_ft > 5:
        raise ValueError("Unarmed Strike target must be within 5 feet.")
    attacker_size = _SIZE_ORDER.index(attacker.template.size)
    defender_size = _SIZE_ORDER.index(defender.template.size)
    if defender_size > attacker_size + 1:
        raise ValueError("Target is too large for this Unarmed Strike option.")
    if require_free_hand and attacker.template.free_hands < 1:
        raise ValueError("Grapple requires a free hand.")


def _control_dc(attacker: CombatantState) -> int:
    return 8 + ability_modifier(attacker, Ability.STRENGTH) + attacker.template.proficiency_bonus


def _save_event(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    feature_id: str,
    dc: int,
    dice: DiceProvider,
) -> tuple[BattleEvent, bool]:
    ability = choose_best_save(defender, _SAVE_OPTIONS)
    roll, success = resolve_saving_throw(defender, ability, dc, dice)
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=defender.instance_id,
        actor_name=defender.template.name,
        target_id=attacker.instance_id,
        target_name=attacker.template.name,
        saving_throw=roll,
        test_dc=dc,
        test_ability=ability,
        test_success=success,
        feature_id=feature_id,
        animation="saving-throw",
        description=(
            f"{defender.template.name} makes a {ability.value.title()} save "
            f"against {feature_id}: {'success' if success else 'failure'}."
        ),
    ), success


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
        _validate_unarmed_control(attacker, defender, distance_ft, require_free_hand=True)
        dc = _control_dc(attacker)
        save_event, success = _save_event(
            sequence, round_number, attacker, defender, "unarmed-grapple", dc, dice
        )
        events = [save_event]
        if not success and apply_condition(
            defender, ConditionType.GRAPPLED, attacker, escape_dc=dc
        ):
            events.append(BattleEvent(
                sequence=sequence + 1,
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
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Unarmed Grapple failed.")
        raise RuntimeError("Unarmed Grapple could not be resolved.") from exc


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
        _validate_unarmed_control(attacker, defender, battlefield.distance_ft, require_free_hand=False)
        dc = _control_dc(attacker)
        save_event, success = _save_event(
            sequence, round_number, attacker, defender, "unarmed-shove", dc, dice
        )
        if success:
            return [save_event]
        if outcome == "prone":
            apply_condition(defender, ConditionType.PRONE, attacker)
            effect = BattleEvent(
                sequence=sequence + 1, round_number=round_number, event_type="condition",
                actor_id=attacker.instance_id, actor_name=attacker.template.name,
                target_id=defender.instance_id, target_name=defender.template.name,
                condition=ConditionType.PRONE, condition_active=True, feature_id="unarmed-shove",
                animation="shove-prone", description=f"{defender.template.name} is knocked Prone.",
            )
        else:
            before = battlefield.distance_ft
            battlefield.distance_ft += 5
            effect = BattleEvent(
                sequence=sequence + 1, round_number=round_number, event_type="forced_movement",
                actor_id=attacker.instance_id, actor_name=attacker.template.name,
                target_id=defender.instance_id, target_name=defender.template.name,
                distance_before_ft=before, distance_after_ft=battlefield.distance_ft,
                movement_ft=5, feature_id="unarmed-shove", animation="push",
                description=f"{defender.template.name} is shoved 5 ft. away.",
            )
        return [save_event, effect]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Unarmed Shove failed.")
        raise RuntimeError("Unarmed Shove could not be resolved.") from exc
