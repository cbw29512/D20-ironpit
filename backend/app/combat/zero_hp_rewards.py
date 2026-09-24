from __future__ import annotations

import logging

from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def _target_member(setup: EncounterSetup, target_id: str | None) -> EncounterCombatant | None:
    try:
        if target_id is None:
            return None
        return next(
            (
                member
                for member in [*setup.heroes, *setup.monsters]
                if member.combatant_id == target_id
            ),
            None,
        )
    except Exception as exc:
        logger.exception("Failed to resolve zero-HP reward target %s.", target_id)
        raise RuntimeError("Zero-HP reward target could not be resolved.") from exc


def resolve_zero_hp_temporary_hp_reward(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Grant source-declared Temporary HP after reducing one hostile creature from above 0 HP to 0 HP."""
    try:
        grant = source.state.template.progression_features.zero_hp_temporary_hp_grant
        if grant is None:
            return None
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Zero-HP reward source must match the triggering event actor.")
        if triggering_event.hp_before is None or triggering_event.hp_after is None:
            return None
        if triggering_event.hp_before <= 0 or triggering_event.hp_after != 0:
            return None

        target = _target_member(setup, triggering_event.target_id)
        if target is None or target.side == source.side:
            return None

        before = source.state.temporary_hp
        after = grant_temporary_hit_points(source.state, grant.temporary_hp)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=source.combatant_id,
            target_name=source.state.template.name,
            temporary_hp_before=before,
            temporary_hp_after=after,
            feature_id=grant.source_id,
            animation="temporary-hp",
            description=(
                f"{source.state.template.name}'s {grant.source_name} grants "
                f"{grant.temporary_hp} Temporary HP."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Zero-HP Temporary HP reward failed for %s after event %s.",
            source.combatant_id,
            triggering_event.sequence,
        )
        raise RuntimeError("Zero-HP Temporary HP reward could not be resolved.") from exc
