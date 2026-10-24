from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# The 327-card ingest retained only the heading plus semantic tokens for this
# SRD 5.1 trait. Keep the correction content-owned and drift-checked; combat
# runtime never sees or dispatches on this source identity.
_EXPECTED_DAMAGED_SOURCE = (
    "<em><strong>Fear Aura.</strong></em>incapacitatedfrightened"
    "<em><strong>Magic Resistance.</strong></em>"
    "<em><strong>Magic Weapons.</strong></em>"
    "<em><strong>Innate Spellcasting.</strong></em>"
    "detect magicfireballhold monsterwall of fire"
)
_REVIEWED_FEAR_AURA = (
    "Fear Aura. Any creature hostile to the pit fiend that starts its turn within "
    "20 feet of the pit fiend must make a DC 21 Wisdom saving throw, unless the "
    "pit fiend is incapacitated. On a failed save, the creature is frightened "
    "until the start of its next turn. If a creature's saving throw is successful, "
    "the creature is immune to the pit fiend's Fear Aura for the next 24 hours."
)


def corrected_condition_aura_source_2014(source_traits: object) -> str:
    """Restore one reviewed source clause only while the damaged ingest fingerprint matches."""
    try:
        raw = str(source_traits or "")
        if raw != _EXPECTED_DAMAGED_SOURCE:
            return raw
        return f"{_REVIEWED_FEAR_AURA} {raw}"
    except Exception:
        logger.exception("Failed to apply reviewed 2014 condition-aura source correction.")
        raise
