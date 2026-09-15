from __future__ import annotations

import logging

from app.combat.ongoing_damage_policy import source_attacks_blocked
from app.domain.models import CombatantState, WeaponAttack
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _held_by_attack(attack: WeaponAttack, attacker_event_id: str, defender: CombatantState) -> bool:
    return any(
        source.source_id == attacker_event_id and source.source_effect_id == attack.id
        for source in defender.grapple_sources
    )


def attack_is_automatic_hit(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
) -> bool:
    return attack.grapple_target_policy == "auto_hit_own_grapple" and _held_by_attack(
        attack, attacker_event_id, defender,
    )


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
    opponent_states: list[CombatantState] | None = None,
) -> bool:
    try:
        if opponent_states is not None and source_attacks_blocked(attacker_event_id, opponent_states):
            return False
        restraint = attack.breakable_restraint
        if restraint is not None:
            if restraint.max_target_size is not None and not size_at_most(defender.template.size, restraint.max_target_size):
                return False
            if any(source.source_id == attacker_event_id and source.source_effect_id == attack.id for source in defender.restraint_sources):
                return False
        if attack.forbid_target_grappled_by_self and any(
            source.source_id == attacker_event_id for source in defender.grapple_sources
        ):
            return False
        restrict_to_held = attack.grapple_target_policy in {"auto_hit_own_grapple", "own_grapple_only"}
        if not restrict_to_held or opponent_states is None:
            return True
        held_any = any(_held_by_attack(attack, attacker_event_id, state) for state in opponent_states)
        return not held_any or _held_by_attack(attack, attacker_event_id, defender)
    except Exception as exc:
        logger.exception("Failed to evaluate target legality for attack %s.", attack.id)
        raise RuntimeError("Attack target legality could not be evaluated.") from exc
