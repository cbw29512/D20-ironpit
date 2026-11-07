"""Universal Multiattack hit-count grapple: card-parameterized and source-neutral."""
from __future__ import annotations

import logging
from collections import Counter

from app.combat.grapple import apply_grapple
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def resolve_hit_grapple(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, successful_hits: list[tuple[str, str]],
) -> tuple[list[BattleEvent], int]:
    """Use exactly one same-target hit requirement over the current action."""
    try:
        action = attacker.state.template.attack_action
        rule = action.hit_grapple if action is not None else None
        if rule is None or not attacker.state.is_alive or attacker.state.is_dead:
            return [], sequence
        members = [*setup.heroes, *setup.monsters]
        hits = Counter(
            target_id for attack_id, target_id in successful_hits
            if attack_id == rule.attack_id
        )
        current = sum(
            1 for member in members
            if member.combatant_id != attacker.combatant_id
            and any(
                held.source_id == attacker.combatant_id
                and rule.ownership_marker_id in held.linked_condition_ids
                for held in member.state.grapple_sources
            )
        )
        if current >= rule.max_active_targets:
            return [], sequence
        for target in members:
            if hits[target.combatant_id] < rule.required_hits:
                continue
            if target.side == attacker.side or target.state.swallowed is not None:
                continue
            if target.state.is_dead or not target.state.is_alive or target.state.current_hp <= 0:
                continue
            if not size_at_most(target.state.template.size, rule.max_target_size):
                continue
            if abs(attacker.position_ft - target.position_ft) > rule.grapple_range_ft:
                continue
            applied = apply_grapple(
                target.state, attacker.combatant_id,
                rule.grapple_escape_dc, rule.grapple_range_ft, restrains=True,
                linked_condition_ids=tuple(rule.linked_condition_ids),
            )
            if "grappled" not in applied:
                continue
            return [BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=rule.source_name, applied_condition_ids=applied,
                animation="feature",
                description=(
                    f"{attacker.state.template.name}: {rule.source_name} triggers after "
                    f"{rule.required_hits} successful {rule.attack_id} hits on "
                    f"{target.state.template.name}; grappled (escape DC "
                    f"{rule.grapple_escape_dc}), blinded and restrained."
                ),
            )], sequence + 1
        return [], sequence
    except Exception:
        logger.exception("Multiattack hit-grapple resolution failed for %s.", attacker.combatant_id)
        raise
