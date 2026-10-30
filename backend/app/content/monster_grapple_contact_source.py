from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.auras import StartTurnGrappleContactDamage
from app.domain.models import CombatantTemplate
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_BARBED_HIDE = re.compile(
    r"Barbed Hide\.\s+At the start of each of its turns, the [^.]+ deals "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"(?P<dtype>[A-Za-z]+) damage to any creature it is grappling or any creature grappling it\.",
    re.IGNORECASE,
)


def parse_grapple_contact_damage(source_traits: object) -> StartTurnGrappleContactDamage | None:
    try:
        text = str(source_traits or "")
        if "Barbed Hide." not in text:
            return None
        match = _BARBED_HIDE.search(text)
        if match is None:
            raise ValueError("Barbed Hide source text is present but unsupported.")
        bonus = int(match.group("bonus") or 0)
        if match.group("sign") == "-":
            bonus *= -1
        return StartTurnGrappleContactDamage(
            id="barbed-hide",
            name="Barbed Hide",
            damage_dice_count=int(match.group("count")),
            damage_dice_size=int(match.group("size")),
            damage_bonus=bonus,
            damage_type=DamageType(match.group("dtype").lower()),
        )
    except (TypeError, ValueError):
        logger.exception("Invalid grapple-contact source trait.")
        raise
    except Exception as exc:
        logger.exception("Failed to parse grapple-contact source trait.")
        raise RuntimeError("Grapple-contact source trait could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for grapple-contact traits.")
        raise


def complete_monster_grapple_contact_damage(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        completed: list[CombatantTemplate] = []
        rows = _rows_by_name()
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            row = rows.get(template.name)
            if row is None:
                raise ValueError(f"No SRD source row for monster {template.name!r}.")
            completed.append(template.model_copy(update={
                "start_turn_grapple_contact_damage": parse_grapple_contact_damage(
                    row.get("traits", "")
                )
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete monster grapple-contact damage profiles.")
        raise RuntimeError("Monster grapple-contact damage completion failed.") from exc
