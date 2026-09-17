from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import FRENZY_2014_EFFECT_ID, rage_active
from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.pit_policy import choose_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttackKind

logger = logging.getLogger(__name__)


def resolve_frenzy_bonus_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the 2014 Berserker's one Bonus Action melee attack after its Frenzy-entry turn."""
    try:
        state = attacker.state
        started = state.frenzy_2014_started_round
        if (
            state.template.ruleset != "2014"
            or not state.template.progression_features.frenzy_bonus_attack_2014
            or FRENZY_2014_EFFECT_ID not in state.active_effect_ids
            or not rage_active(state)
            or started is None
            or round_number <= started
            or state.turn_terminated
            or is_incapacitated(state)
            or not is_available(state, "bonus_action")
        ):
            return [], sequence
        attack_ids = [state.template.weapon_attack.id, *(attack.id for attack in state.template.alternate_weapon_attacks)]
        choice = choose_attack(attacker, setup, attack_ids, kind=WeaponAttackKind.MELEE)
        if choice is None:
            return [], sequence
        target, attack, distance = choice
        spend(state, "bonus_action")
        event = resolve_encounter_attack(
            sequence, round_number, attacker, target, attack, distance, dice, setup,
            spend_action=False, feature_id=FRENZY_2014_EFFECT_ID, turn_key=turn_key, allow_reckless=False,
        )
        event.description += " 2014 Frenzy uses the Bonus Action melee attack."
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("2014 Frenzy attack failed for %s.", attacker.combatant_id)
        raise RuntimeError("2014 Frenzy bonus attack could not be resolved.") from exc
