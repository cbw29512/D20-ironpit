from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TurnStartEffectCheck:
    source_id: str
    source_name: str
    effect_id: str
    roll: int
    die_size: int
    minimum_roll: int
    activated: bool


def sync_turn_start_effects_after_hp_change(state: CombatantState) -> list[str]:
    """End active source effects whose lifecycle ends when full HP is regained."""
    try:
        if state.current_hp < effective_max_hp(state):
            return []
        removable = {
            rule.effect_id
            for rule in state.template.turn_start_persistent_effects
            if rule.ends_on_full_hp
        }
        ended = [effect_id for effect_id in state.active_effect_ids if effect_id in removable]
        if ended:
            state.active_effect_ids = [
                effect_id for effect_id in state.active_effect_ids
                if effect_id not in removable
            ]
        return ended
    except Exception:
        logger.exception("Failed turn-start effect HP synchronization for %s.", state.template.name)
        raise


def resolve_turn_start_persistent_effects(
    state: CombatantState,
    dice: DiceProvider,
) -> list[TurnStartEffectCheck]:
    try:
        sync_turn_start_effects_after_hp_change(state)
        checks: list[TurnStartEffectCheck] = []
        for rule in state.template.turn_start_persistent_effects:
            if (
                rule.effect_id in state.active_effect_ids
                or state.current_hp <= 0
                or state.current_hp > rule.max_current_hp
            ):
                continue
            roll = dice.roll(rule.die_size)
            activated = roll >= rule.minimum_roll
            if activated:
                state.active_effect_ids.append(rule.effect_id)
            checks.append(TurnStartEffectCheck(
                source_id=rule.source_id,
                source_name=rule.source_name,
                effect_id=rule.effect_id,
                roll=roll,
                die_size=rule.die_size,
                minimum_roll=rule.minimum_roll,
                activated=activated,
            ))
        return checks
    except Exception:
        logger.exception("Failed turn-start persistent effect resolution for %s.", state.template.name)
        raise
