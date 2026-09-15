from __future__ import annotations

import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.combatants import CombatantTemplate, ResourceDefinition

_RESOURCE_ID = "legendary-resistance"
_PATTERN = re.compile(r"Legendary Resistance\s*\((\d+)/Day(?:,\s*or\s*\d+/Day\s+in\s+Lair)?\)\.", re.I)


@lru_cache(maxsize=1)
def _rows() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_legendary_resistance_uses(name: str) -> int | None:
    row = _rows().get(name)
    if row is None:
        raise ValueError(f"No SRD source row for {name!r}.")
    match = _PATTERN.search(str(row.get("traits", "")))
    return int(match.group(1)) if match else None


def complete_monster_legendary_resistance(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    completed: list[CombatantTemplate] = []
    for template in templates:
        if template.kind != "monster":
            completed.append(template)
            continue
        uses = source_legendary_resistance_uses(template.name)
        resources = [item for item in template.resources if item.id != _RESOURCE_ID]
        if uses is not None:
            resources.append(ResourceDefinition(id=_RESOURCE_ID, name="Legendary Resistance", max_uses=uses))
        completed.append(template.model_copy(update={"resources": resources}))
    return completed


def legendary_resistance_trait_issues(template: CombatantTemplate, expected: list[str]) -> tuple[list[str], bool]:
    source_has = "Legendary Resistance" in expected
    matches = [item for item in template.resources if item.id == _RESOURCE_ID]
    if source_has:
        uses = source_legendary_resistance_uses(template.name)
        if len(matches) != 1 or uses is None or matches[0].max_uses != uses:
            return ["trait-runtime-missing:legendary-resistance"], False
        return [], True
    if matches:
        return ["trait-source-missing:legendary-resistance"], False
    return [], False
