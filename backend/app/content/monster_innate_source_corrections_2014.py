from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_DAMAGED_TRAITS = (
    "<em><strong>Fear Aura.</strong></em>incapacitatedfrightened"
    "<em><strong>Magic Resistance.</strong></em>"
    "<em><strong>Magic Weapons.</strong></em>"
    "<em><strong>Innate Spellcasting.</strong></em>"
    "detect magicfireballhold monsterwall of fire"
)
_DAMAGED_UNSUPPORTED = (
    "Fear Aura. incapacitatedfrightened Magic Resistance. Magic Weapons. "
    "Innate Spellcasting. detect magicfireballhold monsterwall of fire"
)


def corrected_innate_spellcasting_2014(
    monster: SourceMonster2014,
) -> dict[str, object] | None:
    """Return a reviewed structured view only for the exact damaged SRD ingest."""
    try:
        raw = monster.innate_spellcasting
        if not isinstance(raw, dict):
            return None
        expected = {
            "ability": "charisma",
            "spells": [],
            "source_complete": False,
            "unsupported_text": _DAMAGED_UNSUPPORTED,
        }
        if raw != expected or monster.source_traits != _DAMAGED_TRAITS:
            return raw
        return {
            "ability": "charisma",
            "save_dc": 21,
            "spells": [
                {
                    "id": "detect-magic", "name": "detect magic",
                    "usage": "at_will", "uses_per_day": None,
                    "shared_pool": False, "qualifier": None,
                },
                {
                    "id": "fireball", "name": "fireball",
                    "usage": "at_will", "uses_per_day": None,
                    "shared_pool": False, "qualifier": None,
                },
                {
                    "id": "hold-monster", "name": "hold monster",
                    "usage": "per_day", "uses_per_day": 3,
                    "shared_pool": False, "qualifier": None,
                },
                {
                    "id": "wall-of-fire", "name": "wall of fire",
                    "usage": "per_day", "uses_per_day": 3,
                    "shared_pool": False, "qualifier": None,
                },
            ],
            "source_complete": True,
            "unsupported_text": None,
        }
    except Exception:
        logger.exception(
            "Failed to apply reviewed 2014 innate-spell source correction for %s.",
            monster.id,
        )
        raise
