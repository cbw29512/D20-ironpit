"""Source-authorized action removal of a continuing timed-damage effect.

The source does not define how another creature targets the fire. Only
self-dousing is resolved until helper geometry is source-proven.
"""
from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
DOUSE_ACTION_ID = "douse-fire"


def douseable_effects(target: EncounterCombatant):
    """Only source-authorized ongoing damage may be doused."""
    try:
        return [
            effect for effect in target.state.timed_effects
            if effect.end_of_turn_dice_count > 0
            and DOUSE_ACTION_ID in effect.allowed_removal_action_ids
        ]
    except Exception:
        logger.exception("Douse eligibility failed for %s", target.combatant_id)
        raise


def choose_douse_target(actor: EncounterCombatant, setup: EncounterSetup):
    """The affected creature may spend its own Action without a range assumption."""
    try:
        if not is_available(actor.state, "action"):
            return None
        return actor if actor.state.is_alive and not actor.state.is_dead and douseable_effects(actor) else None
    except Exception:
        logger.exception("Douse target selection failed for %s", actor.combatant_id)
        raise


def resolve_douse_action(
    sequence: int, round_number: int, actor: EncounterCombatant,
    target: EncounterCombatant,
) -> BattleEvent:
    """Spend one Action and remove only the approved recurring fire effect."""
    try:
        if actor.combatant_id != target.combatant_id:
            raise ValueError("Helper dousing requires an unspecified target range.")
        effects = douseable_effects(target)
        if not effects or not target.state.is_alive or target.state.is_dead:
            raise ValueError("Target has no source-authorized douseable effect.")
        if not is_available(actor.state, "action"):
            raise ValueError("Douse requires an available Action.")
        spend(actor.state, "action")
        removed = []
        sources = []
        for effect in effects:
            if effect.source_name and effect.source_name not in sources:
                sources.append(effect.source_name)
            if remove_effect_instance(target.state, effect):
                removed.append(effect.effect_id)
        return BattleEvent(
            sequence=sequence, round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            removed_condition_ids=removed, feature_id=DOUSE_ACTION_ID,
            animation="condition-ended",
            description=(
                f"{actor.state.template.name} uses Douse Fire on "
                f"{target.state.template.name}; "
                f"{', '.join(sources) or 'ongoing fire'} ends."
            ),
        )
    except Exception:
        logger.exception("Douse action failed: %s -> %s", actor.combatant_id, target.combatant_id)
        raise
