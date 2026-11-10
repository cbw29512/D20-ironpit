"""Generic source-owned control capacity: a newly affected target replaces oldest.

The printed card owns the capacity and control effect. Runtime source_id and
source_effect_id identify one live owner's specific control without name dispatch.
"""
from __future__ import annotations

import logging

from app.combat.source_effect_immunity import (
    grant_source_effect_immunity,
    has_source_effect_immunity,
)
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def enforce_source_target_capacity(
    actor: EncounterCombatant,
    newest: EncounterCombatant,
    action_id: str,
    effect_id: str,
    maximum: int,
    setup: EncounterSetup | None,
) -> list[str]:
    """End excess oldest source-owned effects only after a new effect landed."""
    try:
        if maximum < 1 or maximum > 20:
            raise ValueError("Source-target capacity must be between 1 and 20.")
        if setup is None:
            raise ValueError("Source-target capacity needs an encounter roster.")
        members = [*setup.heroes, *setup.monsters]
        if newest not in members or actor not in members:
            raise ValueError("Source-target capacity actor/target must belong to encounter.")
        active = []
        for member in members:
            instance = next((
                effect for effect in member.state.timed_effects
                if effect.effect_id == effect_id
                and effect.source_id == actor.combatant_id
                and effect.source_effect_id == action_id
            ), None)
            if instance is not None:
                active.append((member, instance))
        if not any(member.combatant_id == newest.combatant_id for member, _ in active):
            raise ValueError("Source-target capacity requires the newly applied effect.")
        if len(active) <= maximum:
            return []
        # Keep the freshly selected target; expire oldest other targets first.
        others = sorted(
            ((member, effect) for member, effect in active
             if member.combatant_id != newest.combatant_id),
            key=lambda pair: (pair[1].applied_round or 0, pair[0].combatant_id),
        )
        expired = []
        for member, effect in others[:len(active) - maximum]:
            remove_effect_group(member.state, effect)
            if any(
                item.effect_id == effect_id
                and item.source_id == actor.combatant_id
                and item.source_effect_id == action_id
                for item in member.state.timed_effects
            ):
                raise RuntimeError("Source-owned control was not released.")
            # A second source may still apply the same Charmed condition. The
            # existing group removal can return [] in that case; still record
            # printed immunity for the effect that actually ended.
            if effect.source_effect_immunity_on_end and not has_source_effect_immunity(
                member.state, action_id, actor.combatant_id,
            ):
                grant_source_effect_immunity(
                    member.state, action_id, actor.combatant_id,
                    member.state.current_round or 1,
                    source_is_magical=effect.source_is_magical,
                )
            expired.append(member.combatant_id)
        return expired
    except Exception:
        logger.exception("Failed source-target capacity for %s/%s.", actor.combatant_id, action_id)
        raise
