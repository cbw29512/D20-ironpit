from __future__ import annotations

import re

from app.content.monster_spell_selection import MONSTER_CASTER_SPELL_SELECTIONS
from app.content.monster_spell_source_parser import spell_daily_uses, spell_save_dc
from app.content.simple_save_damage_spells import build_simple_save_damage_capability


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def curated_spell_save_capabilities(
    row: dict[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Bind reviewed named monster spells to shared spell effects and caster-owned access resources."""
    selection = MONSTER_CASTER_SPELL_SELECTIONS.get(str(row.get("name", "")))
    if selection is None or not selection.included:
        return [], []
    dc = spell_save_dc(row)
    monster_slug = _slug(str(row["name"]))
    actions: list[dict[str, object]] = []
    resources: list[dict[str, object]] = []
    for source_name, runtime_id in selection.included:
        uses = spell_daily_uses(row, source_name)
        resource_id = None if uses is None else f"srd-{monster_slug}-spell-{_slug(runtime_id)}-uses"
        capability = build_simple_save_damage_capability(runtime_id, dc, resource_id=resource_id)
        actions.append(capability.model_dump(mode="json", exclude_none=True))
        if uses is not None:
            resources.append({"id": resource_id, "name": source_name, "max_uses": uses})
    return actions, resources
