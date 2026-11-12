"""Target ordering for save actions whose printed scope can include allies."""
from __future__ import annotations

import logging

from app.combat.charmed_targeting import charmed_blocks_hostile_target
from app.combat.pit_policy import is_backline, target_order
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def save_action_target_order(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    target_scope: str,
) -> list[EncounterCombatant]:
    """Return legal-scope candidates, keeping normal enemies ahead of willing allies."""
    try:
        if target_scope not in {"enemies", "all-other-creatures"}:
            raise ValueError(f"Unsupported save-action target scope: {target_scope}")
        primary = target_order(attacker, setup)
        if target_scope == "enemies":
            return primary

        enemies = setup.monsters if attacker.side == "heroes" else setup.heroes
        allies = setup.heroes if attacker.side == "heroes" else setup.monsters
        primary_ids = {member.combatant_id for member in primary}

        def eligible(member: EncounterCombatant) -> bool:
            state = member.state
            return (
                member.combatant_id != attacker.combatant_id
                and state.is_alive and not state.is_dead
                and state.swallowed is None
                and not any(effect.removed_from_battlefield for effect in state.timed_effects)
                and not charmed_blocks_hostile_target(attacker.state, member.combatant_id)
            )

        remaining_enemies = [
            member for member in enemies
            if member.combatant_id not in primary_ids and eligible(member)
        ]
        remaining_allies = [
            member for member in allies
            if member.combatant_id not in primary_ids and eligible(member)
        ]
        formation_order = lambda members: sorted(
            members, key=lambda member: (is_backline(member), member.combatant_id),
        )
        return [*primary, *formation_order(remaining_enemies), *formation_order(remaining_allies)]
    except Exception as exc:
        logger.exception("Save-action target ordering failed for %s.", attacker.combatant_id)
        raise RuntimeError("Save-action targets could not be ordered.") from exc
