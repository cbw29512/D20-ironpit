from __future__ import annotations

import logging

from app.combat.deferred_save_effect import (
    deferred_save_effect_candidate,
    resolve_deferred_save_effect,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_deferred_effect_attack_slot(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> BattleEvent | None:
    """Use one Attack-action slot to activate an armed deferred effect when source data permits it."""
    try:
        rule = actor.state.template.progression_features.deferred_save_effect
        if rule is None or not rule.allow_attack_slot_activation:
            return None
        if deferred_save_effect_candidate(actor, setup, require_action=False) is None:
            return None
        return resolve_deferred_save_effect(
            sequence,
            round_number,
            actor,
            setup,
            dice,
            spend_action=False,
        )
    except Exception as exc:
        logger.exception("Failed deferred-effect attack-slot activation for %s.", actor.combatant_id)
        raise RuntimeError("Deferred effect attack-slot activation failed.") from exc
