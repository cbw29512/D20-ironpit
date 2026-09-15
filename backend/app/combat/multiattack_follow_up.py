from __future__ import annotations

import logging

from app.combat.grapple import apply_grapple
from app.combat.swallow_application import apply_swallowed, capacity_available
from app.domain.actions import AttackActionDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def resolve_multiattack_follow_up(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    definition: AttackActionDefinition,
    slot_attack_events: list[BattleEvent],
) -> tuple[list[BattleEvent], int]:
    """Resolve a source-declared post-Multiattack action after its generic trigger succeeds."""
    try:
        policy = definition.policy
        if policy is None or policy.follow_up_action_id is None:
            return [], sequence
        if policy.follow_up_condition != "all_attacks_hit_same_target":
            raise ValueError(f"Unsupported Multiattack follow-up trigger {policy.follow_up_condition!r}.")
        if len(slot_attack_events) != len(definition.slots) or not slot_attack_events:
            return [], sequence
        if any(event.hit is not True or event.target_id is None for event in slot_attack_events):
            return [], sequence
        target_ids = {event.target_id for event in slot_attack_events}
        if len(target_ids) != 1:
            return [], sequence
        target_id = next(iter(target_ids))
        target = next((member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == target_id), None)
        if target is None or target.state.is_dead or not target.state.is_alive or target.state.swallowed is not None:
            return [], sequence
        if policy.follow_up_max_target_size is not None and not size_at_most(
            target.state.template.size, policy.follow_up_max_target_size,
        ):
            return [], sequence
        action = next(
            (item for item in attacker.state.template.swallow_actions if item.id == policy.follow_up_action_id),
            None,
        )
        if action is None or action.attack_id is not None or not action.requires_existing_grapple:
            raise ValueError(f"Follow-up action {policy.follow_up_action_id!r} is not direct containment.")
        if policy.follow_up_grapple_escape_dc is None:
            raise ValueError("Direct containment follow-up requires a source-derived grapple escape DC.")
        if not capacity_available(attacker, setup, action):
            return [], sequence
        apply_grapple(
            target.state, attacker.combatant_id, policy.follow_up_grapple_escape_dc,
            source_size=attacker.state.template.size,
        )
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=action.id, animation="grapple",
            description=f"{attacker.state.template.name} uses {action.name} on {target.state.template.name}.",
        )
        apply_swallowed(attacker, target, action, event)
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Multiattack follow-up failed for %s.", attacker.combatant_id)
        raise RuntimeError("Multiattack follow-up could not be resolved.") from exc
