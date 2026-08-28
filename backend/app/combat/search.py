from __future__ import annotations

import logging

from app.combat.conditions import require_activity
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.combat.stealth import break_hidden
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)
SEARCH_FEATURE = "search"


def take_search_action(
    sequence: int,
    round_number: int,
    observer: CombatantState,
    target: CombatantState,
    dice: DiceProvider,
) -> BattleEvent:
    try:
        require_activity(observer, "Action")
        if not observer.action_available:
            raise ValueError("Action is not available for Search.")
        if not target.hidden or target.hidden_dc is None:
            raise ValueError("Target is not hidden.")

        check = roll_d20(dice, observer.template.skill_bonuses.get("perception", 0))
        observer.action_available = False
        found = check.total >= target.hidden_dc
        if found:
            break_hidden(target)
        result = "finds" if found else "does not find"
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="search",
            actor_id=observer.template.id,
            actor_name=observer.template.name,
            target_id=target.template.id,
            target_name=target.template.name,
            check_roll=check,
            feature_id=SEARCH_FEATURE,
            animation="search",
            description=f"{observer.template.name} {result} {target.template.name}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Search action failed for %s.", observer.template.name)
        raise RuntimeError("Search action could not be resolved.") from exc
