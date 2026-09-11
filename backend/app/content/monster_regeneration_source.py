from __future__ import annotations

import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate, DamageType
from app.domain.regeneration import RegenerationRule

_REGEN = re.compile(r"Regeneration\.\s+The\s+[^.]+?\s+regains\s+(\d+)\s+Hit Points at the start of each of its turns\.", re.I)
_SUPPRESS = re.compile(r"If the [^.]+ takes ([A-Za-z]+)(?: or ([A-Za-z]+))? damage, this trait doesn[’']t function on the [^.]+ next turn", re.I)
_DEFERRED_DEATH = re.compile(r"dies only if it starts its turn with 0 Hit Points and doesn[’']t regenerate", re.I)


@lru_cache(maxsize=1)
def _rows() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_regeneration(name: str) -> RegenerationRule | None:
    row = _rows().get(name)
    if row is None:
        raise ValueError(f"No SRD source row for {name!r}.")
    text = str(row.get("traits", ""))
    match = _REGEN.search(text)
    if match is None:
        return None
    suppression = _SUPPRESS.search(text)
    types: list[DamageType] = []
    if suppression:
        for raw in suppression.groups():
            if raw:
                types.append(DamageType(raw.lower()))
    return RegenerationRule(
        hit_points=int(match.group(1)),
        suppressed_by_damage_types=types,
        dies_at_start_turn_if_zero_and_suppressed=bool(_DEFERRED_DEATH.search(text)),
    )


def complete_monster_regeneration(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [
        template.model_copy(update={"regeneration": source_regeneration(template.name)})
        if template.kind == "monster" else template
        for template in templates
    ]
