from __future__ import annotations

import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

_ABILITY_NAMES = {
    "Str": "strength", "Dex": "dexterity", "Con": "constitution",
    "Int": "intelligence", "Wis": "wisdom", "Cha": "charisma",
}
_SAVE_PATTERN = re.compile(r"\b(Str|Dex|Con|Int|Wis|Cha)\s+\d+\s+([+-]\d+)\s+([+-]\d+)")


def parse_saving_throw_bonuses(row: dict[str, object]) -> dict[str, int]:
    """Parse the six SAVE values from the SRD stat table, never guessing missing modifiers."""
    matches = _SAVE_PATTERN.findall(str(row.get("rawText", "")))
    bonuses = {_ABILITY_NAMES[label]: int(save) for label, _modifier, save in matches}
    if set(bonuses) != set(_ABILITY_NAMES.values()):
        missing = sorted(set(_ABILITY_NAMES.values()) - set(bonuses))
        raise ValueError(f"SRD six-save table incomplete for {row.get('name')!r}: {missing}")
    return bonuses


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_saving_throw_bonuses(name: str) -> dict[str, int]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_saving_throw_bonuses(row)


def with_source_saving_throws(template: CombatantTemplate) -> CombatantTemplate:
    if template.kind != "monster":
        return template
    return template.model_copy(update={"saving_throw_bonuses": source_saving_throw_bonuses(template.name)})


def complete_monster_saving_throws(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [with_source_saving_throws(template) for template in templates]
