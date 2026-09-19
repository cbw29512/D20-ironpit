from __future__ import annotations

import json
import logging
from pathlib import Path

from app.domain.combatant_source import (
    HeroCatalogSource,
    HeroProgressionSource,
    SubclassProgressionSource,
)

LOGGER = logging.getLogger(__name__)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.exception("Unable to read combatant source JSON path=%s", path)
        raise ValueError(f"Unable to read combatant source JSON: {path}") from exc


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


def fold_hero_level(
    progression: HeroProgressionSource,
    subclass: SubclassProgressionSource,
    level: int,
) -> dict[str, object]:
    try:
        if progression.edition != subclass.edition or progression.class_id != subclass.class_id:
            raise ValueError("Class progression and subclass progression must share edition and class.")
        if not 1 <= level <= len(progression.levels):
            raise ValueError(f"Requested level {level} is outside the available progression.")

        state: dict[str, object] = {
            "edition": progression.edition,
            "class_id": progression.class_id,
            "level": level,
            "capabilities": [],
            "arena_ignored": [],
            "resources": {},
        }
        capabilities: list[str] = []
        ignored: list[str] = []
        resources: dict[str, int] = {}
        abilities: dict[str, int] = {}

        for row in progression.levels[:level]:
            dumped = row.model_dump(exclude_none=True)
            for field in ("proficiency_bonus", "max_hp", "attack_count", "weapon_masteries"):
                if field in dumped:
                    state[field] = dumped[field]
            if row.ability_scores:
                abilities.update(row.ability_scores.model_dump(exclude_none=True))
            resources.update(row.resources)
            capabilities = [item for item in capabilities if item not in row.capabilities_removed]
            capabilities.extend(item for item in row.capabilities_added if item not in capabilities)
            ignored.extend(item for item in row.arena_ignored if item not in ignored)

            overlay = subclass.deltas.get(row.level)
            if overlay:
                capabilities = [item for item in capabilities if item not in overlay.capabilities_removed]
                capabilities.extend(item for item in overlay.capabilities_added if item not in capabilities)
                ignored.extend(item for item in overlay.arena_ignored if item not in ignored)

        state["ability_scores"] = abilities
        state["resources"] = resources
        state["capabilities"] = capabilities
        state["arena_ignored"] = ignored
        state["subclass_id"] = subclass.subclass_id
        return state
    except Exception:
        LOGGER.exception(
            "Failed to fold hero progression class=%s subclass=%s level=%s",
            progression.class_id,
            subclass.subclass_id,
            level,
        )
        raise
