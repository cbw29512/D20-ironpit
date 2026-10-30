from __future__ import annotations

import logging
import re

from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_SELF_INVISIBILITY = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"The [^.]+ casts Invisibility on itself, requiring no spell components "
    r"and using (?:(?:the same spellcasting ability as Spellcasting)|"
    r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) as the spellcasting ability)\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to derive timed self-buff id from %r.", value)
        raise RuntimeError("Timed self-buff id could not be derived.") from exc


def source_timed_self_buffs(
    monster_name: str,
    actions: object,
    bonus_actions: object,
) -> list[TimedSelfBuffAction]:
    """Compile source-proven self Invisibility casts into the universal buff grammar."""
    try:
        result: list[TimedSelfBuffAction] = []
        for text, cost in ((str(actions or ""), "action"), (str(bonus_actions or ""), "bonus_action")):
            for match in _SELF_INVISIBILITY.finditer(text):
                name = match.group("name").strip()
                result.append(TimedSelfBuffAction(
                    id=f"srd-{_slug(monster_name)}-{_slug(name)}",
                    name=name,
                    action_cost=cost,
                    duration_rounds=600,
                    condition_ids=["invisible"],
                    magical_effect=True,
                    concentration=True,
                    ends_on_owner_attack=True,
                    ends_on_owner_spell_cast=True,
                    priority=70,
                    animation="invisibility",
                ))
        return result
    except Exception as exc:
        logger.exception("Failed source timed self-buff parsing for %s.", monster_name)
        raise RuntimeError("Source timed self-buffs could not be parsed.") from exc


__all__ = ["source_timed_self_buffs"]
