from __future__ import annotations

import logging

from collections.abc import Iterable

from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def target_grappled_by_attacker(
    attacker_event_id: str,
    defender: CombatantState,
) -> bool:
    return any(source.source_id == attacker_event_id for source in defender.grapple_sources)


def attack_is_automatic_hit(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
) -> bool:
    """Return whether a declared attack automatically hits its own held target."""
    return (
        attack.grapple_target_policy == "auto_hit_own_grapple"
        and target_grappled_by_attacker(attacker_event_id, defender)
    )


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
    encounter_states: Iterable[CombatantState] | None = None,
) -> bool:
    try:
        defender_owned = target_grappled_by_attacker(attacker_event_id, defender)
        if attack.forbid_target_grappled_by_self and defender_owned:
            return False
        if attack.grapple_target_policy == "normal":
            return True
        if attack.grapple_target_policy not in {"own_grapple_only", "auto_hit_own_grapple"}:
            raise ValueError(f"Unsupported grapple target policy: {attack.grapple_target_policy}")
        if defender_owned:
            return True
        if encounter_states is None:
            return True
        return not any(
            any(source.source_id == attacker_event_id for source in state.grapple_sources)
            for state in encounter_states
        )
    except Exception as exc:
        logger.exception("Failed to evaluate target legality for attack %s.", attack.id)
        raise RuntimeError("Attack target legality could not be evaluated.") from exc
