from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import BattleEvent, CombatantState, DiceRoll

logger = logging.getLogger(__name__)


def use_second_wind(
    sequence: int,
    round_number: int,
    fighter: CombatantState,
    dice: DiceProvider,
) -> BattleEvent:
    """Apply the SRD 5.2.1 Second Wind healing/resource rules to a Fighter state."""
    try:
        resource = next((item for item in fighter.resources if item.id == "second-wind"), None)
        if resource is None or resource.current_uses <= 0:
            raise ValueError("Second Wind has no remaining uses.")
        if not fighter.bonus_action_available:
            raise ValueError("Bonus Action is not available.")
        if fighter.template.level is None:
            raise ValueError("Second Wind requires a Fighter level.")

        rolled = dice.roll(10)
        healing_roll = DiceRoll(
            notation=f"1d10+{fighter.template.level}",
            rolls=[rolled],
            modifier=fighter.template.level,
            total=rolled + fighter.template.level,
        )
        hp_before = fighter.current_hp
        fighter.current_hp = min(fighter.template.max_hp, fighter.current_hp + healing_roll.total)
        fighter.bonus_action_available = False
        resource.current_uses -= 1
        healed = fighter.current_hp - hp_before

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="healing",
            actor_id=fighter.template.id,
            actor_name=fighter.template.name,
            target_id=fighter.template.id,
            target_name=fighter.template.name,
            healing_roll=healing_roll,
            hp_before=hp_before,
            hp_after=fighter.current_hp,
            feature_id="second-wind",
            resource_remaining=resource.current_uses,
            animation="second-wind",
            description=f"{fighter.template.name} uses Second Wind and regains {healed} HP.",
        )
    except Exception as exc:
        logger.exception("Second Wind resolution failed for %s.", fighter.template.name)
        raise RuntimeError("Second Wind could not be resolved.") from exc


def use_action_surge(
    sequence: int,
    round_number: int,
    fighter: CombatantState,
) -> BattleEvent:
    """Spend Action Surge to restore one non-Magic action slot for this arena turn."""
    try:
        resource = next((item for item in fighter.resources if item.id == "action-surge"), None)
        if resource is None or resource.current_uses <= 0:
            raise ValueError("Action Surge has no remaining uses.")
        if fighter.action_surge_used_this_turn:
            raise ValueError("Action Surge can be used only once on a turn.")
        if fighter.action_available:
            raise ValueError("Current action must be spent before restoring the additional action slot.")

        resource.current_uses -= 1
        fighter.action_available = True
        fighter.action_surge_used_this_turn = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=fighter.template.id,
            actor_name=fighter.template.name,
            feature_id="action-surge",
            resource_remaining=resource.current_uses,
            animation="action-surge",
            description=f"{fighter.template.name} uses Action Surge and gains an additional action.",
        )
    except Exception as exc:
        logger.exception("Action Surge resolution failed for %s.", fighter.template.name)
        raise RuntimeError("Action Surge could not be resolved.") from exc
