from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _action_dealt_damage(events: list[BattleEvent]) -> bool:
    try:
        return any(
            (component.applied_total or 0) > 0
            for event in events
            for component in event.damage_components
        )
    except Exception as exc:
        logger.exception("Failed to inspect damaging-action event chain.")
        raise RuntimeError("Damaging-action rider could not inspect damage.") from exc


def _choose_target(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    amount: int,
    range_ft: int,
    target_mode: str,
) -> EncounterCombatant | None:
    try:
        allies = setup.heroes if actor.side == "heroes" else setup.monsters
        legal: list[EncounterCombatant] = []
        for target in allies:
            if target.state.is_dead:
                continue
            if target_mode == "self" and target.combatant_id != actor.combatant_id:
                continue
            if target_mode == "self_or_ally" and abs(target.position_ft - actor.position_ft) > range_ft:
                continue
            if target.state.temporary_hp >= amount:
                continue
            legal.append(target)
        if not legal:
            return None
        return min(
            legal,
            key=lambda target: (
                target.state.current_hp / max(1, effective_max_hp(target.state)),
                target.state.temporary_hp,
                target.combatant_id,
            ),
        )
    except Exception as exc:
        logger.exception("Failed to choose damaging-action Temporary HP target.")
        raise RuntimeError("Damaging-action Temporary HP target selection failed.") from exc


def resolve_damaging_action_temporary_hp(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action_id: str,
    events: list[BattleEvent],
) -> BattleEvent | None:
    """Resolve a generic post-damage Temporary HP rider from progression data."""
    try:
        rule = actor.state.template.progression_features.damaging_action_temporary_hp_rider
        if rule is None or action_id not in rule.action_ids or not _action_dealt_damage(events):
            return None

        scores = actor.state.template.ability_scores
        if scores is None:
            raise ValueError("Ability-scaled Temporary HP requires certified ability scores.")
        amount = max(0, scores.modifier(rule.ability) * rule.multiplier)
        target = _choose_target(actor, setup, amount, rule.range_ft, rule.target_mode)
        if target is None:
            return None

        before = target.state.temporary_hp
        after = grant_temporary_hit_points(target.state, amount)
        if after <= before:
            return None

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            temporary_hp_before=before,
            temporary_hp_after=after,
            feature_id=rule.source_id,
            animation="temporary-hp",
            description=(
                f"{actor.state.template.name} grants {target.state.template.name} "
                f"{after - before} Temporary HP with {rule.source_name}."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to resolve damaging-action Temporary HP for %s.",
            actor.combatant_id,
        )
        raise RuntimeError("Damaging-action Temporary HP could not be resolved.") from exc
