"""Universal same-target hit threshold that applies a source-owned grapple.

Cards declare attack ID and thresholds. Every resolved attack still goes through
the ordinary attack, condition immunity, grapple escape, and cleanup engines.
"""
from __future__ import annotations

import logging

from app.combat.grapple import apply_grapple
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def apply_multi_hit_grapples(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, attack_events: list[BattleEvent],
) -> tuple[list[BattleEvent], int]:
    """Compose action-local hit evidence; never carry it into another turn."""
    try:
        rules = attacker.state.template.multi_hit_grapple_effects
        if not rules or attacker.state.is_dead or not attacker.state.is_alive:
            return [], sequence
        members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        results: list[BattleEvent] = []
        for rule in rules:
            hits: dict[str, int] = {}
            for event in attack_events:
                if event.event_type != "attack" or event.attack_id != rule.attack_id:
                    continue
                if not event.hit or not event.target_id:
                    continue
                hits[event.target_id] = hits.get(event.target_id, 0) + 1
                if hits[event.target_id] != rule.hits_required:
                    continue
                target = members.get(event.target_id)
                if target is None or target.side == attacker.side:
                    raise ValueError("Multi-hit grapple target is not an opponent.")
                state = target.state
                if state.is_dead or not state.is_alive or state.current_hp <= 0:
                    continue
                if not size_at_most(state.template.size, rule.max_target_size):
                    continue
                if abs(attacker.position_ft - target.position_ft) > rule.range_ft:
                    continue
                held = sum(
                    any(source.source_id == attacker.combatant_id for source in member.state.grapple_sources)
                    for member in members.values() if member.combatant_id != attacker.combatant_id
                )
                if held >= rule.max_active_grapples:
                    continue
                applied = apply_grapple(
                    state, attacker.combatant_id, rule.escape_dc, rule.range_ft,
                    restrains=rule.restrains, blinds=rule.blinds,
                    prevents_breathing=rule.prevents_breathing,
                )
                if not applied:
                    continue
                conditions = [*applied]
                if rule.blinds and "blinded" in state.active_effect_ids:
                    conditions.append("blinded")
                results.append(BattleEvent(
                    sequence=sequence, round_number=round_number,
                    event_type="feature", actor_id=attacker.combatant_id,
                    actor_name=attacker.state.template.name,
                    target_id=target.combatant_id, target_name=state.template.name,
                    feature_id=rule.source_name,
                    applied_condition_ids=list(dict.fromkeys(conditions)),
                    animation="feature",
                    description=(
                        f"{attacker.state.template.name}: {rule.source_name} after "
                        f"{rule.hits_required} hits on {state.template.name}; "
                        f"Grappled (escape DC {rule.escape_dc})"
                        + (", Blinded" if rule.blinds else "")
                        + (", Restrained" if rule.restrains else "")
                        + (", unable to breathe" if rule.prevents_breathing else "")
                        + "."
                    ),
                ))
                sequence += 1
        return results, sequence
    except Exception:
        logger.exception("Shared Multiattack-hit grapple failed for %s.", attacker.combatant_id)
        raise
