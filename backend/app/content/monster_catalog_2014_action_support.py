from __future__ import annotations

import re
import unicodedata

from app.content.monster_catalog_2014_models import CatalogMonster2014


def action_key_2014(value: str) -> str:
    clean = re.sub(r"\s*\(Recharge\s+[^)]+\)", "", value, flags=re.I).rstrip(".")
    text = unicodedata.normalize("NFKD", clean).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def supported_action_ids_2014(source: CatalogMonster2014) -> set[str]:
    supported = {attack.id for attack in source.attacks}
    supported.update(action.id for action in source.saving_throw_actions)
    supported.update(
        action.resource_id for action in source.saving_throw_actions if action.resource_id
    )
    if source.multiattack_slots:
        supported.add("multiattack")
    return supported


def unresolved_actions_2014(source: CatalogMonster2014) -> list[str]:
    supported = supported_action_ids_2014(source)
    return [name for name in source.action_names if action_key_2014(name) not in supported]
