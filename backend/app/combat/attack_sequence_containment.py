"""Universal same-target hit-count trigger for a source-owned containment state."""
from __future__ import annotations

import logging

from app.combat.grapple import apply_grapple
from app.combat.swallow_state import swallow_after_bite
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def apply_attack_sequence_containment(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack,
    current_action_events: list[BattleEvent],
) -> BattleEvent | None:
    """Trigger only after N real hits in the same Multiattack on one target.

    The printed grapple is resolved through the ordinary universal grapple
    primitive and immediately transitioned into the existing contained state.
    """
    try:
        if not (target.state.is_alive and not target.state.is_dead
                and target.state.current_hp > 0 and target.state.swallowed is None):
            return None
        for rule in attacker.state.template.swallow_actions:
            if rule.delivery_mode != "attack_sequence" or rule.attack_id != attack.id:
                continue
            if (rule.required_sequence_hits < 2 or rule.sequence_grapple_dc is None
                    or not size_at_most(target.state.template.size, rule.max_target_size)):
                continue
            hits = sum(
                event.event_type == "attack" and event.hit is True
                and event.actor_id == attacker.combatant_id
                and event.target_id == target.combatant_id
                and event.attack_id == rule.attack_id
                for event in current_action_events
            )
            if hits != rule.required_sequence_hits:
                continue
            if (rule.max_swallowed is not None
                    and len(attacker.state.swallowed_target_ids) >= rule.max_swallowed):
                continue
            grapple = apply_grapple(
                target.state, attacker.combatant_id, rule.sequence_grapple_dc,
                attack.weapon.reach_ft,
            )
            if "grappled" not in grapple:
                continue
            if not swallow_after_bite(
                attacker.combatant_id, attacker.state,
                target.combatant_id, target.state, rule, bite_hit=True,
            ):
                raise RuntimeError("A validated hit sequence could not complete containment.")
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=rule.source_name, animation="feature",
                applied_condition_ids=["blinded", "restrained"],
                description=(f"{attacker.state.template.name}: two {attack.weapon.name} hits "
                             f"grapple {target.state.template.name} (escape DC "
                             f"{rule.sequence_grapple_dc}), then {rule.source_name} "
                             "contains the target: Blinded and Restrained."
                             + (" Unable to breathe." if rule.cannot_breathe else "")),
            )
        return None
    except Exception:
        logger.exception("Failed universal attack-sequence containment.")
        raise
