from __future__ import annotations

import logging

from app.combat.selectable_damage_resistance import score_enemy_damage_types
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def choose_timed_defense_by_threat(
    member: EncounterCombatant,
    setup: EncounterSetup,
    choices: list[TimedSelfBuffAction],
) -> TimedSelfBuffAction | None:
    """Keep declared priority unless matching defensive variants counter observed enemy offense."""
    try:
        preferred = max(choices, key=lambda item: item.priority, default=None)
        if preferred is None or preferred.selection_strategy != "incoming-damage":
            return preferred
        variants = [
            action for action in choices
            if action.selection_group == preferred.selection_group
            and action.selection_strategy == preferred.selection_strategy
            and action.resource_id == preferred.resource_id
        ]
        types = list(dict.fromkeys(action.damage_resistances[0] for action in variants))
        incoming = score_enemy_damage_types(member, setup, types)
        if not any(incoming.values()):
            return preferred
        return max(
            variants,
            key=lambda action: (incoming[action.damage_resistances[0]], action.priority),
        )
    except Exception:
        logger.exception("Timed defensive variant selection failed for %s.", member.combatant_id)
        raise
