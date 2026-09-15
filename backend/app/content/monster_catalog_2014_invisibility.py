from __future__ import annotations

from app.content.monster_catalog_2014_action_support import action_key_2014
from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.invisibility import InvisibilityAction


def starts_invisible_2014(source: CatalogMonster2014) -> bool:
    return "Invisibility" in source.trait_names


def invisibility_action_2014(source: CatalogMonster2014) -> InvisibilityAction | None:
    action_names = {action_key_2014(name) for name in source.action_names}
    if "invisibility" not in action_names:
        return None
    return InvisibilityAction(
        ends_on_action_ids=["life-drain"] if "life-drain" in action_names else [],
    )
