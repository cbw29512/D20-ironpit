from __future__ import annotations

from app.content.hero_catalog import build_hero_catalog
from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import FullContentCatalog


def build_full_content_catalog() -> FullContentCatalog:
    heroes = build_hero_catalog()
    monsters = build_monster_catalog()
    return FullContentCatalog(
        hero_count=len(heroes),
        monster_count=len(monsters),
        heroes=heroes,
        monsters=monsters,
    )
