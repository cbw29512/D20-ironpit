from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.domain.runtime import CombatantState
from app.domain.targeting_overrides import TurnStartTargetingOverrideRule

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TargetingOverrideCheck:
    source_id: str
    source_name: str
    roll: int
    die_size: int
    minimum_roll: int
    activated: bool


def active_targeting_override(state: CombatantState) -> TurnStartTargetingOverrideRule | None:
    try:
        active_ids = set(state.active_targeting_override_ids)
        matches = [
            rule for rule in state.template.turn_start_targeting_overrides
            if rule.source_id in active_ids
        ]
        if len(matches) > 1:
            raise ValueError("Only one persistent targeting override may control a combatant at a time.")
        return matches[0] if matches else None
    except Exception:
        logger.exception("Failed active targeting-override lookup for %s.", state.template.name)
        raise


def sync_targeting_overrides_after_hp_change(state: CombatantState) -> list[str]:
    """End source rules whose printed lifecycle ends when full HP is regained."""
    try:
        if state.current_hp < effective_max_hp(state):
            return []
        removable = {
            rule.source_id for rule in state.template.turn_start_targeting_overrides
            if rule.ends_on_full_hp
        }
        ended = [source_id for source_id in state.active_targeting_override_ids if source_id in removable]
        if ended:
            state.active_targeting_override_ids = [
                source_id for source_id in state.active_targeting_override_ids
                if source_id not in removable
            ]
        return ended
    except Exception:
        logger.exception("Failed targeting-override HP synchronization for %s.", state.template.name)
        raise


def resolve_turn_start_targeting_overrides(
    state: CombatantState,
    dice: DiceProvider,
) -> list[TargetingOverrideCheck]:
    try:
        sync_targeting_overrides_after_hp_change(state)
        checks: list[TargetingOverrideCheck] = []
        active_ids = set(state.active_targeting_override_ids)
        for rule in state.template.turn_start_targeting_overrides:
            if rule.source_id in active_ids or state.current_hp <= 0 or state.current_hp > rule.max_current_hp:
                continue
            roll = dice.roll(rule.die_size)
            activated = roll >= rule.minimum_roll
            if activated:
                state.active_targeting_override_ids.append(rule.source_id)
                active_ids.add(rule.source_id)
            checks.append(TargetingOverrideCheck(
                source_id=rule.source_id,
                source_name=rule.source_name,
                roll=roll,
                die_size=rule.die_size,
                minimum_roll=rule.minimum_roll,
                activated=activated,
            ))
        return checks
    except Exception:
        logger.exception("Failed turn-start targeting override resolution for %s.", state.template.name)
        raise
