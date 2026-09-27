from __future__ import annotations

import logging

from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
    if combatant_id is None:
        return None
    return next(
        (
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == combatant_id
        ),
        None,
    )


def resolve_source_zero_hp_triggers(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-owned effects triggered by reducing a hostile creature to 0 HP."""
    try:
        rule = source.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
        if rule is None:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Zero-HP trigger source must match the triggering event actor.")

        target = _member_by_id(setup, triggering_event.target_id)
        if target is None or target.combatant_id == source.combatant_id or target.side == source.side:
            return [], sequence
        if triggering_event.hp_before is None or triggering_event.hp_after is None:
            return [], sequence
        if triggering_event.hp_before <= 0 or triggering_event.hp_after != 0:
            return [], sequence

        scores = source.state.template.ability_scores
        level = source.state.template.level
        if scores is None or level is None:
            raise ValueError("Zero-HP Temporary HP trigger requires certified ability scores and level.")

        amount = max(
            rule.minimum,
            rule.flat_bonus + rule.per_level * level + scores.modifier(rule.ability),
        )
        before = source.state.temporary_hp
        after = grant_temporary_hit_points(source.state, amount)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=source.combatant_id,
            target_name=source.state.template.name,
            hp_before=source.state.current_hp,
            hp_after=source.state.current_hp,
            temporary_hp_before=before,
            temporary_hp_after=after,
            feature_id=rule.source_id,
            animation="feature",
            description=(
                f"{source.state.template.name} gains {amount} Temporary HP from {rule.source_name} "
                f"after reducing a hostile creature to 0 HP."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Source zero-HP trigger dispatch failed after event %s.", triggering_event.sequence)
        raise RuntimeError("Source zero-HP trigger could not be resolved.") from exc
