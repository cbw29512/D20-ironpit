"""Target ordering for save actions whose printed scope can include allies."""
from __future__ import annotations

import logging

from app.combat.charmed_targeting import charmed_blocks_hostile_target
from app.combat.encounter_targeting import active_target_policy, target_priority
from app.combat.pit_policy import is_backline, target_order
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def save_action_target_order(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    target_scope: str,
) -> list[EncounterCombatant]:
    """Return all in-scope candidates, with enemies ahead of willing allies."""
    try:
        if target_scope not in {"enemies", "all-other-creatures"}:
            raise ValueError(f"Unsupported save-action target scope: {target_scope}")
        if target_scope == "enemies":
            return target_order(attacker, setup)
        if active_target_policy(attacker) == "nearest_visible_creature":
            return target_order(attacker, setup)

        candidates: list[tuple[int, EncounterCombatant]] = []
        for member in [*setup.heroes, *setup.monsters]:
            state = member.state
            if (
                member.combatant_id == attacker.combatant_id
                or not state.is_alive or state.is_dead
                or state.swallowed is not None
                or any(effect.removed_from_battlefield for effect in state.timed_effects)
                or charmed_blocks_hostile_target(attacker.state, member.combatant_id)
            ):
                continue
            priority = target_priority(member)
            if priority is None and state.current_hp == 0:
                priority = 3
            if priority is not None:
                candidates.append((priority, member))

        return [member for _priority, member in sorted(
            candidates,
            key=lambda item: (
                item[0],
                item[1].side == attacker.side,
                is_backline(item[1]),
                item[1].combatant_id,
            ),
        )]
    except Exception as exc:
        logger.exception("Save-action target ordering failed for %s.", attacker.combatant_id)
        raise RuntimeError("Save-action targets could not be ordered.") from exc
