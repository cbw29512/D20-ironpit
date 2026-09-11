from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.auras import EndTurnDamageAura
from app.domain.models import CombatantTemplate, DamageType

logger = logging.getLogger(__name__)
_FIRE_AURA = re.compile(
    r"Fire Aura\.\s+At the end of each of the [^.]+ turns, each creature(?: of the [^.]+ choice)? "
    r"in a (?P<radius>\d+)-foot Emanation originating from the [^.]+ takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"(?P<dtype>[A-Za-z]+) damage(?P<tail>[^.]*)\.",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_end_turn_damage_auras(name: str) -> list[EndTurnDamageAura]:
    """Compile supported printed end-turn damage auras; runtime remains source-name agnostic."""
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    text = str(row.get("traits", ""))
    match = _FIRE_AURA.search(text)
    if not match:
        return []
    bonus = int(match.group("bonus") or 0)
    if match.group("sign") == "-":
        bonus = -bonus
    return [EndTurnDamageAura(
        id="fire-aura", name="Fire Aura", radius_ft=int(match.group("radius")),
        damage_dice_count=int(match.group("count")), damage_dice_size=int(match.group("size")),
        damage_bonus=bonus, damage_type=DamageType(match.group("dtype").lower()),
        disabled_while_incapacitated="incapacitated condition" in match.group("tail").lower(),
    )]


def complete_monster_end_turn_damage_auras(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"end_turn_damage_auras": source_end_turn_damage_auras(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception as exc:
        logger.exception("Failed to derive monster end-turn damage auras from SRD source.")
        raise RuntimeError("Monster aura source compilation failed.") from exc


def fire_aura_source_is_fully_modeled(row: dict[str, object]) -> bool:
    """Only the pure damage aura is certified; ignition/burning clauses remain blockers."""
    text = str(row.get("traits", ""))
    if not _FIRE_AURA.search(text):
        return False
    lowered = text.lower()
    return not any(term in lowered for term in ("burning", "ignite", "ignites", "catches fire"))
