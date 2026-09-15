from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def forbidden_attacks_while_swallowing(attacker: EncounterCombatant, setup: EncounterSetup) -> set[str]:
    try:
        members = [*setup.heroes, *setup.monsters]
        swallowed_states = [
            member.state.swallowed
            for member in members
            if member.state.swallowed and member.state.swallowed.source_id == attacker.combatant_id
        ]
        if not swallowed_states:
            return set()
        actions = {item.id: item for item in attacker.state.template.swallow_actions}
        forbidden: set[str] = set()
        for swallowed in swallowed_states:
            action = actions.get(swallowed.action_id)
            if action is None:
                raise ValueError(f"Missing active Swallow action {swallowed.action_id!r}.")
            forbidden.update(action.forbidden_attack_ids_while_active)
        return forbidden
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to inspect swallowed attack restrictions for %s.", attacker.combatant_id)
        raise RuntimeError("Swallow attack restrictions could not be evaluated.") from exc
