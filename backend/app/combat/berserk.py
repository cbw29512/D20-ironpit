from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.events import BattleEvent
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def resolve_start_turn_berserk(
    sequence: int,
    round_number: int,
    combatant_id: str,
    state: CombatantState,
    dice: DiceProvider,
) -> BattleEvent | None:
    try:
        profile = state.template.berserk
        if profile is None:
            return None
        active = profile.effect_id in state.active_effect_ids
        if active and state.current_hp >= state.template.max_hp:
            state.active_effect_ids.remove(profile.effect_id)
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=combatant_id, actor_name=state.template.name,
                feature_id=profile.effect_id, removed_condition_ids=[profile.effect_id], animation="feature",
                description=f"{state.template.name} is no longer berserk after regaining all its hit points.",
            )
        if active or state.current_hp > profile.hp_threshold:
            return None
        roll = dice.roll(profile.die_size)
        triggered = roll == profile.trigger_roll
        if triggered:
            state.active_effect_ids.append(profile.effect_id)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=combatant_id, actor_name=state.template.name,
            feature_id=profile.effect_id if triggered else "berserk-check",
            resource_roll={
                "notation": f"1d{profile.die_size}", "rolls": [roll], "selected_roll": roll,
                "modifier": 0, "mode": "normal", "total": roll,
            },
            applied_condition_ids=[profile.effect_id] if triggered else [], animation="feature",
            description=(
                f"{state.template.name} rolls {roll} on d{profile.die_size} for Berserk and goes berserk."
                if triggered else
                f"{state.template.name} rolls {roll} on d{profile.die_size} for Berserk and remains controlled."
            ),
        )
    except Exception:
        logger.exception("Failed to resolve Berserk for %s.", state.template.name)
        raise
