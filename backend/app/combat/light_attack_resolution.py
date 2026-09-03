from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.light_weapons import mark_light_extra_attack_used, plan_light_extra_attack
from app.combat.pit_policy import choose_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_light_extra_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    trigger_attack: WeaponAttack,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the Light extra attack in fixed Pit formation; Nick changes timing, never attack count."""
    try:
        plan = plan_light_extra_attack(attacker.state, trigger_attack, turn_key)
        if plan is None:
            return [], sequence
        if plan.uses_bonus_action and not is_available(attacker.state, "bonus_action"):
            return [], sequence

        choice = choose_attack(attacker, setup, [plan.attack.id])
        if choice is None:
            return [], sequence
        target, attack, distance = choice
        if plan.uses_bonus_action:
            spend(attacker.state, "bonus_action")
        mark_light_extra_attack_used(attacker.state, turn_key)
        pack = pack_tactics_active(attacker, target, setup)
        event = resolve_encounter_attack(
            sequence, round_number, attacker, target, attack, distance, dice, setup,
            spend_action=False, advantage_sources=1 if pack else 0,
            feature_id=plan.feature_id, turn_key=turn_key, allow_reckless=True,
            close_enemy_active=False,
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Light extra attack resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Light extra attack could not be resolved.") from exc
