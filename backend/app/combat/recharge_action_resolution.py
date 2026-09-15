from __future__ import annotations

import logging

from app.combat.ally_context import pack_tactics_active
from app.combat.area_save_actions import resolve_area_save_action
from app.combat.opening_burst import opening_feature_id
from app.combat.recharge_action_policy import recharge_action_choice
from app.combat.saving_throws import resolve_save_action
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_priority_recharge_action(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int, bool]:
    try:
        choice = recharge_action_choice(attacker, setup)
        if choice is None:
            return [], sequence, False
        kind, payload = choice
        if kind == "save":
            target, action, distance = payload
            affected = [member.state for member in [*setup.heroes, *setup.monsters]]
            event = resolve_save_action(
                sequence, round_number, attacker, target, action, distance, dice,
                affected_states=affected,
            )
            return [event], sequence + 1, True
        if kind == "area-save":
            action, placement = payload
            events, sequence, _ = resolve_area_save_action(
                sequence, round_number, attacker, setup, action, dice, placement=placement,
            )
            return events, sequence, True
        if kind == "attack":
            target, attack, distance = payload
            pack = pack_tactics_active(attacker, target, setup)
            feature = opening_feature_id(round_number, attacker, setup) or ("pack-tactics" if pack else None)
            events, sequence = resolve_standard_attack_action(
                sequence, round_number, attacker, target, attack, distance, dice, setup, turn_key,
                advantage_sources=1 if pack else 0, feature_id=feature,
            )
            return events, sequence, True
        raise ValueError(f"Unsupported Recharge action family: {kind!r}.")
    except Exception as exc:
        logger.exception("Failed prioritized Recharge resolution for %s.", attacker.combatant_id)
        raise RuntimeError("Prioritized Recharge action could not be resolved.") from exc
