from __future__ import annotations

import logging

from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_source_damage_temporary_hp(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    applied_damage: int,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-owned Temporary HP after a declared action deals actual damage."""
    try:
        rule = source.state.template.progression_features.source_damage_temporary_hp
        if rule is None or applied_damage <= 0:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Damage-triggered Temporary HP source must match the event actor.")
        if triggering_event.feature_id not in rule.trigger_action_ids:
            return [], sequence

        scores = source.state.template.ability_scores
        if scores is None:
            raise ValueError("Damage-triggered Temporary HP requires certified ability scores.")

        amount = max(
            rule.minimum,
            rule.flat_bonus + rule.ability_multiplier * scores.modifier(rule.ability),
        )
        if amount <= 0:
            return [], sequence

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
                f"{source.state.template.name} gains {amount} Temporary HP "
                f"from {rule.source_name} after dealing damage."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Source damage-triggered Temporary HP failed after event %s.",
            triggering_event.sequence,
        )
        raise RuntimeError("Damage-triggered Temporary HP could not be resolved.") from exc
