from __future__ import annotations

import logging

from collections.abc import Iterable

from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
    encounter_states: Iterable[CombatantState] | None = None,
) -> bool:
    try:
        defender_owned = any(source.source_id == attacker_event_id for source in defender.grapple_sources)
        if attack.forbid_target_grappled_by_self and defender_owned:
            return False
        if attack.grapple_target_policy == "normal":
            return True
        if attack.grapple_target_policy != "own_grapple_only":
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
