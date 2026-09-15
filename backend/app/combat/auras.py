from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.ongoing_damage import encounter_members, resolve_ongoing_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_end_turn_damage_auras(
    sequence: int, round_number: int, source: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-defined damaging emanations at the owner's end-turn timing window."""
    try:
        events: list[BattleEvent] = []
        if source.state.is_dead or not source.state.is_alive:
            return events, sequence
        for aura in source.state.template.end_turn_damage_auras:
            if aura.disabled_while_incapacitated and is_incapacitated(source.state):
                continue
            targets = [
                member for member in encounter_members(setup)
                if member.side != source.side and member.state.is_alive and not member.state.is_dead
                and combatant_distance(source, member) <= aura.radius_ft
            ]
            for target in targets:
                events.append(resolve_ongoing_damage(
                    sequence, round_number, source, target, setup, dice,
                    feature_id=aura.id, feature_name=aura.name,
                    dice_count=aura.damage_dice_count, dice_size=aura.damage_dice_size,
                    damage_bonus=aura.damage_bonus, damage_type=aura.damage_type,
                    animation="aura-damage",
                ))
                sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed end-turn aura resolution for %s.", source.combatant_id)
        raise RuntimeError("End-turn aura resolution failed.") from exc
