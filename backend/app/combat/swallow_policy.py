from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def forbidden_attacks_while_swallowing(attacker: EncounterCombatant, setup: EncounterSetup) -> set[str]:
    try:
        members = [*setup.heroes, *setup.monsters]
        swallowed = next(
            (
                member.state.swallowed
                for member in members
                if member.state.swallowed and member.state.swallowed.source_id == attacker.combatant_id
            ),
            None,
        )
        if swallowed is None:
            return set()
        action = next(
            (item for item in attacker.state.template.swallow_actions if item.id == swallowed.action_id),
            None,
        )
        if action is None:
            raise ValueError(f"Missing active Swallow action {swallowed.action_id!r}.")
        return set(action.forbidden_attack_ids_while_active)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to inspect swallowed attack restrictions for %s.", attacker.combatant_id)
        raise RuntimeError("Swallow attack restrictions could not be evaluated.") from exc
