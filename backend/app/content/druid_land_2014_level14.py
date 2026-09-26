from __future__ import annotations

import logging

from app.domain.passive_modifiers import PassiveModifierGrant

logger = logging.getLogger(__name__)

_PROTECTED_SOURCE_TYPES = ["beast", "plant"]


def natures_sanctuary_2014(save_dc: int) -> list[PassiveModifierGrant]:
    """Bind Nature's Sanctuary to the universal typed targeting-save gate."""
    try:
        return [
            PassiveModifierGrant(
                source_id="natures-sanctuary",
                source_name="Nature's Sanctuary",
                kind="targeting-save-gate",
                source_creature_types=list(_PROTECTED_SOURCE_TYPES),
                save_ability="wisdom",
                save_dc=save_dc,
                ends_on_owner_attack=False,
                success_immunity_hours=24,
            )
        ]
    except Exception:
        logger.exception("Failed to compile 2014 Nature's Sanctuary.")
        raise
