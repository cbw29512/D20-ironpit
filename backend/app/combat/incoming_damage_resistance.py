from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.timed_conditions import apply_timed_condition, remove_effect_instance
from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState, DamageRollComponent

logger = logging.getLogger(__name__)
INCOMING_RESISTANCE_EFFECT_ID = "incoming-damage-type-resistance"


def apply_incoming_damage_type_resistance(
    target: CombatantState,
    components: list[DamageRollComponent],
) -> bool:
    """Spend a Reaction to resist the triggering damage type until the current turn ends."""
    try:
        rule = target.template.incoming_damage_type_resistance_reaction
        if rule is None or target.current_hp <= 0 or target.is_dead:
            return False
        if not is_available(target, "reaction"):
            return False
        damage_type = next((item.damage_type for item in components if item.total > 0), None)
        if damage_type is None:
            return False
        spend(target, "reaction")
        applied = apply_timed_condition(
            target,
            INCOMING_RESISTANCE_EFFECT_ID,
            rule.source_id,
            source_effect_id=rule.source_id,
            applied_round=target.current_round,
            expires_at_start_of_source_turn=False,
            expiry_timing=None,
            owned_damage_resistances=[damage_type],
        )
        return applied is not None
    except Exception:
        logger.exception("Incoming damage-type resistance failed for %s.", target.template.name)
        raise


def expire_current_turn_type_resistances(setup: EncounterSetup) -> None:
    try:
        for member in [*setup.heroes, *setup.monsters]:
            for effect in list(member.state.timed_effects):
                if effect.effect_id == INCOMING_RESISTANCE_EFFECT_ID:
                    remove_effect_instance(member.state, effect)
    except Exception:
        logger.exception("End-of-turn damage-type resistance expiry failed.")
        raise
