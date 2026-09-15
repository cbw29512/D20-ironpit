from __future__ import annotations

import logging
import re

from app.domain.death_triggers import DeathTriggeredSaveEffect
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)

_DEATH_BURST = re.compile(
    r"Death Burst\.\s+.*?explodes when it dies\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*"
    r"DC (?P<dc>\d+), each creature in a (?P<radius>\d+)-foot Emanation originating from the [^.]+\.\s+"
    r"Failure:\s*\d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"(?P<damage_type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage\.\s+"
    r"Success:\s*Half damage\.",
    re.IGNORECASE,
)


def parse_death_trigger_effects(source_traits: object) -> list[DeathTriggeredSaveEffect]:
    """Parse supported source-defined death triggers without claiming runtime certification."""
    try:
        text = str(source_traits or "").strip()
        if "Death Burst." not in text:
            return []
        match = _DEATH_BURST.search(text)
        if match is None:
            raise ValueError("Death Burst source text is present but is not supported by the canonical parser.")
        bonus = int(match.group("bonus") or 0)
        if match.group("sign") == "-":
            bonus *= -1
        damage_type = DamageType(match.group("damage_type").lower())
        return [DeathTriggeredSaveEffect(
            id="death-burst",
            name="Death Burst",
            radius_ft=int(match.group("radius")),
            save_ability=match.group("ability").lower(),
            dc=int(match.group("dc")),
            damage_dice_count=int(match.group("count")),
            damage_dice_size=int(match.group("size")),
            damage_bonus=bonus,
            damage_type=damage_type,
            half_damage_on_success=True,
        )]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse source death-trigger effects.")
        raise RuntimeError("Source death-trigger effects could not be parsed.") from exc
