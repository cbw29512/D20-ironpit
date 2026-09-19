from __future__ import annotations

import json
import logging
from pathlib import Path

from app.domain.combatant_source import (
    HeroBuildSource,
    HeroCatalogSource,
    HeroProgressionSource,
    HeroTrackSource,
    SpeciesSource,
    SubclassProgressionSource,
)

LOGGER = logging.getLogger(__name__)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.exception("Unable to read combatant source JSON path=%s", path)
        raise ValueError(f"Unable to read combatant source JSON: {path}") from exc


def load_hero_build(path: Path) -> HeroBuildSource:
    try:
        return HeroBuildSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero build path=%s", path)
        raise


def load_hero_catalog(path: Path) -> HeroCatalogSource:
    try:
        return HeroCatalogSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero catalog path=%s", path)
        raise


def load_hero_progression(path: Path) -> HeroProgressionSource:
    try:
        return HeroProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero progression path=%s", path)
        raise


def load_subclass_progression(path: Path) -> SubclassProgressionSource:
    try:
        return SubclassProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid subclass progression path=%s", path)
        raise


def load_species(path: Path) -> SpeciesSource:
    try:
        return SpeciesSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid species path=%s", path)
        raise


def load_hero_track(path: Path) -> HeroTrackSource:
    try:
        return HeroTrackSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero track path=%s", path)
        raise


def load_hero_bundle(root: Path, edition: str, slug: str):
    try:
        catalog = load_hero_catalog(root / f"data/heroes/{edition}/heroes.json")
        identity = next(item for item in catalog.heroes if item.id == slug)
        progression = load_hero_progression(
            root / f"data/heroes/{edition}/class_progressions/{identity.class_id}.json"
        )
        subclass = load_subclass_progression(
            root / f"data/heroes/{edition}/subclasses/{identity.subclass_id}.json"
        )
        species = load_species(root / f"data/heroes/{edition}/species/{identity.species}.json")
        track = load_hero_track(root / f"data/heroes/{edition}/tracks/{identity.id}.json")
        build = load_hero_build(root / f"data/heroes/{edition}/builds/{identity.id}.json")
        return identity, progression, subclass, species, track, build
    except Exception:
        LOGGER.exception("Failed to load hero bundle edition=%s slug=%s", edition, slug)
        raise
