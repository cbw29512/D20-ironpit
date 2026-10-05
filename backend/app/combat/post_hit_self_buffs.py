from __future__ import annotations

import logging

from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.timed_self_buff_policy import timed_self_buff_active
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def apply_triggered_post_hit_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup | None,
    attack_event: BattleEvent,
) -> str | None:
    """Activate a declared timed self-buff only when its paid post-hit damage resolved."""
    try:
        if setup is None or not attack_event.hit:
            return None
        rule = member.state.template.progression_features.resource_backed_post_hit_damage
        if rule is None or rule.post_hit_self_buff_action_id is None:
            return None
        if not any(component.source_effect_id == rule.source_id for component in attack_event.damage_components):
            return None
        action = next(
            (
                item for item in member.state.template.timed_self_buff_actions
                if item.id == rule.post_hit_self_buff_action_id
            ),
            None,
        )
        if action is None:
            raise ValueError(
                f"Post-hit buff action {rule.post_hit_self_buff_action_id} is not declared."
            )
        if timed_self_buff_active(member, action):
            sync_friendly_save_auras(setup)
            return None
        resolve_timed_self_buff(
            sequence,
            round_number,
            member,
            action,
            spend_action_cost=False,
            affected_states=[entry.state for entry in [*setup.heroes, *setup.monsters]],
        )
        sync_friendly_save_auras(setup)
        return action.name
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Triggered post-hit self-buff failed for %s.", member.combatant_id)
        raise RuntimeError("Triggered post-hit self-buff could not be resolved.") from exc
