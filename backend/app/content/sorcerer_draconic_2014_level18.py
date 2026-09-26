from __future__ import annotations

from app.domain.timed_self_buffs import TimedHostileConditionAura, TimedSelfBuffAction


def draconic_presence_fear_2014(save_dc: int) -> TimedSelfBuffAction:
    """Deterministic Fear-mode Draconic Presence using universal timed-aura mechanics."""
    return TimedSelfBuffAction(
        id="draconic-presence-fear",
        name="Draconic Presence: Fear",
        action_cost="action",
        resource_id="sorcery-points",
        resource_cost=5,
        duration_rounds=10,
        hostile_start_turn_condition_aura=TimedHostileConditionAura(
            trigger="enemy_turn_start",
            radius_ft=60,
            save_ability="wisdom",
            save_dc=save_dc,
            condition_id="frightened",
            success_immunity_rounds=14400,
            source_is_magical=True,
        ),
        concentration=True,
        ends_if_source_incapacitated=True,
        ends_if_source_dead=True,
        expiry_timing="source_turn_start",
        priority=130,
        animation="draconic-presence",
    )
