from __future__ import annotations

import logging

from app.domain.models import BattlefieldState, CombatantState, ConditionKind

logger = logging.getLogger(__name__)


def can_see_combatant(
    observer: CombatantState,
    target: CombatantState,
    battlefield: BattlefieldState | None = None,
) -> bool:
    """Resolve sight for the currently supported visibility subset."""
    try:
        if ConditionKind.INVISIBLE in target.conditions:
            return False
        if battlefield is None:
            return True
        visibility = battlefield.visibility_by_actor.get(target.template.id)
        return visibility is None or visibility.enemy_line_of_sight
    except Exception as exc:
        logger.exception(
            "Sight resolution failed: %s -> %s.",
            observer.template.name,
            target.template.name,
        )
        raise RuntimeError("Combat sight could not be resolved.") from exc


def resolve_visibility_attack_sources(
    attacker: CombatantState,
    defender: CombatantState,
    battlefield: BattlefieldState | None = None,
) -> tuple[int, int]:
    """Return unseen-attacker Advantage and unseen-target Disadvantage sources."""
    try:
        advantage = int(not can_see_combatant(defender, attacker, battlefield))
        disadvantage = int(not can_see_combatant(attacker, defender, battlefield))
        return advantage, disadvantage
    except Exception as exc:
        logger.exception("Attack visibility effects could not be resolved.")
        raise RuntimeError("Attack visibility effects could not be resolved.") from exc
