from __future__ import annotations

import logging
import re

from app.content.monster_source_attack_target_filter import source_target_filter
from app.domain.capability_effects import HitSavingThrowEffectDefinition
from app.domain.zero_hp_replacement import ZeroHpReplacementEffectDefinition

logger = logging.getLogger(__name__)

_CURSE_REPLACEMENT = re.compile(
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"Saving Throw:\s*DC\s*(?P<dc>\d+)\.\s*"
    r"Failure:\s*The target is cursed\.\s*"
    r"If the cursed target drops to 0 Hit Points, it instead becomes an? "
    r"(?P<form>[A-Za-z -]+?) under the GM[’']s control and has (?P<hp>\d+) Hit Points\.\s*"
    r"Success:\s*The target is immune to this [^.]+?[’']s curse for 24 hours\.",
    re.IGNORECASE,
)


def lycanthrope_curse_hit_save(text: str) -> HitSavingThrowEffectDefinition | None:
    """Compile the shared curse/replacement lifecycle from printed source text."""
    try:
        match = _CURSE_REPLACEMENT.search(text)
        if match is None:
            return None
        return HitSavingThrowEffectDefinition(
            save_ability=match.group("ability").lower(),
            dc=int(match.group("dc")),
            target_filter=source_target_filter(text),
            source_effect_immunity_on_success=True,
            failure_effects=[
                ZeroHpReplacementEffectDefinition(
                    effect_id="cursed",
                    replacement_hp=int(match.group("hp")),
                )
            ],
        )
    except (TypeError, ValueError):
        logger.exception("Invalid zero-HP curse replacement source.")
        raise
    except Exception as exc:
        logger.exception("Failed to compile zero-HP curse replacement source.")
        raise RuntimeError("Zero-HP curse replacement source could not be compiled.") from exc


__all__ = ["lycanthrope_curse_hit_save"]
