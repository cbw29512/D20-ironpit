from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.resources import resource_available, spend_resource
from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import BattleEvent, EncounterCombatant
from app.domain.progression import TimedSelfEffectGrant

logger = logging.getLogger(__name__)


def can_activate_timed_self_effect(actor: EncounterCombatant, grant: TimedSelfEffectGrant) -> bool:
    """Fail closed unless both the printed action cost and finite resource are available."""
    try:
        return is_available(actor.state, grant.action_cost) and resource_available(
            actor.state, grant.resource_id, grant.resource_cost
        )
    except Exception:
        logger.exception("Failed to check timed self effect %s for %s", grant.source_id, actor.state.template.name)
        return False


def activate_timed_self_effect(
    actor: EncounterCombatant,
    grant: TimedSelfEffectGrant,
    *,
    round_number: int,
    sequence: int,
) -> BattleEvent:
    """Spend generic costs and install one source-owned timed composite self effect."""
    try:
        if not grant.condition_ids:
            raise ValueError("Timed self effect requires at least one condition/effect id.")
        if not can_activate_timed_self_effect(actor, grant):
            raise ValueError(f"{grant.source_name} is not currently legal.")

        # Validate before mutating either action economy or resource state.
        resistances = list(grant.damage_resistances)
        expires_round = round_number + grant.duration_rounds

        spend(actor.state, grant.action_cost)
        remaining = spend_resource(actor.state, grant.resource_id, grant.resource_cost)

        for index, condition_id in enumerate(grant.condition_ids):
            apply_timed_condition(
                actor.state,
                condition_id,
                actor.combatant_id,
                source_effect_id=grant.source_id,
                applied_round=round_number,
                expires_round=expires_round,
                expires_at_start_of_source_turn=True,
                # The source-owned defenses are attached once to the group. All
                # grouped conditions still expire together via source_effect_id.
                owned_damage_resistances=resistances if index == 0 else [],
                affected_states=[actor.state],
                use_default_poison_recovery=False,
            )

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=actor.combatant_id,
            target_name=actor.state.template.name,
            feature_id=grant.source_id,
            resource_id=grant.resource_id,
            resource_cost=grant.resource_cost if grant.resource_id else None,
            resource_remaining=remaining,
            animation="buff",
            description=f"{actor.state.template.name} activates {grant.source_name}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to activate timed self effect %s for %s", grant.source_id, actor.state.template.name)
        raise RuntimeError(f"Could not activate {grant.source_name}.") from exc
