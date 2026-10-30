from __future__ import annotations

import logging
import re

from app.domain.death_triggers import DeathTriggeredSaveEffect
from app.domain.save_damage import SaveDamageComponent
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_DEATH_TRIGGER = re.compile(
    r"(?P<name>Death Burst|Death Throes)\.\s+.*?explodes when it dies\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*"
    r"DC (?P<dc>\d+), each creature in a (?P<radius>\d+)-foot Emanation originating from the [^.]+\.\s+"
    r"Failure:\s*\d+ \((?P<count1>\d+)d(?P<size1>\d+)(?:\s*(?P<sign1>[+-])\s*(?P<bonus1>\d+))?\) "
    r"(?P<type1>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage"
    r"(?: plus \d+ \((?P<count2>\d+)d(?P<size2>\d+)(?:\s*(?P<sign2>[+-])\s*(?P<bonus2>\d+))?\) "
    r"(?P<type2>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage)?\.\s+"
    r"Success:\s*Half damage\.",
    re.IGNORECASE,
)


def _bonus(match: re.Match[str], suffix: str) -> int:
    try:
        value = int(match.group(f"bonus{suffix}") or 0)
        return -value if match.group(f"sign{suffix}") == "-" else value
    except Exception as exc:
        logger.exception("Failed to parse death-trigger damage bonus.")
        raise RuntimeError("Death-trigger damage bonus could not be parsed.") from exc


def parse_death_trigger_effects(source_traits: object) -> list[DeathTriggeredSaveEffect]:
    """Parse source-defined death-trigger saves, including mixed typed damage."""
    try:
        text = str(source_traits or "").strip()
        if "Death Burst." not in text and "Death Throes." not in text:
            return []
        match = _DEATH_TRIGGER.search(text)
        if match is None:
            raise ValueError("Death-trigger source text is present but is not supported by the canonical parser.")
        name = match.group("name").strip()
        additional: list[SaveDamageComponent] = []
        if match.group("count2") is not None:
            additional.append(SaveDamageComponent(
                dice_count=int(match.group("count2")),
                dice_size=int(match.group("size2")),
                damage_bonus=_bonus(match, "2"),
                damage_type=DamageType(match.group("type2").lower()),
            ))
        return [DeathTriggeredSaveEffect(
            id=re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
            name=name,
            radius_ft=int(match.group("radius")),
            save_ability=match.group("ability").lower(),
            dc=int(match.group("dc")),
            damage_dice_count=int(match.group("count1")),
            damage_dice_size=int(match.group("size1")),
            damage_bonus=_bonus(match, "1"),
            damage_type=DamageType(match.group("type1").lower()),
            additional_damage_components=additional,
            half_damage_on_success=True,
        )]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse source death-trigger effects.")
        raise RuntimeError("Source death-trigger effects could not be parsed.") from exc
