from __future__ import annotations

import logging
import re

from app.domain.capability_effects import HitSavingThrowEffectDefinition
from app.domain.ongoing_hp_loss import OngoingHpLossEffectDefinition

logger = logging.getLogger(__name__)
_ONGOING_HP_LOSS = re.compile(
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*"
    r"DC\s*(?P<dc>\d+)\.\s*Failure:\s*The target receives an? (?P<name>[^.]+)\.\s*"
    r"While wounded, the target loses \d+ \((?P<count>\d+)d(?P<size>\d+)\) Hit Points "
    r"at the start of each of its turns\.\s*"
    r"The wound closes after (?P<minutes>\d+) minute(?:s)?, after a spell restores Hit Points to the target, "
    r"or after the target or a creature within (?P<range>\d+) feet of it takes an action to stanch the wound, "
    r"doing so by succeeding on a DC (?P<remove_dc>\d+) Wisdom \(Medicine\) check\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed ongoing HP-loss source id derivation.")
        raise RuntimeError("Ongoing HP-loss source id could not be derived.") from exc


def ongoing_hp_loss_hit_save(text: str) -> HitSavingThrowEffectDefinition | None:
    """Compile a failed on-hit save into a non-damage recurring HP-loss wound."""
    try:
        match = _ONGOING_HP_LOSS.search(text)
        if match is None:
            return None
        name = match.group("name").strip()
        effect_id = _slug(name)
        effect = OngoingHpLossEffectDefinition(
            effect_id=effect_id,
            name=name.title(),
            dice_count=int(match.group("count")),
            dice_size=int(match.group("size")),
            duration_rounds=int(match.group("minutes")) * 10,
            ends_on_spell_healing=True,
            removal_ability="wisdom",
            removal_skill="medicine",
            removal_dc=int(match.group("remove_dc")),
            removal_range_ft=int(match.group("range")),
        )
        return HitSavingThrowEffectDefinition(
            save_ability=match.group("ability").lower(),
            dc=int(match.group("dc")),
            failure_effects=[effect],
            forbid_target_ongoing_hp_loss_id=effect_id,
        )
    except (TypeError, ValueError):
        logger.exception("Invalid ongoing HP-loss source text.")
        raise
    except Exception as exc:
        logger.exception("Ongoing HP-loss source parsing failed.")
        raise RuntimeError("Ongoing HP-loss source could not be parsed.") from exc
