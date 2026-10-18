from __future__ import annotations

import logging

from app.combat.spellcasting import slot_spell_available, spell_turn_legal
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.teleport_actions import TeleportAction

logger = logging.getLogger(__name__)


def choose_teleport_destination(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: TeleportAction,
) -> GridPosition | None:
    """Pit-banned teleport never selects a new square."""
    try:
        if setup is None or action is None:
            raise ValueError("Teleport destination choice requires a setup and action.")
        if caster is None or caster.state.position is None:
            return None
        return caster.state.position.model_copy(deep=True)
    except Exception:
        logger.exception("Failed to choose teleport destination for %s.", getattr(caster, "combatant_id", "?"))
        raise


def choose_teleport_action(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[TeleportAction, GridPosition] | None:
    """Arena AI never teleports away. It may clear teleport-cancelable debuffs in place."""
    try:
        if caster is None or setup is None or not str(turn_key or "").strip():
            raise ValueError("Teleport choice requires a caster, setup, and turn key.")
        from app.combat.action_economy import is_available
        from app.combat.teleport_cancel import teleport_cancelable_effect_ids

        if caster.state.position is None:
            return None
        if not teleport_cancelable_effect_ids(caster.state):
            return None
        actions = []
        for action in caster.state.template.teleport_actions:
            if not is_available(caster.state, action.action_cost):
                continue
            # Only spell teleports participate in the spell-turn restriction.
            if (action.level > 0 or action.expends_spell_slot) and not spell_turn_legal(
                caster.state, turn_key, action.action_cost, action.level,
            ):
                continue
            if action.expends_spell_slot and not slot_spell_available(caster.state, turn_key):
                continue
            if action.resource_id:
                resource = next(
                    (item for item in caster.state.resources if item.id == action.resource_id),
                    None,
                )
                if resource is None or resource.current_uses < action.resource_cost:
                    continue
            actions.append(action)
        if not actions:
            return None
        action = min(actions, key=lambda item: (item.level, item.id))
        return action, caster.state.position.model_copy(deep=True)
    except Exception:
        logger.exception("Failed teleport choice for %s.", getattr(caster, "combatant_id", "?"))
        raise
