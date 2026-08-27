from __future__ import annotations

import logging
from collections.abc import Callable

from app.content.catalog_characters import CHARACTER_BUILDERS
from app.content.catalog_monsters import MONSTER_BUILDERS
from app.domain.catalog import CatalogEntry

logger = logging.getLogger(__name__)
_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    **CHARACTER_BUILDERS,
    **MONSTER_BUILDERS,
}


class CatalogEntryNotFoundError(LookupError):
    pass


def get_catalog_entry(combatant_id: str) -> CatalogEntry:
    try:
        builder = _BUILDERS.get(combatant_id)
        if builder is None:
            raise CatalogEntryNotFoundError(f"Unknown combatant: {combatant_id}")
        return builder()
    except CatalogEntryNotFoundError:
        logger.warning("Catalog lookup failed for %s.", combatant_id)
        raise
    except Exception as exc:
        logger.exception("Catalog entry build failed for %s.", combatant_id)
        raise RuntimeError("Catalog entry could not be built.") from exc


def _list_catalog(builders: dict[str, Callable[[], CatalogEntry]]) -> list[CatalogEntry]:
    try:
        return [builder() for builder in builders.values()]
    except Exception as exc:
        logger.exception("Catalog list build failed.")
        raise RuntimeError("Catalog list could not be built.") from exc


def list_character_catalog() -> list[CatalogEntry]:
    return _list_catalog(CHARACTER_BUILDERS)


def list_monster_catalog() -> list[CatalogEntry]:
    return _list_catalog(MONSTER_BUILDERS)
