from __future__ import annotations

import logging

from app.domain.models import CombatantState

LOGGER = logging.getLogger(__name__)
FEATURE_ID = "boon-combat-prowess"


def apply_peerless_aim(
    attacker: CombatantState,
    hit: bool,
    natural_1: bool,
    turn_key: str | None,
) -> tuple[bool, bool]:
    """Convert one non-natural-1 miss into a hit once per turn (Boon of Combat Prowess)."""
    try:
        if hit or natural_1 or not turn_key:
            return hit, False
        if not attacker.template.progression_features.peerless_aim:
            return False, False
        if attacker.feature_last_turn_keys.get(FEATURE_ID) == turn_key:
            return False, False
        attacker.feature_last_turn_keys[FEATURE_ID] = turn_key
        return True, True
    except Exception:
        LOGGER.exception("Peerless Aim failed for %s", attacker.template.name)
        raise
