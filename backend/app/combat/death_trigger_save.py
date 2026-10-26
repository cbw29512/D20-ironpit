"""Resolve passive death-trigger saves through the normal universal save engine."""
from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.saving_throws import resolve_save_action
from app.content.monster_death_trigger_saves_2014 import DeathTriggeredSave
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_death_trigger_save(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    rule: DeathTriggeredSave,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Use ordinary saves/damage for death at any HP, without spending an Action."""
    try:
        if not source.state.is_dead:
            raise ValueError("A source-death trigger requires a dead source.")
        if target.state.is_dead:
            return None
        return resolve_save_action(
            sequence, round_number, source, target, rule.save_action,
            distance_ft, dice, spend_action=False, check_resource=False,
            spend_resource=False, setup=setup,
        )
    except Exception:
        logger.exception(
            "Death-trigger save resolution failed: source=%s target=%s rule=%s",
            source.combatant_id, target.combatant_id, rule.source_id,
        )
        raise
