from __future__ import annotations

import logging
from copy import deepcopy

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014

logger = logging.getLogger(__name__)

_CORRECTIONS = {
    ("warhorse", "hooves"): {
        "expected": {"minimum_move_ft": 20, "prone_save_ability": "strength", "prone_save_dc": 14},
        "follow_up_attack_id": "hooves",
    },
}


def corrected_charge_profile_2014(monster: SourceMonster2014, attack: SourceAttack2014) -> object | None:
    """Apply reviewed parser corrections while failing closed if the pinned source shape drifts."""
    try:
        profile = attack.charge_profile
        correction = _CORRECTIONS.get((monster.id, attack.id))
        if correction is None:
            return profile
        expected = correction["expected"]
        if profile != expected:
            raise RuntimeError(
                f"2014 Charge correction source drift for {monster.id}/{attack.id}: {profile!r} != {expected!r}"
            )
        corrected = deepcopy(profile)
        assert isinstance(corrected, dict)
        corrected["follow_up_attack_id"] = correction["follow_up_attack_id"]
        return corrected
    except Exception:
        logger.exception("Failed to apply 2014 Charge source correction for %s/%s.", monster.id, attack.id)
        raise
